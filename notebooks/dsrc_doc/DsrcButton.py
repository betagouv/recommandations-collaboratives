#!/usr/bin/env python
# coding: utf-8
# %%
# Initialize Notebook

from notebooks.django_for_jupyter import init_django

init_django("recoco")


# %%

from recoco.apps.projects.models import Project

projects = Project.objects.all()

# %%

from IPython.display import HTML, display
from django.template import Context, Template

# %%
from notebooks.dsrc_doc.dsrc_utils import load_asset

csscore = load_asset("css/dsrc-csscore.css")
csstokens = load_asset("css/dsrc-csstokens.css")
cssoverrides = load_asset("css/output.css")
jscore = load_asset("js/index.js")
component = load_asset("js/components/DsrcButton.js")
# print(component.data)
# print(csscore.data)

# %%
from IPython.display import Javascript, Markdown
from ipywidgets import widgets

out = widgets.Output(layout={"border": "1px solid black"})


def on_button_clicked(b):
    my_js = """
    console.log('Hello world2!');
    alert("hi");
    """
    with out:
        # print(my_js)
        display(Javascript(my_js))
        display(Markdown("on_button_clicked called"))
        print("on_button_clicked call ended")


button = widgets.Button(
    description="Button",
    disabled=False,
    button_style="",
    tooltip="Button",
    icon="check",
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
        "label": "Label of the button item",
        "name": "(Optional) name of the button",
        "type": "(Optional) type of button (submit or button - default: submit)",
        "onclick": "button action",
        "is_disabled": "(Optional) boolean that indicate if the button is activated"
            (default: False)",
        "size": "(Optional) `sm` or `lg`",
        "variant": "(Optional) `primary` `secondary`, or  `tertiary-no-outline`",
        "color": "(Optional) color class name",
        "icon": "(Optional) icon class name: ex `fr-icon-info-fill`
            (see: https://www.systeme-de-design.gouv.fr/elements-d-interface/fondamentaux-techniques/icone)",
        "align": "(Optional) align icon `left` or `right` - icon value must be set for alignment class to take effect",
        "title": "(Optional) if True, the icon will be displayed without a visible label,
            and the label will be used as the icon title (default: False)",
        "classes": "(Optional) extra classes"
    }

    ```

    All of the keys of the dict can be passed directly as named parameters of the tag.

    **Tag name**:

        dsrc_button

    **Usage**:

        `{% dsrc_button data_dict %}`

        For JavaScript developers, this is roughly equivalent to writing:

        `<DsrcButton props={data_dict} />` # ~ Svelte / Vue / React
"""

template = Template(
    """
{% load dsrc_tags %}
{% block css %}
    <style>
        {{csscore}} # necessary in Jupyter Notebooks only
    </style>
{% endblock %}

{% block main %}
    {% dsrc_button data_dict %}
{% endblock %}
"""
)

data_dict = {
    "label": "DsrcButton",
    "onclick": "(event) => alert('clicked')",
    "type": "button",
    "name": "dsrc_button",
    "is_disabled": False,
    "size": "md",
    "variant": "secondary",
    "icon": "fr-icon--info-fill",  # nom de l'icône, sans l'extension SVG
    "align": "right",
    "classes": "dsrc-color--primary",
}

context = Context({"data_dict": data_dict, "csscore": csscore.data})

HTML(template.render(context))
