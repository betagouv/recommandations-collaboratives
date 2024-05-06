# Bibliothèque SCSS pour DSRC UI

Ce dossier contient les feuilles de style en SCSS qui accompagnent les templates `dsrc` et `dsrc_crsipy_forms`.

Il contient

- l'intégration du Systéme de Design de l'État (DSRF)
- Les définitions de tokens et styles spécifiques de DSRC
- Les surcharges de style des bibliothèques externes

La bibliothèque est divisée en deux parties:

- `tokens` : contient les définitions de variables CSS spécifiques au projet DSRC
- `core` : contient la configuration, les styles spéficifiques au projet, let les surcharges des libs externes (sous `ext`)

## Prise en Main

Les feuilles de style CSS sont générées avec les scripts `build:csstokens` et `build:csscore` dans le répértoire `static` du projet Django avec Rollup.

Ces scripts utilisent les fichiers `index.js` dans `tokens` and `core` pour faire la transpilation: ils importent le fichier `index.scss`, ce qui rend les code source SCSS visible à Rollup pour traitement.

## Ajout de feulles de style

Afin d'inclure des nouvelles feulles de style, il suffit d'inclure le `path` de la feuille de style dans le fichier `index.scss` du dossier correspondant et de lancer un build.

## Build et Dev

Pour lancer un build des `tokens`:

```sh
yarn build:csstokens
```

Pour lancer un build du `core`:

```sh
yarn build:csscore
```

Des scripts de dev correspondants sont aussi disponibles: `dev:csstokens` et `dev:csscore`.
Ces scripts lanceront Rollup avec l'option `watch` configurée pour observer les changements des répertoires SCSS correspondants.

## Configuration

Les configurations pour les librairies `tokens` et `core` se trouvent dans les fichiers `rollup.config.csstokens.js` et  `rollup.config.csscore.js` respectivement.

## Architecture SCSS

Afin de faciliter la lecture des correspondances entre les styles et la bibliothèque de templates Django, il est suggéré d'utiliser l'organisation de répertoires SCSS suivante:

```sh
.
`-- scss
    |-- core
    |   |-- blocks # styles correspondants à des composants élémentaires et indivisibles: buttons, inputs, icons, etc
    |   |-- compositions # styles correspondants à des composants complexes, faits des `blocks` et d'autres `compsitions` : formulaires, headers, navs, etc
    |   |-- config # resets, glbals, mixins, utilities
    |   |-- ext # surcharges de bibliothèques externes, nommées d'après la bibliothèque source à surcharger
    |   |-- layouts # surcharges de bibliothèques externes, nommées d'après la bibliothèque source
    |   `-- pages # surcharges de style pour des pages `home.scss`, `contact.scss` etc
    `-- tokens # variables SCSS
```

Par ailleurs, il est conseillé de grouper les tokens par catégorie: `colors.scss`, `layouts.scss`, `icons.scss` etc.
