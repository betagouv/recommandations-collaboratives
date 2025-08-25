# Recoco (Recommandations Collaboratives)

![Recoco](logo.png)

## Mission

Le logiciel Recoco est un outil numérique permettant d'épauler une méthodologie de
Recommandations Collaboratives se focalisant sur les problématiques complexes et nécessitant
de multiples expertises sur des temps longs.

Historiquement, le logiciel Recoco est issu de la mission UrbanVitaliz (équipe-projet portée
par le CEREMA), en partenariat avec Beta.gouv.fr et sponsorisé par le Ministère
de la Transition Ecologique et l'Etablissement Public Foncier du
Nord-Pas-de-Calais.

Nos sponsors: CEREMA, DGALN et ANCT.

## Logiciel

Il est réalisé en python/django côté moteur et alpinejs/bootstrap/dsfr côté interface.

Il est par nature multi-portails, permettant ainsi d'héberger plusieurs
thématiques disposant de leur propre espace tout en proposant une porosité entre
celles-ci.

Son code est couvert par la licence AGPL v3.0.

En savoir plus sur https://recommandations-collaboratives.beta.gouv.fr/

Vous pouvez trouver notre carnet de route ici: https://github.com/orgs/betagouv/projects/89/views/9

## Installation

Deux choix :

1.  Via virtualenv et uv
2.  Via Docker

### Virtualenv

#### Prérequis

Installez `pandoc` et `gdal`

Pour les sytèmes debian:

```sh
sudo apt install python3-gdal pandoc
```

Installez `uv` sur votre machine avec pip ou votre gestionnaire de paquets. Si vous n'avez pas de moyen connu, référez vous à la page de `uv` ( https://github.com/astral-sh/uv ).

Créez et sourcez l'environnement:

```sh
uv venv
source .venv/bin/activate
```

```sh
uv sync
```

Il faut aussi une base de données postgres. Configurez-là pour le projet:
```sh
sudo -u postgres psql < sql/init.sql
```
La base ainsi créée s'appelle `recoco` et appartient à un utilisateur nommé `recoco` avec le mot de passe `recoco`. À ne laisser tel quel ue pour un environement de développement pour des raisons de sécurité.

Les modules suivants sont installés en production et peuvent être requis (à affiner, plusieurs ne sont plus vraiment utilisés) :
* agestore
* pgcrypto
* trgm
* postgis
* postgis topology
* unaccent
* uuid-ossp

#### Configuration de l'applicatif

Copiez le fichier de variables d'environnement d'exemple :

```sh
cp .env.example .env
```

Puis compléter le fichier `.env` avec les informations de votre base de données.

```bash
DJANGO_DB_NAME=recoco
DJANGO_DB_TEST_NAME=test_recoco
DJANGO_DB_USER=recoco
DJANGO_DB_PASSWORD=
DJANGO_DB_HOST=localhost
DJANGO_DB_PORT=5432
DJANGO_VITE_TEST_SERVER_PORT=3001
DJANGO_VITE_DEV_SERVER_PORT=3000
GDAL_LIBRARY_PATH=
GEOS_LIBRARY_PATH=
SKIP_TEST_METRICS_CREATE_ROLES=
```

Copiez le fichier de configuration d'exemple :

```sh
cp recoco/settings/development.py.example recoco/settings/development.py
```

Vous pouvez aussi renseigner les valeurs dans le fichier si vous préférez ne pas utiliser des variables d'environnement.

### Docker

Un environnement Docker et fourni et orchestré avec le fichier
[`docker-compose.yml](./docker-compose.yml). Pour le lancer :

```sh
docker compose up
```

Une fois votre environnement installé, initialisez ou synchroniser la
base de données depuis le conteneur du serveur :

```sh
docker compose run --rm server bash
python manage.py migrate
```

## Lancement de l'applicatif

_Les commandes suivantes ne sont pas nécessaire si vous êtes avec Docker._

Pour lancer l'applicatif en mode `développement`:

- installez les dépendances:

```sh
cd recoco/frontend
yarn install
```

- montez le serveur dev des static sur le port 3000:

```sh
cd recoco/frontend && yarn dev
```

(Laissez la commande ouverte)

Puis, exécutez le backend :

```sh
./manage.py runserver 0.0.0.0:8000
```

Vous devriez pouvoir vous connecter sur http://localhost:8000 !

## Chargement de données

### données de démo

```bash
./manage.py loaddata data/geomatics.json
```

Création du premier site

```bash
./manage.py shell
```

```python
from recoco.apps.home import utils
site = utils.make_new_site("Example", "example.com", "sender@example.com", "Sender", "noreply@example.com", "postal adress")
site.aliases.create(domain="localhost", redirect_to_canonical=False)
```

### données de la prod

Avec un dump de db de prod, vous pouvez restaurer ces donnés:

```bash
sudo -u postgres psql < [path vers le dump]
```


### Récupérer les portails existants
Plusieurs portails (ie sites) ont déjà été configurés et sont disponibles sur le dépôt [recoco-portails](https://github.com/betagouv/recoco-portails). Pour y avoir accès en local, il faut cloner ce dépôt dans un dossier `multisites` à la racine du projet global.

Pour créer les bons alias dans l'interface d'administration, exécuter depuis le shell django

```python
run scripts/create_site_localhost_aliases.py
```
Pour vérifier que ç'a bien fonctionner, vérifiez que l'accès à http://sosponts.localhost:8000 fonctionne bien (par ex)

## Environnement de développement

### pre-commit

Pour que des PRs soient acceptées, on requiert que pre-commit ait été passé. La configuration est en principe bonne avec les étapes précédentes, mais il faut exécuter la commande
```bash
pre-commit install
```
pour que cette configuration soit bien appliquée.

## Tests

### Tests Front End

#### Unitaires

Pour lancer les tests unitaires front end, vous pouvez utiliser la commande suivante :

```sh
cd recoco/frontend
yarn test
```

#### Bout en bout

Merci de trouver la documentation de tests front end [ici](./frontend_tests/README.md).

### Tests Back End

Pour lancer les tests back end, vous pouvez utiliser la commande suivante :

```sh
pytest --create-db
```

## En cas de difficultés

Dans le cas où vous rencontrez une difficulté, n'hésitez pas à ouvrir une `issue` sur
GitHub, nous vous répondrons dans les plus brefs délais !
