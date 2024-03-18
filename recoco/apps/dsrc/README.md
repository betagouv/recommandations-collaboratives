# DSRC Django Template Library

Ce dossier contient une bibliothèque de templates Django basée sur le [Système de Design de l'État (DSFR) Version Courante](https://www.systeme-de-design.gouv.fr/a-propos/versions/version-courante/) ( v1.11.0 ).

La bibliothèque se compose de deux modules: `dsrc` et `dsrc-crispy-forms`

- module `dsrc` bibliothèque de templates Django réutilisables
- module `dsrc-crispy-forms` template pack:  bibliothèque pour la gestion des formulaires

## DSRC

Le module `dsrc/templates/core` est organisé dans les modules suivants:

- **blocks -** fragments faits d'un composant indivisible qui sert de base pour la création de `compositions`
- **compositions -** fragments crées à partir de `blocks` et d'autres `compositions` et qui permettent de répondre à un besoin spécifique des usagers de l'interface
- **layouts -** fragments dénoués de sémantique qui servent uniquement au placement et alignement de leur contenu
- **pages -** modèles de page type du projet qui intègrent les éléments globaux par défault de l'application (header, footer, ...), faites à partir de `layouts` et de `compositions`

### Exemples

Le module `dsrc/templates/samples` contient des bases de code à prendre comme example pour des intégrations spécifiques.

Un démo de formulaire est visible sur `http://recoco.localhost:8000/dsrc/`

- voir l'intégration dans `urls.py`, `views.py` et `forms.py`

## dsrc-cripsy-forms

La structure est celle attendue par `crispy-forms` : [Cripsy Forms - How to create your own template packs](https://django-crispy-forms.readthedocs.io/en/latest/template_packs.html#)

- Utilise également des templates de la bibliothèque `dsrc`