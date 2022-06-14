# encoding: utf-8

"""
Fabfile to drive development and deployment of urbanvitaliz-django

authors : raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created : 2021-06-01 09:54:36 CEST
"""

import os
import pytest

from distutils.core import run_setup
from fabric import task

import urbanvitaliz


PACKAGE = f"urbanvitaliz-django-{urbanvitaliz.VERSION}.tar.gz"

# TODO make target folder being
# - prod if branch == main,
# - develop if branch == develop, and
# - error otherwise.


@task
def upgrade(cnx, site=None):
    """Upgrade requirements to last version on server for site"""
    if site not in ["production", "development"]:
        print("Usage: fab upgrade --site={production,development} --hosts=...")
        return
    cnx.put(
        "./requirements.txt",
        remote=f"./urbanvitaliz-{site}/requirements.txt",
    )
    cnx.run(
        f"cd urbanvitaliz-{site} "
        "&& venv/bin/pip install --upgrade -r requirements.txt"
    )

@task
def setup(cnx, site=None):
    """Setup a server with the minimum for deploying"""
    if site not in ["production", "development"]:
        print("Usage: fab deploy --site={production,development} --hosts=...")
        return
    cnx.run(
        f"mkdir -p urbanvitaliz-{site}/dist"
        f"&& virtualenv urbanvitaliz-{site}/venv")

@task
def deploy(cnx, site=None):
    """Deploy new version of project to server for site"""
    if site not in ["production", "development"]:
        print("Usage: fab deploy --site={production,development} --hosts=...")
        return
    run_setup("setup.py", script_args=["sdist"])
    cnx.put(
        f"./dist/{PACKAGE}",
        remote=f"./urbanvitaliz-{site}/dist/{PACKAGE}",
    )
    cnx.run(
        f"cd urbanvitaliz-{site} "
        f"&& ./venv/bin/pip install ./dist/{PACKAGE}"
        "&& ./manage.py migrate"
        "&& ./manage.py compilescss"
        "&& ./manage.py collectstatic --noinput"
    )


# eof
