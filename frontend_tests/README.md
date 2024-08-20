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
            'NAME':'test_recoco'
        }
    }
}
```

## Lancer les tests

### Lancement de la serie de tests Cypress

```bash
$ yarn test
```

Cela permettra de :

- Démarrer un serveur Vite (front end)
- Démarrer un serveur Django en mode test (back end)
- Lancer les tests Cypress
- Générer un rapport d'éxecution des tests dans le dossier `frontend_tests/cypress/reports`

### Lancement de l'interface graphique de Cypress

Pour lancer les tests, il faut lancer plusieurs processus dans des consoles distinctes:

- Console 1: Initialiser un server django en mode test avec la base de test et les différentes fixtures avec la commande : `yarn django:start-server`
- Console 2:
  - Lancer la commande de mise à jour des permissions: `yarn django:update-permissions`
  - Lancer la commande de dev front qui met les static et composants JS à disposition de Django: `yarn frontend:start-server`
- Console 3: Vous pouvez maintenant exécuter les différents tests avec les commandes suivantes au choix :
  - `yarn test_ui` -> pour lancer cypress avec une interface graphique
  - `yarn cy:run` -> pour lancer cypress en ligne de commande
