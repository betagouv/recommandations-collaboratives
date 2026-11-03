from unittest.mock import patch

import pytest
from model_bakery import baker

from ..models import DSResource


@pytest.mark.parametrize(
    "autoload_enabled,expected_call", [(True, True), (False, False)]
)
@pytest.mark.django_db
def test_trigger_load_ds_resource_schema(settings, autoload_enabled, expected_call):
    settings.DS_AUTOLOAD_SCHEMA = autoload_enabled

    with patch(
        "recoco.apps.demarches_simplifiees.signals.load_ds_resource_schema"
    ) as mock_load_ds_resource_schema:
        ds_resource = baker.make(DSResource)
        ds_resource.schema = {"number": 123}
        ds_resource.save()

        if expected_call:
            mock_load_ds_resource_schema.assert_called_once_with(
                ds_resource_id=ds_resource.id
            )
        else:
            mock_load_ds_resource_schema.assert_not_called()
