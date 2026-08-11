# Geomatics i18n
#
# Switches Region and Department from `code` (a country-specific string,
# e.g. French INSEE region/department code) as primary key to the surrogate
# `id` added in the previous migration, so `code` can become a plain,
# per-country-scoped field instead of a globally-unique identifier.
#
# `code` is still referenced, as a *foreign key target*, by every table that
# stores a Department/Region reference (Commune.department, Department.region,
# and every M2M through-table: UserProfile.departments, Organization.departments,
# Resource.departments, Task.departments, DSResource.departments,
# AdvisorAccessRequest.departments). Postgres refuses to drop the old
# `code` primary key while those foreign keys still target it, so the actual
# database changes (in `database_operations` below) repoint every one of
# those columns onto `id` *before* dropping the old `code` primary key - in
# an order Postgres will actually accept. Django's autodetector cannot
# generate this by itself (it doesn't touch the tables owned by other apps
# just because a referenced model's PK type changes), hence the
# SeparateDatabaseAndState split: Django's migration *state* below matches
# the desired model definition exactly, the real SQL just gets there safely.
#
# Column type changes (ALTER COLUMN TYPE) and constraint add/drop have no
# Django ORM equivalent - they're plain SQL. But the actual *data* move for
# each repoint (translating existing `code` values into the matching
# `id`, and back) is expressed through the ORM (Subquery/OuterRef) against
# the historical models, not a hand-written UPDATE ... FROM join. This only
# works because `id` was added in the *previous*, ordinary migration
# (0008_region_department_surrogate_id): a RunPython inside this migration's
# SeparateDatabaseAndState only ever sees the project state as of before
# *this* migration, so `id` has to already be tracked state by then, not
# something this same migration's own state_operations introduces.
#
# Constraint names are looked up dynamically (information_schema) rather
# than hardcoded: Django auto-generates them as a hash of table/column
# names, and while that hash is deterministic for a given migration
# history, nothing guarantees every database ran the exact same history
# (squashed migrations, historical app/table renames, manual tweaks). Each
# repoint reuses whatever name is already in place, so the constraint's
# name never actually changes underneath it.
#
# The metrics app's "users" materialized view (built outside Django's
# migration graph entirely, by the `update_materialized_views` management
# command) selects `profile__departments__code`, i.e. it depends on
# `home_userprofile_departments.department_id`. Postgres refuses *any*
# schema change to a column a materialized view depends on - not just
# DROP COLUMN, ALTER COLUMN TYPE too - so that view (base + one per site)
# has to be dropped immediately before repointing that specific table and
# recreated immediately after, both directions.

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import migrations, models
from django.db.models import BigIntegerField, OuterRef, Subquery
from django.db.models.functions import Cast
import django.db.models.deletion

from recoco.apps.metrics.processor import MaterializedView


def get_users_materialized_view():
    for spec in settings.METRICS_MATERIALIZED_VIEWS_SPEC:
        if spec.get("name") == "users":
            return MaterializedView.from_spec(spec=spec)
    raise RuntimeError("No 'users' materialized view spec found")


def drop_materialized_views_depending_on(cursor, table, column):
    """Drop every materialized view that depends on this column, found via
    catalog introspection rather than the current METRICS_MATERIALIZED_VIEWS_SPEC
    + Site rows - environments accumulate orphaned per-site metrics schemas
    (renamed/decommissioned sites, older view names no longer in the spec)
    that a spec-and-Site-driven drop would silently miss, and Postgres
    refuses to ALTER a column any of them still reference, tracked or not.
    Nothing here is recreated from this generic pass - only
    recreate_users_materialized_view (spec + current Site rows) rebuilds
    what should actually still exist.
    """
    cursor.execute(
        """
        SELECT DISTINCT dependent_ns.nspname, dependent_view.relname
        FROM pg_depend
        JOIN pg_rewrite ON pg_depend.objid = pg_rewrite.oid
        JOIN pg_class AS dependent_view ON pg_rewrite.ev_class = dependent_view.oid
        JOIN pg_class AS source_table ON pg_depend.refobjid = source_table.oid
        JOIN pg_namespace dependent_ns ON dependent_ns.oid = dependent_view.relnamespace
        JOIN pg_attribute
          ON pg_depend.refobjid = pg_attribute.attrelid
         AND pg_depend.refobjsubid = pg_attribute.attnum
        WHERE source_table.relname = %s
          AND pg_attribute.attname = %s
          AND dependent_view.relkind = 'm'
        """,
        [table, column],
    )
    # CASCADE: per-site views select FROM the base `metrics.users` view, so
    # without it, dropping `metrics.users` before its per-site dependents
    # (fetch order isn't guaranteed to respect that) fails. Every view this
    # could cascade into is already one this query would find and drop on
    # its own, since they all depend on the same source column.
    for schema, view in cursor.fetchall():
        cursor.execute(f"DROP MATERIALIZED VIEW {schema}.{view} CASCADE")


def recreate_users_materialized_view(cursor):
    mv = get_users_materialized_view()
    mv.set_cursor(cursor)
    mv.create()
    mv.refresh()
    for site in Site.objects.order_by("id"):
        mv.create_for_site(site=site)
        mv.refresh_for_site(site=site)


# Every model whose column(s) reference Department, as (app_label,
# model_name, field_name). A plain ForeignKey resolves to the model itself;
# a ManyToManyField resolves to its Django-managed through model.
DEPARTMENT_REFERENCES = [
    ("geomatics", "commune", "department"),
    ("addressbook", "organization", "departments"),
    ("demarches_simplifiees", "dsresource", "departments"),
    ("home", "advisoraccessrequest", "departments"),
    ("home", "userprofile", "departments"),
    ("tasks", "taskrecommendation", "departments"),
    ("resources", "resource", "departments"),
]


def get_fk_constraint_name(cursor, table, column):
    cursor.execute(
        """
        SELECT tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_name = %s
          AND kcu.column_name = %s
        """,
        [table, column],
    )
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError(f"No foreign key found on {table}.{column}")
    return row[0]


def drop_pattern_ops_indexes(cursor, table, column):
    """Drop any varchar_pattern_ops/text_pattern_ops index Django added on
    this column (to support LIKE queries under a non-C locale) - Postgres
    refuses to convert such an index in place when the column's type
    changes to something non-textual (bigint), so it has to go before
    ALTER COLUMN TYPE. Not worth recreating: a numeric column gets no
    benefit from a pattern-ops index.
    """
    cursor.execute(
        "SELECT indexname, indexdef FROM pg_indexes WHERE tablename = %s", [table]
    )
    for indexname, indexdef in cursor.fetchall():
        if f"({column} varchar_pattern_ops)" in indexdef or (
            f"({column} text_pattern_ops)" in indexdef
        ):
            cursor.execute(f"DROP INDEX {indexname}")


def get_pk_constraint_name(cursor, table):
    cursor.execute(
        """
        SELECT conname FROM pg_constraint
        WHERE contype = 'p' AND conrelid = %s::regclass
        """,
        [table],
    )
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError(f"No primary key found on {table}")
    return row[0]


def get_unique_constraint_on_column(cursor, table, column):
    """Return (name, [columns]) for a UNIQUE constraint involving this
    column (e.g. every M2M through table's implicit unique_together on
    (parent_id, department_id)), or None if there isn't one."""
    cursor.execute(
        """
        SELECT tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'UNIQUE'
          AND tc.table_name = %s
          AND kcu.column_name = %s
        """,
        [table, column],
    )
    row = cursor.fetchone()
    if row is None:
        return None
    name = row[0]
    cursor.execute(
        """
        SELECT column_name FROM information_schema.key_column_usage
        WHERE constraint_name = %s
        ORDER BY ordinal_position
        """,
        [name],
    )
    return name, [r[0] for r in cursor.fetchall()]


def resolve_department_reference(apps, app_label, model_name, field_name):
    """Return (model, column) actually holding the department_id FK: the
    model itself for a plain ForeignKey, or its auto-generated M2M through
    model for a ManyToManyField."""
    model = apps.get_model(app_label, model_name)
    field = model._meta.get_field(field_name)
    if field.many_to_many:
        return field.remote_field.through, "department_id"
    return model, field.attname


def repoint_fk(cursor, referencing_model, column, target_model, target_table):
    """Move `referencing_model.<column>` from holding `target_model.code`
    values to holding `target_model.id` values, and repoint the FK
    constraint accordingly.

    A UNIQUE constraint involving this column (every M2M through table
    has one on (parent_id, department_id), from Django's own
    unique_together) is a separate problem: it's checked immediately per
    row, not deferred, and a bulk value *swap* can transiently collide -
    e.g. department A's new id happening to equal department B's old
    code - even though the final state has no real duplicates. Only
    FOREIGN KEY constraints support toggling deferrability in place
    (`ALTER CONSTRAINT`); a UNIQUE constraint has to be dropped and
    recreated either way, so it's dropped for the duration of the update
    and recreated identically right after.
    """
    table = referencing_model._meta.db_table
    constraint = get_fk_constraint_name(cursor, table, column)
    cursor.execute(f"ALTER TABLE {table} DROP CONSTRAINT {constraint}")

    unique_name = unique_columns = None
    unique = get_unique_constraint_on_column(cursor, table, column)
    if unique:
        unique_name, unique_columns = unique
        cursor.execute(f"ALTER TABLE {table} DROP CONSTRAINT {unique_name}")

    referencing_model.objects.update(
        **{
            column: Subquery(
                target_model.objects.filter(code=OuterRef(column)).values("id")[:1]
            )
        }
    )
    # The UPDATE above queues a pending trigger event for *every* deferred
    # constraint on this table, not just the one on this column - e.g.
    # resources_resource_departments also has a deferred FK on
    # resource_id, untouched by this UPDATE, but Postgres still refuses
    # any further ALTER TABLE on the table until that's cleared.
    cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
    drop_pattern_ops_indexes(cursor, table, column)
    cursor.execute(
        f"ALTER TABLE {table} ALTER COLUMN {column} TYPE bigint USING {column}::bigint"
    )

    if unique_name and unique_columns:
        cols = ", ".join(unique_columns)
        cursor.execute(
            f"ALTER TABLE {table} ADD CONSTRAINT {unique_name} UNIQUE ({cols})"
        )

    cursor.execute(
        f"ALTER TABLE {table} ADD CONSTRAINT {constraint} FOREIGN KEY ({column}) "
        f"REFERENCES {target_table}(id) DEFERRABLE INITIALLY DEFERRED"
    )


def unrepoint_fk(
    cursor, referencing_model, column, target_model, target_table, code_max_length
):
    """Reverse of repoint_fk: move `referencing_model.<column>` from
    `target_model.id` values back to `target_model.code` values. Same
    transient-collision risk applies in reverse, so the same
    drop/recreate dance around any UNIQUE constraint on this column."""
    table = referencing_model._meta.db_table
    constraint = get_fk_constraint_name(cursor, table, column)
    cursor.execute(f"ALTER TABLE {table} DROP CONSTRAINT {constraint}")

    unique_name = unique_columns = None
    unique = get_unique_constraint_on_column(cursor, table, column)
    if unique:
        unique_name, unique_columns = unique
        cursor.execute(f"ALTER TABLE {table} DROP CONSTRAINT {unique_name}")

    cursor.execute(
        f"ALTER TABLE {table} ALTER COLUMN {column} "
        f"TYPE varchar({code_max_length}) USING {column}::text"
    )
    referencing_model.objects.update(
        **{
            column: Subquery(
                target_model.objects.filter(
                    id=Cast(OuterRef(column), output_field=BigIntegerField())
                ).values("code")[:1]
            )
        }
    )
    # See repoint_fk: the UPDATE queues a pending trigger event for every
    # deferred constraint on this table, not just this column's.
    cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")

    if unique_name and unique_columns:
        cols = ", ".join(unique_columns)
        cursor.execute(
            f"ALTER TABLE {table} ADD CONSTRAINT {unique_name} UNIQUE ({cols})"
        )

    cursor.execute(
        f"ALTER TABLE {table} ADD CONSTRAINT {constraint} FOREIGN KEY ({column}) "
        f"REFERENCES {target_table}(code) DEFERRABLE INITIALLY DEFERRED"
    )


def promote_id_to_pk(cursor, table):
    """Swap the primary key from `code` to `id`, reusing the plain unique
    index the previous migration created on `id` (`<table>_id_key`) - an
    index promoted this way keeps its identity, so any FK already
    depending on it (every dependent was repointed onto `id` just above)
    survives untouched. No full index rebuild needed.
    """
    old_pk = get_pk_constraint_name(cursor, table)
    cursor.execute(f"ALTER TABLE {table} DROP CONSTRAINT {old_pk}")
    cursor.execute(
        f"ALTER TABLE {table} ADD CONSTRAINT {old_pk} "
        f"PRIMARY KEY USING INDEX {table}_id_key"
    )


def demote_id_from_pk(cursor, table):
    """Reverse of promote_id_to_pk: swap the primary key back to `code`
    (via the plain unique index on `code` created earlier in
    remove_surrogate_pks - the caller must repoint every dependent off
    `id` *before* calling this, for the same reason promote_id_to_pk's
    docstring gives in reverse: dropping the id-based PK constraint here
    destroys its backing index, and Postgres won't allow that while any
    live FK still depends on it), and restores a plain unique index on
    `id` so the column stays consistent with the previous migration's
    state (`BigIntegerField(unique=True)`) if only this migration is
    reversed.
    """
    old_pk = get_pk_constraint_name(cursor, table)
    cursor.execute(f"ALTER TABLE {table} DROP CONSTRAINT {old_pk}")
    cursor.execute(
        f"ALTER TABLE {table} ADD CONSTRAINT {old_pk} "
        f"PRIMARY KEY USING INDEX {table}_code_key"
    )
    cursor.execute(f"CREATE UNIQUE INDEX {table}_id_key ON {table} (id)")


def add_surrogate_pks(apps, schema_editor):
    Region = apps.get_model("geomatics", "Region")
    Department = apps.get_model("geomatics", "Department")

    with schema_editor.connection.cursor() as cursor:
        # 1. Move every dependent's *values* from code to id via the ORM,
        #    then repoint the column/constraint onto the surrogate id.
        repoint_fk(cursor, Department, "region_id", Region, "geomatics_region")

        for app_label, model_name, field_name in DEPARTMENT_REFERENCES:
            model, column = resolve_department_reference(
                apps, app_label, model_name, field_name
            )
            is_user_profile = (app_label, model_name) == ("home", "userprofile")
            if is_user_profile:
                drop_materialized_views_depending_on(
                    cursor, "home_userprofile_departments", "department_id"
                )
            repoint_fk(cursor, model, column, Department, "geomatics_department")
            if is_user_profile:
                recreate_users_materialized_view(cursor)

        # 2. Nothing references the old `code` primary keys anymore: drop
        #    them and promote `id` to be the real primary key.
        promote_id_to_pk(cursor, "geomatics_region")
        promote_id_to_pk(cursor, "geomatics_department")

        # 3. Composite uniqueness matching the new Meta.unique_together.
        cursor.execute(
            "ALTER TABLE geomatics_region ADD CONSTRAINT geomatics_region_country_code_uniq "
            "UNIQUE (country_id, code)"
        )
        cursor.execute(
            "ALTER TABLE geomatics_department ADD CONSTRAINT geomatics_department_region_code_uniq "
            "UNIQUE (region_id, code)"
        )

        # 4. country is now required (already backfilled to France in an
        #    earlier migration).
        cursor.execute(
            "ALTER TABLE geomatics_region ALTER COLUMN country_id SET NOT NULL"
        )


def remove_surrogate_pks(apps, schema_editor):
    Region = apps.get_model("geomatics", "Region")
    Department = apps.get_model("geomatics", "Department")

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "ALTER TABLE geomatics_region ALTER COLUMN country_id DROP NOT NULL"
        )
        cursor.execute(
            "ALTER TABLE geomatics_department DROP CONSTRAINT geomatics_department_region_code_uniq"
        )
        cursor.execute(
            "ALTER TABLE geomatics_region DROP CONSTRAINT geomatics_region_country_code_uniq"
        )

        # `code` needs its own unique target again before any dependent can
        # repoint back onto it - a plain index, independent of `id`'s
        # current PK, so this doesn't touch anything the still-live
        # (id-based) dependents currently reference.
        cursor.execute(
            "CREATE UNIQUE INDEX geomatics_department_code_key ON geomatics_department (code)"
        )
        cursor.execute(
            "CREATE UNIQUE INDEX geomatics_region_code_key ON geomatics_region (code)"
        )

        # Repoint every dependent from `id` back onto `code`, in reverse
        # order (cosmetic - each repoint is independent). This has to
        # happen *before* demote_id_from_pk: demoting drops the id-based
        # PK constraint, which destroys its backing index, and Postgres
        # won't allow that while any dependent's FK still targets it.
        for app_label, model_name, field_name in reversed(DEPARTMENT_REFERENCES):
            model, column = resolve_department_reference(
                apps, app_label, model_name, field_name
            )
            if (app_label, model_name) == ("home", "userprofile"):
                # Not recreated here: recreate_users_materialized_view
                # builds its SQL from the *currently loaded* models.py
                # (sql_queries/users.py, via the live ORM), which already
                # assumes the post-migration, id-based FK shape - it can
                # only ever generate a query matching that shape,
                # regardless of which direction this migration is
                # running. Recreating it here, mid-reversal, while the
                # column is transiently back to varchar/code, would
                # build a query that doesn't match the schema it's
                # running against. A real rollback pairs this reversal
                # with reverting the codebase too (standard Django
                # migration practice) - at that point the *older*
                # sql_queries/users.py is what's loaded, and recreating
                # the view is that older code's concern, not this
                # migration's.
                drop_materialized_views_depending_on(
                    cursor, "home_userprofile_departments", "department_id"
                )
            unrepoint_fk(cursor, model, column, Department, "geomatics_department", 3)

        unrepoint_fk(cursor, Department, "region_id", Region, "geomatics_region", 2)

        demote_id_from_pk(cursor, "geomatics_department")
        demote_id_from_pk(cursor, "geomatics_region")


class Migration(migrations.Migration):
    dependencies = [
        ("geomatics", "0008_region_department_surrogate_id"),
        ("home", "0045_siteconfiguration_plugin_fields"),
        ("addressbook", "0013_alter_organization_name"),
        ("resources", "0033_resource_support_orga"),
        (
            "tasks",
            "0008_rename_condition_tags_taggit_taskrecommendation_condition_tags",
        ),
        ("demarches_simplifiees", "0006_delete_dsfolder"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_surrogate_pks, remove_surrogate_pks),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name="department",
                    name="code",
                    field=models.CharField(max_length=3),
                ),
                migrations.AlterField(
                    model_name="region",
                    name="code",
                    field=models.CharField(max_length=2),
                ),
                migrations.AlterField(
                    model_name="department",
                    name="id",
                    field=models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                migrations.AlterField(
                    model_name="region",
                    name="id",
                    field=models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                migrations.AlterField(
                    model_name="region",
                    name="country",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="regions",
                        to="geomatics.country",
                    ),
                ),
                migrations.AlterUniqueTogether(
                    name="department",
                    unique_together={("region", "code")},
                ),
                migrations.AlterUniqueTogether(
                    name="region",
                    unique_together={("country", "code")},
                ),
            ],
        ),
    ]
