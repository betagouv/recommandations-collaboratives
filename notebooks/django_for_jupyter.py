import os
import sys
import django

PWD = os.getenv("PWD")
DEBUG = os.getenv("DEBUG")

PROJ_MISSING_MSG = """Set an enviroment variable:\n
`DJANGO_PROJECT=your_project_name`\n
or call:\n
`init_django(your_project_name)`
"""

"""
Use this function inside a jupyter notebook to initialize the project
NOTE: use insied Jupyter Notebook only
"""


def init_django(project_name=None):
    os.environ.setdefault("JUPYTER_CONFIG_PATH", f"~/.jupyter:{PWD}")
    os.chdir(PWD)
    project_name = project_name or os.environ.get("DJANGO_PROJECT") or None
    if project_name is None:
        raise ValueError(PROJ_MISSING_MSG)
    sys.path.insert(0, os.getenv("PWD"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{project_name}.settings")
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    django.setup()
