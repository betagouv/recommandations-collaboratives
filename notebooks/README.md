# DSRC - Documentation

Ce module contient la documentation pour la bibliothèque de templates Django du Système de Design des portails Recoco, DSRC.

## Prise en Main

Le code su système de design DSRC est composé de 4 modules:

- `dsrc-doc` : contient la documentation interactive de la bibliothèque sous forme de Jupyter Notebooks (c'est ici!)
- `dsrc-ui` : contient les fichiers source CSS et JavaScript de la librairie de composants
- `dsrc-dj` : contient les templates Django des composants (HTML)
- `dsrc-tests` : contient les tests unitaires et d'intégration des composants

L'arborsecence de ces modules dans le projet est la suivante:

```sh
.
|-- dsrc-tests
|-- notebooks
|   `-- dsrc-doc
`-- urbanvitaliz
    |-- dsrc-ui
    |-- templates
    |   `-- dsrc-dj
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

1. 🎨 Terminal 3 : Démarrer le serveur de dev de la lib `dsrc-ui` dans `[root]/urbanvitaliz/dsrc-ui`

```sh
yarn dev
```

Pour travailler sur les composants ui de l'application:

1. ✨ Terminal 4 : Démarrer le serveur de dev du `frontend` dans `[root]/urbanvitaliz/frontend`

```sh
yarn dev
```

## CSS dans Jupyter dans Django

Afin d'appliquer des styles à un Template Django à l'intérieur d'une cellule Jupyter Notebooks, on charge le CSS dans un `string` qui est injecté dans le `Template` construit dans Jupyter via le dict `Context`. Les styles sont ensuite rendus dans un tag `<style>` à l'intérieur d'un `{% block css %}`.

Le CSS de la librairie DSRC est généré à partir de sources SCSS dans le dossier `[root]/urbanvitaliz/dsrc-ui`.

Les fichiers sont générés dans `[root]/static/` et chargés dans Jupyter Notebooks à partir de `[root]/static/`.

Fonction permettant de charger des styles depuis le dossier `static` :

- Copier le code dans une cellule du Notebook :

```python
# Load CSS files as raw text using python
"""
Read a CSS file and load it into Jupyter.
Pass the file path to the CSS file.
"""
def _set_css_style(css_file_path):

   styles = open(css_file_path, "r").read()
   mycss = '%s' % styles
   return HTML('<style>{}</style>'.format(mycss))

csscore = _set_css_style('static/css/dsfr.css') # changer pour le fichier de style souhaité
```

Définir un Template dans la cellule suivante:

```python
template = Template("""
{% load static %}
{% load sass_tags %}
{% load django_vite %}

{% block css %}
    <style>
        {{csscore}} {# Chargement de styles ici #}
    </style>
{% endblock %}

<table class="fr-table">
    <tr>
        <th>Projet</th>
        <th>Ville</th>
        <th>Gigs</th>
    </tr>
    {% for p in projects %}
    <tr>
        <td>{{p.name}}</td>
        <td>{{p.created_on}}</td>
        <td>{{p.location}}</td>
    </tr>
    {% endfor %}
    <button class="fr-primary">Add Project</button>
</table>
""")

context = Context(
    {'projects': projects.order_by("-created_on")[:10], 'csscore': csscore.data } # On passe les styles, contenus dans `data`
)

HTML(template.render(context)) # Affiche le template
```

- [Source: solution pour charger du CSS dans une cellule Jupyter Notebook (SO)](https://stackoverflow.com/questions/32156248/how-do-i-set-custom-css-for-my-ipython-ihaskell-jupyter-notebook)

### Controle de version de Jupyter Notebooks

Afin de ne pas surcharger le dépôt avec des données générées par la doc, ce module privilégie une gestion de versions de Jupyter Notebooks sous format de fichiers `.py` avec le paquet `jupoytext`, ce qui rend l'usage notebooks facilement compatible avec git.

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
