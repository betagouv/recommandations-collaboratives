# encoding: utf-8

"""
Tags used by the DSRC template library.

This file is largely adapted from the work done on the project `django-dsfr`, in particular : https://github.com/numerique-gouv/django-dsfr/blob/main/dsfr/templatetags/dsfr_tags.py

What changes from `django-dsfr`:

- this library uses `dsrc` prefixes instead of `dsfr`
- the folder structure for templates differs. For mode details on folder structure please refer to `urbanvitaliz/apps/dsrc/README.md`

Templatetag parameters are kept as-is from `django-dsfr` definitions in order to retain compatibility with that project.

authors: patricia.boh@beta.gouv.fr
created: 2024-01-31 11:19:06 CEST
"""

from django import template
from django.template.context import Context

from urbanvitaliz.apps.dsrc.utils import generate_random_id

register = template.Library()

def parse_tag_args(args, kwargs, allowed_keys: list) -> dict:
    """
    Allows to use a tag with either all the arguments in a dict or by declaring them separately
    """
    if args:
        tag_data = args[0]
    else:
        tag_data = {}

    for k in kwargs:
        if k in allowed_keys:
            tag_data[k] = kwargs[k]

    return tag_data

@register.inclusion_tag("dsrc/core/compositions/forms/form_base.html", takes_context=True)
def dsrc_form(context) -> dict:
    """
    Returns the HTML for a form snippet

    **Tag name**:
        dsrc_form

    **Usage**:
        `{% dsrc_form %}`
    """

    return context

@register.inclusion_tag("dsrc/core/compositions/forms/form_multistep.html", takes_context=True)
def dsrc_form_multistep(context) -> dict:
    """
    Returns the HTML for a multi step form snippet

    **Tag name**:
        dsrc_form_multistep

    **Usage**:
        `{% dsrc_form_multistep %}`
    """

    if "id" not in context:
        context["id"] = generate_random_id("dsrc-form-multistep")
    if "classes" not in context:
        context["classes"] = "dsrc-form"

    return context

@register.inclusion_tag("dsrc/core/blocks/inputs/field.html")
def dsrc_form_field(field) -> dict:
    """
    Returns the HTML for a form field

    **Tag name**:
        dsrc_form_field

    **Usage**:
        `{% dsrc_form_field field %}`
    """

    return {"field": field}

@register.inclusion_tag("dsrc/core/compositions/forms/fieldset.html")
def dsrc_fieldset(fieldset) -> dict:
    """
    Returns the HTML for a form fieldset

    **Tag name**:
        dsrc_fieldset

    **Usage**:
        `{% dsrc_fieldset fieldset %}`
    """

    return {"fieldset": fieldset}

@register.inclusion_tag("dsrc/core/blocks/inputs/input_text.html")
def dsrc_input_text(*args, **kwargs) -> dict:
    """
    Returns a input item. Takes a dict as parameter, with the following structure:

    ```python
    data_dict = {
        "id": "The unique html id of the input item",
        "label": "Label of the input item",
        "type": "Type of the input item (default: 'text')",
        "onchange": "(Optional) Action that happens when the input is changed",
        "value": "(Optional) Value of the input item",
        "min": "(Optional) Minimum value of the input item (for type='date')",
        "max": "(Optional) Maximum value of the input item (for type='date')",
        "classes": "(Optional) string with names of extra classes"
    }
    ```

    All of the keys of the dict can be passed directly as named parameters of the tag.

    Use `classes` to override  DSFR / DSRC with site specific styles :

    - `ecoq-input`
    - `mec-input`
    - `sosm-input`
    - `sosp-input`
    - `uv-input`


    **Tag name**:
        dsrc_input

    **Usage**:
        `{% dsrc_input data_dict %}`
    """

    allowed_keys = [
        "id",
        "label",
        "type",
        "onchange",
        "value",
        "min",
        "max",
        "classes",
    ]
    tag_data = parse_tag_args(args, kwargs, allowed_keys)

    if "id" not in tag_data:
        tag_data["id"] = generate_random_id("input")
    if "classes" not in tag_data:
        tag_data["classes"] = "dsrc-input"

    return {"self": tag_data}

@register.inclusion_tag("dsrc/core/blocks/buttons/button.html")
def dsrc_button(*args, **kwargs) -> dict:
    """
    Returns a button item. Takes a dict as parameter, with the following structure:

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
    

    Use `classes` to override  DSFR / DSRC with site specific styles :

    - `ecoq-btn`
    - `mec-btn`
    - `sosm-btn`
    - `sosp-btn`
    - `uv-btn`

    **Tag name**:
        dsrc_button

    **Usage**:
        `{% dsrc_button data_dict %}`
    """
    allowed_keys = [
        "label",
        "name",
        "type",
        "onclick",
        "is_disabled",
        "size",
        "variant",
        "color",
        "icon",
        "align",
        "title",
        "classes"
    ]
    tag_data = parse_tag_args(args, kwargs, allowed_keys)

    if "is_disabled" not in tag_data:
        tag_data["is_disabled"] = False
    if "title" not in tag_data:
        tag_data["title"] = False
    return {"self": tag_data}

@register.inclusion_tag("dsrc/core/blocks/inputs/select.html")
def dsrc_select(*args, **kwargs) -> dict:
    """
    Returns a select item. Takes a dict as parameter, with the following structure:

    ```python
    data_dict = {
        "id": "The html id of the select item",
        "label": "Label of the select item",
        "onchange": "(Optional) Action that happens when the select is changed",
        "selected": "(Optional) If the item is selected",
        "default": { # Optional
            "disabled": "If the item is disabled",
            "hidden": "If the item is hidden",
        },
        "options": [
            {"text": "Option 1", "value": 1 },
            {"text": "Option 2", "value": 2 }
        ],
        "classes": "(Optional) string with names of extra classes"
    }
    ```

    All of the keys of the dict can be passed directly as named parameters of the tag.

    Use `classes` to override  DSFR / DSRC with site specific styles :

    - `ecoq-select`
    - `mec-select`
    - `sosm-select`
    - `sosp-select`
    - `uv-select`

    **Tag name**:
        dsrc_select

    **Usage**:
        `{% dsrc_select data_dict %}`
    """

    allowed_keys = [
        "id",
        "label",
        "onchange",
        "selected",
        "default",
        "options",
        "classes",
    ]
    tag_data = parse_tag_args(args, kwargs, allowed_keys)

    if "id" not in tag_data:
        tag_data["id"] = generate_random_id("select")
    if "classes" not in tag_data:
        tag_data["classes"] = "dsrc-select"

    return {"self": tag_data}

@register.inclusion_tag("dsrc/core/compositions/navs/breadcrumb.html", takes_context=True)
def dsrc_breadcrumb(context: Context, tag_data: dict = {}) -> dict:
    """
    Returns a breadcrumb item. Takes a dict as parameter, with the following structure:

    ```python
    data_dict = {
        "links": [{"url": "first-url", "title": "First title"}, {...}],
        "current": "Current page title",
        "root_dir": "the root directory, if the site is not installed at the root of the domain",
        "classes": "(Optional) string with names of classes to override default theme.",
    }
    ```

    If the dict is not passed as a parameter, it extracts it from context.

    **Tag name**:
        dsrc_breadcrumb

    **Usage**:
        `{% dsrc_breadcrumb data_dict %}`
    """  # noqa
    if not tag_data:
        if "breadcrumb_data" in context:
            tag_data = context["breadcrumb_data"]
        else:
            tag_data = {}
    if "classes" not in tag_data:
        tag_data["classes"] = "dsrc-breadcrumb"
    return {"self": tag_data}

@register.inclusion_tag("dsrc/core/blocks/global/link.html")
def dsrc_link(*args, **kwargs) -> dict:
    """
    Returns a link item. Takes a dict as parameter, with the following structure:

    ```python
    data_dict = {
        "url": "URL of the link item",
        "label": "Label of the link item",
        "is_external": "(Optional) Indicate if the link is external",
        "size": "(Optional) `sm` or `lg`",
        "icon": "(Optional) icon class name: ex `fr-icon-info-fill`
            (see: https://www.systeme-de-design.gouv.fr/elements-d-interface/fondamentaux-techniques/icone)",
        "align": "(Optional) align icon `left` or `right` - icon value must be set for alignment class to take effect",
        "classes": "(Optional) string with names of extra classes: override with site specific prefix.",
    }
    ```

    All of the keys of the dict can be passed directly as named parameters of the tag.

    Use `classes` to override  DSFR / DSRC with site specific styles :

    - `ecoq-link`
    - `mec-link`
    - `sosm-link`
    - `sosp-link`
    - `uv-link`

    **Tag name**:
        dsrc_link

    **Usage**:
        `{% dsrc_link data_dict %}`
    """

    allowed_keys = [
        "url",
        "label",
        "is_external",
        "size",
        "icon",
        "align",
        "classes",
    ]
    tag_data = parse_tag_args(args, kwargs, allowed_keys)

    if "id" not in tag_data:
        tag_data["id"] = generate_random_id("select")
    if "classes" not in tag_data:
        tag_data["classes"] = "dsrc-link"

    return {"self": tag_data}

@register.inclusion_tag("dsrc/core/blocks/global/skiplinks.html", takes_context=True)
def dsrc_skiplinks(context: Context, items: list) -> dict:
    """
    Returns a skiplinks item. Takes a list as parameter, with the following structure:

    ```python
    items = [{ "link": "item1", "label": "First item title"}, {...}]
    ```

    If the list is not passed as a parameter, it extracts it from context.

    **Tag name**:
        dsrc_skiplinks

    **Usage**:
        `{% dsrc_skiplinks items %}`
    """
    if not items:
        if "skiplinks" in context:
            items = context["skiplinks"]
        else:
            items = {}
    return {"self": {"items": items}}

@register.inclusion_tag("dsrc/core/compositions/forms/stepper.html")
def dsrc_stepper(*args, **kwargs) -> dict:
    """
    Returns a stepper item. Takes a dict as parameter, with the following structure:

    ```python
    data_dict = {
        "current_step_id": "Number of current step",
        "current_step_title": "Title of current step",
        "next_step_title": "(Optional) Title of next step",
        "total_steps": "Total number of steps",
        "classes": "(Optional) string with names of extra classes: override with site specific prefix.",
    }
    ```

    All of the keys of the dict can be passed directly as named parameters of the tag.

    Use `classes` to override  DSFR / DSRC with site specific styles :

    - `ecoq-stepper`
    - `mec-stepper`
    - `sosm-stepper`
    - `sosp-stepper`
    - `uv-stepper`

    **Tag name**:
        dsrc_stepper

    **Usage**:
        `{% dsrc_stepper data_dict %}`
    """
    allowed_keys = [
        "current_step_id",
        "current_step_title",
        "next_step_title",
        "total_steps",
        "classes",
    ]
    tag_data = parse_tag_args(args, kwargs, allowed_keys)

    if "classes" not in tag_data:
        tag_data["classes"] = "dsrc-stepper"

    return {"self": tag_data}

@register.inclusion_tag("dsrc/core/compositions/content/card.html")
def dsfr_card(*args, **kwargs) -> dict:
    """
    Returns a card item. Takes a dict as parameter, with the following structure:

    ```python
    data_dict = {
        "title": "Title of the card item",
        "heading_tag": "(Optional) Heading tag for the title (h2, etc. Default: p)"
        "description": "Text of the card item",
        "image_url": "(Optional) url of the image",
        "image_alt": "(Optional) alt text of the image",
        "media_badges": "(Optional) list of badges for the media area (similar to a badge_group tag)"
        "new_tab": "(Optional) if True, forces steppers to open in a new tab",
        "link": "(Optional) link of the tag",
        "enlarge_link": "(Optional) boolean. If true (default), the link covers the whole card",
        "orientation": "(Optional) if `horizontal`: enables horizontal card layout. Default = None (vertical)",
        "ratio": "(Optional) Use `tier` for 33% ratio layout, `half` for 50% ratio layout",
        "top_detail": "(Optional) dict with a top detail content and optional tags or badges",
        "bottom_detail": "(Optional) a detail string and optional icon",
        "call_to_action": "(Optional) a list of buttons or links at the bottom of the card",
        "id": "(Optional) id of the tile item",
        "icon": "(Optional) icon class name. Ex `fr-card--download` replaces the forward arrow icon with a download one",
        "classes": "(Optional) string with names of extra classes: override with site specific prefix.",
    }
    ```

    All of the keys of the dict can be passed directly as named parameters of the tag.


    Use `classes` to override  DSFR / DSRC with site specific styles :

    - `ecoq-card`
    - `mec-card`
    - `sosm-card`
    - `sosp-card`
    - `uv-card`

    Format of the top_detail dict (every field is optional):
    top_detail = {
        "detail": {
            "text": "the detail text",
            "icon_class": "(Optional) an icon class (eg, fr-icon-warning-fill)"
        },
        "tags": "a list of tag items (mutually exclusive with badges)",
        "badges": "a list of badge items (mutually exclusive with tags)"
    }

    Format of the bottom_detail dict :
    bottom_detail = {
        "text": "the detail text",
        "icon_class": "(Optional) an icon class (eg, fr-icon-warning-fill)"
    },


    **Tag name**:
        dsfr_card

    **Usage**:
        `{% dsfr_card data_dict %}`
    """  # noqa
    allowed_keys = [
        "title",
        "heading_tag",
        "description",
        "image_url",
        "image_alt",
        "media_badges",
        "new_tab",
        "link",
        "enlarge_link",
        "extra_classes",
        "top_detail",
        "bottom_detail",
        "call_to_action",
        "id",
        "icon",
        "classes",
    ]
    tag_data = parse_tag_args(args, kwargs, allowed_keys)

    if "enlarge_link" not in tag_data:
        tag_data["enlarge_link"] = True

    if "call_to_action" in tag_data:
        # Forcing the enlarge_link to false if there is a CTA
        tag_data["enlarge_link"] = False
    if "classes" not in tag_data:
        tag_data["classes"] = "dsrc-card"

    return {"self": tag_data}

@register.filter
def concatenate(value, arg):
    """Concatenate value and arg"""
    return f"{value}{arg}"

@register.filter
def hyphenate(value, arg):
    """Concatenate value and arg with hyphens as separator, if neither is empty"""
    return "-".join(filter(None, [str(value), str(arg)]))
# eof
