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

## Philosophie des tests

### Ajout d'une nouvelle fonctionnalité ou modification

Lors de l'ajout d'une nouvelle fonctionnalité ou d'une modification, il est nécessaire de créer les tests front end s'il n'existe pas ou alors ou de mettre à jour l'existant.
Pour pouvoir retrouver facilement un test, une recherche peut-être effectuée pour retrouver le bon fichier en fonction de la classification proposée dans la prochaine section.

Avant de pousser son code sur le dépôt, il est nécessaire de lancer les tests afin de détecter d'éventuelles régréssions.

Toute les semaines (pour les releases) l'ensemble des test doivent être lancés pour s'assurer que tout fonctionne correctement.

## Classifications des tests

Pour pouvoir classifier les tests, il est nécessaire de suivre la nomenclature suivante en fonction de la page impactée :
Légende :

- ❌ : pas encore utilisé
- 🚧 : partiellement utilisé
- ✅ : positionné sur tout les tests concernés

Merci de mettre à jour la colonne `Utilisé` en fonction de l'utilisation du code.

| Page                       | Url                            | Fonctionnalité                                     | Code à insérer                                      | Utilisé |
| -------------------------- | ------------------------------ | -------------------------------------------------- | --------------------------------------------------- | ------: |
| Navigation principale      | `/`                            | Liste projet récents                               | `// @liste-projets-recents`                         |      ❌ |
| Navigation principale      | `/`                            | Projets à examiner                                 | `// @acces-moderation`                              |      ❌ |
| Navigation principale      | `/`                            | Ressources                                         | `// @acces-ressources`                              |      ❌ |
| Navigation principale      | `/`                            | Notifications                                      | `// @liste-notifications`                           |      ❌ |
| Navigation principale      | `/`                            | Accès rapide utilisateur                           | `// @acces-rapide-utilisateur`                      |      ❌ |
| Liste des projets tableau  | `/projects/staff`              | Page                                               | `// @page-kanban-projets`                           |      ❌ |
| Liste des projets tableau  | `/projects/staff`              | Recherche                                          | `// @recherche-kanban-projets`                      |      ❌ |
| Liste des projets tableau  | `/projects/staff`              | Déposer projet pour le compte de                   | `// @bouton-deposer-projet`                         |      ❌ |
| Liste des projets tableau  | `/projects/staff`              | Export CSV                                         | `// @kanban-export-csv`                             |      ❌ |
| Liste des projets liste    | `/projects/advisor`            | Page                                               | `// @page-liste-projets`                            |      ❌ |
| Liste des projets liste    | `/projects/advisor`            | Recherche                                          | `// @recherche-liste-projets`                       |      ❌ |
| Liste des projets liste    | `/projects/advisor`            | Création projet                                    | `// @bouton-deposer-projet`                         |      ❌ |
| Liste des projets liste    | `/projects/advisor`            | Export CSV                                         | `// @liste-projets-export-csv`                      |      ❌ |
| Liste des projets carte    | `/projects/map`                | Page                                               | `// @page-map-projets`                              |      ❌ |
| Liste des projets carte    | `/projects/map`                | Recherche                                          | `// @recherche-map-projets`                         |      ❌ |
| Liste des projets carte    | `/projects/map`                | Création projet                                    | `// @bouton-deposer-projet`                         |      ❌ |
| Liste des projets carte    | `/projects/map`                | Export CSV                                         | `// @map-projets-export-csv`                        |      ❌ |
| Projet                     | `/project/{id}`                | Navigation                                         | `// @navigation-projet`                             |      ❌ |
| Projet                     | `/project/{id}`                | Raccourci CRM projet                               | `// @bouton-raccourci-crm-staff`                    |      ❌ |
| Projet                     | `/project/{id}`                | Inviter                                            | `// @bouton-inviter-projet`                         |      ❌ |
| Projet                     | `/project/{id}`                | Changement role                                    | `// @changement-role-projet`                        |      ❌ |
| Projet - Présentation      | `/project/{id}/overview`       | Page                                               | `// @page-projet-presentation`                      |      🚧 |
| Projet - Présentation      | `/project/{id}/overview`       | Rappel Email                                       | `// @page-projet-presentation-rappel-email`         |      ❌ |
| Projet - Présentation      | `/project/{id}/overview`       | Thématique projet                                  | `// @page-projet-presentation-thematique`           |      ❌ |
| Projet - Présentation      | `/project/{id}/overview`       | Note interne                                       | `// @page-projet-presentation-note-interne`         |      ❌ |
| Projet - Présentation      | `/project/{id}/overview`       | Résumé projet saisine                              | `// @page-projet-presentation-resume-saisine`       |      ❌ |
| Projet - Présentation      | `/project/{id}/overview`       | Activité du projet                                 | `// @page-projet-presentation-activite`             |      ❌ |
| Projet - Présentation      | `/project/{id}/overview`       | Tags projet                                        | `// @page-projet-presentation-tags`                 |      ❌ |
| Projet - Présentation      | `/project/{id}/overview`       | Modal localisation projet                          | `// @page-projet-presentation-localisation`         |      ❌ |
| Projet - Présentation      | `/project/{id}/overview`       | Inviter partenaire (ancien collectivité)           | `// @page-projet-presentation-inviter-partenaire`   |      ❌ |
| Projet - Présentation      | `/project/{id}/overview`       | Inviter dans l'équipe de suivi (ancien conseiller) | `// @page-projet-presentation-inviter-suivie`       |      ❌ |
| Projet - Diagnostic        | `/project/{id}/overview`       | Marquer le diagnostic comme fait                   | `// @page-projet-presentation-mark-diagnostic-done` |      ✅ |
| Projet - État des lieux    | `/project/{id}/connaissance`   | Page                                               | `// @page-projet-edl`                               |      ❌ |
| Projet - État des lieux    | `/project/{id}/connaissance`   | CTA complétion                                     | `// @page-projet-edl-completer`                     |      ❌ |
| Projet - État des lieux    | `/project/{id}/connaissance`   | Partage                                            | `// @page-projet-edl-partager`                      |      ❌ |
| Projet - Recommandations   | `/project/{id}/actions`        | Page                                               | `// @page-projet-recommandations`                   |      🚧 |
| Projet - Recommandations   | `/project/{id}/actions`        | Création                                           | `// @page-projet-recommandations-creation`          |      🚧 |
| Projet - Recommandations   | `/project/{id}/actions`        | Modification                                       | `// @page-projet-recommandations-modification`      |      ❌ |
| Projet - Recommandations   | `/project/{id}/actions`        | Passer en brouillon                                | `// @page-projet-recommandations-brouillon`         |      ❌ |
| Projet - Recommandations   | `/project/{id}/actions`        | Suppression                                        | `// @page-projet-recommandations-suppression`       |      ❌ |
| Projet - Recommandations   | `/project/{id}/actions`        | Changement ordre recommandation                    | `// @page-projet-recommandations-ordre`             |      ❌ |
| Projet - Recommandations   | `/project/{id}/actions`        | Etiquette non lu                                   | `// @page-projet-recommandations-etiquette-non-lue` |      ❌ |
| Projet - Recommandations   | `/project/{id}/actions`        | Modal - Echange                                    | `// @page-projet-recommandations-modal`             |      ❌ |
| Projet - Recommandations   | `/project/{id}/actions`        | Status (En cours, faite, non applicable)           | `// @page-projet-recommandations-status`            |      🚧 |
| Projet - Recommandations   | `/project/{id}/actions`        | Bandeau recos non lues                             | `// @page-projet-recommandations-bandeau-non-lue`   |      ❌ |
| Projet - Conversations     | `/project/{id}/conversations`  | Page                                               | `// @page-projet-conversations`                     |      ❌ |
| Projet - Conversations     | `/project/{id}/conversations`  | Nouveau message                                    | `// @page-projet-conversations-nouveau-message`     |      ❌ |
| Projet - Fichier           | `/project/{id}/documents`      | Page                                               | `// @page-projet-fichier`                           |      ❌ |
| Projet - Fichier           | `/project/{id}/documents`      | Recherche                                          | `// @page-projet-fichier-recherche`                 |      ❌ |
| Projet - Fichier           | `/project/{id}/documents`      | Ajouter un fichier                                 | `// @page-projet-fichier-ajouter`                   |      ❌ |
| Projet - Fichier           | `/project/{id}/documents`      | Fichier - mettre en favori                         | `// @page-projet-fichier-favori`                    |      ❌ |
| Projet - Fichier           | `/project/{id}/documents`      | Fichier - supprimer                                | `// @page-projet-fichier-supprimer`                 |      ❌ |
| Projet - Fichier           | `/project/{id}/documents`      | Fichier - télécharger                              | `// @page-projet-fichier-télécharger`               |      ❌ |
| Projet - Fichier           | `/project/{id}/documents`      | Fichier reco                                       | `// @page-projet-fichier-reco`                      |      ❌ |
| Projet - Fichier           | `/project/{id}/documents`      | Fichier EDL - télécharger                          | `// @page-projet-fichier-edl-télécharger`           |      ❌ |
| Projet - Fichier           | `/project/{id}/documents`      | Epingler un lien                                   | `// @page-projet-fichier-epingler-lien`             |      ❌ |
| Projet - Espace conseiller | `/project/{id}/suivi`          | Page                                               | `// @page-projet-espace-conseiller`                 |      ❌ |
| Projet - Espace conseiller | `/project/{id}/suivi`          | Nouveau message                                    | `// @page-projet-espace-conseiller-nouveau-message` |      ❌ |
| Projet - Paramètres        | `/project/{id}/administration` | Page                                               | `// @page-projet-parametres`                        |      ❌ |
| Projet - Paramètres        | `/project/{id}/administration` | Modifier info projet                               | `// @page-projet-parametres-modifier`               |      ❌ |
| Projet - Paramètres        | `/project/{id}/administration` | Gestion des utilisateurs                           | `// @page-projet-parametres-gestion-utilisateur`    |      ❌ |
| Projet - Paramètres        | `/project/{id}/administration` | Gestion invitation                                 | `// @page-projet-parametres-gestion-invitation`     |      ❌ |
| Projet - Paramètres        | `/project/{id}/administration` | Mettre projet en pause                             | `// @page-projet-parametres-pause-projet`           |      ❌ |
| Projet - Paramètres        | `/project/{id}/administration` | Quitter le projet                                  | `// @page-projet-parametres-quitter-projet`         |      ❌ |
| Déposer un projet          | `/onboarding/project`          | Page                                               | `// @deposer-projet`                                |      🚧 |
| Demande compte conseiller  | `/advisor-access-request`      | Demande de compte conseiller                       | `// @demande-compte-conseiller`                     |      🚧 |

Le code est a positionner dans les fichiers de tests Cypress dans le nom du test pour permettre de retrouver facilement les tests concernés et de les executer selectivement à l'aide du package @cypress/grep.

Exemple :

```js
describe('I can view kanban when connected as staff @page-kanban-projets @exemple-autre-code', () => {
  beforeEach(() => {
    cy.login('staff');
  });

  it('visits kanban page', () => {
    cy.visit(`/projects/staff`);
  });
});
```
