from time import sleep

from django.contrib.sites.models import Site
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation

from recoco.apps.demarches_simplifiees.models import DSMapping, DSResource
from recoco.apps.demarches_simplifiees.tasks import load_ds_resource_schema
from recoco.apps.geomatics.models import Department
from recoco.apps.resources.models import Resource


def normalize(value: str) -> str:
    norm_value = value.replace(".", "")
    for c in (",", "/"):
        # "/", "(", ")", ":", ";", "!", "?", "’", "«", "»", "…", "–", "—"):
        norm_value = norm_value.replace(c, " ")
    return norm_value[:300].strip()


def main():
    site = Site.objects.filter(domain="sosponts.recoconseil.fr").first()

    resource = Resource.objects.get(pk=487)

    ds_resource, created = DSResource.objects.get_or_create(
        name="pnp-travaux-dispositif-d-aide",
        defaults={"resource": resource},
    )
    if created:
        ds_resource.departments.add(Department.objects.all())
        load_ds_resource_schema.delay(ds_resource.id)
        sleep(5)
        ds_resource.refresh_from_db()

    ds_mapping, _ = DSMapping.objects.get_or_create(
        ds_resource=ds_resource,
        sites=site,
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "mapping"

    max_rows = 1000

    # build a list of availbale fields in the DS resource
    ds_fields = [normalize(f["field_label"]) for f in ds_mapping.ds_resource.fields]

    # build a list of lookup fields available for a site project
    lookup_fields = ["project_name", "project_description", "project_other_field"]

    # create a sheet to register the ds fields dropdown values
    ws_ds_fields = wb.create_sheet("ds-fields")
    for i, f in enumerate(ds_fields, start=1):
        ws_ds_fields[f"A{i}"] = f

    # create a sheet to register the lookup fields dropdown values
    ws_lookup_fields = wb.create_sheet("lookup-fields")
    for i, f in enumerate(lookup_fields, start=1):
        ws_lookup_fields[f"A{i}"] = f

    # create the mapping sheet headers
    ws["A1"] = "DS Field"
    ws["B1"] = "Lookup Field"

    # setup the dropdowns for the mapping sheet
    ds_field_validation = DataValidation(
        type="list",
        formula1=f"'ds-fields'!$A$1:$A${len(ds_fields)}",
        allowBlank=True,
        showInputMessage=True,
        showErrorMessage=True,
    )
    ws.add_data_validation(ds_field_validation)
    for row in range(2, max_rows):
        ds_field_validation.add(ws[f"A{row}"])

    recoco_field_validation = DataValidation(
        type="list",
        formula1=f"'lookup-fields'!$A$1:$A${len(lookup_fields)}",
        allow_blank=True,
        showInputMessage=True,
        showErrorMessage=True,
    )
    ws.add_data_validation(recoco_field_validation)
    for row in range(2, max_rows):
        recoco_field_validation.add(ws[f"B{row}"])

    wb.save("sample.xlsx")


main()
