# Frontend documentation

## Composants

### Fenêtre modale

Vous trouverez une interface à utiliser pour normaliser l'utilisation des fenetre modal dans l'application.

`recoco/frontend/src/js/models/Modal.js`

Elle permet de définir le comportement d'une fenetre modale lors de sa fermeture avec deux possibilités :

- fermeture avec envoi de données `responseModal`
- fermeture sans envoi de données `closeModal`

Ces fonctions utilisent un evènement qui devra être écouté dans le composant parent de la fenetre modale : `@modal-response`

Exemple dans le template du composant parent :

```html
<div @modal-response="handleModalResponse($event)">
  <!-- Modal component --->
</div>
```

## Icônes

### Comment ajouter une icône personnalisée ?

Placer le svg dans le dossier `recoco/frontend/src/assets/`.

Pour ajouter une icône personnalisée, il faut ajouter le nom de l'icône dans le fichier `recoco/frontend/src/css/custom-icon.css`.

Exemple :

```css
.fr-icon-contact-book-line::after,
.fr-icon-contact-book-line::before {
  mask-image: url(../assets/contacts-book-line.svg);
}
```

Et enfin utiliser l'icône dans le code html.

## Tests

### Tests unitaires (Jest)

Les tests unitaires sont dans `tests/`.

```bash
yarn test
```

### Tests End-to-End (Cypress)

Les tests E2E sont dans `cypress/` (à la racine de `recoco/frontend/`).

#### Prérequis

S'assurer que les variables d'environnement suivantes sont définies dans le `.env` à la racine du projet :

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

S'assurer que dans `recoco/settings/development.py`, la base de test est bien configurée :

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DJANGO_DB_NAME"),
        "USER": os.getenv("DJANGO_DB_USER"),
        "PASSWORD": os.getenv("DJANGO_DB_PASSWORD"),
        "HOST": os.getenv("DJANGO_DB_HOST"),
        "PORT": os.getenv("DJANGO_DB_PORT"),
        "TEST": {"NAME": os.getenv("DJANGO_DB_TEST_NAME")},
    }
}
```

#### Settings Django dédiés

- `recoco/settings/e2e_tests.py` : configuration Django pour les tests E2E (DEBUG, reCAPTCHA bypass, Celery eager, port Vite 3001).
- `recoco/settings/e2e_tests_permissions.py` : configuration utilisée par `update_permissions` lors du run des tests.

#### Installation de l'environnement de tests

> ⚠️ S'assurer d'être dans son environnement virtuel Django.

```bash
yarn install        # une seule fois
npx cypress install # permet d'installer Cypress sur la machine
```

> ℹ️ si besoin d'aide pour Cypress [documentation Cypress](https://docs.cypress.io/app/get-started/install-cypress)

#### Lancer les tests

> ⚠️ S'assurer d'être dans son environnement virtuel Django.

```bash
yarn e2e            # exécution headless (Chrome) — démarre Vite + Django + Cypress
yarn e2e:ui         # ouvre l'interface graphique Cypress
yarn e2e:open       # raccourci équivalent à `cypress open`
yarn e2e:run        # raccourci équivalent à `cypress run`
yarn e2e:parallel   # exécution parallèle (2 threads)
```

Un rapport HTML est généré dans `cypress/reports/` après chaque exécution headless.

## Autres commandes

- `yarn e2e:django-server` : Initialiser un serveur de test Django et une base données de test et les différentes fixtures.
- `yarn e2e:django-update-permissions` : Mise à jour des permissions des utilisateurs
- `yarn e2e:frontend-server` : Mise à disposition des statics et composants JS

#### Philosophie

Lors de l'ajout d'une fonctionnalité ou d'une modification, créer le test E2E s'il n'existe pas, ou mettre à jour l'existant. Avant de pousser son code, lancer les tests pour détecter d'éventuelles régressions.

#### Classification des tests (tags `@cypress/grep`)

Légende :

- ❌ : pas encore utilisé
- 🚧 : partiellement utilisé
- ✅ : positionné sur tous les tests concernés
- ⏭️ : tous les tests du tag sont désactivés (`describe.skip`)
- ✅⏭️ : tag couvert mais au moins un test associé est désactivé (`describe.skip`)

| Page                       | Url                            | Fonctionnalité                                     | Code à insérer                                      | Utilisé |
| -------------------------- | ------------------------------ | -------------------------------------------------- | --------------------------------------------------- | ------: |
| Navigation principale      | `/`                            | Liste projet récents                               | `// @liste-projets-recents`                         |      ❌ |
| Navigation principale      | `/`                            | Projets à examiner                                 | `// @acces-moderation`                              |      ✅ |
| Navigation principale      | `/`                            | Ressources                                         | `// @acces-ressources`                              |      ✅ |
| Navigation principale      | `/`                            | Notifications                                      | `// @liste-notifications`                           |      ✅ |
| Navigation principale      | `/`                            | Accès rapide utilisateur                           | `// @acces-rapide-utilisateur`                      |    ✅⏭️ |
| Site public                | `/`                            | Contact équipe (visiteur non connecté)             | `// @contact-equipe`                                |      ✅ |
| Liste des projets tableau  | `/projects/staff`              | Page                                               | `// @page-kanban-projets`                           |      ✅ |
| Liste des projets tableau  | `/projects/staff`              | Recherche                                          | `// @recherche-kanban-projets`                      |      ✅ |
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
| Tutoriel                   | `/project/{id}`                | Tutoriel présentation projet                       | `// @tutoriel-presentation-projet`                  |      ✅ |
| Tutoriel                   | `/project/{id}`                | Tutoriel onboarding conseiller                     | `// @tutoriel-onboarding-conseiller`                |      ✅ |
| Projet                     | `/project/{id}`                | Navigation                                         | `// @navigation-projet`                             |      ✅ |
| Projet                     | `/project/{id}`                | Raccourci CRM projet                               | `// @bouton-raccourci-crm-staff`                    |      ✅ |
| Projet                     | `/project/{id}`                | Inviter                                            | `// @bouton-inviter-projet`                         |      ✅ |
| Projet                     | `/project/{id}`                | Changement role                                    | `// @changement-role-projet`                        |      ✅ |
| Projet - Présentation      | `/project/{id}/overview`       | Page                                               | `// @page-projet-presentation`                      |      ✅ |
| Projet - Présentation      | `/project/{id}/overview`       | Rappel Email                                       | `// @page-projet-presentation-rappel-email`         |      ✅ |
| Projet - Présentation      | `/project/{id}/overview`       | Thématique projet                                  | `// @page-projet-presentation-thematique`           |      ✅ |
| Projet - Présentation      | `/project/{id}/overview`       | Note interne                                       | `// @page-projet-presentation-note-interne`         |      ✅ |
| Projet - Présentation      | `/project/{id}/overview`       | Résumé projet saisine                              | `// @page-projet-presentation-resume-saisine`       |      ✅ |
| Projet - Présentation      | `/project/{id}/overview`       | Activité du projet                                 | `// @page-projet-presentation-activite`             |      ❌ |
| Projet - Présentation      | `/project/{id}/overview`       | Tags projet                                        | `// @page-projet-presentation-tags`                 |      ✅ |
| Projet - Présentation      | `/project/{id}/overview`       | Modal localisation projet                          | `// @page-projet-presentation-localisation`         |    ✅⏭️ |
| Projet - Présentation      | `/project/{id}/overview`       | Inviter partenaire (ancien collectivité)           | `// @page-projet-presentation-inviter-partenaire`   |      ✅ |
| Projet - Présentation      | `/project/{id}/overview`       | Inviter dans l'équipe de suivi (ancien conseiller) | `// @page-projet-presentation-inviter-suivie`       |      ✅ |
| Projet - Diagnostic        | `/project/{id}/overview`       | Marquer le diagnostic comme fait                   | `// @page-projet-presentation-mark-diagnostic-done` |      ✅ |
| Projet - État des lieux    | `/project/{id}/connaissance`   | Page                                               | `// @page-projet-edl`                               |      ✅ |
| Projet - État des lieux    | `/project/{id}/connaissance`   | CTA complétion                                     | `// @page-projet-edl-completer`                     |      ✅ |
| Projet - État des lieux    | `/project/{id}/connaissance`   | Partage                                            | `// @page-projet-edl-partager`                      |      ✅ |
| Tutoriel                   | `/project/{id}/actions`        | Tutoriel ressource externe                         | `// @tutoriel-ressource-externe`                    |      ⏭️ |
| Projet - Recommandations   | `/project/{id}/actions`        | Page                                               | `// @page-projet-recommandations`                   |      ⏭️ |
| Projet - Recommandations   | `/project/{id}/actions`        | Création                                           | `// @page-projet-recommandations-creation`          |      ⏭️ |
| Projet - Recommandations   | `/project/{id}/actions`        | Modification                                       | `// @page-projet-recommandations-modification`      |      ⏭️ |
| Projet - Recommandations   | `/project/{id}/actions`        | Passer en brouillon                                | `// @page-projet-recommandations-brouillon`         |      ⏭️ |
| Projet - Recommandations   | `/project/{id}/actions`        | Suppression                                        | `// @page-projet-recommandations-suppression`       |      ⏭️ |
| Projet - Recommandations   | `/project/{id}/actions`        | Changement ordre recommandation                    | `// @page-projet-recommandations-ordre`             |      ⏭️ |
| Projet - Recommandations   | `/project/{id}/actions`        | Etiquette non lu                                   | `// @page-projet-recommandations-etiquette-non-lue` |      ❌ |
| Projet - Recommandations   | `/project/{id}/actions`        | Modal - Echange                                    | `// @page-projet-recommandations-modal`             |      ⏭️ |
| Projet - Recommandations   | `/project/{id}/actions`        | Status (En cours, faite, non applicable)           | `// @page-projet-recommandations-status`            |      ⏭️ |
| Projet - Recommandations   | `/project/{id}/actions`        | Bandeau recos non lues                             | `// @page-projet-recommandations-bandeau-non-lue`   |      ⏭️ |
| Projet - Conversations     | `/project/{id}/conversations`  | Page                                               | `// @page-projet-conversations`                     |      ✅ |
| Projet - Conversations     | `/project/{id}/conversations`  | Nouveau message                                    | `// @page-projet-conversations-nouveau-message`     |      ✅ |
| Projet - Fichier           | `/project/{id}/documents`      | Page                                               | `// @page-projet-fichier`                           |      ✅ |
| Projet - Fichier           | `/project/{id}/documents`      | Recherche                                          | `// @page-projet-fichier-recherche`                 |      ❌ |
| Projet - Fichier           | `/project/{id}/documents`      | Ajouter un fichier                                 | `// @page-projet-fichier-ajouter`                   |      ✅ |
| Projet - Fichier           | `/project/{id}/documents`      | Fichier - mettre en favori                         | `// @page-projet-fichier-favori`                    |      ✅ |
| Projet - Fichier           | `/project/{id}/documents`      | Fichier - supprimer                                | `// @page-projet-fichier-supprimer`                 |      ✅ |
| Projet - Fichier           | `/project/{id}/documents`      | Fichier - télécharger                              | `// @page-projet-fichier-télécharger`               |      ❌ |
| Projet - Fichier           | `/project/{id}/documents`      | Fichier reco                                       | `// @page-projet-fichier-reco`                      |      ❌ |
| Projet - Fichier           | `/project/{id}/documents`      | Fichier EDL - télécharger                          | `// @page-projet-fichier-edl-télécharger`           |      ❌ |
| Projet - Fichier           | `/project/{id}/documents`      | Epingler un lien                                   | `// @page-projet-fichier-epingler-lien`             |      ✅ |
| Projet - Espace conseiller | `/project/{id}/suivi`          | Page                                               | `// @page-projet-espace-conseiller`                 |      ✅ |
| Projet - Espace conseiller | `/project/{id}/suivi`          | Nouveau message                                    | `// @page-projet-espace-conseiller-nouveau-message` |      ✅ |
| Projet - Paramètres        | `/project/{id}/administration` | Page                                               | `// @page-projet-parametres`                        |      ✅ |
| Projet - Paramètres        | `/project/{id}/administration` | Modifier info projet                               | `// @page-projet-parametres-modifier`               |      ✅ |
| Projet - Paramètres        | `/project/{id}/administration` | Gestion des utilisateurs                           | `// @page-projet-parametres-gestion-utilisateur`    |      ✅ |
| Projet - Paramètres        | `/project/{id}/administration` | Gestion invitation                                 | `// @page-projet-parametres-gestion-invitation`     |      ✅ |
| Projet - Paramètres        | `/project/{id}/administration` | Mettre projet en pause                             | `// @page-projet-parametres-pause-projet`           |      ✅ |
| Projet - Paramètres        | `/project/{id}/administration` | Quitter le projet                                  | `// @page-projet-parametres-quitter-projet`         |      ✅ |
| Déposer un projet          | `/onboarding/project`          | Page                                               | `// @deposer-projet`                                |      ✅ |
| Demande compte conseiller  | `/advisor-access-request`      | Demande de compte conseiller                       | `// @demande-compte-conseiller`                     |      ✅ |
| Connexion                  | `/accounts/login/`             | Connexion (UI et programmatique)                   | `// @connexion`                                     |      ✅ |
| Inscription                | `/accounts/signup/`            | Inscription utilisateur                            | `// @inscription`                                   |      ✅ |
| Smoke / transverse         | tous URLs                      | Exploration de toutes les URLs accessibles         | `// @can-explore-all-urls`                          |      ✅ |
| DSRC (formulaires)         | n/a (composant)                | Validation des formulaires DSRC (test désactivé)   | `// @dsrc-form-validator`                           |      ⏭️ |

Le code est à positionner dans le nom du `describe` du test, pour permettre de retrouver et d'exécuter sélectivement les tests via `@cypress/grep`.

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
