# Tests Front End

Dossier de tests : `frontend_tests/`

## Démarrer

- Ajouter un fichier `frontend_tests.py` dans les settings de `django`, calqué sur le fichier `development.py` contenu dans le même dossier
- Ajouter la clé `TEST` dans les configs de la BDD, et modifiez le nom de la bdd, pour utiliser la BDD de tests que vous venez de créer :

    ```python
              DATABASES = {
              'default': {
                  'ENGINE': 'django.db.backends.postgresql',
                  'NAME': os.environ.get('POSTGRES_NAME'), # ex. 'test_urbanvitaliz'
                  'USER': os.environ.get('POSTGRES_USER'),
                  'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
                  'HOST': 'localhost',
                  'PORT': 5432,
                  'TEST': {
                      'NAME':'test_urbanvitaliz'
                  }
              }
          }
    ```

- Initialiser un server django en mode test avec la base de test et les différentes fixtures avec la commande : `npm run db:test:init`
- Dans une nouvelle console, dans le dossier `frontend_tests/` lancer la commande de mise à jour des permissions: `db:test:update_permissions`
- Vous pouvez maintenant exécuter les différents tests avec les commandes suivantes au choix :
    - `npm run test_ui` -> pour lancer cypress avec une interface visuelle
    - `npm run test` -> pour lancer cypress en ligne de commande


TODO : continue doc
