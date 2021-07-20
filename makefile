#
# Development makefile
#
#
# authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
# created: 2021-06-22 11:49:13 CEST
#


all:
	echo "what do you want?"

test:
	pytest

nice:
	black urbanvitaliz
	flake8 urbanvitaliz

coverage:
	pytest --cov

clean:
	find . -name \*.pyc -delete
	find . -name __pycache__ -delete
	rm -rf ./static
	rm -rf ./htmlcov .coverage

deploy:
	fab deploy

migrations:
	./manage.py makemigrations

migrate:
	./manage.py migrate

safe:
	bandit -x tests,development.py -r urbanvitaliz
	semgrep --config=p/ci urbanvitaliz

# eof
