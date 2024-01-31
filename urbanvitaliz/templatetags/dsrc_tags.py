# encoding: utf-8

"""
Tags used by the DSRC template library.

This file is largely adapted from the work done on the project `django-dsfr`, in particular : https://github.com/numerique-gouv/django-dsfr/blob/main/dsfr/templatetags/dsfr_tags.py

What changes from `django-dsfr`:

- this library uses `dsrc` prefixes instead of `dsfr`
- the folder structure for templates differs. For mode details on fodler structure please refer to `MULTISITE_DEFAULT_TEMPLATE_DIR/dsrc_dj`

Templatetag parameters are kept as-is from `django-dsfr` definitions in order to retain compatibility with that project.

authors: patricia.boh@beta.gouv.fr
created: 2024-01-31 11:19:06 CEST
"""

from django import template
from django.template.context import Context

from urbanvitaliz import verbs

register = template.Library()


def generate_random_id(start: str = ""):
    """
    Generates a random alphabetic id.
    """
    result = "".join(random.SystemRandom().choices(string.ascii_lowercase, k=16))
    if start:
        result = "-".join([start, result])
    return result


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

@register.inclusion_tag("dsrc_dj/core/compositions/forms/dsrc_form_base.html", takes_context=True)
def dsrc_form(context) -> dict:
    """
    Returns the HTML for a form snippet

    **Tag name**:
        dsrc_form

    **Usage**:
        `{% dsrc_form %}`
    """
    return context

@register.inclusion_tag("dsrc_dj/core/blocks/inputs/dsrc_field.html")
def dsrc_form_field(field) -> dict:
    """
    Returns the HTML for a form field

    **Tag name**:
        dsrc_form_field

    **Usage**:
        `{% dsrc_form_field field %}`
    """
    return {"field": field}


@register.inclusion_tag("dsrc_dj/core/blocks/inputs/dsrc_input.html")
def dsrc_input(*args, **kwargs) -> dict:
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
        "extra_classes": "(Optional) string with names of extra classes"
    }
    ```


    All of the keys of the dict can be passed directly as named parameters of the tag.

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
        "extra_classes",
    ]
    tag_data = parse_tag_args(args, kwargs, allowed_keys)

    if "id" not in tag_data:
        tag_data["id"] = generate_random_id("input")

    return {"self": tag_data}

@register.inclusion_tag("dsrc_dj/core/blocks/buttons/dsrc_button.html")
def dsrc_button(*args, **kwargs) -> dict:
    """
    Returns a button item. Takes a dict as parameter, with the following structure:

    ```python
    data_dict = {
        "label": "Label of the button item",
        "onclick": "button action",
        "type": "(Optional) type of button (submit or button - default: submit),
        "name": "(Optional) name of the button",
        "is_disabled": "(Optional) boolean that indicate if the button is activated
        (default: False)",
        "extra_classes": "(Optional) string with names of extra classes."
    }
    ```

    All of the keys of the dict can be passed directly as named parameters of the tag.

    Relevant `extra_classes`:

    - `fr-btn--secondary` : secondary button
    - `fr-btn--icon-left` and `fr-btn--icon-right`: add an icon to the button
      (associated with an icon class)
    - `fr-btn--sm` and `fr-btn--lg`: button smaller or larger than the default size

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
        "extra_classes",
    ]
    tag_data = parse_tag_args(args, kwargs, allowed_keys)

    if "is_disabled" not in tag_data:
        tag_data["is_disabled"] = False
    return {"self": tag_data}

@register.inclusion_tag("dsrc_dj/core/blocks/inputs/dsrc_select.html")
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
        "extra_classes": "(Optional) string with names of extra classes"
    }
    ```

    All of the keys of the dict can be passed directly as named parameters of the tag.

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
        "extra_classes",
    ]
    tag_data = parse_tag_args(args, kwargs, allowed_keys)

    if "id" not in tag_data:
        tag_data["id"] = generate_random_id("select")

    return {"self": tag_data}

@register.inclusion_tag("dsrc_dj/core/compositions/navs/dsrc_breadcrumb.html", takes_context=True)
def dsrc_breadcrumb(context: Context, tag_data: dict = {}) -> dict:
    """
    Returns a breadcrumb item. Takes a dict as parameter, with the following structure:

    ```python
    data_dict = {
        "links": [{"url": "first-url", "title": "First title"}, {...}],
        "current": "Current page title",
        "root_dir": "the root directory, if the site is not installed at the root of the domain"
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
    return {"self": tag_data}

@register.inclusion_tag("dsrc_dj/core/blocks/global/dsrc_link.html")
def dsrc_link(*args, **kwargs) -> dict:
    """
    Returns a link item. Takes a dict as parameter, with the following structure:

    ```python
    data_dict = {
        "url": "URL of the link item",
        "label": "Label of the link item",
        "is_external": "(Optional) Indicate if the link is external",
        "extra_classes": "(Optional) string with names of extra classes"
    }
    ```

    Relevant extra_classes:

    - `fr-link--icon-left` or `fr-link--icon-right` with an icon class
    - `fr-link--sm` for small links
    - `fr-link--lg` for large links


    All of the keys of the dict can be passed directly as named parameters of the tag.

    **Tag name**:
        dsrc_link

    **Usage**:
        `{% dsrc_link data_dict %}`
    """

    allowed_keys = [
        "url",
        "label",
        "is_external",
        "extra_classes",
    ]
    tag_data = parse_tag_args(args, kwargs, allowed_keys)

    return {"self": tag_data}

@register.inclusion_tag("dsrc_dj/core/blocks/global/dsrc_skiplinks.html", takes_context=True)
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

@register.inclusion_tag("dsrc_dj/core/compositions/navs/dsrc_stepper.html")
def dsrc_stepper(*args, **kwargs) -> dict:
    """
    Returns a stepper item. Takes a dict as parameter, with the following structure:

    ```python
    data_dict = {
        "current_step_id": "Number of current step",
        "current_step_title": "Title of current step",
        "next_step_title": "(Optional) Title of next step",
        "total_steps": "Total number of steps",
    }
    ```

    All of the keys of the dict can be passed directly as named parameters of the tag.

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
    ]
    tag_data = parse_tag_args(args, kwargs, allowed_keys)

    return {"self": tag_data}


@register.inclusion_tag("dsrc_dj/core/compositions/content/dsrc_card.html")
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
        "new_tab": "(Optional) if True, forces links to open in a new tab",
        "link": "(Optional) link of the tag",
        "enlarge_link": "(Optional) boolean. If true (default), the link covers the whole card",
        "extra_classes": "(Optional) string with names of extra classes",
        "top_detail": "(Optional) dict with a top detail content and optional tags or badges",
        "bottom_detail": "(Optional) a detail string and optional icon",
        "call_to_action": "(Optional) a list of buttons or links at the bottom of the card,
        "id": "(Optional) id of the tile item",
    }
    ```

    All of the keys of the dict can be passed directly as named parameters of the tag.

    Relevant extra classes:

    - `fr-card--horizontal`: makes the card horizontal
    - `fr-card--horizontal-tier`: allows a 33% ratio instead of the 40% default
    - `fr-card--horizontal-half`: allows a 50% ratio instead of the 40% default
    - `fr-card--download`: Replaces the forward arrow icon with a download one

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
    ]
    tag_data = parse_tag_args(args, kwargs, allowed_keys)

    if "enlarge_link" not in tag_data:
        tag_data["enlarge_link"] = True

    if "call_to_action" in tag_data:
        # Forcing the enlarge_link to false if there is a CTA
        tag_data["enlarge_link"] = False

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
