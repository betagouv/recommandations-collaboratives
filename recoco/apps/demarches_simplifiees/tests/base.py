import pytest


class BaseTestMixin:
    @pytest.fixture(autouse=True)
    def tweak_ds_settings(self, settings):
        settings.DS_AUTOLOAD_SCHEMA = False
        settings.DS_ADAPTERS_DIR = (
            settings.BASE_DIR / "apps/demarches_simplifiees/tests/adapters"
        )
