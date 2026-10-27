from django.db.models import QuerySet
from watson import search as watson
from watson.models import SearchEntry

from .resolvers import get_enabled_plugins
from .utils import is_plugin_label


def tenant_search_models(models=None):
    """Scope a watson ``models`` list (models and/or querysets) to the current
    tenant.

    Plugin tables are shared by all tenants, and so is the watson index, so:

    - plugin models of a plugin that is not enabled for the tenant are dropped;
    - the others are restricted to the current site (``on_site``), which makes
      watson filter the index entries on ``object_id IN (subquery)``.

    Core models are returned unchanged. ``None`` means every registered model,
    like ``watson.search``.
    """
    if models is None:
        models = watson.get_registered_models()

    enabled_plugins = get_enabled_plugins()
    scoped = []
    for model in models:
        if isinstance(model, QuerySet):
            model_cls, queryset = model.model, model
        else:
            model_cls, queryset = model, None

        app_label = model_cls._meta.app_label
        if not is_plugin_label(app_label):
            scoped.append(model)
            continue
        if app_label not in enabled_plugins:
            continue
        # an enabled plugin's model
        if queryset is None:
            # Keep the adapter's live queryset, as watson would
            queryset = watson.get_adapter(model_cls).get_live_queryset()
        on_site = model_cls.on_site.all()
        scoped.append(on_site if queryset is None else queryset & on_site)
    return scoped


def tenant_search(search_text, models=None, exclude=(), **kwargs):
    """``watson.search`` restricted to what the current tenant may see from
    plugins (see ``tenant_search_models``).

    ``watson.filter(queryset, ...)`` needs no wrapper: the queryset already
    decides which objects are searched.
    """
    scoped_models = tenant_search_models(models)
    if not scoped_models:
        # watson.search treats an empty list as "every registered model" which we want to avoid
        return SearchEntry.objects.none()
    return watson.search(search_text, models=scoped_models, exclude=exclude, **kwargs)
