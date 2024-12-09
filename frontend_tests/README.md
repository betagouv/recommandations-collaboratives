# Tests Front End

Dossier de tests : `frontend_tests/`

## Démarrer

- S'assurer que les variables d'environnement sont bien configurées dans le fichier `.env` à la racine du projet. Par exemple :

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
```

- S'assurer que dans le fichier `development.py` dans les settings de `Django`, la base de données de test est bien configurée. Par exemple :

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DJANGO_DB_NAME"),
        "USER": os.getenv("DJANGO_DB_USER"),
        "PASSWORD": os.getenv("DJANGO_DB_PASSWORD"),
        "HOST": os.getenv("DJANGO_DB_HOST"),
        "PORT": os.getenv("DJANGO_DB_PORT"),
        "TEST": {"NAME": os.getenv("DJANGO_DB_TEST_NAME")}, # <-- ici
    }
}
```

Ce fichier est utilisé pour copier la structure de la base de données de développement dans la base de données de test.
`DATABASES["default"]["NAME"]` : Nom de la base de données de développement
`DATABASES["default"]["TEST"]["NAME"]` : Nom de la base de données de test

- Le fichier `frontend_tests.py` contient les paramètres de configuration pour les tests front end. Notamment les paramètres de connexion à la base de données de développement et de test.

- Le fichier `frontend_tests_permissions.py` contient les paramètres de connexion à la base de données pour lancer la mise à jour des permissions à l'aide du script `update_permissions.py`

## Lancer les tests

### Lancement de la serie de tests Cypress (mode non interactif)

Installer les dépendances :

```bash
$ yarn install
```

> ⚠️ Attention
>
> S'assurer d'être dans son environnement virtuel Django.

Lancer les tests :

```bash
$ yarn test
```

Cela permettra de :

- Démarrer un serveur Vite (front end)
- Démarrer un serveur Django en mode test (back end)
- Lancer les tests Cypress
- Générer un rapport d'éxecution des tests dans le dossier `frontend_tests/cypress/reports`

### Lancement de l'interface graphique de Cypress

Installer les dépendances :

```bash
$ yarn install
```

> ⚠️ Attention
>
> S'assurer d'être dans son environnement virtuel Django.

Lancer les tests :

```bash
$ yarn test_ui
```

Cela permettra de :

- Démarrer un serveur Vite (front end)
- Démarrer un serveur Django en mode test (back end)
- Lancer les tests Cypress
- Générer un rapport d'éxecution des tests dans le dossier `frontend_tests/cypress/reports`

## Autres commandes

- `yarn django:start-server` : Initialiser un serveur de test Django et une base données de test et les différentes fixtures.
- `yarn django:update-permissions` : Mise à jour des permissions des utilisateurs
- `yarn frontend:start-server` : Mise à disposition des statics et composants JS
