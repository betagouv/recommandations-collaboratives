# Tests E2E Playwright

Suite E2E migrée depuis Cypress (`cypress/e2e/`), à périmètre identique :
126 fichiers, mêmes describe/it, mêmes assertions. Pendant la coexistence,
les données de test restent dans `cypress/fixtures/` (elles servent aussi au
seeding Django via `manage.py testserver`).

**Durée** (référence : ~13 min en Cypress) : **~3,8 min** avec 2 workers
(défaut), **~3,2 min** avec `PW_WORKERS=4`. Les seuls échecs attendus sont
les 3 tests déjà cassés en amont (voir plus bas), qui échouent aussi en
Cypress.

## Lancement

```bash
yarn e2e:pw          # run complet headless (build Vite + testserver Django + Playwright)
yarn e2e:pw:ui       # mode UI Playwright
yarn e2e:pw:report   # ouvrir le dernier rapport HTML
PW_WORKERS=4 yarn e2e:pw   # ajuster le parallélisme (2 par défaut)
```

Prérequis identiques à Cypress : Postgres démarré, `.env` renseigné
(`DJANGO_DB_*`, `GDAL/GEOS_LIBRARY_PATH`), venv Python actif.

Filtrer par tag (équivalent de @cypress/grep) : `playwright test --grep @connexion`.

## Architecture

```
e2e/
├── setup/auth.setup.ts    # login API par rôle → storageState (1 fois par run)
├── .auth/                 # storageStates générés (gitignoré)
├── fixtures/index.ts      # `test` étendu : fixture loginAs(role)
├── helpers/
│   ├── users.ts           # mapping rôle → users.json, authFile(role)
│   ├── commands.ts        # port des commandes custom Cypress
│   ├── tools/editor.ts, tools/geolocation.ts, views/project.ts, dsrc/forms.tools.ts
└── tests/                 # miroir de cypress/e2e/ (canXxx.cy.js → canXxx.spec.ts)
```

**Authentification** : le projet Playwright `setup` se connecte une fois par
rôle (flux CSRF de `cy.login`, sans navigateur) et sauvegarde les cookies dans
`e2e/.auth/`. Les specs déclarent leur rôle via
`test.use({ storageState: authFile('conseiller1') })` — plus aucun login par
test. Pour changer de rôle en cours de test : `const page2 = await loginAs('staff')`.
Le rôle `nonactive` (compte désactivé) n'a pas de storageState : utiliser
`loginViaForm(page, 'nonactive')`.

Le storageState par défaut (`anonymous.json`) contient uniquement le cookie
`cookie_consent` qui neutralise le bandeau DSFR (ex-`beforeEach` global
Cypress). Les tests du bandeau lui-même utilisent
`test.use({ storageState: { cookies: [], origins: [] } })`.

## Table de conversion Cypress → Playwright

| Cypress | Playwright |
|---|---|
| `describe('X @tag', ...)` | `test.describe('X', { tag: '@tag' }, ...)` |
| `describe.skip` | `test.describe.skip` (commentaires d'origine conservés) |
| `it(...)` | `test(...)` |
| `cy.login(role)` en beforeEach | `test.use({ storageState: authFile(role) })` en tête de fichier |
| `cy.login(role)` en cours de test | `const page2 = await loginAs(role)` (fixture) |
| `before()` + état module partagé | `test.describe.configure({ mode: 'serial' })` + `test.beforeAll` |
| `cy.get(sel)` | `page.locator(sel)` |
| `cy.contains(txt)` | `page.getByText(txt)` + `await expect(...).toBeVisible()` |
| `.should('have.value', v)` | `await expect(loc).toHaveValue(v)` |
| `.should('not.exist')` | `await expect(loc).toHaveCount(0)` |
| `.type(t)` | `loc.fill(t)` — ou `pressSequentially(t)` pour les champs à autocomplétion (postcode, recherche) et `page.keyboard.type` pour TipTap/ProseMirror |
| `.click({ force: true })` | `loc.click({ force: true })` — si l'élément est hors viewport (« Element is outside of the viewport »), utiliser `loc.dispatchEvent('click')` |
| `cy.url().should('include', p)` | `await expect(page).toHaveURL(new RegExp(p))` |
| `cy.intercept` + `cy.wait` | `page.waitForResponse(...)` ou assertion sur `page.goto()` |
| `cy.viewport(w, h)` | `test.use({ viewport: { width, height } })` par describe |
| `.selectFile(path)` | `loc.setInputFiles(path)` |
| `cy.setCookie` | couvert par le storageState |
| `canXxx.cy.js` | `canXxx.spec.ts` (arborescence miroir) |

## Parallélisme

`fullyParallel: false` (parallélisme au niveau fichier, comme
cypress-parallel), 2 workers par défaut (`PW_WORKERS` pour ajuster). Les
fichiers qui mutent un même état seedé (projet 18 « Mise en pause -
Collectivité », ressource 1) sont regroupés dans le projet Playwright
`chromium-serial` (`workers: 1` — liste `SHARED_STATE_MUTATORS` dans
`playwright.config.ts`) pour ne jamais se chevaucher. Certains tests sont
« one-shot » (suppression de document, inscription, tutoriel…) : ils ne
passent qu'une fois par base fraîche, exactement comme en Cypress — relancer
`yarn e2e:pw` redémarre un testserver avec une base neuve.

## Différences assumées avec Cypress

- Le login est fait une fois par rôle au setup (storageState), pas à chaque
  test — gain de temps principal de la migration.
- `Cypress.on('uncaught:exception')` n'a pas d'équivalent nécessaire :
  Playwright ne fait pas échouer un test sur une exception page non gérée.
- `canExploreAllUrls` : le statut est vérifié sur la réponse de `page.goto`
  (au lieu d'un `cy.intercept`).
- La visibilité Playwright ignore le *clipping* par un ancêtre
  (`overflow: hidden`) que Cypress prend en compte : pour les dropdowns
  Bootstrap, l'état ouvert/fermé est vérifié via la classe `show`, et les
  clics sur des éléments clippés utilisent `dispatchEvent('click')`.
- Cypress tape lentement et réessaie ses assertions, ce qui masquait des
  courses d'hydratation Alpine/TipTap. Les points de synchronisation ajoutés
  (motif `expect(async () => {...}).toPass()`, helper `waitForAlpine`,
  attente du peuplement d'un formulaire rechargé par API) rendent ces
  attentes explicites sans changer ce qui est testé.
- Deux titres de tests dupliqués dans Cypress (interdits par Playwright) ont
  été dédoublonnés : « toggle off an impact tag »
  (`canToggleProjectImpactTagInCRM`) et « should not display CTA as advisor »
  (`canSeeCtaOnSurvey`) — commentaires en place dans les fichiers.
- Tests connus comme cassés en amont (échouent aussi en Cypress) :
  - `public/canAccessAWayToContactTheTeam` : le formulaire `/contact` n'est
    rendu que pour un utilisateur connecté (« quick fix to unlock brevo » dans
    `recoco/apps/home/templates/home/contact.html`), le test visiteur ne peut
    plus passer.
  - `header/canCreateANewProject` (« display button as a collectivity ») :
    échoue également en Cypress sur les mêmes données.
  - `project/staff/kanban/canDisplayOnlyMyProjects` : le toggle « mes
    dossiers » ne filtre aucune carte sur les données seedées ; échoue aussi
    en Cypress sur base fraîche (le spec porte un TODO « Verify when the
    fixing frontend test environment is done »).
