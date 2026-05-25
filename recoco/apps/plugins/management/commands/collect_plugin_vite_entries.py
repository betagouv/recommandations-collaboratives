import inspect
import json
import os

from django.core.management.base import BaseCommand

from recoco.apps.plugins.manager import get_plugin_manager

FRONTEND_SRC = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "../../../..", "frontend/src")
)
PLUGINS_PROXY_DIR = os.path.join(FRONTEND_SRC, "js", "plugins")
PLUGIN_ENTRIES_JSON = os.path.join(os.path.dirname(FRONTEND_SRC), "plugin-entries.json")


class Command(BaseCommand):
    help = (
        "Generate Vite proxy entry files for installed plugins and write "
        "plugin-entries.json so vite.config.js can discover them."
    )

    def handle(self, *args, **options):
        os.makedirs(PLUGINS_PROXY_DIR, exist_ok=True)

        pm = get_plugin_manager()
        manifest = {}

        for _name, plugin in pm.list_name_plugin():
            vite_entries = getattr(plugin, "vite_entries", None)
            if not vite_entries:
                continue

            plugin_file = inspect.getfile(type(plugin))
            pkg_dir = os.path.dirname(plugin_file)

            for entry_name, rel_path in vite_entries.items():
                abs_path = os.path.normpath(os.path.join(pkg_dir, rel_path))
                if not os.path.isfile(abs_path):
                    self.stderr.write(
                        self.style.WARNING(
                            f"Skipping {entry_name}: {abs_path} not found"
                        )
                    )
                    continue

                proxy_filename = f"{entry_name}.js"
                proxy_path = os.path.join(PLUGINS_PROXY_DIR, proxy_filename)
                with open(proxy_path, "w") as f:
                    f.write(f"import '{abs_path}';\n")

                manifest[entry_name] = f"js/plugins/{proxy_filename}"

        with open(PLUGIN_ENTRIES_JSON, "w") as f:
            json.dump(manifest, f, indent=2)

        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {len(manifest)} plugin entr{'y' if len(manifest) == 1 else 'ies'} "
                f"→ {PLUGIN_ENTRIES_JSON}"
            )
        )
