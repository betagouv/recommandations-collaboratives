Dossier de tests : `frontend_tests/`

- Ajouter un fichier `frontend_tests.py` dans les settings de `django`, ne pas oublier la clé test dans les configs de la BDD avec le nom de la bdd de tests que vous voulez utiliser
    ```
              DATABASES = {
              'default': {
                  'ENGINE': 'django.db.backends.postgresql',
                  'NAME': os.environ.get('POSTGRES_NAME'),
                  'USER': os.environ.get('POSTGRES_USER'),
                  'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
                  'HOST': 'db',
                  'PORT': 5432,
                  'TEST': {
                      'NAME':'test_urbanvitaliz'
                  }
              }
          }
    ```
- Exécuter la commande pour initialiser un server django en mode test avec la base de test et les différentes fixtures avec la commande : `npm run db:test:init` 
- Vous pouvez maintenant exécuter les différents tests avec les commandes suivantes au choix : 
    - `npm run test_ui` -> pour lancer cypress avec une interface visuelle
    - `npm run test` -> pour lancer cypress en ligne de commande


TODO : continue doc
