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
            mock_load_ds_resource_schema.delay.assert_called_once_with(
                ds_resource_id=ds_resource.id
            )
        else:
            mock_load_ds_resource_schema.delay.assert_not_called()


@pytest.mark.parametrize(
    "autoload_enabled,expected_call", [(True, True), (False, False)]
)
@pytest.mark.django_db
def test_trigger_ds_from_task(settings, autoload_enabled, expected_call):
    settings.DS_AUTOCREATE_FOLDER = autoload_enabled

    with patch(
        "recoco.apps.demarches_simplifiees.signals.update_or_create_ds_folder"
    ) as mock_update_or_create_ds_folder:
        task = baker.make("tasks.Task")

    if expected_call:
        mock_update_or_create_ds_folder.delay.assert_called_once_with(
            recommendation_id=task.id
        )
    else:
        mock_update_or_create_ds_folder.delay.assert_not_called()
