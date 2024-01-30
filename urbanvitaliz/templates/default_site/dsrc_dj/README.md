# DSRC Django Template Library

Ce dossier contient une la librairie de templates Django basée sur le [Système de Design de l'État (DSFR) Version Courante](https://www.systeme-de-design.gouv.fr/a-propos/versions/version-courante/) ( v1.11.0 ).

La bibliothèque se compose d'un module `core` et de deux templates de base: un qui sert de racine pour l'application, et l'autre pour effectuer des tests.

Le module core est organisé dans les modules suivants:

- **blocks** fragments faits d'un composant indivisible qui sert de base pour la création de **compositions**
- **compositions** fragments crées à partir de `blocks` et d'autres `compositions` et qui permettent de répondre à un besoin spécifique des usagers de l'interface
- **layouts** fragments dénoués de sémantique et qui servent uniquement au placement et alignement de contenu dans une vue
- **pages** modèles de page type du projet qui intègrent les éléments globaux par défault de l'application

La structure de la bibliothèque est la suivante:

```sh
.
`-- urbanvitaliz/
    |-- templates/
    |   `-- default_site/
    |       |-- dsrc_dj/
    |       |   `-- core/
    |       |       |-- blocks/
    |       |       |   |-- buttons/
    |       |       |   |-- global/
    |       |       |   `-- inputs/
    |       |       |-- compositions/
    |       |       |   |-- content/
    |       |       |   |-- forms/
    |       |       |   |-- headers/
    |       |       |   |-- menus/
    |       |       |   `-- navs/
    |       |       |-- layouts/
    |       |       `-- pages/
```

## Prise en main
