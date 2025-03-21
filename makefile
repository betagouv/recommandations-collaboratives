#
# Development makefile
#
#
# authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
# created: 2021-06-22 11:49:13 CEST
#

which=recoco  # default package for linting

SETTINGS=recoco.settings.development

# docker things
DOCKER-RUN = docker compose run -e TERM --rm --entrypoint=""

all:
	echo "what do you want?"

test:
	pytest

.PHONY: tags
tags:
	@ctags --exclude=*.js --exclude=.venv --exclude=*.css -R ./recoco/
	@find ./recoco -name \*.py | etags --language=python -

nice:
	pre-commit run --all-files

lint:
	pylint --django-settings-module=$(SETTINGS) $(which)

coverage:
	pytest --cov
	coverage html

clean:
	rm -f tags TAGS
	find . -name \*.pyc -delete
	find . -name __pycache__ -delete
	rm -rf ./static
	rm -rf ./htmlcov .coverage
	rm -rf .pytest_cache
	rm -rf ./recoco.egg-info

deploy:
	fab deploy

migrations:
	./manage.py makemigrations

migrate:
	./manage.py migrate

safe: nice
	semgrep --config=p/ci recoco

runserver:
	@python manage.py runserver 0.0.0.0:8000

runworker:
	@celery -A recoco worker -l info --concurrency=1

build:
	docker compose build

up:
	docker compose up

sh:
	$(DOCKER-RUN) server bash

# eof
