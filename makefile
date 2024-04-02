#
# Development makefile
#
#
# authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
# created: 2021-06-22 11:49:13 CEST
#

which=urbanvitliz  # default package for linting

SETTINGS=recoco.settings.development

all:
	echo "what do you want?"

test:
	pytest

.PHONY: tags
tags:
	@ctags --exclude=*.js --exclude=.venv --exclude=*.css -R ./recoco/
	@find ./recoco -name \*.py | etags --language=python -

nice:
	isort recoco
	black recoco
	flake8 recoco

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

safe:
	bandit -x tests,development.py -r recoco
	semgrep --config=p/ci recoco

# eof
