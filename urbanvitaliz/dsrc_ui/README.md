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
- feuilles de style (`src/lib/styles/scss/core`, compilées en CSS dans le dossier `static` en sortie)
- surcharges de variables CSS (`src/lib/styles/scss/tokens`, compilées en CSS dans le dossier `static` en sortie)
- jeux de polices (`src/lib/fonts`)
- icônes (`src/lib/icons`)

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

## Fonts

// TODO Français

## Icons

// TODO Français

## Working with Forms

// TODO Français

### Input Validation

// TODO Français

- [AJV Standalone Validation Mode](https://ajv.js.org/standalone.html)

## Troubleshooting

Ajv and Rollup

Ajv uses `commonjs` modules in its setup. To use it in the browser, we need to convert commonjs module syntax to ES modules syntax.
This is done using `@rollup/plugin-commonjs` and setting the `transformMixedEsModules` to `true`.
You can see the full configuration in `rollup.config.js`.

More resources here:

- [@rollup/plugin-commonjs transform option](https://github.com/rollup/plugins/tree/master/packages/commonjs#transformmixedesmodules)
- Based on [this comment on how to use AJV `commonjs` modules with ESM syntax](https://github.com/ajv-validator/ajv/issues/2209)

## Ressources

- [DSFR - Éléments d'interface](https://www.systeme-de-design.gouv.fr/elements-d-interface)
- [DSFR - API Javascript](https://www.systeme-de-design.gouv.fr/utilisation-et-organisation/developpeurs/api-javascript)
- [Rollup Config options](https://rollupjs.org/configuration-options/)
