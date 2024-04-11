# DSRC - Documentation

Ce module contient la documentation pour la bibliothèque de templates Django du Système de Design des portails Recoco, DSRC.

## Prise en Main

Le code su système de design DSRC est composé de 4 modules:

- `dsrc_doc` : contient la documentation interactive de la bibliothèque sous forme de Jupyter Notebooks (c'est ici!)
- `dsrc_ui` : contient les fichiers source CSS et JavaScript de la librairie de composants
- `dsrc` : Django app qui fournit des templates Django réutilisables basés sur DSFR avec surcharges DSRC
- `dsrc_tests` : contient les tests unitaires et d'intégration des composants (TODO: pour le moment les tests sont dans `frontend_tests`)

L'arborescence de ces modules dans le projet est la suivante:

```sh
.
|-- dsrc_tests // TODO
|-- notebooks
|   `-- dsrc_doc
`-- recoco
    |-- apps
    |   |-- dsrc
    |   |   |-- templates
    |   |   |   |-- dsrc
    |   |   |   |-- dsrc-crispy-forms
    |-- dsrc_ui
```

### Prérequis

- le projet Django qui contient ce module est installé et peut être lancé en mode développement
- pour démarrer l'installation ci-dessous, vous avez une console ouverte à la racine du projet
- vous avez démarré un environnement virtuel (`virtualenv` ou équivalent)

Note: cette documentation est en cours de création, l'intégration avec Docker n'a pas encore été traitée

### Installer Jupyter Notebooks dans Django

Installer les paquets qui permettent le lancement de Jupyter dans le projet Django:

```sh
pip install jupyter ipython django-extensions
```

Installer la version de `notebooks` qui sera compatible avec l'extension `shell_plus`:

```sh
pip install --upgrade notebook==6.4.12
```

## Usage de Jupyter Notebooks

Pour lancer Jupyter dans Django et interagir avec le backend:

1. 🗒️ Terminal 1 : Démarrer Jupyter Notebooks à la racine du projet

```sh
python manage.py shell_plus --notebook
```

1. 🐍 Terminal 2 : Démarrer le backend Django à la racine du projet

```sh
python manage.py runserver
```

Pour travailler sur les composants ui du DSRC:

1. 🎨 Terminal 3 : Démarrer le serveur de dev de la lib `dsrc_ui` dans `[root]/recoco/dsrc_ui`

```sh
yarn dev
```

Pour travailler sur les composants ui de l'application:

1. ✨ Terminal 4 : Démarrer le serveur de dev du `frontend` dans `[root]/recoco/frontend`

```sh
yarn dev
```

## CSS dans Jupyter dans Django

Afin d'appliquer des styles à un Template Django à l'intérieur d'une cellule Jupyter Notebooks, on charge le CSS dans un `string` qui est injecté dans le `Template` construit dans Jupyter via le dict `Context`. Les styles sont ensuite rendus dans un tag `<style>` à l'intérieur d'un `{% block css %}`.

Le CSS de la librairie DSRC est généré à partir de sources SCSS dans le dossier `[root]/recoco/dsrc_ui`.

Les fichiers sont générés dans `[root]/static/` et chargés dans Jupyter Notebooks à partir de `[root]/static/`.

Le fichier `ComponentTemplate.py` contient un exemple de chargement CSS dan une cellule Juypyter Notebooks.


- [Source: solution pour charger du CSS dans une cellule Jupyter Notebook (SO)](https://stackoverflow.com/questions/32156248/how-do-i-set-custom-css-for-my-ipython-ihaskell-jupyter-notebook)

### Controle de version de Jupyter Notebooks

Afin de ne pas surcharger le dépôt avec des données générées par la doc, ce module privilégie une gestion de versions de Jupyter Notebooks sous format de fichiers `.py` avec le paquet `jupitext`, ce qui rend l'usage notebooks facilement compatible avec git.

- [jupytext](https://jupytext.readthedocs.io/en/latest/)

### Problèmes d'installation Jupyter

En cas d'erreur :

```sh
ModuleNotFoundError: No module named 'notebook.notebookapp'
```

Tout d'abord, il faut s'assurer qu'on a installé une version de `notebooks` compatible avec l'extension `shell_plus` :

```sh
pip install --upgrade notebook==6.4.12
```

[Voir cette réponse au problème (SO)](https://stackoverflow.com/questions/76893872/modulenotfounderror-no-module-named-notebook-base-when-installing-nbextension)

Ensuite, si les problèmes persitent, ils se peut qu'ils soient dus à une incompatibilité de numéros de version de `traitlets`. Si c'est le cas, il peuvent être résolus en exécutant la mise à jour suivante:

```sh
pip uninstall traitlets
pip install traitlets==5.9.0
```

En cas de problèmes de lancement de commandes `graphviz`, vérifier l'installation des librairies nécessaires selon votre OS.

[Guide d'installation Graphviz](https://pygraphviz.github.io/documentation/stable/install.html)

Lors de l'installation de `pygraphviz` sous MacOS, en cas d'erreur:

```sh
error: command '/usr/bin/clang' failed with exit code 1
```

Relancez l'installation de `pygraphviz` avec la commande suivante (voir [ce commentaire sur GitHub](https://github.com/pygraphviz/pygraphviz/issues/398#issuecomment-1531236926)):

```sh
python3 -m pip install -U --no-cache-dir  \
    --config-settings="--global-option=build_ext" \
    --config-settings="--global-option=-I$(brew --prefix graphviz)/include/" \
    --config-settings="--global-option=-L$(brew --prefix graphviz)/lib/" \
    pygraphviz
```

## Ressources

Guides d'installation:

- [Install Jupyter Notebook](https://github.com/jupyter/notebook)
