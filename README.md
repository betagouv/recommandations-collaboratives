# Recoco (Recommendations Collaboratives)

## Mission

Le logiciel Recoco est un commun numérique permettant d'outiller une méthodologie de Recommandations Collaboratives se focalisant sur les problématiques complexes et nécessitant de multiples expertises sur des temps longs.


Historiquement, le logiciel Recoco est issu de la mission UrbanVitaliz (équipe-projet portée
par le Cerema), en partenariat avec Beta.gouv.fr et sponsorisé par le Ministère
de la Transition Ecologique et l'Etablissement Public Foncier du
Nord-Pas-de-Calais.

## Logiciel

Il est réalisé en python/django côté moteur et alpinejs/bootstrap/dsfr côté interface.

Il est par nature multi-portails, permettant ainsi d'héberger plusieurs
thématiques disposant de leur propre espace tout en proposant une porosité entre
celles-ci.

Son code est couvert par la licence AGPL v3.0.

En savoir plus sur https://recommandations-collaboratives.beta.gouv.fr/

## Installation

Deux choix :

1.  Via virtualenv et uv
2.  Via Docker

### Virtualenv

Commencez par installer `uv` sur votre machine avec pip ou votre gestionnaire de paquets. Si vous n'avez pas de moyen connu, référez vous à la page de `uv` ( https://github.com/astral-sh/uv ).

Créez et sourcez l'environnement:
```sh
uv venv
source .venv/bin/activate
```

```sh
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt
```
#### Configuration de l'applicatif

Copiez le fichier de configuration d'exemple :

```sh
cp recoco/settings/development.py.example recoco/settings/development.py
```

Puis modifiez la configuration de la base de données :

```python
DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.postgresql',
         'NAME': os.environ.get('POSTGRES_NAME'),
         'USER': os.environ.get('POSTGRES_USER'),
         'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
         'HOST': 'db',
         'PORT': 5432,
     }
}
```

Vous pouvez aussi renseigner les valeurs dans le fichier si vous préférez ne pas utiliser des variables d'environnement.



### Docker

Les fichiers docker se trouvent à la racine dans le dossier `docker`.

#### Configuration de l'applicatif

Référez vous à la section de Virtualenv, mais limitez vous aux variables d'environnement.

#### Création des conteneurs

En ligne de commandes, aller dans ce dossier `Docker` et taper :

```sh
docker-compose up -d
```

Après quelques minutes d'installation, vous devriez avoir un environnement prêt.


#### Création de la base de donnnées

Entrez dans le container `app` en tapant :

```sh
docker-compose exec app /bin/bash
```

Initialisez ou synchronisez la base de données en tapant :

```sh
./manage.py migrate
```

## Lancement de l'applicatif

*Les commandes suivantes ne sont pas nécessaire si vous êtes avec Docker.*

Pour lancer l'applicatif en mode `développement`:

- compilez le module `dsrc_ui`:

```sh
cd recoco/frontend/modules/dsrc_ui
yarn install
yarn build
```

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


## Chargement des données de démo

```bash
./manage.py loaddata data/geomatics.json
```

Création du premier site
```bash
./manage.py shell
```

```python
from recoco.apps.home import utils
site = utils.make_new_site("Example", "example.com", "sender@example.com", "Sender")
site.aliases.create(domain="localhost", redirect_to_canonical=False)
```

## En cas de difficultés

Dans le cas où vous rencontrez une difficulté, n'hésitez pas à ouvrir une `issue` sur
GitHub, nous vous répondrons dans les plus brefs délais !
