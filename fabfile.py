# encoding: utf-8

"""
Fabfile to drive development and deployment of urbanvitaliz-django

authors : raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created : 2021-06-01 09:54:36 CEST
"""

import os
from distutils.core import run_setup

from dotenv import load_dotenv
import requests
import json
from fabric import task
from invoke import run as local

import urbanvitaliz


load_dotenv()

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
        f"mkdir -p urbanvitaliz-{site}/dist" f"&& virtualenv urbanvitaliz-{site}/venv"
    )


@task
def deploy(cnx, site=None):
    """Deploy new version of project to server for site"""
    if site not in ["production", "development"]:
        print("Usage: fab deploy --site={production,development} --hosts=...")
        return

    local("cd urbanvitaliz/frontend && yarn build")

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


def ad_staging_create_database(db_name: str):
    """Create a new database on alwaysdata infrastructure"""
    address = "https://api.alwaysdata.com/v1/database/"
    fullname = f"uvstaging_{db_name}"
    database = {
        "name": fullname,
        "type": "POSTGRESQL",
        "locale": "fr_FR.utf8",
        "extensions": ["pg_trgm", "postgis", "postgis_topology", "unaccent"],
        "permissions": {"uvstaging": "FULL"},
    }
    data = json.dumps(database)

    credentials = (
        "{API_KEY} account=uvstaging".format(
            API_KEY=os.getenv("AD_RECOCO_STAGING_CREDENTIALS")
        ),
        "",
    )

    requests.post(address, auth=credentials, data=data)


def ad_staging_drop_database(db_name: str):
    api_root = "https://api.alwaysdata.com/"

    credentials = (
        "{API_KEY} account=uvstaging".format(
            API_KEY=os.getenv("AD_RECOCO_STAGING_CREDENTIALS")
        ),
        "",
    )

    response = requests.get(f"{api_root}/v1/database/", auth=credentials)
    db_json = response.json()

    for db in db_json:
        if db["name"] == f"uvstaging_{db_name}":
            response = requests.delete(
                f"{api_root}{db['href']}",
                auth=credentials,
            )
            print(response)
            return


@task
def replicate_prod_to_staging(cnx, site=None):
    #    ad_staging_create_database("truc")
    ad_staging_drop_database("truc")
    # cnx.run(f"./replicate_staging_to_prod.sh")


# eof
