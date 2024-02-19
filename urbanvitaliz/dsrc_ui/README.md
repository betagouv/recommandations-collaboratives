# DSRC UI

Ce paquet contient:

1. Une biliothèque de composants JavaScript
1. Une biliothèque SCSS
1. Une biliothèque de polices de caractères
1. Une bibliothèaque d'icônes

Les biliothèques ci-dessus sont basées sur le [Système de Design de l'État (DSFR) Version Courante](https://www.systeme-de-design.gouv.fr/a-propos/versions/version-courante/) ( v1.11.0 ).

Le paquet centralise la séléction des ressources front nécéssaires au projet et leur export dans le dossier `static/assets` du projet racine Django.

Les resources prises en charge par le paquet sont:

- intégration de modules externes JavaScript et CSS (sousdossiers `src/**/ext`)
- modules JavaScript (`src/lib/components`)
- feuilles de style (`src/lib/styles/scss/core`, )
- surcharges de variables CSS (`src/lib/styles/scss/tokens`)
- jeux de polices (`src/lib/fonts`)
- icônes (`src/lib/icons`)

Toutes ces bibliothèques sont copiées ou transpilées dans le dossier dans le dossier `static` en sortie

## Prise en main

### Dev

Installer les dependances:

```shell
yarn install
```

Lancer l'environnement de développement:

```bash
yarn dev
```

### Build

Pour créer un bundle pour l'environnement de production:

```bash
yarn build
```

## Gestion des assets

Les `assets` utilisés par les composants Alpine et les templates Django sont générés avec des scripts dans `package.json`, en utilisant la config correspondante.

Les scripts doivent être préfixés de `npm run` (ou `yarn` ou `pnpm`)

### CSS

#### Tokens

- **config :** `rollup.config.csstokens.js`
- **scripts :** `build:csstokens` et `dev:css:tokens`

#### Core

- **config :** `rollup.config.csscore.js`
- **scripts :** `build:csscore` et `dev:css:csscore`

### JavaScript

#### Composants (bibliothèque entière)

- **config :** `vite.config.js` et fichier `src/lib/index.js`
- **scripts :** `build` et `dev`

#### Composants (composants séparés)

- **config :** `rollup.config.modules.js`
- **scripts :** `build:modules` et `dev:modules`

#### Fonctions de validation Ajv

- **config :**  les fichiers `src/ext/ajv.*` permettent de définir des schemas pour générer les fonctions de validation
- **scripts :** `build:ajv`

### Jeux de Polices (fonts)

- **config :** `rollup.config.fonts.js`
- **scripts :** `build:fonts`

### Icônes

- **config :** `rollup.config.icons.js`
- **scripts :** `build:icons`

#### Ajout d'icônes

Les icones utilisés par la librairie DSFR et DSRC sont rendus grace à des règles CSS.
Les fichiers SVG source doivent être placés dans le sous dossier `icons` afin d'être détectés par Rollup pour le build.

Si les icônes sont issus du DSFR:

- copier le fichier `svg` de l'icône depuis `node_modules/@gouvfr/dsrf/dist/icons/*/`
- il faut garder la structure de répertoires de `dsfr`. Ainsi, si l'icone se trouve dans le sous-dossier `logo`, alors il faut créer le sous-dossier `icons/logo` si celui-ci n'existe pas. Ceci permet au CSS issu de DSFR d'avoir accès aux icônes dans les chemins attendus.

Si les icônes sont spécifiques à `dsrc`:

- ajouter le fichier `svg` de l'icône dans le sous dossier `icons/dsrc`
- ajouter la règle CSS correspondante dans le fichier `src/lib/styles/scss/core/blocks/icons`

Si les icônes appartiennent à une bibliothèque externe, par exemple `remix-icon`

- ajouter le fichier `svg` de l'icône dans le sous dossier `icons/ext`
- ajouter la règle CSS correspondante dans le fichier `src/lib/styles/scss/core/ext/remix-icon.scss`

## CI

Un script `build:ci` permet de produire des assets sans utiliser les scripts `build:fonts` et `build:icons`. Ceci permet d'éviter de copier inutilement des assets qui ne changeront pas pendant des longues périodes.

TODO: utiliser le hash du bundle pour switcher vers le script `build` complet losque les jeux de police ou les ic icônes changent.

## Validation des Formulaires

Un formulaire rendu en Django peut être agrémenté de la validation côté client en utilisant le composant `DsrcFormValidator` qui prend en paramètre l'`id` du form, l'objet `form_data` fourni par le contexte du Template Django, et le nom de la fonction de validation à utiliser.

Pour définir la fonction de validation du formulaire:

- définir le JSON schema dans `src/ext/ajv.schemas.forms.js`
- ajouter le schéma dans le fichier `src/ext/ajv.cjs`
- lancer le script `build:ajv` qui généréra la fonction de validation

Lors du build de la bibliohèque `dsrc_ui`, les fonctions de validation définies par les schémas seront prêtes à être utilisées par `DsrcFormValidator` dans le tempate Django.

Plus d'informations sur AJV:

- [AJV Standalone Validation Mode](https://ajv.js.org/standalone.html)
- [AJV - Doc for JSON Schema](https://ajv.js.org/json-schema.html)

### Ajv et Rollup

Ajv utilise des modules `commonjs`. Pourque cela marche dans le browser, on doit convertir le module js en syntaxe ESM.
On fait ceci grâce au plugin `@rollup/plugin-commonjs`  avec le setting `transformMixedEsModules` à `true`.
La configuration des ces options se trouve dans `vite.config.js`.

Plus de resources ici:

- [@rollup/plugin-commonjs transform option](https://github.com/rollup/plugins/tree/master/packages/commonjs#transformmixedesmodules)
- Basé sur [ce commentaire sur comment utiliser les modules `commonjs` avec la syntaxe ESM](https://github.com/ajv-validator/ajv/issues/2209)

## Ressources

- [DSFR - Éléments d'interface](https://www.systeme-de-design.gouv.fr/elements-d-interface)
- [DSFR - API Javascript](https://www.systeme-de-design.gouv.fr/utilisation-et-organisation/developpeurs/api-javascript)
- [Rollup Config options](https://rollupjs.org/configuration-options/)
