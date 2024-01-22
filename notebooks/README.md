# DSRC - Documentation des Templates Django

Ce module contient la documentation pour la bibliothèque de templates Django du Système de Design des portails Recoco, DSRC.

## Prise en Main

### Prérequis

- le projet Django qui contient ce module est installé et peut être lancé en mode développement
- pour démarrer l'installation ci-dessous, vous avez une console ouverte à la racine du projet Django
- vous avez démarré un environnement virtuel (`virtualenv` ou équivalent)

Note: cette documentation est en cours de création,  l'intégration avec Docker n'a pas encore été traitée

### Installer Jupyter Notebooks dans Django

Installer les paquets qui permettent le lancement de Jupyter dans le projet Django:

```sh
pip install jupyter ipython django-extensions
```

Installer la version de `notebooks` qui sera compatible avec l'extension  `shell_plus`:

```sh
pip install --upgrade notebook==6.4.12
```

## Usage des Notebooks

Pour lancer Jupyter dans Django et interagir avec le backend:

1. 🗒️ Terminal 1: Démarrer Jupyter Notebooks à la racine du projet

```sh
python manage.py shell_plus --notebook
```

1. 🐍 Terminal 2: Démarrer le backend Django à la racine du projet

```sh
python manage.py runserver
```

1. 🎨 Terminal 3: Démarrer  le serveur de dev de la lib `dsrc-ui` dans `[racine-django]/dsrc-ui` (optionnel, selon la tâche)

```sh
yarn dev
```

1. ✨ Terminal 4: Démarrer   le serveur de dev du `frontend` dans `[racine-django]/frontend` (optionnel, selon la tâche)

```sh
yarn dev
```

## CSS dans Jupyter dans Django

Afin d'appliquer des styles à un Template Django à l'intérieur d'une cellule Jupyter Notebooks,  on charge le CSS dans un `string` qui est injecté  dans le `Template` construit dans Jupyter via le dict `Context`. Les styles sont ensuite rendus dans un tag `<style>` à l'intérieur d'un `{% block css %}`.


Fonction permettant de charger des styles depuis le dossier `static` :

- Copier le code dans une cellule du Notebook qui précède le rendu du Template

```python
# Load CSS files as raw text using python
"""
Read a CSS file and load it into Jupyter.
Pass the file path to the CSS file.
"""
def _set_css_style(css_file_path):

   styles = open(css_file_path, "r").read()
   s = '%s' % styles     
   return HTML(s)

csscore = _set_css_style('static/css/dsfr.css') # changer pour le fichier de style souhaité
```

Ensuite, définir un Template dans une cellule suivante:

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
    <button class="fr-tag">Test CSS button</button>
</table>
""")

context = Context(
    {'projects': projects.order_by("-created_on")[:10], 'csscore': csscore.data } # On passe les styles, contenus dans `data`
)

HTML(template.render(context)) # Affiche le template
```

- [Source: solution pour charger du CSS dans une cellule Jupyter Notebook (SO)](https://stackoverflow.com/questions/32156248/how-do-i-set-custom-css-for-my-ipython-ihaskell-jupyter-notebook)


### Problèmes d'installation Jupyter

En cas d'erreur:

```sh
ModuleNotFoundError: No module named 'notebook.notebookapp'
```

Tout d'abord, il faut s'assurer qu'on a installé une version de `notebooks` compatible avec l'extension `shell_plus`:

```sh
pip install --upgrade notebook==6.4.12
```

[Voir cette réponse au problème (SO)](https://stackoverflow.com/questions/76893872/modulenotfounderror-no-module-named-notebook-base-when-installing-nbextension)

Ensuite, si les problèmes persitent, ils se peut qu'ils soient dus à une incompatibilité de numéros de version de `traitlets`. Si c'est le cas, il peuvent être résolus en exécutant la mise à jour suivante:

```sh
pip uninstall traitlets
pip install traitlets==5.9.0
```

## Resources

Guides d'installation:

- [Install Jupyter Notebook](https://github.com/jupyter/notebook)