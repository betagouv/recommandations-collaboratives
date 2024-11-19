# Tests Front End

Dossier de tests : `frontend_tests/`

## Démarrer

- S'assurer que dans le fichier `development.py` dans les settings de `django`, la base de données de test est bien configurée. Par exemple :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_NAME'), # ex 'recoco'
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': 'localhost',
        'PORT': 5432,
        'TEST': {
            'NAME':'test_recoco' # <-- ici
        }
    }
}
```

- Dupliquer le fichier `development.py` en `frontend_tests.py` et modifier les paramètres de la base de données pour qu'ils correspondent à la base de données de test.

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': test_recoco, # <-- ici
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': 'localhost',
        'PORT': 5432,
    }
}
```

Ces paramètres sont seulement utilisés pour lancer la mise à jour des permissions à l'aide du script `update_permissions.py`

- Dans le fichier `frontend_tests.py`, modifier le port d'accès du front end, cela permettra de lancer le serveur front end sur un port différent du serveur de développement Django et de pouvoir lancer les tests en parallèle.:

```python
DJANGO_VITE = {"default": {"dev_mode": DEBUG, "dev_server_port": 3001}}
```

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
