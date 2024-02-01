#!/usr/bin/env python
# coding: utf-8
# %%
# Initialize Notebook

from notebooks.django_for_jupyter import init_django

init_django("urbanvitaliz")


# %%

from django.db.models import Model
from urbanvitaliz.apps.projects.models import Project



# %%

from django.template import Context, Template
from IPython.display import display, HTML


# %%


projects = Project.objects.all()


# %%
# Load CSS files as raw text using python
"""
Read a CSS or JS file and load it into Jupyter.
Make sure you trust the code you are loading.

Arg: the file path to the file, relative to the project's static assets folder
Returns: IPython.core.display.HTML object: contains JS/CSS in `data` property
"""


def _load_asset(rel_file_path):
    assets_folder = "static/assets/"
    assets_file_path = f"{assets_folder}{rel_file_path}"
    asset_content = open(assets_file_path, "r").read()
    asset = "%s" % asset_content
    return HTML(asset)


csscore = _load_asset("css/dsrc-csscore.css")
csstokens = _load_asset("css/dsrc-csstokens.css")
jscore = _load_asset("js/index.js")
component = _load_asset("js/components/DsrcButton.js")
# print(component.data)
# print(csscore.data)


# %%
from ipywidgets import widgets
from IPython.display import Javascript, Markdown

out = widgets.Output(layout={'border': '1px solid black'})

def on_button_clicked(b):
    my_js = """
    console.log('Hello world2!');
    alert("hi");
    """
    with out:
        #print(my_js)
        display(Javascript(my_js))
        display(Markdown("on_button_clicked called"))
        print("on_button_clicked call ended")

button = widgets.Button(
    description='Button',
    disabled=False,
    button_style='',
    tooltip='Button',
    icon='check'
)

# button.on_click(on_button_clicked)
# display(button, out)




 # %%
 """
    Params  : `data_dict` a dict structure that contains `<button>` element parameters
              (equivalent of `props` in JavaScript components)
    Returns : a styled `<button>` element with an event handler

    ```python
    data_dict = {
        "label"         : "Label of the button",
        "onclick"       : "Button action: a Python string that contains a JavaScript event handler",
        "type"          : "(Optional) type of button ('submit' or 'button' - default: 'submit')",
        "name"          : "(Optional) name of the button",
        "is_disabled"   : "(Optional) Indicates button state: True if the button is disabled (default: False)",
        "extra_classes" : "(Optional) Concatenated string of CSS classes"
    }
    ```

    All of the keys of the dict can be passed directly as named parameters of the tag.

    Relevant `extra_classes`:

    - `fr-btn--secondary` : secondary button
    - `fr-btn--icon-left` and `fr-btn--icon-right`: add an icon to the button and set alignment
      (associated with an icon class)
    - `fr-btn--sm` and `fr-btn--lg`: button smaller or larger than the default size

    **Tag name**:

        dsrc_button

    **Usage**:

        `{% dsrc_button data_dict %}`

        For JavaScript developers, this is equivalent to writing:

        `<DsrcButton props={data_dict} />` # ~= Svelte / Vue / React
"""

template = Template(
    """
{% load static %}
{% load dsrc_tags %}
{% block css %}
    <style>
        {{csscore}}
    </style>
{% endblock %}

{% dsrc_button data_dict %}
"""
)

data_dict = {
    "label"         : "DsrcButton",
    "onclick"       : "(event) => alert('clicked')",
    "type"          : "button",
    "name"          : "dsrc_button",
    "is_disabled"   : False,
    "extra_classes" : "fr-btn--lg dsrc-primary"
}

context = Context(
    {"data_dict": data_dict, "csscore": csscore.data, "component": component.data, "jscore": jscore.data}
)

HTML(template.render(context))


# %%

# %%

# %%
