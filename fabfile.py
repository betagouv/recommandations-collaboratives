# encoding: utf-8

"""
Fabfile to drive development and deployment of urbanvitaliz-django

authors : raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created : 2021-06-01 09:54:36 CEST
"""

import pytest

from distutils.core import run_setup
from fabric import task


@task
def deploy(cnx):
    run_setup("setup.py", script_args=["sdist"])
    cnx.put(
        "./dist/urbanvitaliz-django-0.1.0.tar.gz",
        remote="./urbanvitaliz-site/dist/urbanvitaliz-django-0.1.0.tar.gz",
    )
    cnx.run(
        "cd urbanvitaliz-site "
        "&& ./venv/bin/pip install ./dist/urbanvitaliz-django-0.1.0.tar.gz"
        "&& ./manage.py migrate"
        "&& ./manage.py collectstatic --noinput"
    )


# eof
