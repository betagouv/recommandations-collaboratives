# encoding: utf-8

"""
Fabfile to drive development and deployment of recoco

authors : raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created : 2021-06-01 09:54:36 CEST
"""

import json
import os

import requests
from dotenv import load_dotenv
from fabric import task
from invoke import run as local

import recoco

load_dotenv()

PACKAGE = f"recoco-{recoco.__version__}.tar.gz"

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
        remote=f"./recoco-{site}/requirements.txt",
    )
    cnx.run(f"cd recoco-{site} " "&& ./.venv/bin/uv pip install -r requirements.txt")


@task
def setup(cnx, site=None):
    """Setup a server with the minimum for deploying"""
    if site not in ["production", "development"]:
        print("Usage: fab deploy --site={production,development} --hosts=...")
        return
    cnx.run(
        f"mkdir -p recoco-{site}/dist"
        f"&& virtualenv recoco-{site}/.venv"
        f"&& recoco-{site}/.venv/bin/pip install uv"
    )


@task
def deploy(cnx, site=None):
    """Deploy new version of project to server for site"""
    if site not in ["production", "development"]:
        print("Usage: fab deploy --site={production,development} --hosts=...")
        return

    local("cd recoco/frontend && yarn build")
    local("uv build")

    cnx.put(
        f"./dist/{PACKAGE}",
        remote=f"./recoco-{site}/dist/{PACKAGE}",
    )
    cnx.run(
        f"cd recoco-{site} "
        f'&& ./.venv/bin/uv pip install "recoco @ ./dist/{PACKAGE}" --reinstall-package "recoco"'
        "&& ./manage.py migrate"
        "&& ./manage.py compilescss"
        "&& ./manage.py collectstatic --noinput"
    )

    print("Copying manifest.json to static dir...")
    cnx.run(
        f"cd recoco-{site} "
        "&& cp .venv/lib/python3*/site-packages/recoco/frontend/dist/manifest.json public/static/"
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

    requests.post(address, auth=credentials, data=data, timeout=10)


def ad_staging_drop_database(db_name: str):
    api_root = "https://api.alwaysdata.com/"

    credentials = (
        "{API_KEY} account=uvstaging".format(
            API_KEY=os.getenv("AD_RECOCO_STAGING_CREDENTIALS")
        ),
        "",
    )

    response = requests.get(f"{api_root}/v1/database/", auth=credentials, timeout=10)
    db_json = response.json()

    for db in db_json:
        if db["name"] == f"uvstaging_{db_name}":
            response = requests.delete(
                f"{api_root}{db['href']}", auth=credentials, timeout=10
            )

            print(response)
            return


@task
def replicate_prod_to_staging(cnx, site=None):
    if site != "production":
        print("This can only be run on the prod site.")

    cnx.run("./replicate_staging_to_prod.sh")


@task
def load_prod_db_to_staging(cnx, site=None):
    db_name = "development"

    if site != "development":
        print("This can only be run on the dev site.")

    ad_staging_drop_database(db_name)
    ad_staging_create_database(db_name)

    cnx.run("./load_prod_dump_to_db.sh")

    cnx.run(f"cd recoco-{site}/multisites" "&& git pull")

    cnx.run(
        f"cd recoco-{site} "
        "&& ./manage.py compilescss"
        "&& ./manage.py collectstatic --noinput"
    )


# eof
