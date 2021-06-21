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


@task
def check(cnx):
    os.system("bandit -x tests,development.py -r urbanvitaliz")
    os.system("semgrep --config=p/ci urbanvitaliz")


@task
def upgrade(cnx):
    """Upgrade requirements to last version on server"""
    cnx.put(
        "./requirements-srv.txt",
        remote="./urbanvitaliz-site/requirements.txt",
    )
    cnx.run(
        "cd urbanvitaliz-site " "&& venv/bin/pip install --upgrade -r requirements.txt"
    )


@task
def deploy(cnx):
    """Deploy new version of project to server"""
    run_setup("setup.py", script_args=["sdist"])
    cnx.put(
        "./dist/urbanvitaliz-django-0.6.0.tar.gz",
        remote="./urbanvitaliz-site/dist/urbanvitaliz-django-0.6.0.tar.gz",
    )
    cnx.run(
        "cd urbanvitaliz-site "
        "&& ./venv/bin/pip install ./dist/urbanvitaliz-django-0.6.0.tar.gz"
        "&& ./manage.py migrate"
        "&& ./manage.py compilescss"
        "&& ./manage.py collectstatic --noinput"
    )


# eof
