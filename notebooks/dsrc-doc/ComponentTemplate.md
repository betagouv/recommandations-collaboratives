```python
# Initialize Notebook

from notebooks.django_for_jupyter import init_django
init_django("urbanvitaliz")
```


```python
from urbanvitaliz.apps.projects.models import Project
from django.db.models import Model
```


```python
from django.template import Context, Template
from IPython.display import display, HTML
```


```python
projects = Project.objects.all()
```


```python
# Load CSS files as raw text using python
"""
Read a CSS or JS file and load it into Jupyter.
Make sure you trust the code you are loading.

Arg: the file path to the file, relative to the project's static assets folder
Returns: IPython.core.display.HTML object: contains JS/CSS in `data` property
"""
def _load_asset(rel_file_path):
    assets_folder = 'static/assets/'
    assets_file_path = f"{assets_folder}{rel_file_path}"
    asset_content = open(assets_file_path, "r").read()
    asset = '%s' % asset_content     
    return HTML(asset)

csscore = _load_asset('css/dsrc-csscore.css')
csstokens = _load_asset('css/dsrc-csstokens.css')
button_component = _load_asset('components/DsrcButton.js')
# print(button_component)
# print(csscore.data)
```


```python
template = Template("""

{% load static %}
{% load sass_tags %}
{% load django_vite %}
{% block css %}
    <style>
        {{csscore}}
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
</table>
<ul class="fr-btns-group fr-btns-group--inline-sm unstyled">
    <li>
        <button class="fr-btn">Bouton</button>
    </li>
    <li>
        <button class="fr-btn fr-btn--secondary">Bouton Secondaire</button>
    </li>
    <li>
        <button class="fr-btn fr-btn--tertiary">Bouton Tertiaire</button>
    </li>
</ul>
""")

context = Context(
    {'projects': projects.order_by("-created_on")[:5], 'csscore': csscore.data }
)

HTML(template.render(context))
```










    <style>

:root{
  --text-decoration: underline;
  --idle: transparent;
  --active: inherit;
  --underline-max-width: 100%;
  --grey-1000-50: #fff;
  --grey-1000-50-hover: #f6f6f6;
  --grey-1000-50-active: #ededed;
  --grey-975-75: #f6f6f6;
  --grey-975-75-hover: #dfdfdf;
  --grey-975-75-active: #cfcfcf;
  --blue-france-975-75: #f5f5fe;
  --blue-france-975-75-hover: #dcdcfc;
  --blue-france-975-75-active: #cbcbfa;
  --red-marianne-975-75: #fef4f4;
  --red-marianne-975-75-hover: #fcd7d7;
  --red-marianne-975-75-active: #fac4c4;
  --green-tilleul-verveine-975-75: #fef7da;
  --green-tilleul-verveine-975-75-hover: #fce552;
  --green-tilleul-verveine-975-75-active: #ebd54c;
  --green-bourgeon-975-75: #e6feda;
  --green-bourgeon-975-75-hover: #a7fc62;
  --green-bourgeon-975-75-active: #98ed4d;
  --green-emeraude-975-75: #e3fdeb;
  --green-emeraude-975-75-hover: #94f9b9;
  --green-emeraude-975-75-active: #6df1a3;
  --green-menthe-975-75: #dffdf7;
  --green-menthe-975-75-hover: #84f9e7;
  --green-menthe-975-75-active: #70ebd8;
  --green-archipel-975-75: #e5fbfd;
  --green-archipel-975-75-hover: #99f2f8;
  --green-archipel-975-75-active: #73e9f0;
  --blue-ecume-975-75: #f4f6fe;
  --blue-ecume-975-75-hover: #d7dffb;
  --blue-ecume-975-75-active: #c3cffa;
  --blue-cumulus-975-75: #f3f6fe;
  --blue-cumulus-975-75-hover: #d3dffc;
  --blue-cumulus-975-75-active: #bed0fa;
  --purple-glycine-975-75: #fef3fd;
  --purple-glycine-975-75-hover: #fcd4f8;
  --purple-glycine-975-75-active: #fabff5;
  --pink-macaron-975-75: #fef4f2;
  --pink-macaron-975-75-hover: #fcd8d0;
  --pink-macaron-975-75-active: #fac5b8;
  --pink-tuile-975-75: #fef4f3;
  --pink-tuile-975-75-hover: #fcd7d3;
  --pink-tuile-975-75-active: #fac4be;
  --yellow-tournesol-975-75: #fef6e3;
  --yellow-tournesol-975-75-hover: #fce086;
  --yellow-tournesol-975-75-active: #f5d24b;
  --yellow-moutarde-975-75: #fef5e8;
  --yellow-moutarde-975-75-hover: #fcdca3;
  --yellow-moutarde-975-75-active: #fbcd64;
  --orange-terre-battue-975-75: #fef4f2;
  --orange-terre-battue-975-75-hover: #fcd8d0;
  --orange-terre-battue-975-75-active: #fac5b8;
  --brown-cafe-creme-975-75: #fbf6ed;
  --brown-cafe-creme-975-75-hover: #f2deb6;
  --brown-cafe-creme-975-75-active: #eacf91;
  --brown-caramel-975-75: #fbf5f2;
  --brown-caramel-975-75-hover: #f1dbcf;
  --brown-caramel-975-75-active: #ecc9b5;
  --brown-opera-975-75: #fbf5f2;
  --brown-opera-975-75-hover: #f1dbcf;
  --brown-opera-975-75-active: #ecc9b5;
  --beige-gris-galet-975-75: #f9f6f2;
  --beige-gris-galet-975-75-hover: #eadecd;
  --beige-gris-galet-975-75-active: #e1ceb1;
  --grey-950-100: #eee;
  --grey-950-100-hover: #d2d2d2;
  --grey-950-100-active: #c1c1c1;
  --blue-france-950-100: #ececfe;
  --blue-france-950-100-hover: #cecefc;
  --blue-france-950-100-active: #bbbbfc;
  --red-marianne-950-100: #fee9e9;
  --red-marianne-950-100-hover: #fdc5c5;
  --red-marianne-950-100-active: #fcafaf;
  --green-tilleul-verveine-950-100: #fceeac;
  --green-tilleul-verveine-950-100-hover: #e8d45c;
  --green-tilleul-verveine-950-100-active: #d4c254;
  --green-bourgeon-950-100: #c9fcac;
  --green-bourgeon-950-100-hover: #9ae95d;
  --green-bourgeon-950-100-active: #8dd555;
  --green-emeraude-950-100: #c3fad5;
  --green-emeraude-950-100-hover: #77eda5;
  --green-emeraude-950-100-active: #6dd897;
  --green-menthe-950-100: #bafaee;
  --green-menthe-950-100-hover: #79e7d5;
  --green-menthe-950-100-active: #6fd3c3;
  --green-archipel-950-100: #c7f6fc;
  --green-archipel-950-100-hover: #64ecf8;
  --green-archipel-950-100-active: #5bd8e3;
  --blue-ecume-950-100: #e9edfe;
  --blue-ecume-950-100-hover: #c5d0fc;
  --blue-ecume-950-100-active: #adbffc;
  --blue-cumulus-950-100: #e6eefe;
  --blue-cumulus-950-100-hover: #bcd3fc;
  --blue-cumulus-950-100-active: #9fc3fc;
  --purple-glycine-950-100: #fee7fc;
  --purple-glycine-950-100-hover: #fdc0f8;
  --purple-glycine-950-100-active: #fca8f6;
  --pink-macaron-950-100: #fee9e6;
  --pink-macaron-950-100-hover: #fdc6bd;
  --pink-macaron-950-100-active: #fcb0a2;
  --pink-tuile-950-100: #fee9e7;
  --pink-tuile-950-100-hover: #fdc6c0;
  --pink-tuile-950-100-active: #fcb0a7;
  --yellow-tournesol-950-100: #feecc2;
  --yellow-tournesol-950-100-hover: #fbd335;
  --yellow-tournesol-950-100-active: #e6c130;
  --yellow-moutarde-950-100: #feebd0;
  --yellow-moutarde-950-100-hover: #fdcd6d;
  --yellow-moutarde-950-100-active: #f4be30;
  --orange-terre-battue-950-100: #fee9e5;
  --orange-terre-battue-950-100-hover: #fdc6ba;
  --orange-terre-battue-950-100-active: #fcb09e;
  --brown-cafe-creme-950-100: #f7ecdb;
  --brown-cafe-creme-950-100-hover: #edce94;
  --brown-cafe-creme-950-100-active: #dabd84;
  --brown-caramel-950-100: #f7ebe5;
  --brown-caramel-950-100-hover: #eccbb9;
  --brown-caramel-950-100-active: #e6b79a;
  --brown-opera-950-100: #f7ece4;
  --brown-opera-950-100-hover: #eccdb3;
  --brown-opera-950-100-active: #e6ba90;
  --beige-gris-galet-950-100: #f3ede5;
  --beige-gris-galet-950-100-hover: #e1d0b5;
  --beige-gris-galet-950-100-active: #d1bea2;
  --info-950-100: #e8edff;
  --info-950-100-hover: #c2d1ff;
  --info-950-100-active: #a9bfff;
  --success-950-100: #b8fec9;
  --success-950-100-hover: #46fd89;
  --success-950-100-active: #34eb7b;
  --warning-950-100: #ffe9e6;
  --warning-950-100-hover: #ffc6bd;
  --warning-950-100-active: #ffb0a2;
  --error-950-100: #ffe9e9;
  --error-950-100-hover: #ffc5c5;
  --error-950-100-active: #ffafaf;
  --grey-200-850: #3a3a3a;
  --blue-france-sun-113-625: #000091;
  --red-marianne-425-625: #c9191e;
  --green-tilleul-verveine-sun-418-moon-817: #66673d;
  --green-bourgeon-sun-425-moon-759: #447049;
  --green-emeraude-sun-425-moon-753: #297254;
  --green-menthe-sun-373-moon-652: #37635f;
  --green-archipel-sun-391-moon-716: #006a6f;
  --blue-ecume-sun-247-moon-675: #2f4077;
  --blue-cumulus-sun-368-moon-732: #3558a2;
  --purple-glycine-sun-319-moon-630: #6e445a;
  --pink-macaron-sun-406-moon-833: #8d533e;
  --pink-tuile-sun-425-moon-750: #a94645;
  --yellow-tournesol-sun-407-moon-922: #716043;
  --yellow-moutarde-sun-348-moon-860: #695240;
  --orange-terre-battue-sun-370-moon-672: #755348;
  --brown-cafe-creme-sun-383-moon-885: #685c48;
  --brown-caramel-sun-425-moon-901: #845d48;
  --brown-opera-sun-395-moon-820: #745b47;
  --beige-gris-galet-sun-407-moon-821: #6a6156;
  --info-425-625: #0063cb;
  --success-425-625: #18753c;
  --warning-425-625: #b34000;
  --error-425-625: #ce0500;
  --blue-france-sun-113-625-hover: #1212ff;
  --blue-france-sun-113-625-active: #2323ff;
  --red-marianne-425-625-hover: #f93f42;
  --red-marianne-425-625-active: #f95a5c;
  --green-tilleul-verveine-sun-418-moon-817-hover: #929359;
  --green-tilleul-verveine-sun-418-moon-817-active: #a7a967;
  --green-bourgeon-sun-425-moon-759-hover: #639f6a;
  --green-bourgeon-sun-425-moon-759-active: #72b77a;
  --green-emeraude-sun-425-moon-753-hover: #3ea47a;
  --green-emeraude-sun-425-moon-753-active: #49bc8d;
  --green-menthe-sun-373-moon-652-hover: #53918c;
  --green-menthe-sun-373-moon-652-active: #62a9a2;
  --green-archipel-sun-391-moon-716-hover: #009fa7;
  --green-archipel-sun-391-moon-716-active: #00bbc3;
  --blue-ecume-sun-247-moon-675-hover: #4e68bb;
  --blue-ecume-sun-247-moon-675-active: #667dcf;
  --blue-cumulus-sun-368-moon-732-hover: #5982e0;
  --blue-cumulus-sun-368-moon-732-active: #7996e6;
  --purple-glycine-sun-319-moon-630-hover: #a66989;
  --purple-glycine-sun-319-moon-630-active: #bb7f9e;
  --pink-macaron-sun-406-moon-833-hover: #ca795c;
  --pink-macaron-sun-406-moon-833-active: #e08e73;
  --pink-tuile-sun-425-moon-750-hover: #d5706f;
  --pink-tuile-sun-425-moon-750-active: #da8a89;
  --yellow-tournesol-sun-407-moon-922-hover: #a28a62;
  --yellow-tournesol-sun-407-moon-922-active: #ba9f72;
  --yellow-moutarde-sun-348-moon-860-hover: #9b7b61;
  --yellow-moutarde-sun-348-moon-860-active: #b58f72;
  --orange-terre-battue-sun-370-moon-672-hover: #ab7b6b;
  --orange-terre-battue-sun-370-moon-672-active: #c68f7d;
  --brown-cafe-creme-sun-383-moon-885-hover: #97866a;
  --brown-cafe-creme-sun-383-moon-885-active: #ae9b7b;
  --brown-caramel-sun-425-moon-901-hover: #bb8568;
  --brown-caramel-sun-425-moon-901-active: #d69978;
  --brown-opera-sun-395-moon-820-hover: #a78468;
  --brown-opera-sun-395-moon-820-active: #c09979;
  --beige-gris-galet-sun-407-moon-821-hover: #988b7c;
  --beige-gris-galet-sun-407-moon-821-active: #afa08f;
  --info-425-625-hover: #3b87ff;
  --info-425-625-active: #6798ff;
  --success-425-625-hover: #27a959;
  --success-425-625-active: #2fc368;
  --warning-425-625-hover: #ff6218;
  --warning-425-625-active: #ff7a55;
  --error-425-625-hover: #ff2725;
  --error-425-625-active: #ff4140;
  --blue-france-925-125: #e3e3fd;
  --blue-france-925-125-hover: #c1c1fb;
  --blue-france-925-125-active: #adadf9;
  --red-marianne-925-125: #fddede;
  --red-marianne-925-125-hover: #fbb6b6;
  --red-marianne-925-125-active: #fa9e9e;
  --green-tilleul-verveine-925-125: #fbe769;
  --green-tilleul-verveine-925-125-hover: #d7c655;
  --green-tilleul-verveine-925-125-active: #c2b24c;
  --green-bourgeon-925-125: #a9fb68;
  --green-bourgeon-925-125-hover: #8ed654;
  --green-bourgeon-925-125-active: #7fc04b;
  --green-emeraude-925-125: #9ef9be;
  --green-emeraude-925-125-hover: #69df97;
  --green-emeraude-925-125-active: #5ec988;
  --green-menthe-925-125: #8bf8e7;
  --green-menthe-925-125-hover: #6ed5c5;
  --green-menthe-925-125-active: #62bfb1;
  --green-archipel-925-125: #a6f2fa;
  --green-archipel-925-125-hover: #62dbe5;
  --green-archipel-925-125-active: #58c5cf;
  --blue-ecume-925-125: #dee5fd;
  --blue-ecume-925-125-hover: #b4c5fb;
  --blue-ecume-925-125-active: #99b3f9;
  --blue-cumulus-925-125: #dae6fd;
  --blue-cumulus-925-125-hover: #a9c8fb;
  --blue-cumulus-925-125-active: #8ab8f9;
  --purple-glycine-925-125: #fddbfa;
  --purple-glycine-925-125-hover: #fbaff5;
  --purple-glycine-925-125-active: #fa96f2;
  --pink-macaron-925-125: #fddfda;
  --pink-macaron-925-125-hover: #fbb8ab;
  --pink-macaron-925-125-active: #faa18d;
  --pink-tuile-925-125: #fddfdb;
  --pink-tuile-925-125-hover: #fbb8ad;
  --pink-tuile-925-125-active: #faa191;
  --yellow-tournesol-925-125: #fde39c;
  --yellow-tournesol-925-125-hover: #e9c53b;
  --yellow-tournesol-925-125-active: #d3b235;
  --yellow-moutarde-925-125: #fde2b5;
  --yellow-moutarde-925-125-hover: #f6c43c;
  --yellow-moutarde-925-125-active: #dfb135;
  --orange-terre-battue-925-125: #fddfd8;
  --orange-terre-battue-925-125-hover: #fbb8a5;
  --orange-terre-battue-925-125-active: #faa184;
  --brown-cafe-creme-925-125: #f4e3c7;
  --brown-cafe-creme-925-125-hover: #e1c386;
  --brown-cafe-creme-925-125-active: #ccb078;
  --brown-caramel-925-125: #f3e2d9;
  --brown-caramel-925-125-hover: #e7bea6;
  --brown-caramel-925-125-active: #e1a982;
  --brown-opera-925-125: #f3e2d7;
  --brown-opera-925-125-hover: #e7bfa0;
  --brown-opera-925-125-active: #deaa7e;
  --beige-gris-galet-925-125: #eee4d9;
  --beige-gris-galet-925-125-hover: #dbc3a4;
  --beige-gris-galet-925-125-active: #c6b094;
  --grey-925-125: #e5e5e5;
  --grey-1000-75: #fff;
  --grey-1000-75-hover: #f6f6f6;
  --grey-1000-75-active: #ededed;
  --grey-1000-100: #fff;
  --grey-1000-100-hover: #f6f6f6;
  --grey-1000-100-active: #ededed;
  --grey-975-100: #f6f6f6;
  --grey-975-100-hover: #dfdfdf;
  --grey-975-100-active: #cfcfcf;
  --grey-975-125: #f6f6f6;
  --grey-975-125-hover: #dfdfdf;
  --grey-975-125-active: #cfcfcf;
  --grey-950-125: #eee;
  --grey-950-125-hover: #d2d2d2;
  --grey-950-125-active: #c1c1c1;
  --grey-950-150: #eee;
  --grey-950-150-hover: #d2d2d2;
  --grey-950-150-active: #c1c1c1;
  --grey-50-1000: #161616;
  --grey-425-625: #666;
  --blue-france-975-sun-113: #f5f5fe;
  --info-975-75: #f4f6ff;
  --success-975-75: #dffee6;
  --warning-975-75: #fff4f3;
  --error-975-75: #fff4f4;
  --grey-625-425: #929292;
  --grey-0-1000: #000;
  --grey-900-175: #ddd;
  --blue-france-main-525: #6a6af4;
  --red-marianne-main-472: #e1000f;
  --green-tilleul-verveine-main-707: #b7a73f;
  --green-bourgeon-main-640: #68a532;
  --green-emeraude-main-632: #00a95f;
  --green-menthe-main-548: #009081;
  --green-archipel-main-557: #009099;
  --blue-ecume-main-400: #465f9d;
  --blue-cumulus-main-526: #417dc4;
  --purple-glycine-main-494: #a558a0;
  --pink-macaron-main-689: #e18b76;
  --pink-tuile-main-556: #ce614a;
  --yellow-tournesol-main-731: #c8aa39;
  --yellow-moutarde-main-679: #c3992a;
  --orange-terre-battue-main-645: #e4794a;
  --brown-cafe-creme-main-782: #d1b781;
  --brown-caramel-main-648: #c08c65;
  --brown-opera-main-680: #bd987a;
  --beige-gris-galet-main-702: #aea397;
  --blue-france-850-200: #cacafb;
  --red-marianne-850-200: #fcbfbf;
  --green-tilleul-verveine-850-200: #e2cf58;
  --green-bourgeon-850-200: #95e257;
  --green-emeraude-850-200: #6fe49d;
  --green-menthe-850-200: #73e0cf;
  --green-archipel-850-200: #60e0eb;
  --blue-ecume-850-200: #bfccfb;
  --blue-cumulus-850-200: #b6cffb;
  --purple-glycine-850-200: #fbb8f6;
  --pink-macaron-850-200: #fcc0b4;
  --pink-tuile-850-200: #fcbfb7;
  --yellow-tournesol-850-200: #efcb3a;
  --yellow-moutarde-850-200: #fcc63a;
  --orange-terre-battue-850-200: #fcc0b0;
  --brown-cafe-creme-850-200: #e7ca8e;
  --brown-caramel-850-200: #eac7b2;
  --brown-opera-850-200: #eac7ad;
  --beige-gris-galet-850-200: #e0cab0;
  --shadow-color: rgba(0, 0, 18, 0.32);
  --underline-img: none;
  --underline-x: calc(var(--underline-max-width) * 0);
  --underline-thickness: calc(0.0625em + 0.25px);
  --underline-hover-width: var(--underline-max-width);
  --underline-idle-width: var(--underline-max-width);
  --icon-size: 1rem;
  --external-link-content: none;
  --hover: inherit;
  --text-disabled-grey: var(--grey-625-425);
  --title-spacing: 0;
  --text-spacing: 0;
  --xl-block: 0;
  --xl-base: 1em;
  --ul-type: none;
  --ul-start: 0;
  --xl-size: var(--xl-base);
  --ol-type: none;
  --ol-start: 0;
  --ol-content: none;
  --li-bottom: 0;
  --display-spacing: 0 0 2rem;
  --background-default-grey: var(--grey-1000-50);
  --background-default-grey-hover: var(--grey-1000-50-hover);
  --background-default-grey-active: var(--grey-1000-50-active);
  --text-default-grey: var(--grey-200-850);
  --scrollbar-width: 0;
  --border-default-grey: var(--grey-900-175);
  --collapse-max-height: 0;
  --collapser: &quot;&quot;;
  --collapse: -99999px;
  --artwork-decorative-blue-france: var(--blue-france-950-100);
  --artwork-minor-red-marianne: var(--red-marianne-main-472);
  --artwork-major-blue-france: var(--blue-france-sun-113-625);
  --artwork-background-grey: var(--grey-975-75);
  --artwork-motif-grey: var(--grey-925-125);
  --artwork-minor-green-tilleul-verveine: var(--green-tilleul-verveine-main-707);
  --artwork-minor-green-bourgeon: var(--green-bourgeon-main-640);
  --artwork-minor-green-emeraude: var(--green-emeraude-main-632);
  --artwork-minor-green-menthe: var(--green-menthe-main-548);
  --artwork-minor-green-archipel: var(--green-archipel-main-557);
  --artwork-minor-blue-ecume: var(--blue-ecume-main-400);
  --artwork-minor-blue-cumulus: var(--blue-cumulus-main-526);
  --artwork-minor-purple-glycine: var(--purple-glycine-main-494);
  --artwork-minor-pink-macaron: var(--pink-macaron-main-689);
  --artwork-minor-pink-tuile: var(--pink-tuile-main-556);
  --artwork-minor-yellow-tournesol: var(--yellow-tournesol-main-731);
  --artwork-minor-yellow-moutarde: var(--yellow-moutarde-main-679);
  --artwork-minor-orange-terre-battue: var(--orange-terre-battue-main-645);
  --artwork-minor-brown-cafe-creme: var(--brown-cafe-creme-main-782);
  --artwork-minor-brown-caramel: var(--brown-caramel-main-648);
  --artwork-minor-brown-opera: var(--brown-opera-main-680);
  --artwork-minor-beige-gris-galet: var(--beige-gris-galet-main-702);
  --text-title-grey: var(--grey-50-1000);
  --hover-tint: var(--hover);
  --active-tint: var(--active);
  --background-action-high-blue-france: var(--blue-france-sun-113-625);
  --background-action-high-blue-france-hover: var(--blue-france-sun-113-625-hover);
  --background-action-high-blue-france-active: var(--blue-france-sun-113-625-active);
  --text-inverted-blue-france: var(--blue-france-975-sun-113);
  --equisized-width: auto;
  --background-disabled-grey: var(--grey-925-125);
  --text-action-high-blue-france: var(--blue-france-sun-113-625);
  --border-action-high-blue-france: var(--blue-france-sun-113-625);
  --border-disabled-grey: var(--grey-925-125);
  --table-offset: 1rem;
  --border-plain-grey: var(--grey-200-850);
  --background-contrast-grey: var(--grey-950-100);
  --background-contrast-grey-hover: var(--grey-950-100-hover);
  --background-contrast-grey-active: var(--grey-950-100-active);
  --background-alt-grey: var(--grey-975-75);
  --background-alt-grey-hover: var(--grey-975-75-hover);
  --background-alt-grey-active: var(--grey-975-75-active);
  --border-plain-green-tilleul-verveine: var(--green-tilleul-verveine-sun-418-moon-817);
  --background-contrast-green-tilleul-verveine: var(--green-tilleul-verveine-950-100);
  --background-contrast-green-tilleul-verveine-hover: var(--green-tilleul-verveine-950-100-hover);
  --background-contrast-green-tilleul-verveine-active: var(--green-tilleul-verveine-950-100-active);
  --background-alt-green-tilleul-verveine: var(--green-tilleul-verveine-975-75);
  --background-alt-green-tilleul-verveine-hover: var(--green-tilleul-verveine-975-75-hover);
  --background-alt-green-tilleul-verveine-active: var(--green-tilleul-verveine-975-75-active);
  --border-default-green-tilleul-verveine: var(--green-tilleul-verveine-main-707);
  --border-plain-green-bourgeon: var(--green-bourgeon-sun-425-moon-759);
  --background-contrast-green-bourgeon: var(--green-bourgeon-950-100);
  --background-contrast-green-bourgeon-hover: var(--green-bourgeon-950-100-hover);
  --background-contrast-green-bourgeon-active: var(--green-bourgeon-950-100-active);
  --background-alt-green-bourgeon: var(--green-bourgeon-975-75);
  --background-alt-green-bourgeon-hover: var(--green-bourgeon-975-75-hover);
  --background-alt-green-bourgeon-active: var(--green-bourgeon-975-75-active);
  --border-default-green-bourgeon: var(--green-bourgeon-main-640);
  --border-plain-green-emeraude: var(--green-emeraude-sun-425-moon-753);
  --background-contrast-green-emeraude: var(--green-emeraude-950-100);
  --background-contrast-green-emeraude-hover: var(--green-emeraude-950-100-hover);
  --background-contrast-green-emeraude-active: var(--green-emeraude-950-100-active);
  --background-alt-green-emeraude: var(--green-emeraude-975-75);
  --background-alt-green-emeraude-hover: var(--green-emeraude-975-75-hover);
  --background-alt-green-emeraude-active: var(--green-emeraude-975-75-active);
  --border-default-green-emeraude: var(--green-emeraude-main-632);
  --border-plain-green-menthe: var(--green-menthe-sun-373-moon-652);
  --background-contrast-green-menthe: var(--green-menthe-950-100);
  --background-contrast-green-menthe-hover: var(--green-menthe-950-100-hover);
  --background-contrast-green-menthe-active: var(--green-menthe-950-100-active);
  --background-alt-green-menthe: var(--green-menthe-975-75);
  --background-alt-green-menthe-hover: var(--green-menthe-975-75-hover);
  --background-alt-green-menthe-active: var(--green-menthe-975-75-active);
  --border-default-green-menthe: var(--green-menthe-main-548);
  --border-plain-green-archipel: var(--green-archipel-sun-391-moon-716);
  --background-contrast-green-archipel: var(--green-archipel-950-100);
  --background-contrast-green-archipel-hover: var(--green-archipel-950-100-hover);
  --background-contrast-green-archipel-active: var(--green-archipel-950-100-active);
  --background-alt-green-archipel: var(--green-archipel-975-75);
  --background-alt-green-archipel-hover: var(--green-archipel-975-75-hover);
  --background-alt-green-archipel-active: var(--green-archipel-975-75-active);
  --border-default-green-archipel: var(--green-archipel-main-557);
  --border-plain-blue-ecume: var(--blue-ecume-sun-247-moon-675);
  --background-contrast-blue-ecume: var(--blue-ecume-950-100);
  --background-contrast-blue-ecume-hover: var(--blue-ecume-950-100-hover);
  --background-contrast-blue-ecume-active: var(--blue-ecume-950-100-active);
  --background-alt-blue-ecume: var(--blue-ecume-975-75);
  --background-alt-blue-ecume-hover: var(--blue-ecume-975-75-hover);
  --background-alt-blue-ecume-active: var(--blue-ecume-975-75-active);
  --border-default-blue-ecume: var(--blue-ecume-main-400);
  --border-plain-blue-cumulus: var(--blue-cumulus-sun-368-moon-732);
  --background-contrast-blue-cumulus: var(--blue-cumulus-950-100);
  --background-contrast-blue-cumulus-hover: var(--blue-cumulus-950-100-hover);
  --background-contrast-blue-cumulus-active: var(--blue-cumulus-950-100-active);
  --background-alt-blue-cumulus: var(--blue-cumulus-975-75);
  --background-alt-blue-cumulus-hover: var(--blue-cumulus-975-75-hover);
  --background-alt-blue-cumulus-active: var(--blue-cumulus-975-75-active);
  --border-default-blue-cumulus: var(--blue-cumulus-main-526);
  --border-plain-purple-glycine: var(--purple-glycine-sun-319-moon-630);
  --background-contrast-purple-glycine: var(--purple-glycine-950-100);
  --background-contrast-purple-glycine-hover: var(--purple-glycine-950-100-hover);
  --background-contrast-purple-glycine-active: var(--purple-glycine-950-100-active);
  --background-alt-purple-glycine: var(--purple-glycine-975-75);
  --background-alt-purple-glycine-hover: var(--purple-glycine-975-75-hover);
  --background-alt-purple-glycine-active: var(--purple-glycine-975-75-active);
  --border-default-purple-glycine: var(--purple-glycine-main-494);
  --border-plain-pink-macaron: var(--pink-macaron-sun-406-moon-833);
  --background-contrast-pink-macaron: var(--pink-macaron-950-100);
  --background-contrast-pink-macaron-hover: var(--pink-macaron-950-100-hover);
  --background-contrast-pink-macaron-active: var(--pink-macaron-950-100-active);
  --background-alt-pink-macaron: var(--pink-macaron-975-75);
  --background-alt-pink-macaron-hover: var(--pink-macaron-975-75-hover);
  --background-alt-pink-macaron-active: var(--pink-macaron-975-75-active);
  --border-default-pink-macaron: var(--pink-macaron-main-689);
  --border-plain-pink-tuile: var(--pink-tuile-sun-425-moon-750);
  --background-contrast-pink-tuile: var(--pink-tuile-950-100);
  --background-contrast-pink-tuile-hover: var(--pink-tuile-950-100-hover);
  --background-contrast-pink-tuile-active: var(--pink-tuile-950-100-active);
  --background-alt-pink-tuile: var(--pink-tuile-975-75);
  --background-alt-pink-tuile-hover: var(--pink-tuile-975-75-hover);
  --background-alt-pink-tuile-active: var(--pink-tuile-975-75-active);
  --border-default-pink-tuile: var(--pink-tuile-main-556);
  --border-plain-yellow-tournesol: var(--yellow-tournesol-sun-407-moon-922);
  --background-contrast-yellow-tournesol: var(--yellow-tournesol-950-100);
  --background-contrast-yellow-tournesol-hover: var(--yellow-tournesol-950-100-hover);
  --background-contrast-yellow-tournesol-active: var(--yellow-tournesol-950-100-active);
  --background-alt-yellow-tournesol: var(--yellow-tournesol-975-75);
  --background-alt-yellow-tournesol-hover: var(--yellow-tournesol-975-75-hover);
  --background-alt-yellow-tournesol-active: var(--yellow-tournesol-975-75-active);
  --border-default-yellow-tournesol: var(--yellow-tournesol-main-731);
  --border-plain-yellow-moutarde: var(--yellow-moutarde-sun-348-moon-860);
  --background-contrast-yellow-moutarde: var(--yellow-moutarde-950-100);
  --background-contrast-yellow-moutarde-hover: var(--yellow-moutarde-950-100-hover);
  --background-contrast-yellow-moutarde-active: var(--yellow-moutarde-950-100-active);
  --background-alt-yellow-moutarde: var(--yellow-moutarde-975-75);
  --background-alt-yellow-moutarde-hover: var(--yellow-moutarde-975-75-hover);
  --background-alt-yellow-moutarde-active: var(--yellow-moutarde-975-75-active);
  --border-default-yellow-moutarde: var(--yellow-moutarde-main-679);
  --border-plain-orange-terre-battue: var(--orange-terre-battue-sun-370-moon-672);
  --background-contrast-orange-terre-battue: var(--orange-terre-battue-950-100);
  --background-contrast-orange-terre-battue-hover: var(--orange-terre-battue-950-100-hover);
  --background-contrast-orange-terre-battue-active: var(--orange-terre-battue-950-100-active);
  --background-alt-orange-terre-battue: var(--orange-terre-battue-975-75);
  --background-alt-orange-terre-battue-hover: var(--orange-terre-battue-975-75-hover);
  --background-alt-orange-terre-battue-active: var(--orange-terre-battue-975-75-active);
  --border-default-orange-terre-battue: var(--orange-terre-battue-main-645);
  --border-plain-brown-cafe-creme: var(--brown-cafe-creme-sun-383-moon-885);
  --background-contrast-brown-cafe-creme: var(--brown-cafe-creme-950-100);
  --background-contrast-brown-cafe-creme-hover: var(--brown-cafe-creme-950-100-hover);
  --background-contrast-brown-cafe-creme-active: var(--brown-cafe-creme-950-100-active);
  --background-alt-brown-cafe-creme: var(--brown-cafe-creme-975-75);
  --background-alt-brown-cafe-creme-hover: var(--brown-cafe-creme-975-75-hover);
  --background-alt-brown-cafe-creme-active: var(--brown-cafe-creme-975-75-active);
  --border-default-brown-cafe-creme: var(--brown-cafe-creme-main-782);
  --border-plain-brown-caramel: var(--brown-caramel-sun-425-moon-901);
  --background-contrast-brown-caramel: var(--brown-caramel-950-100);
  --background-contrast-brown-caramel-hover: var(--brown-caramel-950-100-hover);
  --background-contrast-brown-caramel-active: var(--brown-caramel-950-100-active);
  --background-alt-brown-caramel: var(--brown-caramel-975-75);
  --background-alt-brown-caramel-hover: var(--brown-caramel-975-75-hover);
  --background-alt-brown-caramel-active: var(--brown-caramel-975-75-active);
  --border-default-brown-caramel: var(--brown-caramel-main-648);
  --border-plain-brown-opera: var(--brown-opera-sun-395-moon-820);
  --background-contrast-brown-opera: var(--brown-opera-950-100);
  --background-contrast-brown-opera-hover: var(--brown-opera-950-100-hover);
  --background-contrast-brown-opera-active: var(--brown-opera-950-100-active);
  --background-alt-brown-opera: var(--brown-opera-975-75);
  --background-alt-brown-opera-hover: var(--brown-opera-975-75-hover);
  --background-alt-brown-opera-active: var(--brown-opera-975-75-active);
  --border-default-brown-opera: var(--brown-opera-main-680);
  --border-plain-beige-gris-galet: var(--beige-gris-galet-sun-407-moon-821);
  --background-contrast-beige-gris-galet: var(--beige-gris-galet-950-100);
  --background-contrast-beige-gris-galet-hover: var(--beige-gris-galet-950-100-hover);
  --background-contrast-beige-gris-galet-active: var(--beige-gris-galet-950-100-active);
  --background-alt-beige-gris-galet: var(--beige-gris-galet-975-75);
  --background-alt-beige-gris-galet-hover: var(--beige-gris-galet-975-75-hover);
  --background-alt-beige-gris-galet-active: var(--beige-gris-galet-975-75-active);
  --border-default-beige-gris-galet: var(--beige-gris-galet-main-702);
}
@charset &quot;UTF-8&quot;;
/* Global config */
/**
* source : https://github.com/hankchizljaw/modern-css-reset/blob/master/src/reset.css
**/
/* Box sizing rules */
*,
*::before,
*::after {
  box-sizing: border-box;
}

/* Remove default margin */
body,
h1,
h2,
h3,
h4,
p,
figure,
blockquote,
dl,
dd,
menu {
  margin: 0;
}

/* Remove list styles on ul, ol elements with a list role, which suggests default styling will be removed */
menu[role=group],
ul[role=group],
li[role=group] {
  list-style: none;
  padding: 0;
}

/* Set core root defaults */
html:focus-within {
  scroll-behavior: smooth;
}

/* Set core body defaults */
body {
  min-height: 100vh;
  text-rendering: optimizespeed;
  line-height: 1.5;
}

/* A elements that don&#x27;t have a class get default styles */
a:not([class]) {
  -webkit-text-decoration-skip: ink;
          text-decoration-skip-ink: auto;
}

/* Make images easier to work with */
img,
picture {
  max-width: 100%;
  display: block;
}

/* Inherit fonts for inputs and buttons */
input,
button,
textarea,
select {
  font: inherit;
}

ul.unstyled {
  list-style: none;
  padding-left: 0;
}

/* Remove all animations and transitions for people that prefer not to see them */
@media (prefers-reduced-motion: reduce) {
  html:focus-within {
    scroll-behavior: auto;
  }
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
/* DSFR config */
/*!
 * DSFR v1.11.0 | SPDX-License-Identifier: MIT | License-Filename: LICENSE.md | restricted use (see terms and conditions)
 */
/* ¯¯¯¯¯¯¯¯¯ *\
  CORE
\* ˍˍˍˍˍˍˍˍˍ */
a {
  -webkit-text-decoration: var(--text-decoration);
          text-decoration: var(--text-decoration);
  color: inherit;
  --hover-tint: var(--idle);
  --active-tint: var(--active);
}

:root {
  --underline-max-width: 100%;
  --underline-hover-width: 0;
  --underline-idle-width: var(--underline-max-width);
  --underline-x: calc(var(--underline-max-width) * 0);
  --underline-thickness: 0.0625em;
  --underline-img: linear-gradient(0deg, currentColor, currentColor);
  --external-link-content: &quot;&quot;;
  --text-decoration: none;
  --ul-type: disc;
  --ol-type: decimal;
  --ul-start: 1rem;
  --ol-start: 1.5rem;
  --xl-block: 0.5rem;
  --li-bottom: 0.25rem;
  --xl-base: 1em;
  --ol-content: counters(li-counter, &quot;.&quot;) &quot;.  &quot;;
  --text-spacing: 0 0 1.5rem;
  --title-spacing: 0 0 1.5rem;
  --display-spacing: 0 0 2rem;
  --background-default-grey: var(--grey-1000-50);
  --background-default-grey-hover: var(--grey-1000-50-hover);
  --background-default-grey-active: var(--grey-1000-50-active);
  --background-alt-grey: var(--grey-975-75);
  --background-alt-grey-hover: var(--grey-975-75-hover);
  --background-alt-grey-active: var(--grey-975-75-active);
  --background-alt-blue-france: var(--blue-france-975-75);
  --background-alt-blue-france-hover: var(--blue-france-975-75-hover);
  --background-alt-blue-france-active: var(--blue-france-975-75-active);
  --background-alt-red-marianne: var(--red-marianne-975-75);
  --background-alt-red-marianne-hover: var(--red-marianne-975-75-hover);
  --background-alt-red-marianne-active: var(--red-marianne-975-75-active);
  --background-alt-green-tilleul-verveine: var(--green-tilleul-verveine-975-75);
  --background-alt-green-tilleul-verveine-hover: var(--green-tilleul-verveine-975-75-hover);
  --background-alt-green-tilleul-verveine-active: var(--green-tilleul-verveine-975-75-active);
  --background-alt-green-bourgeon: var(--green-bourgeon-975-75);
  --background-alt-green-bourgeon-hover: var(--green-bourgeon-975-75-hover);
  --background-alt-green-bourgeon-active: var(--green-bourgeon-975-75-active);
  --background-alt-green-emeraude: var(--green-emeraude-975-75);
  --background-alt-green-emeraude-hover: var(--green-emeraude-975-75-hover);
  --background-alt-green-emeraude-active: var(--green-emeraude-975-75-active);
  --background-alt-green-menthe: var(--green-menthe-975-75);
  --background-alt-green-menthe-hover: var(--green-menthe-975-75-hover);
  --background-alt-green-menthe-active: var(--green-menthe-975-75-active);
  --background-alt-green-archipel: var(--green-archipel-975-75);
  --background-alt-green-archipel-hover: var(--green-archipel-975-75-hover);
  --background-alt-green-archipel-active: var(--green-archipel-975-75-active);
  --background-alt-blue-ecume: var(--blue-ecume-975-75);
  --background-alt-blue-ecume-hover: var(--blue-ecume-975-75-hover);
  --background-alt-blue-ecume-active: var(--blue-ecume-975-75-active);
  --background-alt-blue-cumulus: var(--blue-cumulus-975-75);
  --background-alt-blue-cumulus-hover: var(--blue-cumulus-975-75-hover);
  --background-alt-blue-cumulus-active: var(--blue-cumulus-975-75-active);
  --background-alt-purple-glycine: var(--purple-glycine-975-75);
  --background-alt-purple-glycine-hover: var(--purple-glycine-975-75-hover);
  --background-alt-purple-glycine-active: var(--purple-glycine-975-75-active);
  --background-alt-pink-macaron: var(--pink-macaron-975-75);
  --background-alt-pink-macaron-hover: var(--pink-macaron-975-75-hover);
  --background-alt-pink-macaron-active: var(--pink-macaron-975-75-active);
  --background-alt-pink-tuile: var(--pink-tuile-975-75);
  --background-alt-pink-tuile-hover: var(--pink-tuile-975-75-hover);
  --background-alt-pink-tuile-active: var(--pink-tuile-975-75-active);
  --background-alt-yellow-tournesol: var(--yellow-tournesol-975-75);
  --background-alt-yellow-tournesol-hover: var(--yellow-tournesol-975-75-hover);
  --background-alt-yellow-tournesol-active: var(--yellow-tournesol-975-75-active);
  --background-alt-yellow-moutarde: var(--yellow-moutarde-975-75);
  --background-alt-yellow-moutarde-hover: var(--yellow-moutarde-975-75-hover);
  --background-alt-yellow-moutarde-active: var(--yellow-moutarde-975-75-active);
  --background-alt-orange-terre-battue: var(--orange-terre-battue-975-75);
  --background-alt-orange-terre-battue-hover: var(--orange-terre-battue-975-75-hover);
  --background-alt-orange-terre-battue-active: var(--orange-terre-battue-975-75-active);
  --background-alt-brown-cafe-creme: var(--brown-cafe-creme-975-75);
  --background-alt-brown-cafe-creme-hover: var(--brown-cafe-creme-975-75-hover);
  --background-alt-brown-cafe-creme-active: var(--brown-cafe-creme-975-75-active);
  --background-alt-brown-caramel: var(--brown-caramel-975-75);
  --background-alt-brown-caramel-hover: var(--brown-caramel-975-75-hover);
  --background-alt-brown-caramel-active: var(--brown-caramel-975-75-active);
  --background-alt-brown-opera: var(--brown-opera-975-75);
  --background-alt-brown-opera-hover: var(--brown-opera-975-75-hover);
  --background-alt-brown-opera-active: var(--brown-opera-975-75-active);
  --background-alt-beige-gris-galet: var(--beige-gris-galet-975-75);
  --background-alt-beige-gris-galet-hover: var(--beige-gris-galet-975-75-hover);
  --background-alt-beige-gris-galet-active: var(--beige-gris-galet-975-75-active);
  --background-contrast-grey: var(--grey-950-100);
  --background-contrast-grey-hover: var(--grey-950-100-hover);
  --background-contrast-grey-active: var(--grey-950-100-active);
  --background-contrast-blue-france: var(--blue-france-950-100);
  --background-contrast-blue-france-hover: var(--blue-france-950-100-hover);
  --background-contrast-blue-france-active: var(--blue-france-950-100-active);
  --background-contrast-red-marianne: var(--red-marianne-950-100);
  --background-contrast-red-marianne-hover: var(--red-marianne-950-100-hover);
  --background-contrast-red-marianne-active: var(--red-marianne-950-100-active);
  --background-contrast-green-tilleul-verveine: var(--green-tilleul-verveine-950-100);
  --background-contrast-green-tilleul-verveine-hover: var(--green-tilleul-verveine-950-100-hover);
  --background-contrast-green-tilleul-verveine-active: var(--green-tilleul-verveine-950-100-active);
  --background-contrast-green-bourgeon: var(--green-bourgeon-950-100);
  --background-contrast-green-bourgeon-hover: var(--green-bourgeon-950-100-hover);
  --background-contrast-green-bourgeon-active: var(--green-bourgeon-950-100-active);
  --background-contrast-green-emeraude: var(--green-emeraude-950-100);
  --background-contrast-green-emeraude-hover: var(--green-emeraude-950-100-hover);
  --background-contrast-green-emeraude-active: var(--green-emeraude-950-100-active);
  --background-contrast-green-menthe: var(--green-menthe-950-100);
  --background-contrast-green-menthe-hover: var(--green-menthe-950-100-hover);
  --background-contrast-green-menthe-active: var(--green-menthe-950-100-active);
  --background-contrast-green-archipel: var(--green-archipel-950-100);
  --background-contrast-green-archipel-hover: var(--green-archipel-950-100-hover);
  --background-contrast-green-archipel-active: var(--green-archipel-950-100-active);
  --background-contrast-blue-ecume: var(--blue-ecume-950-100);
  --background-contrast-blue-ecume-hover: var(--blue-ecume-950-100-hover);
  --background-contrast-blue-ecume-active: var(--blue-ecume-950-100-active);
  --background-contrast-blue-cumulus: var(--blue-cumulus-950-100);
  --background-contrast-blue-cumulus-hover: var(--blue-cumulus-950-100-hover);
  --background-contrast-blue-cumulus-active: var(--blue-cumulus-950-100-active);
  --background-contrast-purple-glycine: var(--purple-glycine-950-100);
  --background-contrast-purple-glycine-hover: var(--purple-glycine-950-100-hover);
  --background-contrast-purple-glycine-active: var(--purple-glycine-950-100-active);
  --background-contrast-pink-macaron: var(--pink-macaron-950-100);
  --background-contrast-pink-macaron-hover: var(--pink-macaron-950-100-hover);
  --background-contrast-pink-macaron-active: var(--pink-macaron-950-100-active);
  --background-contrast-pink-tuile: var(--pink-tuile-950-100);
  --background-contrast-pink-tuile-hover: var(--pink-tuile-950-100-hover);
  --background-contrast-pink-tuile-active: var(--pink-tuile-950-100-active);
  --background-contrast-yellow-tournesol: var(--yellow-tournesol-950-100);
  --background-contrast-yellow-tournesol-hover: var(--yellow-tournesol-950-100-hover);
  --background-contrast-yellow-tournesol-active: var(--yellow-tournesol-950-100-active);
  --background-contrast-yellow-moutarde: var(--yellow-moutarde-950-100);
  --background-contrast-yellow-moutarde-hover: var(--yellow-moutarde-950-100-hover);
  --background-contrast-yellow-moutarde-active: var(--yellow-moutarde-950-100-active);
  --background-contrast-orange-terre-battue: var(--orange-terre-battue-950-100);
  --background-contrast-orange-terre-battue-hover: var(--orange-terre-battue-950-100-hover);
  --background-contrast-orange-terre-battue-active: var(--orange-terre-battue-950-100-active);
  --background-contrast-brown-cafe-creme: var(--brown-cafe-creme-950-100);
  --background-contrast-brown-cafe-creme-hover: var(--brown-cafe-creme-950-100-hover);
  --background-contrast-brown-cafe-creme-active: var(--brown-cafe-creme-950-100-active);
  --background-contrast-brown-caramel: var(--brown-caramel-950-100);
  --background-contrast-brown-caramel-hover: var(--brown-caramel-950-100-hover);
  --background-contrast-brown-caramel-active: var(--brown-caramel-950-100-active);
  --background-contrast-brown-opera: var(--brown-opera-950-100);
  --background-contrast-brown-opera-hover: var(--brown-opera-950-100-hover);
  --background-contrast-brown-opera-active: var(--brown-opera-950-100-active);
  --background-contrast-beige-gris-galet: var(--beige-gris-galet-950-100);
  --background-contrast-beige-gris-galet-hover: var(--beige-gris-galet-950-100-hover);
  --background-contrast-beige-gris-galet-active: var(--beige-gris-galet-950-100-active);
  --background-contrast-info: var(--info-950-100);
  --background-contrast-info-hover: var(--info-950-100-hover);
  --background-contrast-info-active: var(--info-950-100-active);
  --background-contrast-success: var(--success-950-100);
  --background-contrast-success-hover: var(--success-950-100-hover);
  --background-contrast-success-active: var(--success-950-100-active);
  --background-contrast-warning: var(--warning-950-100);
  --background-contrast-warning-hover: var(--warning-950-100-hover);
  --background-contrast-warning-active: var(--warning-950-100-active);
  --background-contrast-error: var(--error-950-100);
  --background-contrast-error-hover: var(--error-950-100-hover);
  --background-contrast-error-active: var(--error-950-100-active);
  --background-flat-grey: var(--grey-200-850);
  --background-flat-blue-france: var(--blue-france-sun-113-625);
  --background-flat-red-marianne: var(--red-marianne-425-625);
  --background-flat-green-tilleul-verveine: var(--green-tilleul-verveine-sun-418-moon-817);
  --background-flat-green-bourgeon: var(--green-bourgeon-sun-425-moon-759);
  --background-flat-green-emeraude: var(--green-emeraude-sun-425-moon-753);
  --background-flat-green-menthe: var(--green-menthe-sun-373-moon-652);
  --background-flat-green-archipel: var(--green-archipel-sun-391-moon-716);
  --background-flat-blue-ecume: var(--blue-ecume-sun-247-moon-675);
  --background-flat-blue-cumulus: var(--blue-cumulus-sun-368-moon-732);
  --background-flat-purple-glycine: var(--purple-glycine-sun-319-moon-630);
  --background-flat-pink-macaron: var(--pink-macaron-sun-406-moon-833);
  --background-flat-pink-tuile: var(--pink-tuile-sun-425-moon-750);
  --background-flat-yellow-tournesol: var(--yellow-tournesol-sun-407-moon-922);
  --background-flat-yellow-moutarde: var(--yellow-moutarde-sun-348-moon-860);
  --background-flat-orange-terre-battue: var(--orange-terre-battue-sun-370-moon-672);
  --background-flat-brown-cafe-creme: var(--brown-cafe-creme-sun-383-moon-885);
  --background-flat-brown-caramel: var(--brown-caramel-sun-425-moon-901);
  --background-flat-brown-opera: var(--brown-opera-sun-395-moon-820);
  --background-flat-beige-gris-galet: var(--beige-gris-galet-sun-407-moon-821);
  --background-flat-info: var(--info-425-625);
  --background-flat-success: var(--success-425-625);
  --background-flat-warning: var(--warning-425-625);
  --background-flat-error: var(--error-425-625);
  --background-action-high-blue-france: var(--blue-france-sun-113-625);
  --background-action-high-blue-france-hover: var(--blue-france-sun-113-625-hover);
  --background-action-high-blue-france-active: var(--blue-france-sun-113-625-active);
  --background-action-high-red-marianne: var(--red-marianne-425-625);
  --background-action-high-red-marianne-hover: var(--red-marianne-425-625-hover);
  --background-action-high-red-marianne-active: var(--red-marianne-425-625-active);
  --background-action-high-green-tilleul-verveine: var(--green-tilleul-verveine-sun-418-moon-817);
  --background-action-high-green-tilleul-verveine-hover: var(--green-tilleul-verveine-sun-418-moon-817-hover);
  --background-action-high-green-tilleul-verveine-active: var(--green-tilleul-verveine-sun-418-moon-817-active);
  --background-action-high-green-bourgeon: var(--green-bourgeon-sun-425-moon-759);
  --background-action-high-green-bourgeon-hover: var(--green-bourgeon-sun-425-moon-759-hover);
  --background-action-high-green-bourgeon-active: var(--green-bourgeon-sun-425-moon-759-active);
  --background-action-high-green-emeraude: var(--green-emeraude-sun-425-moon-753);
  --background-action-high-green-emeraude-hover: var(--green-emeraude-sun-425-moon-753-hover);
  --background-action-high-green-emeraude-active: var(--green-emeraude-sun-425-moon-753-active);
  --background-action-high-green-menthe: var(--green-menthe-sun-373-moon-652);
  --background-action-high-green-menthe-hover: var(--green-menthe-sun-373-moon-652-hover);
  --background-action-high-green-menthe-active: var(--green-menthe-sun-373-moon-652-active);
  --background-action-high-green-archipel: var(--green-archipel-sun-391-moon-716);
  --background-action-high-green-archipel-hover: var(--green-archipel-sun-391-moon-716-hover);
  --background-action-high-green-archipel-active: var(--green-archipel-sun-391-moon-716-active);
  --background-action-high-blue-ecume: var(--blue-ecume-sun-247-moon-675);
  --background-action-high-blue-ecume-hover: var(--blue-ecume-sun-247-moon-675-hover);
  --background-action-high-blue-ecume-active: var(--blue-ecume-sun-247-moon-675-active);
  --background-action-high-blue-cumulus: var(--blue-cumulus-sun-368-moon-732);
  --background-action-high-blue-cumulus-hover: var(--blue-cumulus-sun-368-moon-732-hover);
  --background-action-high-blue-cumulus-active: var(--blue-cumulus-sun-368-moon-732-active);
  --background-action-high-purple-glycine: var(--purple-glycine-sun-319-moon-630);
  --background-action-high-purple-glycine-hover: var(--purple-glycine-sun-319-moon-630-hover);
  --background-action-high-purple-glycine-active: var(--purple-glycine-sun-319-moon-630-active);
  --background-action-high-pink-macaron: var(--pink-macaron-sun-406-moon-833);
  --background-action-high-pink-macaron-hover: var(--pink-macaron-sun-406-moon-833-hover);
  --background-action-high-pink-macaron-active: var(--pink-macaron-sun-406-moon-833-active);
  --background-action-high-pink-tuile: var(--pink-tuile-sun-425-moon-750);
  --background-action-high-pink-tuile-hover: var(--pink-tuile-sun-425-moon-750-hover);
  --background-action-high-pink-tuile-active: var(--pink-tuile-sun-425-moon-750-active);
  --background-action-high-yellow-tournesol: var(--yellow-tournesol-sun-407-moon-922);
  --background-action-high-yellow-tournesol-hover: var(--yellow-tournesol-sun-407-moon-922-hover);
  --background-action-high-yellow-tournesol-active: var(--yellow-tournesol-sun-407-moon-922-active);
  --background-action-high-yellow-moutarde: var(--yellow-moutarde-sun-348-moon-860);
  --background-action-high-yellow-moutarde-hover: var(--yellow-moutarde-sun-348-moon-860-hover);
  --background-action-high-yellow-moutarde-active: var(--yellow-moutarde-sun-348-moon-860-active);
  --background-action-high-orange-terre-battue: var(--orange-terre-battue-sun-370-moon-672);
  --background-action-high-orange-terre-battue-hover: var(--orange-terre-battue-sun-370-moon-672-hover);
  --background-action-high-orange-terre-battue-active: var(--orange-terre-battue-sun-370-moon-672-active);
  --background-action-high-brown-cafe-creme: var(--brown-cafe-creme-sun-383-moon-885);
  --background-action-high-brown-cafe-creme-hover: var(--brown-cafe-creme-sun-383-moon-885-hover);
  --background-action-high-brown-cafe-creme-active: var(--brown-cafe-creme-sun-383-moon-885-active);
  --background-action-high-brown-caramel: var(--brown-caramel-sun-425-moon-901);
  --background-action-high-brown-caramel-hover: var(--brown-caramel-sun-425-moon-901-hover);
  --background-action-high-brown-caramel-active: var(--brown-caramel-sun-425-moon-901-active);
  --background-action-high-brown-opera: var(--brown-opera-sun-395-moon-820);
  --background-action-high-brown-opera-hover: var(--brown-opera-sun-395-moon-820-hover);
  --background-action-high-brown-opera-active: var(--brown-opera-sun-395-moon-820-active);
  --background-action-high-beige-gris-galet: var(--beige-gris-galet-sun-407-moon-821);
  --background-action-high-beige-gris-galet-hover: var(--beige-gris-galet-sun-407-moon-821-hover);
  --background-action-high-beige-gris-galet-active: var(--beige-gris-galet-sun-407-moon-821-active);
  --background-action-high-info: var(--info-425-625);
  --background-action-high-info-hover: var(--info-425-625-hover);
  --background-action-high-info-active: var(--info-425-625-active);
  --background-action-high-success: var(--success-425-625);
  --background-action-high-success-hover: var(--success-425-625-hover);
  --background-action-high-success-active: var(--success-425-625-active);
  --background-action-high-warning: var(--warning-425-625);
  --background-action-high-warning-hover: var(--warning-425-625-hover);
  --background-action-high-warning-active: var(--warning-425-625-active);
  --background-action-high-error: var(--error-425-625);
  --background-action-high-error-hover: var(--error-425-625-hover);
  --background-action-high-error-active: var(--error-425-625-active);
  --background-action-low-blue-france: var(--blue-france-925-125);
  --background-action-low-blue-france-hover: var(--blue-france-925-125-hover);
  --background-action-low-blue-france-active: var(--blue-france-925-125-active);
  --background-action-low-red-marianne: var(--red-marianne-925-125);
  --background-action-low-red-marianne-hover: var(--red-marianne-925-125-hover);
  --background-action-low-red-marianne-active: var(--red-marianne-925-125-active);
  --background-action-low-green-tilleul-verveine: var(--green-tilleul-verveine-925-125);
  --background-action-low-green-tilleul-verveine-hover: var(--green-tilleul-verveine-925-125-hover);
  --background-action-low-green-tilleul-verveine-active: var(--green-tilleul-verveine-925-125-active);
  --background-action-low-green-bourgeon: var(--green-bourgeon-925-125);
  --background-action-low-green-bourgeon-hover: var(--green-bourgeon-925-125-hover);
  --background-action-low-green-bourgeon-active: var(--green-bourgeon-925-125-active);
  --background-action-low-green-emeraude: var(--green-emeraude-925-125);
  --background-action-low-green-emeraude-hover: var(--green-emeraude-925-125-hover);
  --background-action-low-green-emeraude-active: var(--green-emeraude-925-125-active);
  --background-action-low-green-menthe: var(--green-menthe-925-125);
  --background-action-low-green-menthe-hover: var(--green-menthe-925-125-hover);
  --background-action-low-green-menthe-active: var(--green-menthe-925-125-active);
  --background-action-low-green-archipel: var(--green-archipel-925-125);
  --background-action-low-green-archipel-hover: var(--green-archipel-925-125-hover);
  --background-action-low-green-archipel-active: var(--green-archipel-925-125-active);
  --background-action-low-blue-ecume: var(--blue-ecume-925-125);
  --background-action-low-blue-ecume-hover: var(--blue-ecume-925-125-hover);
  --background-action-low-blue-ecume-active: var(--blue-ecume-925-125-active);
  --background-action-low-blue-cumulus: var(--blue-cumulus-925-125);
  --background-action-low-blue-cumulus-hover: var(--blue-cumulus-925-125-hover);
  --background-action-low-blue-cumulus-active: var(--blue-cumulus-925-125-active);
  --background-action-low-purple-glycine: var(--purple-glycine-925-125);
  --background-action-low-purple-glycine-hover: var(--purple-glycine-925-125-hover);
  --background-action-low-purple-glycine-active: var(--purple-glycine-925-125-active);
  --background-action-low-pink-macaron: var(--pink-macaron-925-125);
  --background-action-low-pink-macaron-hover: var(--pink-macaron-925-125-hover);
  --background-action-low-pink-macaron-active: var(--pink-macaron-925-125-active);
  --background-action-low-pink-tuile: var(--pink-tuile-925-125);
  --background-action-low-pink-tuile-hover: var(--pink-tuile-925-125-hover);
  --background-action-low-pink-tuile-active: var(--pink-tuile-925-125-active);
  --background-action-low-yellow-tournesol: var(--yellow-tournesol-925-125);
  --background-action-low-yellow-tournesol-hover: var(--yellow-tournesol-925-125-hover);
  --background-action-low-yellow-tournesol-active: var(--yellow-tournesol-925-125-active);
  --background-action-low-yellow-moutarde: var(--yellow-moutarde-925-125);
  --background-action-low-yellow-moutarde-hover: var(--yellow-moutarde-925-125-hover);
  --background-action-low-yellow-moutarde-active: var(--yellow-moutarde-925-125-active);
  --background-action-low-orange-terre-battue: var(--orange-terre-battue-925-125);
  --background-action-low-orange-terre-battue-hover: var(--orange-terre-battue-925-125-hover);
  --background-action-low-orange-terre-battue-active: var(--orange-terre-battue-925-125-active);
  --background-action-low-brown-cafe-creme: var(--brown-cafe-creme-925-125);
  --background-action-low-brown-cafe-creme-hover: var(--brown-cafe-creme-925-125-hover);
  --background-action-low-brown-cafe-creme-active: var(--brown-cafe-creme-925-125-active);
  --background-action-low-brown-caramel: var(--brown-caramel-925-125);
  --background-action-low-brown-caramel-hover: var(--brown-caramel-925-125-hover);
  --background-action-low-brown-caramel-active: var(--brown-caramel-925-125-active);
  --background-action-low-brown-opera: var(--brown-opera-925-125);
  --background-action-low-brown-opera-hover: var(--brown-opera-925-125-hover);
  --background-action-low-brown-opera-active: var(--brown-opera-925-125-active);
  --background-action-low-beige-gris-galet: var(--beige-gris-galet-925-125);
  --background-action-low-beige-gris-galet-hover: var(--beige-gris-galet-925-125-hover);
  --background-action-low-beige-gris-galet-active: var(--beige-gris-galet-925-125-active);
  --background-active-blue-france: var(--blue-france-sun-113-625);
  --background-active-blue-france-hover: var(--blue-france-sun-113-625-hover);
  --background-active-blue-france-active: var(--blue-france-sun-113-625-active);
  --background-active-red-marianne: var(--red-marianne-425-625);
  --background-active-red-marianne-hover: var(--red-marianne-425-625-hover);
  --background-active-red-marianne-active: var(--red-marianne-425-625-active);
  --background-open-blue-france: var(--blue-france-925-125);
  --background-open-blue-france-hover: var(--blue-france-925-125-hover);
  --background-open-blue-france-active: var(--blue-france-925-125-active);
  --background-open-red-marianne: var(--red-marianne-925-125);
  --background-open-red-marianne-hover: var(--red-marianne-925-125-hover);
  --background-open-red-marianne-active: var(--red-marianne-925-125-active);
  --background-disabled-grey: var(--grey-925-125);
  --background-raised-grey: var(--grey-1000-75);
  --background-raised-grey-hover: var(--grey-1000-75-hover);
  --background-raised-grey-active: var(--grey-1000-75-active);
  --background-overlap-grey: var(--grey-1000-100);
  --background-overlap-grey-hover: var(--grey-1000-100-hover);
  --background-overlap-grey-active: var(--grey-1000-100-active);
  --background-lifted-grey: var(--grey-1000-75);
  --background-lifted-grey-hover: var(--grey-1000-75-hover);
  --background-lifted-grey-active: var(--grey-1000-75-active);
  --background-alt-raised-grey: var(--grey-975-100);
  --background-alt-raised-grey-hover: var(--grey-975-100-hover);
  --background-alt-raised-grey-active: var(--grey-975-100-active);
  --background-alt-overlap-grey: var(--grey-975-125);
  --background-alt-overlap-grey-hover: var(--grey-975-125-hover);
  --background-alt-overlap-grey-active: var(--grey-975-125-active);
  --background-contrast-raised-grey: var(--grey-950-125);
  --background-contrast-raised-grey-hover: var(--grey-950-125-hover);
  --background-contrast-raised-grey-active: var(--grey-950-125-active);
  --background-contrast-overlap-grey: var(--grey-950-150);
  --background-contrast-overlap-grey-hover: var(--grey-950-150-hover);
  --background-contrast-overlap-grey-active: var(--grey-950-150-active);
  --text-default-grey: var(--grey-200-850);
  --text-default-info: var(--info-425-625);
  --text-default-success: var(--success-425-625);
  --text-default-warning: var(--warning-425-625);
  --text-default-error: var(--error-425-625);
  --text-action-high-grey: var(--grey-50-1000);
  --text-action-high-blue-france: var(--blue-france-sun-113-625);
  --text-action-high-red-marianne: var(--red-marianne-425-625);
  --text-action-high-green-tilleul-verveine: var(--green-tilleul-verveine-sun-418-moon-817);
  --text-action-high-green-bourgeon: var(--green-bourgeon-sun-425-moon-759);
  --text-action-high-green-emeraude: var(--green-emeraude-sun-425-moon-753);
  --text-action-high-green-menthe: var(--green-menthe-sun-373-moon-652);
  --text-action-high-green-archipel: var(--green-archipel-sun-391-moon-716);
  --text-action-high-blue-ecume: var(--blue-ecume-sun-247-moon-675);
  --text-action-high-blue-cumulus: var(--blue-cumulus-sun-368-moon-732);
  --text-action-high-purple-glycine: var(--purple-glycine-sun-319-moon-630);
  --text-action-high-pink-macaron: var(--pink-macaron-sun-406-moon-833);
  --text-action-high-pink-tuile: var(--pink-tuile-sun-425-moon-750);
  --text-action-high-yellow-tournesol: var(--yellow-tournesol-sun-407-moon-922);
  --text-action-high-yellow-moutarde: var(--yellow-moutarde-sun-348-moon-860);
  --text-action-high-orange-terre-battue: var(--orange-terre-battue-sun-370-moon-672);
  --text-action-high-brown-cafe-creme: var(--brown-cafe-creme-sun-383-moon-885);
  --text-action-high-brown-caramel: var(--brown-caramel-sun-425-moon-901);
  --text-action-high-brown-opera: var(--brown-opera-sun-395-moon-820);
  --text-action-high-beige-gris-galet: var(--beige-gris-galet-sun-407-moon-821);
  --text-title-grey: var(--grey-50-1000);
  --text-title-blue-france: var(--blue-france-sun-113-625);
  --text-title-red-marianne: var(--red-marianne-425-625);
  --text-label-grey: var(--grey-50-1000);
  --text-label-blue-france: var(--blue-france-sun-113-625);
  --text-label-red-marianne: var(--red-marianne-425-625);
  --text-label-green-tilleul-verveine: var(--green-tilleul-verveine-sun-418-moon-817);
  --text-label-green-bourgeon: var(--green-bourgeon-sun-425-moon-759);
  --text-label-green-emeraude: var(--green-emeraude-sun-425-moon-753);
  --text-label-green-menthe: var(--green-menthe-sun-373-moon-652);
  --text-label-green-archipel: var(--green-archipel-sun-391-moon-716);
  --text-label-blue-ecume: var(--blue-ecume-sun-247-moon-675);
  --text-label-blue-cumulus: var(--blue-cumulus-sun-368-moon-732);
  --text-label-purple-glycine: var(--purple-glycine-sun-319-moon-630);
  --text-label-pink-macaron: var(--pink-macaron-sun-406-moon-833);
  --text-label-pink-tuile: var(--pink-tuile-sun-425-moon-750);
  --text-label-yellow-tournesol: var(--yellow-tournesol-sun-407-moon-922);
  --text-label-yellow-moutarde: var(--yellow-moutarde-sun-348-moon-860);
  --text-label-orange-terre-battue: var(--orange-terre-battue-sun-370-moon-672);
  --text-label-brown-cafe-creme: var(--brown-cafe-creme-sun-383-moon-885);
  --text-label-brown-caramel: var(--brown-caramel-sun-425-moon-901);
  --text-label-brown-opera: var(--brown-opera-sun-395-moon-820);
  --text-label-beige-gris-galet: var(--beige-gris-galet-sun-407-moon-821);
  --text-active-grey: var(--grey-50-1000);
  --text-active-blue-france: var(--blue-france-sun-113-625);
  --text-active-red-marianne: var(--red-marianne-425-625);
  --text-mention-grey: var(--grey-425-625);
  --text-inverted-grey: var(--grey-1000-50);
  --text-inverted-blue-france: var(--blue-france-975-sun-113);
  --text-inverted-red-marianne: var(--red-marianne-975-75);
  --text-inverted-info: var(--info-975-75);
  --text-inverted-success: var(--success-975-75);
  --text-inverted-warning: var(--warning-975-75);
  --text-inverted-error: var(--error-975-75);
  --text-inverted-green-tilleul-verveine: var(--green-tilleul-verveine-975-75);
  --text-inverted-green-bourgeon: var(--green-bourgeon-975-75);
  --text-inverted-green-emeraude: var(--green-emeraude-975-75);
  --text-inverted-green-menthe: var(--green-menthe-975-75);
  --text-inverted-green-archipel: var(--green-archipel-975-75);
  --text-inverted-blue-ecume: var(--blue-ecume-975-75);
  --text-inverted-blue-cumulus: var(--blue-cumulus-975-75);
  --text-inverted-purple-glycine: var(--purple-glycine-975-75);
  --text-inverted-pink-macaron: var(--pink-macaron-975-75);
  --text-inverted-pink-tuile: var(--pink-tuile-975-75);
  --text-inverted-yellow-tournesol: var(--yellow-tournesol-975-75);
  --text-inverted-yellow-moutarde: var(--yellow-moutarde-975-75);
  --text-inverted-orange-terre-battue: var(--orange-terre-battue-975-75);
  --text-inverted-brown-cafe-creme: var(--brown-cafe-creme-975-75);
  --text-inverted-brown-caramel: var(--brown-caramel-975-75);
  --text-inverted-brown-opera: var(--brown-opera-975-75);
  --text-inverted-beige-gris-galet: var(--beige-gris-galet-975-75);
  --text-disabled-grey: var(--grey-625-425);
  --text-black-white-grey: var(--grey-0-1000);
  --border-default-grey: var(--grey-900-175);
  --border-default-blue-france: var(--blue-france-main-525);
  --border-default-red-marianne: var(--red-marianne-main-472);
  --border-default-green-tilleul-verveine: var(--green-tilleul-verveine-main-707);
  --border-default-green-bourgeon: var(--green-bourgeon-main-640);
  --border-default-green-emeraude: var(--green-emeraude-main-632);
  --border-default-green-menthe: var(--green-menthe-main-548);
  --border-default-green-archipel: var(--green-archipel-main-557);
  --border-default-blue-ecume: var(--blue-ecume-main-400);
  --border-default-blue-cumulus: var(--blue-cumulus-main-526);
  --border-default-purple-glycine: var(--purple-glycine-main-494);
  --border-default-pink-macaron: var(--pink-macaron-main-689);
  --border-default-pink-tuile: var(--pink-tuile-main-556);
  --border-default-yellow-tournesol: var(--yellow-tournesol-main-731);
  --border-default-yellow-moutarde: var(--yellow-moutarde-main-679);
  --border-default-orange-terre-battue: var(--orange-terre-battue-main-645);
  --border-default-brown-cafe-creme: var(--brown-cafe-creme-main-782);
  --border-default-brown-caramel: var(--brown-caramel-main-648);
  --border-default-brown-opera: var(--brown-opera-main-680);
  --border-default-beige-gris-galet: var(--beige-gris-galet-main-702);
  --border-active-blue-france: var(--blue-france-sun-113-625);
  --border-active-red-marianne: var(--red-marianne-425-625);
  --border-action-high-grey: var(--grey-50-1000);
  --border-action-high-blue-france: var(--blue-france-sun-113-625);
  --border-action-high-red-marianne: var(--red-marianne-425-625);
  --border-action-high-info: var(--info-425-625);
  --border-action-high-success: var(--success-425-625);
  --border-action-high-warning: var(--warning-425-625);
  --border-action-high-error: var(--error-425-625);
  --border-action-low-blue-france: var(--blue-france-850-200);
  --border-action-low-red-marianne: var(--red-marianne-850-200);
  --border-action-low-green-tilleul-verveine: var(--green-tilleul-verveine-850-200);
  --border-action-low-green-bourgeon: var(--green-bourgeon-850-200);
  --border-action-low-green-emeraude: var(--green-emeraude-850-200);
  --border-action-low-green-menthe: var(--green-menthe-850-200);
  --border-action-low-green-archipel: var(--green-archipel-850-200);
  --border-action-low-blue-ecume: var(--blue-ecume-850-200);
  --border-action-low-blue-cumulus: var(--blue-cumulus-850-200);
  --border-action-low-purple-glycine: var(--purple-glycine-850-200);
  --border-action-low-pink-macaron: var(--pink-macaron-850-200);
  --border-action-low-pink-tuile: var(--pink-tuile-850-200);
  --border-action-low-yellow-tournesol: var(--yellow-tournesol-850-200);
  --border-action-low-yellow-moutarde: var(--yellow-moutarde-850-200);
  --border-action-low-orange-terre-battue: var(--orange-terre-battue-850-200);
  --border-action-low-brown-cafe-creme: var(--brown-cafe-creme-850-200);
  --border-action-low-brown-caramel: var(--brown-caramel-850-200);
  --border-action-low-brown-opera: var(--brown-opera-850-200);
  --border-action-low-beige-gris-galet: var(--beige-gris-galet-850-200);
  --border-open-blue-france: var(--blue-france-925-125);
  --border-open-red-marianne: var(--red-marianne-925-125);
  --border-plain-grey: var(--grey-200-850);
  --border-plain-blue-france: var(--blue-france-sun-113-625);
  --border-plain-red-marianne: var(--red-marianne-425-625);
  --border-plain-info: var(--info-425-625);
  --border-plain-success: var(--success-425-625);
  --border-plain-warning: var(--warning-425-625);
  --border-plain-error: var(--error-425-625);
  --border-plain-green-tilleul-verveine: var(--green-tilleul-verveine-sun-418-moon-817);
  --border-plain-green-bourgeon: var(--green-bourgeon-sun-425-moon-759);
  --border-plain-green-emeraude: var(--green-emeraude-sun-425-moon-753);
  --border-plain-green-menthe: var(--green-menthe-sun-373-moon-652);
  --border-plain-green-archipel: var(--green-archipel-sun-391-moon-716);
  --border-plain-blue-ecume: var(--blue-ecume-sun-247-moon-675);
  --border-plain-blue-cumulus: var(--blue-cumulus-sun-368-moon-732);
  --border-plain-purple-glycine: var(--purple-glycine-sun-319-moon-630);
  --border-plain-pink-macaron: var(--pink-macaron-sun-406-moon-833);
  --border-plain-pink-tuile: var(--pink-tuile-sun-425-moon-750);
  --border-plain-yellow-tournesol: var(--yellow-tournesol-sun-407-moon-922);
  --border-plain-yellow-moutarde: var(--yellow-moutarde-sun-348-moon-860);
  --border-plain-orange-terre-battue: var(--orange-terre-battue-sun-370-moon-672);
  --border-plain-brown-cafe-creme: var(--brown-cafe-creme-sun-383-moon-885);
  --border-plain-brown-caramel: var(--brown-caramel-sun-425-moon-901);
  --border-plain-brown-opera: var(--brown-opera-sun-395-moon-820);
  --border-plain-beige-gris-galet: var(--beige-gris-galet-sun-407-moon-821);
  --border-disabled-grey: var(--grey-925-125);
  --artwork-major-blue-france: var(--blue-france-sun-113-625);
  --artwork-major-blue-france-hover: var(--blue-france-sun-113-625-hover);
  --artwork-major-blue-france-active: var(--blue-france-sun-113-625-active);
  --artwork-major-red-marianne: var(--red-marianne-425-625);
  --artwork-major-red-marianne-hover: var(--red-marianne-425-625-hover);
  --artwork-major-red-marianne-active: var(--red-marianne-425-625-active);
  --artwork-major-green-tilleul-verveine: var(--green-tilleul-verveine-sun-418-moon-817);
  --artwork-major-green-tilleul-verveine-hover: var(--green-tilleul-verveine-sun-418-moon-817-hover);
  --artwork-major-green-tilleul-verveine-active: var(--green-tilleul-verveine-sun-418-moon-817-active);
  --artwork-major-green-bourgeon: var(--green-bourgeon-sun-425-moon-759);
  --artwork-major-green-bourgeon-hover: var(--green-bourgeon-sun-425-moon-759-hover);
  --artwork-major-green-bourgeon-active: var(--green-bourgeon-sun-425-moon-759-active);
  --artwork-major-green-emeraude: var(--green-emeraude-sun-425-moon-753);
  --artwork-major-green-emeraude-hover: var(--green-emeraude-sun-425-moon-753-hover);
  --artwork-major-green-emeraude-active: var(--green-emeraude-sun-425-moon-753-active);
  --artwork-major-green-menthe: var(--green-menthe-sun-373-moon-652);
  --artwork-major-green-menthe-hover: var(--green-menthe-sun-373-moon-652-hover);
  --artwork-major-green-menthe-active: var(--green-menthe-sun-373-moon-652-active);
  --artwork-major-green-archipel: var(--green-archipel-sun-391-moon-716);
  --artwork-major-green-archipel-hover: var(--green-archipel-sun-391-moon-716-hover);
  --artwork-major-green-archipel-active: var(--green-archipel-sun-391-moon-716-active);
  --artwork-major-blue-ecume: var(--blue-ecume-sun-247-moon-675);
  --artwork-major-blue-ecume-hover: var(--blue-ecume-sun-247-moon-675-hover);
  --artwork-major-blue-ecume-active: var(--blue-ecume-sun-247-moon-675-active);
  --artwork-major-blue-cumulus: var(--blue-cumulus-sun-368-moon-732);
  --artwork-major-blue-cumulus-hover: var(--blue-cumulus-sun-368-moon-732-hover);
  --artwork-major-blue-cumulus-active: var(--blue-cumulus-sun-368-moon-732-active);
  --artwork-major-purple-glycine: var(--purple-glycine-sun-319-moon-630);
  --artwork-major-purple-glycine-hover: var(--purple-glycine-sun-319-moon-630-hover);
  --artwork-major-purple-glycine-active: var(--purple-glycine-sun-319-moon-630-active);
  --artwork-major-pink-macaron: var(--pink-macaron-sun-406-moon-833);
  --artwork-major-pink-macaron-hover: var(--pink-macaron-sun-406-moon-833-hover);
  --artwork-major-pink-macaron-active: var(--pink-macaron-sun-406-moon-833-active);
  --artwork-major-pink-tuile: var(--pink-tuile-sun-425-moon-750);
  --artwork-major-pink-tuile-hover: var(--pink-tuile-sun-425-moon-750-hover);
  --artwork-major-pink-tuile-active: var(--pink-tuile-sun-425-moon-750-active);
  --artwork-major-yellow-tournesol: var(--yellow-tournesol-sun-407-moon-922);
  --artwork-major-yellow-tournesol-hover: var(--yellow-tournesol-sun-407-moon-922-hover);
  --artwork-major-yellow-tournesol-active: var(--yellow-tournesol-sun-407-moon-922-active);
  --artwork-major-yellow-moutarde: var(--yellow-moutarde-sun-348-moon-860);
  --artwork-major-yellow-moutarde-hover: var(--yellow-moutarde-sun-348-moon-860-hover);
  --artwork-major-yellow-moutarde-active: var(--yellow-moutarde-sun-348-moon-860-active);
  --artwork-major-orange-terre-battue: var(--orange-terre-battue-sun-370-moon-672);
  --artwork-major-orange-terre-battue-hover: var(--orange-terre-battue-sun-370-moon-672-hover);
  --artwork-major-orange-terre-battue-active: var(--orange-terre-battue-sun-370-moon-672-active);
  --artwork-major-brown-cafe-creme: var(--brown-cafe-creme-sun-383-moon-885);
  --artwork-major-brown-cafe-creme-hover: var(--brown-cafe-creme-sun-383-moon-885-hover);
  --artwork-major-brown-cafe-creme-active: var(--brown-cafe-creme-sun-383-moon-885-active);
  --artwork-major-brown-caramel: var(--brown-caramel-sun-425-moon-901);
  --artwork-major-brown-caramel-hover: var(--brown-caramel-sun-425-moon-901-hover);
  --artwork-major-brown-caramel-active: var(--brown-caramel-sun-425-moon-901-active);
  --artwork-major-brown-opera: var(--brown-opera-sun-395-moon-820);
  --artwork-major-brown-opera-hover: var(--brown-opera-sun-395-moon-820-hover);
  --artwork-major-brown-opera-active: var(--brown-opera-sun-395-moon-820-active);
  --artwork-major-beige-gris-galet: var(--beige-gris-galet-sun-407-moon-821);
  --artwork-major-beige-gris-galet-hover: var(--beige-gris-galet-sun-407-moon-821-hover);
  --artwork-major-beige-gris-galet-active: var(--beige-gris-galet-sun-407-moon-821-active);
  --artwork-minor-blue-france: var(--blue-france-main-525);
  --artwork-minor-red-marianne: var(--red-marianne-main-472);
  --artwork-minor-green-tilleul-verveine: var(--green-tilleul-verveine-main-707);
  --artwork-minor-green-bourgeon: var(--green-bourgeon-main-640);
  --artwork-minor-green-emeraude: var(--green-emeraude-main-632);
  --artwork-minor-green-menthe: var(--green-menthe-main-548);
  --artwork-minor-green-archipel: var(--green-archipel-main-557);
  --artwork-minor-blue-ecume: var(--blue-ecume-main-400);
  --artwork-minor-blue-cumulus: var(--blue-cumulus-main-526);
  --artwork-minor-purple-glycine: var(--purple-glycine-main-494);
  --artwork-minor-pink-macaron: var(--pink-macaron-main-689);
  --artwork-minor-pink-tuile: var(--pink-tuile-main-556);
  --artwork-minor-yellow-tournesol: var(--yellow-tournesol-main-731);
  --artwork-minor-yellow-moutarde: var(--yellow-moutarde-main-679);
  --artwork-minor-orange-terre-battue: var(--orange-terre-battue-main-645);
  --artwork-minor-brown-cafe-creme: var(--brown-cafe-creme-main-782);
  --artwork-minor-brown-caramel: var(--brown-caramel-main-648);
  --artwork-minor-brown-opera: var(--brown-opera-main-680);
  --artwork-minor-beige-gris-galet: var(--beige-gris-galet-main-702);
  --artwork-decorative-grey: var(--grey-950-100);
  --artwork-decorative-blue-france: var(--blue-france-950-100);
  --artwork-decorative-red-marianne: var(--red-marianne-950-100);
  --artwork-decorative-green-tilleul-verveine: var(--green-tilleul-verveine-950-100);
  --artwork-decorative-green-bourgeon: var(--green-bourgeon-950-100);
  --artwork-decorative-green-emeraude: var(--green-emeraude-950-100);
  --artwork-decorative-green-menthe: var(--green-menthe-950-100);
  --artwork-decorative-green-archipel: var(--green-archipel-950-100);
  --artwork-decorative-blue-ecume: var(--blue-ecume-950-100);
  --artwork-decorative-blue-cumulus: var(--blue-cumulus-950-100);
  --artwork-decorative-purple-glycine: var(--purple-glycine-950-100);
  --artwork-decorative-pink-macaron: var(--pink-macaron-950-100);
  --artwork-decorative-pink-tuile: var(--pink-tuile-950-100);
  --artwork-decorative-yellow-tournesol: var(--yellow-tournesol-950-100);
  --artwork-decorative-yellow-moutarde: var(--yellow-moutarde-950-100);
  --artwork-decorative-orange-terre-battue: var(--orange-terre-battue-950-100);
  --artwork-decorative-brown-cafe-creme: var(--brown-cafe-creme-950-100);
  --artwork-decorative-brown-caramel: var(--brown-caramel-950-100);
  --artwork-decorative-brown-opera: var(--brown-opera-950-100);
  --artwork-decorative-beige-gris-galet: var(--beige-gris-galet-950-100);
  --artwork-background-grey: var(--grey-975-75);
  --artwork-background-blue-france: var(--blue-france-975-75);
  --artwork-background-red-marianne: var(--red-marianne-975-75);
  --artwork-background-green-tilleul-verveine: var(--green-tilleul-verveine-975-75);
  --artwork-background-green-bourgeon: var(--green-bourgeon-975-75);
  --artwork-background-green-emeraude: var(--green-emeraude-975-75);
  --artwork-background-green-menthe: var(--green-menthe-975-75);
  --artwork-background-green-archipel: var(--green-archipel-975-75);
  --artwork-background-blue-ecume: var(--blue-ecume-975-75);
  --artwork-background-blue-cumulus: var(--blue-cumulus-975-75);
  --artwork-background-purple-glycine: var(--purple-glycine-975-75);
  --artwork-background-pink-macaron: var(--pink-macaron-975-75);
  --artwork-background-pink-tuile: var(--pink-tuile-975-75);
  --artwork-background-yellow-tournesol: var(--yellow-tournesol-975-75);
  --artwork-background-yellow-moutarde: var(--yellow-moutarde-975-75);
  --artwork-background-orange-terre-battue: var(--orange-terre-battue-975-75);
  --artwork-background-brown-cafe-creme: var(--brown-cafe-creme-975-75);
  --artwork-background-brown-caramel: var(--brown-caramel-975-75);
  --artwork-background-brown-opera: var(--brown-opera-975-75);
  --artwork-background-beige-gris-galet: var(--beige-gris-galet-975-75);
  --artwork-motif-grey: var(--grey-925-125);
  --artwork-motif-blue-france: var(--blue-france-925-125);
  --artwork-motif-red-marianne: var(--red-marianne-925-125);
  --artwork-motif-green-tilleul-verveine: var(--green-tilleul-verveine-925-125);
  --artwork-motif-green-bourgeon: var(--green-bourgeon-925-125);
  --artwork-motif-green-emeraude: var(--green-emeraude-925-125);
  --artwork-motif-green-menthe: var(--green-menthe-925-125);
  --artwork-motif-green-archipel: var(--green-archipel-925-125);
  --artwork-motif-blue-ecume: var(--blue-ecume-925-125);
  --artwork-motif-blue-cumulus: var(--blue-cumulus-925-125);
  --artwork-motif-purple-glycine: var(--purple-glycine-925-125);
  --artwork-motif-pink-macaron: var(--pink-macaron-925-125);
  --artwork-motif-pink-tuile: var(--pink-tuile-925-125);
  --artwork-motif-yellow-tournesol: var(--yellow-tournesol-925-125);
  --artwork-motif-yellow-moutarde: var(--yellow-moutarde-925-125);
  --artwork-motif-orange-terre-battue: var(--orange-terre-battue-925-125);
  --artwork-motif-brown-cafe-creme: var(--brown-cafe-creme-925-125);
  --artwork-motif-brown-caramel: var(--brown-caramel-925-125);
  --artwork-motif-brown-opera: var(--brown-opera-925-125);
  --artwork-motif-beige-gris-galet: var(--beige-gris-galet-925-125);
  --grey-1000-50: #fff;
  --grey-1000-50-hover: #f6f6f6;
  --grey-1000-50-active: #ededed;
  --grey-975-75: #f6f6f6;
  --grey-975-75-hover: #dfdfdf;
  --grey-975-75-active: #cfcfcf;
  --grey-950-100: #eee;
  --grey-950-100-hover: #d2d2d2;
  --grey-950-100-active: #c1c1c1;
  --grey-200-850: #3a3a3a;
  --grey-925-125: #e5e5e5;
  --grey-1000-75: #fff;
  --grey-1000-75-hover: #f6f6f6;
  --grey-1000-75-active: #ededed;
  --grey-1000-100: #fff;
  --grey-1000-100-hover: #f6f6f6;
  --grey-1000-100-active: #ededed;
  --grey-975-100: #f6f6f6;
  --grey-975-100-hover: #dfdfdf;
  --grey-975-100-active: #cfcfcf;
  --grey-975-125: #f6f6f6;
  --grey-975-125-hover: #dfdfdf;
  --grey-975-125-active: #cfcfcf;
  --grey-950-125: #eee;
  --grey-950-125-hover: #d2d2d2;
  --grey-950-125-active: #c1c1c1;
  --grey-950-150: #eee;
  --grey-950-150-hover: #d2d2d2;
  --grey-950-150-active: #c1c1c1;
  --grey-50-1000: #161616;
  --grey-425-625: #666;
  --grey-625-425: #929292;
  --grey-0-1000: #000;
  --grey-900-175: #ddd;
  --blue-france-975-75: #f5f5fe;
  --blue-france-975-75-hover: #dcdcfc;
  --blue-france-975-75-active: #cbcbfa;
  --blue-france-950-100: #ececfe;
  --blue-france-950-100-hover: #cecefc;
  --blue-france-950-100-active: #bbbbfc;
  --blue-france-sun-113-625: #000091;
  --blue-france-sun-113-625-hover: #1212ff;
  --blue-france-sun-113-625-active: #2323ff;
  --blue-france-925-125: #e3e3fd;
  --blue-france-925-125-hover: #c1c1fb;
  --blue-france-925-125-active: #adadf9;
  --blue-france-975-sun-113: #f5f5fe;
  --blue-france-main-525: #6a6af4;
  --blue-france-850-200: #cacafb;
  --red-marianne-975-75: #fef4f4;
  --red-marianne-975-75-hover: #fcd7d7;
  --red-marianne-975-75-active: #fac4c4;
  --red-marianne-950-100: #fee9e9;
  --red-marianne-950-100-hover: #fdc5c5;
  --red-marianne-950-100-active: #fcafaf;
  --red-marianne-425-625: #c9191e;
  --red-marianne-425-625-hover: #f93f42;
  --red-marianne-425-625-active: #f95a5c;
  --red-marianne-925-125: #fddede;
  --red-marianne-925-125-hover: #fbb6b6;
  --red-marianne-925-125-active: #fa9e9e;
  --red-marianne-main-472: #e1000f;
  --red-marianne-850-200: #fcbfbf;
  --info-950-100: #e8edff;
  --info-950-100-hover: #c2d1ff;
  --info-950-100-active: #a9bfff;
  --info-425-625: #0063cb;
  --info-425-625-hover: #3b87ff;
  --info-425-625-active: #6798ff;
  --info-975-75: #f4f6ff;
  --success-950-100: #b8fec9;
  --success-950-100-hover: #46fd89;
  --success-950-100-active: #34eb7b;
  --success-425-625: #18753c;
  --success-425-625-hover: #27a959;
  --success-425-625-active: #2fc368;
  --success-975-75: #dffee6;
  --warning-950-100: #ffe9e6;
  --warning-950-100-hover: #ffc6bd;
  --warning-950-100-active: #ffb0a2;
  --warning-425-625: #b34000;
  --warning-425-625-hover: #ff6218;
  --warning-425-625-active: #ff7a55;
  --warning-975-75: #fff4f3;
  --error-950-100: #ffe9e9;
  --error-950-100-hover: #ffc5c5;
  --error-950-100-active: #ffafaf;
  --error-425-625: #ce0500;
  --error-425-625-hover: #ff2725;
  --error-425-625-active: #ff4140;
  --error-975-75: #fff4f4;
  --green-tilleul-verveine-975-75: #fef7da;
  --green-tilleul-verveine-975-75-hover: #fce552;
  --green-tilleul-verveine-975-75-active: #ebd54c;
  --green-tilleul-verveine-950-100: #fceeac;
  --green-tilleul-verveine-950-100-hover: #e8d45c;
  --green-tilleul-verveine-950-100-active: #d4c254;
  --green-tilleul-verveine-sun-418-moon-817: #66673d;
  --green-tilleul-verveine-sun-418-moon-817-hover: #929359;
  --green-tilleul-verveine-sun-418-moon-817-active: #a7a967;
  --green-tilleul-verveine-925-125: #fbe769;
  --green-tilleul-verveine-925-125-hover: #d7c655;
  --green-tilleul-verveine-925-125-active: #c2b24c;
  --green-tilleul-verveine-main-707: #b7a73f;
  --green-tilleul-verveine-850-200: #e2cf58;
  --green-bourgeon-975-75: #e6feda;
  --green-bourgeon-975-75-hover: #a7fc62;
  --green-bourgeon-975-75-active: #98ed4d;
  --green-bourgeon-950-100: #c9fcac;
  --green-bourgeon-950-100-hover: #9ae95d;
  --green-bourgeon-950-100-active: #8dd555;
  --green-bourgeon-sun-425-moon-759: #447049;
  --green-bourgeon-sun-425-moon-759-hover: #639f6a;
  --green-bourgeon-sun-425-moon-759-active: #72b77a;
  --green-bourgeon-925-125: #a9fb68;
  --green-bourgeon-925-125-hover: #8ed654;
  --green-bourgeon-925-125-active: #7fc04b;
  --green-bourgeon-main-640: #68a532;
  --green-bourgeon-850-200: #95e257;
  --green-emeraude-975-75: #e3fdeb;
  --green-emeraude-975-75-hover: #94f9b9;
  --green-emeraude-975-75-active: #6df1a3;
  --green-emeraude-950-100: #c3fad5;
  --green-emeraude-950-100-hover: #77eda5;
  --green-emeraude-950-100-active: #6dd897;
  --green-emeraude-sun-425-moon-753: #297254;
  --green-emeraude-sun-425-moon-753-hover: #3ea47a;
  --green-emeraude-sun-425-moon-753-active: #49bc8d;
  --green-emeraude-925-125: #9ef9be;
  --green-emeraude-925-125-hover: #69df97;
  --green-emeraude-925-125-active: #5ec988;
  --green-emeraude-main-632: #00a95f;
  --green-emeraude-850-200: #6fe49d;
  --green-menthe-975-75: #dffdf7;
  --green-menthe-975-75-hover: #84f9e7;
  --green-menthe-975-75-active: #70ebd8;
  --green-menthe-950-100: #bafaee;
  --green-menthe-950-100-hover: #79e7d5;
  --green-menthe-950-100-active: #6fd3c3;
  --green-menthe-sun-373-moon-652: #37635f;
  --green-menthe-sun-373-moon-652-hover: #53918c;
  --green-menthe-sun-373-moon-652-active: #62a9a2;
  --green-menthe-925-125: #8bf8e7;
  --green-menthe-925-125-hover: #6ed5c5;
  --green-menthe-925-125-active: #62bfb1;
  --green-menthe-main-548: #009081;
  --green-menthe-850-200: #73e0cf;
  --green-archipel-975-75: #e5fbfd;
  --green-archipel-975-75-hover: #99f2f8;
  --green-archipel-975-75-active: #73e9f0;
  --green-archipel-950-100: #c7f6fc;
  --green-archipel-950-100-hover: #64ecf8;
  --green-archipel-950-100-active: #5bd8e3;
  --green-archipel-sun-391-moon-716: #006a6f;
  --green-archipel-sun-391-moon-716-hover: #009fa7;
  --green-archipel-sun-391-moon-716-active: #00bbc3;
  --green-archipel-925-125: #a6f2fa;
  --green-archipel-925-125-hover: #62dbe5;
  --green-archipel-925-125-active: #58c5cf;
  --green-archipel-main-557: #009099;
  --green-archipel-850-200: #60e0eb;
  --blue-ecume-975-75: #f4f6fe;
  --blue-ecume-975-75-hover: #d7dffb;
  --blue-ecume-975-75-active: #c3cffa;
  --blue-ecume-950-100: #e9edfe;
  --blue-ecume-950-100-hover: #c5d0fc;
  --blue-ecume-950-100-active: #adbffc;
  --blue-ecume-sun-247-moon-675: #2f4077;
  --blue-ecume-sun-247-moon-675-hover: #4e68bb;
  --blue-ecume-sun-247-moon-675-active: #667dcf;
  --blue-ecume-925-125: #dee5fd;
  --blue-ecume-925-125-hover: #b4c5fb;
  --blue-ecume-925-125-active: #99b3f9;
  --blue-ecume-main-400: #465f9d;
  --blue-ecume-850-200: #bfccfb;
  --blue-cumulus-975-75: #f3f6fe;
  --blue-cumulus-975-75-hover: #d3dffc;
  --blue-cumulus-975-75-active: #bed0fa;
  --blue-cumulus-950-100: #e6eefe;
  --blue-cumulus-950-100-hover: #bcd3fc;
  --blue-cumulus-950-100-active: #9fc3fc;
  --blue-cumulus-sun-368-moon-732: #3558a2;
  --blue-cumulus-sun-368-moon-732-hover: #5982e0;
  --blue-cumulus-sun-368-moon-732-active: #7996e6;
  --blue-cumulus-925-125: #dae6fd;
  --blue-cumulus-925-125-hover: #a9c8fb;
  --blue-cumulus-925-125-active: #8ab8f9;
  --blue-cumulus-main-526: #417dc4;
  --blue-cumulus-850-200: #b6cffb;
  --purple-glycine-975-75: #fef3fd;
  --purple-glycine-975-75-hover: #fcd4f8;
  --purple-glycine-975-75-active: #fabff5;
  --purple-glycine-950-100: #fee7fc;
  --purple-glycine-950-100-hover: #fdc0f8;
  --purple-glycine-950-100-active: #fca8f6;
  --purple-glycine-sun-319-moon-630: #6e445a;
  --purple-glycine-sun-319-moon-630-hover: #a66989;
  --purple-glycine-sun-319-moon-630-active: #bb7f9e;
  --purple-glycine-925-125: #fddbfa;
  --purple-glycine-925-125-hover: #fbaff5;
  --purple-glycine-925-125-active: #fa96f2;
  --purple-glycine-main-494: #a558a0;
  --purple-glycine-850-200: #fbb8f6;
  --pink-macaron-975-75: #fef4f2;
  --pink-macaron-975-75-hover: #fcd8d0;
  --pink-macaron-975-75-active: #fac5b8;
  --pink-macaron-950-100: #fee9e6;
  --pink-macaron-950-100-hover: #fdc6bd;
  --pink-macaron-950-100-active: #fcb0a2;
  --pink-macaron-sun-406-moon-833: #8d533e;
  --pink-macaron-sun-406-moon-833-hover: #ca795c;
  --pink-macaron-sun-406-moon-833-active: #e08e73;
  --pink-macaron-925-125: #fddfda;
  --pink-macaron-925-125-hover: #fbb8ab;
  --pink-macaron-925-125-active: #faa18d;
  --pink-macaron-main-689: #e18b76;
  --pink-macaron-850-200: #fcc0b4;
  --pink-tuile-975-75: #fef4f3;
  --pink-tuile-975-75-hover: #fcd7d3;
  --pink-tuile-975-75-active: #fac4be;
  --pink-tuile-950-100: #fee9e7;
  --pink-tuile-950-100-hover: #fdc6c0;
  --pink-tuile-950-100-active: #fcb0a7;
  --pink-tuile-sun-425-moon-750: #a94645;
  --pink-tuile-sun-425-moon-750-hover: #d5706f;
  --pink-tuile-sun-425-moon-750-active: #da8a89;
  --pink-tuile-925-125: #fddfdb;
  --pink-tuile-925-125-hover: #fbb8ad;
  --pink-tuile-925-125-active: #faa191;
  --pink-tuile-main-556: #ce614a;
  --pink-tuile-850-200: #fcbfb7;
  --yellow-tournesol-975-75: #fef6e3;
  --yellow-tournesol-975-75-hover: #fce086;
  --yellow-tournesol-975-75-active: #f5d24b;
  --yellow-tournesol-950-100: #feecc2;
  --yellow-tournesol-950-100-hover: #fbd335;
  --yellow-tournesol-950-100-active: #e6c130;
  --yellow-tournesol-sun-407-moon-922: #716043;
  --yellow-tournesol-sun-407-moon-922-hover: #a28a62;
  --yellow-tournesol-sun-407-moon-922-active: #ba9f72;
  --yellow-tournesol-925-125: #fde39c;
  --yellow-tournesol-925-125-hover: #e9c53b;
  --yellow-tournesol-925-125-active: #d3b235;
  --yellow-tournesol-main-731: #c8aa39;
  --yellow-tournesol-850-200: #efcb3a;
  --yellow-moutarde-975-75: #fef5e8;
  --yellow-moutarde-975-75-hover: #fcdca3;
  --yellow-moutarde-975-75-active: #fbcd64;
  --yellow-moutarde-950-100: #feebd0;
  --yellow-moutarde-950-100-hover: #fdcd6d;
  --yellow-moutarde-950-100-active: #f4be30;
  --yellow-moutarde-sun-348-moon-860: #695240;
  --yellow-moutarde-sun-348-moon-860-hover: #9b7b61;
  --yellow-moutarde-sun-348-moon-860-active: #b58f72;
  --yellow-moutarde-925-125: #fde2b5;
  --yellow-moutarde-925-125-hover: #f6c43c;
  --yellow-moutarde-925-125-active: #dfb135;
  --yellow-moutarde-main-679: #c3992a;
  --yellow-moutarde-850-200: #fcc63a;
  --orange-terre-battue-975-75: #fef4f2;
  --orange-terre-battue-975-75-hover: #fcd8d0;
  --orange-terre-battue-975-75-active: #fac5b8;
  --orange-terre-battue-950-100: #fee9e5;
  --orange-terre-battue-950-100-hover: #fdc6ba;
  --orange-terre-battue-950-100-active: #fcb09e;
  --orange-terre-battue-sun-370-moon-672: #755348;
  --orange-terre-battue-sun-370-moon-672-hover: #ab7b6b;
  --orange-terre-battue-sun-370-moon-672-active: #c68f7d;
  --orange-terre-battue-925-125: #fddfd8;
  --orange-terre-battue-925-125-hover: #fbb8a5;
  --orange-terre-battue-925-125-active: #faa184;
  --orange-terre-battue-main-645: #e4794a;
  --orange-terre-battue-850-200: #fcc0b0;
  --brown-cafe-creme-975-75: #fbf6ed;
  --brown-cafe-creme-975-75-hover: #f2deb6;
  --brown-cafe-creme-975-75-active: #eacf91;
  --brown-cafe-creme-950-100: #f7ecdb;
  --brown-cafe-creme-950-100-hover: #edce94;
  --brown-cafe-creme-950-100-active: #dabd84;
  --brown-cafe-creme-sun-383-moon-885: #685c48;
  --brown-cafe-creme-sun-383-moon-885-hover: #97866a;
  --brown-cafe-creme-sun-383-moon-885-active: #ae9b7b;
  --brown-cafe-creme-925-125: #f4e3c7;
  --brown-cafe-creme-925-125-hover: #e1c386;
  --brown-cafe-creme-925-125-active: #ccb078;
  --brown-cafe-creme-main-782: #d1b781;
  --brown-cafe-creme-850-200: #e7ca8e;
  --brown-caramel-975-75: #fbf5f2;
  --brown-caramel-975-75-hover: #f1dbcf;
  --brown-caramel-975-75-active: #ecc9b5;
  --brown-caramel-950-100: #f7ebe5;
  --brown-caramel-950-100-hover: #eccbb9;
  --brown-caramel-950-100-active: #e6b79a;
  --brown-caramel-sun-425-moon-901: #845d48;
  --brown-caramel-sun-425-moon-901-hover: #bb8568;
  --brown-caramel-sun-425-moon-901-active: #d69978;
  --brown-caramel-925-125: #f3e2d9;
  --brown-caramel-925-125-hover: #e7bea6;
  --brown-caramel-925-125-active: #e1a982;
  --brown-caramel-main-648: #c08c65;
  --brown-caramel-850-200: #eac7b2;
  --brown-opera-975-75: #fbf5f2;
  --brown-opera-975-75-hover: #f1dbcf;
  --brown-opera-975-75-active: #ecc9b5;
  --brown-opera-950-100: #f7ece4;
  --brown-opera-950-100-hover: #eccdb3;
  --brown-opera-950-100-active: #e6ba90;
  --brown-opera-sun-395-moon-820: #745b47;
  --brown-opera-sun-395-moon-820-hover: #a78468;
  --brown-opera-sun-395-moon-820-active: #c09979;
  --brown-opera-925-125: #f3e2d7;
  --brown-opera-925-125-hover: #e7bfa0;
  --brown-opera-925-125-active: #deaa7e;
  --brown-opera-main-680: #bd987a;
  --brown-opera-850-200: #eac7ad;
  --beige-gris-galet-975-75: #f9f6f2;
  --beige-gris-galet-975-75-hover: #eadecd;
  --beige-gris-galet-975-75-active: #e1ceb1;
  --beige-gris-galet-950-100: #f3ede5;
  --beige-gris-galet-950-100-hover: #e1d0b5;
  --beige-gris-galet-950-100-active: #d1bea2;
  --beige-gris-galet-sun-407-moon-821: #6a6156;
  --beige-gris-galet-sun-407-moon-821-hover: #988b7c;
  --beige-gris-galet-sun-407-moon-821-active: #afa08f;
  --beige-gris-galet-925-125: #eee4d9;
  --beige-gris-galet-925-125-hover: #dbc3a4;
  --beige-gris-galet-925-125-active: #c6b094;
  --beige-gris-galet-main-702: #aea397;
  --beige-gris-galet-850-200: #e0cab0;
  box-sizing: border-box;
  --scrollbar-width: 0;
  --ground: 0;
  --shadow-color: rgba(0, 0, 18, 0.16);
  --raised-shadow: 0 1px 3px var(--shadow-color);
  --overlap-shadow: 0 2px 6px var(--shadow-color);
  --lifted-shadow: 0 3px 9px var(--shadow-color);
}

[href] {
  background-image: var(--underline-img), var(--underline-img);
  background-position: var(--underline-x) 100%, var(--underline-x) calc(100% - var(--underline-thickness));
  background-repeat: no-repeat, no-repeat;
  transition: background-size 0s;
  background-size: var(--underline-hover-width) calc(var(--underline-thickness) * 2), var(--underline-idle-width) var(--underline-thickness);
}

[target=_blank]::after {
  flex: 0 0 auto;
  display: inline-block;
  vertical-align: calc((0.75em - var(--icon-size)) * 0.5);
  background-color: currentColor;
  width: var(--icon-size);
  height: var(--icon-size);
  -webkit-mask-size: 100% 100%;
  mask-size: 100% 100%;
  --icon-size: 1rem;
  -webkit-mask-image: url(&quot;../icons/system/external-link-line.svg&quot;);
  mask-image: url(&quot;../icons/system/external-link-line.svg&quot;);
  content: var(--external-link-content);
  margin-left: 0.25rem;
}

[target=_blank][class^=fr-icon-]::after,
[target=_blank][class*=&quot; fr-icon-&quot;]::after,
[target=_blank][class^=fr-fi-]::after,
[target=_blank][class*=&quot; fr-fi-&quot;]::after {
  flex: 0 0 auto;
  display: inline-block;
  vertical-align: calc((0.75em - var(--icon-size)) * 0.5);
  background-color: currentColor;
  width: var(--icon-size);
  height: var(--icon-size);
  -webkit-mask-size: 100% 100%;
  mask-size: 100% 100%;
  --icon-size: 1rem;
  -webkit-mask-image: url(&quot;../icons/system/external-link-line.svg&quot;);
  mask-image: url(&quot;../icons/system/external-link-line.svg&quot;);
  content: var(--external-link-content);
  margin-left: 0.25rem;
}

form[target=_blank]::after {
  content: none;
}

.fr-raw-link {
  --text-decoration: none;
}

.fr-raw-link[href],
.fr-raw-link [href] {
  --underline-img: none;
  --external-link-content: none;
}

.fr-reset-link {
  --text-decoration: underline;
}

.fr-reset-link[href],
.fr-reset-link [href] {
  --underline-img: none;
  text-underline-offset: 2px;
}

button {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  border: none;
  margin: 0;
  color: inherit;
  background-color: transparent;
  font-family: inherit;
  font-size: inherit;
}

input,
select,
textarea {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  font-family: &quot;Marianne&quot;, arial, sans-serif;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  -webkit-text-size-adjust: 100%;
  border-radius: 0;
  border: 0;
  background-color: transparent;
  margin: 0;
}

input[type=search] {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

input[type=checkbox],
input[type=radio],
input[type=range] {
  -webkit-appearance: auto;
  -moz-appearance: auto;
  appearance: auto;
}

input::-webkit-contacts-auto-fill-button,
input::-webkit-credentials-auto-fill-button {
  margin-left: 1rem;
  margin-right: -1px;
  width: 1.25rem;
  height: 1.25rem;
  -webkit-mask-size: 1.25rem 1.25rem;
}

input[type=range]:focus::-webkit-slider-thumb {
  outline-offset: 2px;
  outline-width: 2px;
  outline-color: #0a76f6;
  outline-style: solid;
}

input[type=range]:focus::-moz-range-thumb {
  outline-offset: 2px;
  outline-width: 2px;
  outline-color: #0a76f6;
  outline-style: solid;
}

input[type=range]:focus::-ms-thumb {
  outline-offset: 2px;
  outline-width: 2px;
  outline-color: #0a76f6;
  outline-style: solid;
}

a:focus,
button:focus,
input:focus,
input[type=checkbox]:focus + label::before,
input[type=radio]:focus + label::before,
input[type=button]:focus,
input[type=image]:focus,
input[type=reset]:focus,
input[type=submit]:focus,
select:focus,
textarea:focus,
[tabindex]:focus,
video:focus[controls],
audio:focus[controls],
[contenteditable]:not([contenteditable=false]):focus,
details:focus,
details &gt; summary:first-of-type:focus {
  outline-offset: 2px;
  outline-width: 2px;
  outline-color: #0a76f6;
  outline-style: solid;
}

input[type=range]:focus:not(:focus-visible)::-webkit-slider-thumb {
  outline-style: none;
}

input[type=range]:focus:not(:focus-visible)::-moz-range-thumb {
  outline-style: none;
}

input[type=range]:focus:not(:focus-visible)::-ms-thumb {
  outline-style: none;
}

a:focus:not(:focus-visible),
button:focus:not(:focus-visible),
input:focus:not(:focus-visible),
input[type=checkbox]:focus:not(:focus-visible) + label::before,
input[type=radio]:focus:not(:focus-visible) + label::before,
input[type=button]:focus:not(:focus-visible),
input[type=image]:focus:not(:focus-visible),
input[type=reset]:focus:not(:focus-visible),
input[type=submit]:focus:not(:focus-visible),
select:focus:not(:focus-visible),
textarea:focus:not(:focus-visible),
[tabindex]:focus:not(:focus-visible),
video:focus:not(:focus-visible)[controls],
audio:focus:not(:focus-visible)[controls],
[contenteditable]:not([contenteditable=false]):focus:not(:focus-visible),
details:focus:not(:focus-visible),
details &gt; summary:first-of-type:focus:not(:focus-visible) {
  outline-style: none;
}

input[type=range]:focus-visible::-webkit-slider-thumb {
  outline-style: solid;
}

input[type=range]:focus-visible::-moz-range-thumb {
  outline-style: solid;
}

input[type=range]:focus-visible::-ms-thumb {
  outline-style: solid;
}

a:focus-visible,
button:focus-visible,
input:focus-visible,
input[type=checkbox]:focus-visible + label::before,
input[type=radio]:focus-visible + label::before,
input[type=button]:focus-visible,
input[type=image]:focus-visible,
input[type=reset]:focus-visible,
input[type=submit]:focus-visible,
select:focus-visible,
textarea:focus-visible,
[tabindex]:focus-visible,
video:focus-visible[controls],
audio:focus-visible[controls],
[contenteditable]:not([contenteditable=false]):focus-visible,
details:focus-visible,
details &gt; summary:first-of-type:focus-visible {
  outline-style: solid;
}

button,
input[type=button],
input[type=image],
input[type=reset],
input[type=submit] {
  --hover-tint: var(--hover);
  --active-tint: var(--active);
}

a,
button,
input[type=checkbox],
input[type=checkbox] + label,
input[type=radio],
input[type=radio] + label,
input[type=file],
input[type=range],
input[type=button],
input[type=image],
input[type=reset],
input[type=submit],
select,
video[controls],
audio[controls],
details,
details &gt; summary:first-of-type {
  cursor: pointer;
}

input[type=range]:disabled::-webkit-slider-thumb,
input[type=range]:disabled::-webkit-slider-thumb:active {
  cursor: not-allowed;
}

input[type=range]:disabled::-moz-range-thumb,
input[type=range]:disabled::-moz-range-thumb:active {
  cursor: not-allowed;
}

input[type=range]:disabled::-ms-thumb,
input[type=range]:disabled::-ms-thumb:active {
  cursor: not-allowed;
}

a:not([href]),
button:disabled,
input:disabled,
input[type=checkbox]:disabled,
input[type=checkbox]:disabled + label,
input[type=radio]:disabled,
input[type=radio]:disabled + label,
input[type=file]:disabled,
input[type=range]:disabled,
input[type=button]:disabled,
input[type=image]:disabled,
input[type=reset]:disabled,
input[type=submit]:disabled,
select:disabled,
textarea:disabled,
video:not([href])[controls],
audio:not([href])[controls] {
  cursor: not-allowed;
}

input[type=range]::-webkit-slider-thumb {
  cursor: grab;
}

input[type=range]::-moz-range-thumb {
  cursor: grab;
}

input[type=range]::-ms-thumb {
  cursor: grab;
}

input[type=range]::-webkit-slider-thumb:active {
  cursor: grabbing;
}

input[type=range]::-moz-range-thumb:active {
  cursor: grabbing;
}

input[type=range]::-ms-thumb:active {
  cursor: grabbing;
}

/**
 * Override de l&#x27;opacité chrome sur un élément disabled
 */
a:not([href]),
button:disabled,
input:disabled,
input[type=checkbox]:disabled,
input[type=checkbox]:disabled + label,
input[type=radio]:disabled,
input[type=radio]:disabled + label,
textarea:disabled,
video:not([href]),
audio:not([href]) {
  opacity: 1;
  color: var(--text-disabled-grey);
}

.fr-enlarge-link {
  position: relative;
}

.fr-enlarge-link a {
  background-image: none;
  outline-width: 0;
}

.fr-enlarge-link a::before {
  content: &quot;&quot;;
  display: block;
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
  outline-offset: 2px;
  outline-style: inherit;
  outline-color: inherit;
  outline-width: 2px;
  z-index: 1;
}

.fr-transition-none {
  transition: none !important;
}

/**
 * Déclaration des fontes
 */
@font-face {
  font-family: Marianne;
  src: url(&quot;../fonts/Marianne-Light.woff2&quot;) format(&quot;woff2&quot;), url(&quot;../fonts/Marianne-Light.woff&quot;) format(&quot;woff&quot;);
  font-weight: 300;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: Marianne;
  src: url(&quot;../fonts/Marianne-Light_Italic.woff2&quot;) format(&quot;woff2&quot;), url(&quot;../fonts/Marianne-Light_Italic.woff&quot;) format(&quot;woff&quot;);
  font-weight: 300;
  font-style: italic;
  font-display: swap;
}
@font-face {
  font-family: Marianne;
  src: url(&quot;../fonts/Marianne-Regular.woff2&quot;) format(&quot;woff2&quot;), url(&quot;../fonts/Marianne-Regular.woff&quot;) format(&quot;woff&quot;);
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: Marianne;
  src: url(&quot;../fonts/Marianne-Regular_Italic.woff2&quot;) format(&quot;woff2&quot;), url(&quot;../fonts/Marianne-Regular_Italic.woff&quot;) format(&quot;woff&quot;);
  font-weight: 400;
  font-style: italic;
  font-display: swap;
}
@font-face {
  font-family: Marianne;
  src: url(&quot;../fonts/Marianne-Medium.woff2&quot;) format(&quot;woff2&quot;), url(&quot;../fonts/Marianne-Medium.woff&quot;) format(&quot;woff&quot;);
  font-weight: 500;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: Marianne;
  src: url(&quot;../fonts/Marianne-Medium_Italic.woff2&quot;) format(&quot;woff2&quot;), url(&quot;../fonts/Marianne-Medium_Italic.woff&quot;) format(&quot;woff&quot;);
  font-weight: 500;
  font-style: italic;
  font-display: swap;
}
@font-face {
  font-family: Marianne;
  src: url(&quot;../fonts/Marianne-Bold.woff2&quot;) format(&quot;woff2&quot;), url(&quot;../fonts/Marianne-Bold.woff&quot;) format(&quot;woff&quot;);
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: Marianne;
  src: url(&quot;../fonts/Marianne-Bold_Italic.woff2&quot;) format(&quot;woff2&quot;), url(&quot;../fonts/Marianne-Bold_Italic.woff&quot;) format(&quot;woff&quot;);
  font-weight: 700;
  font-style: italic;
  font-display: swap;
}
@font-face {
  font-family: Spectral;
  src: url(&quot;../fonts/Spectral-Regular.woff2&quot;) format(&quot;woff2&quot;), url(&quot;../fonts/Spectral-Regular.woff&quot;) format(&quot;woff&quot;);
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: Spectral;
  src: url(&quot;../fonts/Spectral-ExtraBold.woff2&quot;) format(&quot;woff2&quot;), url(&quot;../fonts/Spectral-ExtraBold.woff&quot;) format(&quot;woff&quot;);
  font-weight: 900;
  font-style: normal;
  font-display: swap;
}
h6 {
  font-weight: 700;
  font-size: 1.125rem;
  line-height: 1.5rem;
  margin: var(--title-spacing);
}

h5 {
  font-weight: 700;
  font-size: 1.25rem;
  line-height: 1.75rem;
  margin: var(--title-spacing);
}

h4 {
  font-weight: 700;
  font-size: 1.375rem;
  line-height: 1.75rem;
  margin: var(--title-spacing);
}

h3 {
  font-weight: 700;
  font-size: 1.5rem;
  line-height: 2rem;
  margin: var(--title-spacing);
}

h2 {
  font-weight: 700;
  font-size: 1.75rem;
  line-height: 2.25rem;
  margin: var(--title-spacing);
}

h1 {
  font-weight: 700;
  font-size: 2rem;
  line-height: 2.5rem;
  margin: var(--title-spacing);
}

p {
  font-size: 1rem;
  line-height: 1.5rem;
  margin: var(--text-spacing);
}

ul,
ol,
dl {
  margin: 0;
  padding: 0;
  margin-block-start: var(--xl-block);
  margin-block-end: var(--xl-block);
  --xl-size: var(--xl-base);
}

ul {
  list-style-type: var(--ul-type);
  padding-inline-start: var(--ul-start);
}

ul &gt; li::marker {
  font-size: calc(var(--xl-size) * 0.9);
}

ol {
  list-style-type: var(--ol-type);
  padding-inline-start: var(--ol-start);
  counter-reset: li-counter;
}

ol &gt; li {
  counter-increment: li-counter;
}

ol &gt; li::marker {
  content: var(--ol-content);
  font-size: var(--xl-size);
  font-weight: bold;
}

dl,
dd {
  margin: 0;
  padding-inline-start: var(--ul-start);
}

li,
dd,
dt {
  --xl-base: calc(var(--xl-size) * 0.9);
  padding-bottom: var(--li-bottom);
}

.fr-raw-list {
  --ul-type: none;
  --ol-type: none;
  --ul-start: 0;
  --ol-start: 0;
  --xl-block: 0;
  --li-bottom: 0;
  --ol-content: none;
}

.fr-list {
  --ul-type: disc;
  --ol-type: decimal;
  --ul-start: 1rem;
  --ol-start: 1.5rem;
  --xl-block: 0.5rem;
  --li-bottom: 0.25rem;
  --xl-base: 1em;
  --ol-content: counters(li-counter, &quot;.&quot;) &quot;.  &quot;;
}

sub {
  line-height: 1;
}

sup {
  line-height: 1;
}

.fr-text--light {
  font-weight: 300 !important;
}

.fr-text--regular {
  font-weight: 400 !important;
}

.fr-text--bold {
  font-weight: 700 !important;
}

.fr-text--heavy {
  font-weight: 900 !important;
}

.fr-h6 {
  font-weight: 700 !important;
  font-size: 1.125rem !important;
  line-height: 1.5rem !important;
  margin: var(--title-spacing);
}

.fr-h5 {
  font-weight: 700 !important;
  font-size: 1.25rem !important;
  line-height: 1.75rem !important;
  margin: var(--title-spacing);
}

.fr-h4 {
  font-weight: 700 !important;
  font-size: 1.375rem !important;
  line-height: 1.75rem !important;
  margin: var(--title-spacing);
}

.fr-h3 {
  font-weight: 700 !important;
  font-size: 1.5rem !important;
  line-height: 2rem !important;
  margin: var(--title-spacing);
}

.fr-h2 {
  font-weight: 700 !important;
  font-size: 1.75rem !important;
  line-height: 2.25rem !important;
  margin: var(--title-spacing);
}

.fr-h1 {
  font-weight: 700 !important;
  font-size: 2rem !important;
  line-height: 2.5rem !important;
  margin: var(--title-spacing);
}

.fr-display--xs {
  font-weight: 700 !important;
  font-size: 2.5rem !important;
  line-height: 3rem !important;
  margin: var(--display-spacing);
}

.fr-display--sm {
  font-weight: 700 !important;
  font-size: 3rem !important;
  line-height: 3.5rem !important;
  margin: var(--display-spacing);
}

.fr-display--md {
  font-weight: 700 !important;
  font-size: 3.5rem !important;
  line-height: 4rem !important;
  margin: var(--display-spacing);
}

.fr-display--lg {
  font-weight: 700 !important;
  font-size: 4rem !important;
  line-height: 4.5rem !important;
  margin: var(--display-spacing);
}

.fr-display--xl {
  font-weight: 700 !important;
  font-size: 4.5rem !important;
  line-height: 5rem !important;
  margin: var(--display-spacing);
}

.fr-text--alt {
  font-family: &quot;Spectral&quot;, georgia, serif !important;
}

.fr-text--xs {
  font-size: 0.75rem !important;
  line-height: 1.25rem !important;
  margin: var(--text-spacing);
}

.fr-text--sm {
  font-size: 0.875rem !important;
  line-height: 1.5rem !important;
  margin: var(--text-spacing);
}

.fr-text--md {
  font-size: 1rem !important;
  line-height: 1.5rem !important;
  margin: var(--text-spacing);
}

.fr-text--lg {
  font-size: 1.125rem !important;
  line-height: 1.75rem !important;
  margin: var(--text-spacing);
}

.fr-text--xl,
.fr-text--lead {
  font-size: 1.25rem !important;
  line-height: 2rem !important;
  margin: var(--text-spacing);
}

*,
*::before,
*::after {
  box-sizing: inherit;
}

body {
  font-family: &quot;Marianne&quot;, arial, sans-serif;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  -webkit-text-size-adjust: 100%;
  margin: 0;
  padding: 0;
  font-size: 1rem;
  line-height: 1.5rem;
  background-color: var(--background-default-grey);
  --idle: transparent;
  --hover: var(--background-default-grey-hover);
  --active: var(--background-default-grey-active);
  color: var(--text-default-grey);
}

[class^=fr-icon-]::before,
[class^=fr-icon-]::after,
[class*=&quot; fr-icon-&quot;]::before,
[class*=&quot; fr-icon-&quot;]::after,
[class^=fr-fi-]::before,
[class^=fr-fi-]::after,
[class*=&quot; fr-fi-&quot;]::before,
[class*=&quot; fr-fi-&quot;]::after {
  flex: 0 0 auto;
  display: inline-block;
  vertical-align: calc((0.75em - var(--icon-size)) * 0.5);
  background-color: currentColor;
  width: var(--icon-size);
  height: var(--icon-size);
  -webkit-mask-size: 100% 100%;
  mask-size: 100% 100%;
  --icon-size: 1.5rem;
}

[class^=fr-icon-]::before,
[class*=&quot; fr-icon-&quot;]::before,
[class^=fr-fi-]::before,
[class*=&quot; fr-fi-&quot;]::before {
  content: &quot;&quot;;
}

.fr-icon--xs::before,
.fr-icon--xs::after {
  --icon-size: 0.75rem;
}

.fr-icon--sm::before,
.fr-icon--sm::after {
  --icon-size: 1rem;
}

.fr-icon--md::before,
.fr-icon--md::after {
  --icon-size: 1.5rem;
}

.fr-icon--lg::before,
.fr-icon--lg::after {
  --icon-size: 2rem;
}

.fr-hidden {
  display: none !important;
}

.fr-unhidden {
  display: inherit !important;
}

/**
* Fixe le scroll en arrière plan
*/
:root body {
  border-right: var(--scrollbar-width) solid transparent;
}

:root[data-fr-scrolling] body {
  overflow: hidden;
  bottom: 0;
  left: 0;
  position: fixed;
  right: 0;
  top: 0;
}

.fr-sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap; /* added line */
  border: 0;
  display: block;
}

hr {
  padding: var(--text-spacing);
  margin: 0;
  border: 0;
  display: block;
  background-size: 100% 1px;
  background-repeat: no-repeat;
  background-position: 0 0;
  background-image: linear-gradient(0deg, var(--border-default-grey), var(--border-default-grey));
}

.fr-hr {
  padding: var(--text-spacing);
  margin: 0;
  border: 0;
  display: block;
  background-size: 100% 1px;
  background-repeat: no-repeat;
  background-position: 0 0;
  background-image: linear-gradient(0deg, var(--border-default-grey), var(--border-default-grey));
}

.fr-hr--sm {
  width: 10rem;
  margin-left: auto;
  margin-right: auto;
}

.fr-hr-or {
  font-size: 0.875rem;
  line-height: 1.5rem;
  text-transform: uppercase;
  font-weight: 700;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  flex-wrap: nowrap;
}

.fr-hr-or::before,
.fr-hr-or::after {
  content: &quot;&quot;;
  display: inline-flex;
  height: 1px;
  width: 100%;
  background-color: var(--border-default-grey);
  --idle: transparent;
  --hover: var(--border-default-grey-hover);
  --active: var(--border-default-grey-active);
}

.fr-hr-or::before {
  margin-right: 0.75rem;
}

.fr-hr-or::after {
  margin-left: 0.75rem;
}

.fr-ellipsis {
  display: inline !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

iframe {
  border: 0;
}

.fr-fluid-img {
  max-width: 100%;
  height: auto;
}

@supports (aspect-ratio: 16/9) {
  .fr-ratio-32x9 {
    aspect-ratio: 3.5555555556 !important;
  }
  .fr-ratio-16x9 {
    aspect-ratio: 1.7777777778 !important;
  }
  .fr-ratio-3x2 {
    aspect-ratio: 1.5 !important;
  }
  .fr-ratio-4x3 {
    aspect-ratio: 1.3333333333 !important;
  }
  .fr-ratio-1x1 {
    aspect-ratio: 1 !important;
  }
  .fr-ratio-3x4 {
    aspect-ratio: 0.75 !important;
  }
  .fr-ratio-2x3 {
    aspect-ratio: 0.6666666667 !important;
  }
}
[class^=fr-ratio],
[class*=&quot; fr-ratio&quot;] {
  -o-object-fit: cover;
     object-fit: cover;
  -o-object-position: 50% 50%;
     object-position: 50% 50%;
  width: 100%;
}

iframe[class^=fr-ratio],
iframe[class*=&quot; fr-ratio&quot;] {
  -o-object-fit: fill;
     object-fit: fill;
}

.fr-responsive-img {
  width: 100%;
  height: auto;
}

.fr-responsive-vid {
  position: relative;
  width: 100%;
  aspect-ratio: 1.7777777778;
  display: block;
}

.fr-responsive-vid__player {
  width: 100%;
  height: 100%;
  display: block;
  border: 0;
}

.fr-responsive-vid &gt; .fr-consent-placeholder {
  -o-object-fit: cover;
     object-fit: cover;
  -o-object-position: 50% 50%;
     object-position: 50% 50%;
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.fr-grid-row {
  display: flex;
  flex-wrap: wrap;
  margin: 0;
  padding: 0;
}

.fr-grid-row--top {
  align-items: flex-start;
}

.fr-grid-row--bottom {
  align-items: flex-end;
}

.fr-grid-row--middle {
  align-items: center;
}

.fr-grid-row--left {
  justify-content: flex-start;
}

.fr-grid-row--right {
  justify-content: flex-end;
}

.fr-grid-row--center {
  justify-content: center;
}

.fr-col--top {
  align-self: flex-start;
}

.fr-col--bottom {
  align-self: flex-end;
}

.fr-col--middle {
  align-self: center;
}

.fr-container {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding-left: 1rem;
  padding-right: 1rem;
}

.fr-container--fluid {
  padding-left: 0;
  padding-right: 0;
  max-width: none;
  overflow: hidden;
}

.fr-grid-row--gutters {
  margin: -0.5rem;
}

.fr-grid-row--gutters &gt; [class^=fr-col-],
.fr-grid-row--gutters &gt; [class*=&quot; fr-col-&quot;],
.fr-grid-row--gutters &gt; .fr-col {
  padding: 0.5rem;
}

.fr-grid-row--no-gutters {
  margin: 0;
}

.fr-grid-row--no-gutters &gt; [class^=fr-col-],
.fr-grid-row--no-gutters &gt; [class*=&quot; fr-col-&quot;],
.fr-grid-row--no-gutters &gt; .fr-col {
  padding: 0;
}

.fr-col {
  flex: 1;
}

.fr-col-1 {
  flex: 0 0 8.3333333333%;
  width: 8.3333333333%;
  max-width: 8.3333333333%;
}

.fr-col-offset-1:not(.fr-col-offset-1--right) {
  margin-left: 8.3333333333%;
}

.fr-col-offset-1--right {
  margin-right: 8.3333333333%;
}

.fr-col-2 {
  flex: 0 0 16.6666666667%;
  width: 16.6666666667%;
  max-width: 16.6666666667%;
}

.fr-col-offset-2:not(.fr-col-offset-2--right) {
  margin-left: 16.6666666667%;
}

.fr-col-offset-2--right {
  margin-right: 16.6666666667%;
}

.fr-col-3 {
  flex: 0 0 25%;
  width: 25%;
  max-width: 25%;
}

.fr-col-offset-3:not(.fr-col-offset-3--right) {
  margin-left: 25%;
}

.fr-col-offset-3--right {
  margin-right: 25%;
}

.fr-col-4 {
  flex: 0 0 33.3333333333%;
  width: 33.3333333333%;
  max-width: 33.3333333333%;
}

.fr-col-offset-4:not(.fr-col-offset-4--right) {
  margin-left: 33.3333333333%;
}

.fr-col-offset-4--right {
  margin-right: 33.3333333333%;
}

.fr-col-5 {
  flex: 0 0 41.6666666667%;
  width: 41.6666666667%;
  max-width: 41.6666666667%;
}

.fr-col-offset-5:not(.fr-col-offset-5--right) {
  margin-left: 41.6666666667%;
}

.fr-col-offset-5--right {
  margin-right: 41.6666666667%;
}

.fr-col-6 {
  flex: 0 0 50%;
  width: 50%;
  max-width: 50%;
}

.fr-col-offset-6:not(.fr-col-offset-6--right) {
  margin-left: 50%;
}

.fr-col-offset-6--right {
  margin-right: 50%;
}

.fr-col-7 {
  flex: 0 0 58.3333333333%;
  width: 58.3333333333%;
  max-width: 58.3333333333%;
}

.fr-col-offset-7:not(.fr-col-offset-7--right) {
  margin-left: 58.3333333333%;
}

.fr-col-offset-7--right {
  margin-right: 58.3333333333%;
}

.fr-col-8 {
  flex: 0 0 66.6666666667%;
  width: 66.6666666667%;
  max-width: 66.6666666667%;
}

.fr-col-offset-8:not(.fr-col-offset-8--right) {
  margin-left: 66.6666666667%;
}

.fr-col-offset-8--right {
  margin-right: 66.6666666667%;
}

.fr-col-9 {
  flex: 0 0 75%;
  width: 75%;
  max-width: 75%;
}

.fr-col-offset-9:not(.fr-col-offset-9--right) {
  margin-left: 75%;
}

.fr-col-offset-9--right {
  margin-right: 75%;
}

.fr-col-10 {
  flex: 0 0 83.3333333333%;
  width: 83.3333333333%;
  max-width: 83.3333333333%;
}

.fr-col-offset-10:not(.fr-col-offset-10--right) {
  margin-left: 83.3333333333%;
}

.fr-col-offset-10--right {
  margin-right: 83.3333333333%;
}

.fr-col-11 {
  flex: 0 0 91.6666666667%;
  width: 91.6666666667%;
  max-width: 91.6666666667%;
}

.fr-col-offset-11:not(.fr-col-offset-11--right) {
  margin-left: 91.6666666667%;
}

.fr-col-offset-11--right {
  margin-right: 91.6666666667%;
}

.fr-col-12 {
  flex: 0 0 100%;
  width: 100%;
  max-width: 100%;
}

.fr-col-offset-12:not(.fr-col-offset-12--right) {
  margin-left: 100%;
}

.fr-col-offset-12--right {
  margin-right: 100%;
}

.fr-no-before::before {
  content: none;
}

.fr-no-after::after {
  content: none;
}

.fr-collapse {
  --collapse-max-height: 0;
  --collapse: -99999px;
  --collapser: &quot;&quot;;
  overflow: hidden;
  transition: visibility 0.3s;
  max-height: 0;
  max-height: var(--collapse-max-height);
}

.fr-collapse::before {
  display: block;
  content: &quot;&quot;;
  content: var(--collapser);
  transition: margin-top 0.3s;
  margin-top: 0;
}

.fr-collapse:not(.fr-collapse--expanded) {
  visibility: hidden;
}

.fr-collapse:not(.fr-collapse--expanded)::before {
  margin-top: -99999px;
  margin-top: var(--collapse);
}

.fr-m-n8v,
.fr-m-n4w {
  margin: -2rem !important;
}

.fr-ml-n8v,
.fr-ml-n4w,
.fr-mx-n8v,
.fr-mx-n4w {
  margin-left: -2rem !important;
}

.fr-mr-n8v,
.fr-mr-n4w,
.fr-mx-n8v,
.fr-mx-n4w {
  margin-right: -2rem !important;
}

.fr-mt-n8v,
.fr-mt-n4w,
.fr-my-n8v,
.fr-my-n4w {
  margin-top: -2rem !important;
}

.fr-mb-n8v,
.fr-mb-n4w,
.fr-my-n8v,
.fr-my-n4w {
  margin-bottom: -2rem !important;
}

.fr-m-n7v {
  margin: -1.75rem !important;
}

.fr-ml-n7v,
.fr-mx-n7v {
  margin-left: -1.75rem !important;
}

.fr-mr-n7v,
.fr-mx-n7v {
  margin-right: -1.75rem !important;
}

.fr-mt-n7v,
.fr-my-n7v {
  margin-top: -1.75rem !important;
}

.fr-mb-n7v,
.fr-my-n7v {
  margin-bottom: -1.75rem !important;
}

.fr-m-n6v,
.fr-m-n3w {
  margin: -1.5rem !important;
}

.fr-ml-n6v,
.fr-ml-n3w,
.fr-mx-n6v,
.fr-mx-n3w {
  margin-left: -1.5rem !important;
}

.fr-mr-n6v,
.fr-mr-n3w,
.fr-mx-n6v,
.fr-mx-n3w {
  margin-right: -1.5rem !important;
}

.fr-mt-n6v,
.fr-mt-n3w,
.fr-my-n6v,
.fr-my-n3w {
  margin-top: -1.5rem !important;
}

.fr-mb-n6v,
.fr-mb-n3w,
.fr-my-n6v,
.fr-my-n3w {
  margin-bottom: -1.5rem !important;
}

.fr-m-n5v {
  margin: -1.25rem !important;
}

.fr-ml-n5v,
.fr-mx-n5v {
  margin-left: -1.25rem !important;
}

.fr-mr-n5v,
.fr-mx-n5v {
  margin-right: -1.25rem !important;
}

.fr-mt-n5v,
.fr-my-n5v {
  margin-top: -1.25rem !important;
}

.fr-mb-n5v,
.fr-my-n5v {
  margin-bottom: -1.25rem !important;
}

.fr-m-n4v,
.fr-m-n2w {
  margin: -1rem !important;
}

.fr-ml-n4v,
.fr-ml-n2w,
.fr-mx-n4v,
.fr-mx-n2w {
  margin-left: -1rem !important;
}

.fr-mr-n4v,
.fr-mr-n2w,
.fr-mx-n4v,
.fr-mx-n2w {
  margin-right: -1rem !important;
}

.fr-mt-n4v,
.fr-mt-n2w,
.fr-my-n4v,
.fr-my-n2w {
  margin-top: -1rem !important;
}

.fr-mb-n4v,
.fr-mb-n2w,
.fr-my-n4v,
.fr-my-n2w {
  margin-bottom: -1rem !important;
}

.fr-m-n3v {
  margin: -0.75rem !important;
}

.fr-ml-n3v,
.fr-mx-n3v {
  margin-left: -0.75rem !important;
}

.fr-mr-n3v,
.fr-mx-n3v {
  margin-right: -0.75rem !important;
}

.fr-mt-n3v,
.fr-my-n3v {
  margin-top: -0.75rem !important;
}

.fr-mb-n3v,
.fr-my-n3v {
  margin-bottom: -0.75rem !important;
}

.fr-m-n2v,
.fr-m-n1w {
  margin: -0.5rem !important;
}

.fr-ml-n2v,
.fr-ml-n1w,
.fr-mx-n2v,
.fr-mx-n1w {
  margin-left: -0.5rem !important;
}

.fr-mr-n2v,
.fr-mr-n1w,
.fr-mx-n2v,
.fr-mx-n1w {
  margin-right: -0.5rem !important;
}

.fr-mt-n2v,
.fr-mt-n1w,
.fr-my-n2v,
.fr-my-n1w {
  margin-top: -0.5rem !important;
}

.fr-mb-n2v,
.fr-mb-n1w,
.fr-my-n2v,
.fr-my-n1w {
  margin-bottom: -0.5rem !important;
}

.fr-m-n1v {
  margin: -0.25rem !important;
}

.fr-ml-n1v,
.fr-mx-n1v {
  margin-left: -0.25rem !important;
}

.fr-mr-n1v,
.fr-mx-n1v {
  margin-right: -0.25rem !important;
}

.fr-mt-n1v,
.fr-my-n1v {
  margin-top: -0.25rem !important;
}

.fr-mb-n1v,
.fr-my-n1v {
  margin-bottom: -0.25rem !important;
}

.fr-m-n1-5v {
  margin: -0.375rem !important;
}

.fr-ml-n1-5v,
.fr-mx-n1-5v {
  margin-left: -0.375rem !important;
}

.fr-mr-n1-5v,
.fr-mx-n1-5v {
  margin-right: -0.375rem !important;
}

.fr-mt-n1-5v,
.fr-my-n1-5v {
  margin-top: -0.375rem !important;
}

.fr-mb-n1-5v,
.fr-my-n1-5v {
  margin-bottom: -0.375rem !important;
}

.fr-m-0 {
  margin: 0 !important;
}

.fr-ml-0,
.fr-mx-0 {
  margin-left: 0 !important;
}

.fr-mr-0,
.fr-mx-0 {
  margin-right: 0 !important;
}

.fr-mt-0,
.fr-my-0 {
  margin-top: 0 !important;
}

.fr-mb-0,
.fr-my-0 {
  margin-bottom: 0 !important;
}

.fr-m-n0-5v {
  margin: -0.125rem !important;
}

.fr-ml-n0-5v,
.fr-mx-n0-5v {
  margin-left: -0.125rem !important;
}

.fr-mr-n0-5v,
.fr-mx-n0-5v {
  margin-right: -0.125rem !important;
}

.fr-mt-n0-5v,
.fr-my-n0-5v {
  margin-top: -0.125rem !important;
}

.fr-mb-n0-5v,
.fr-my-n0-5v {
  margin-bottom: -0.125rem !important;
}

.fr-m-0-5v {
  margin: 0.125rem !important;
}

.fr-ml-0-5v,
.fr-mx-0-5v {
  margin-left: 0.125rem !important;
}

.fr-mr-0-5v,
.fr-mx-0-5v {
  margin-right: 0.125rem !important;
}

.fr-mt-0-5v,
.fr-my-0-5v {
  margin-top: 0.125rem !important;
}

.fr-mb-0-5v,
.fr-my-0-5v {
  margin-bottom: 0.125rem !important;
}

.fr-m-1v {
  margin: 0.25rem !important;
}

.fr-ml-1v,
.fr-mx-1v {
  margin-left: 0.25rem !important;
}

.fr-mr-1v,
.fr-mx-1v {
  margin-right: 0.25rem !important;
}

.fr-mt-1v,
.fr-my-1v {
  margin-top: 0.25rem !important;
}

.fr-mb-1v,
.fr-my-1v {
  margin-bottom: 0.25rem !important;
}

.fr-m-1-5v {
  margin: 0.375rem !important;
}

.fr-ml-1-5v,
.fr-mx-1-5v {
  margin-left: 0.375rem !important;
}

.fr-mr-1-5v,
.fr-mx-1-5v {
  margin-right: 0.375rem !important;
}

.fr-mt-1-5v,
.fr-my-1-5v {
  margin-top: 0.375rem !important;
}

.fr-mb-1-5v,
.fr-my-1-5v {
  margin-bottom: 0.375rem !important;
}

.fr-m-2v,
.fr-m-1w {
  margin: 0.5rem !important;
}

.fr-ml-2v,
.fr-ml-1w,
.fr-mx-2v,
.fr-mx-1w {
  margin-left: 0.5rem !important;
}

.fr-mr-2v,
.fr-mr-1w,
.fr-mx-2v,
.fr-mx-1w {
  margin-right: 0.5rem !important;
}

.fr-mt-2v,
.fr-mt-1w,
.fr-my-2v,
.fr-my-1w {
  margin-top: 0.5rem !important;
}

.fr-mb-2v,
.fr-mb-1w,
.fr-my-2v,
.fr-my-1w {
  margin-bottom: 0.5rem !important;
}

.fr-m-3v {
  margin: 0.75rem !important;
}

.fr-ml-3v,
.fr-mx-3v {
  margin-left: 0.75rem !important;
}

.fr-mr-3v,
.fr-mx-3v {
  margin-right: 0.75rem !important;
}

.fr-mt-3v,
.fr-my-3v {
  margin-top: 0.75rem !important;
}

.fr-mb-3v,
.fr-my-3v {
  margin-bottom: 0.75rem !important;
}

.fr-m-4v,
.fr-m-2w {
  margin: 1rem !important;
}

.fr-ml-4v,
.fr-ml-2w,
.fr-mx-4v,
.fr-mx-2w {
  margin-left: 1rem !important;
}

.fr-mr-4v,
.fr-mr-2w,
.fr-mx-4v,
.fr-mx-2w {
  margin-right: 1rem !important;
}

.fr-mt-4v,
.fr-mt-2w,
.fr-my-4v,
.fr-my-2w {
  margin-top: 1rem !important;
}

.fr-mb-4v,
.fr-mb-2w,
.fr-my-4v,
.fr-my-2w {
  margin-bottom: 1rem !important;
}

.fr-m-5v {
  margin: 1.25rem !important;
}

.fr-ml-5v,
.fr-mx-5v {
  margin-left: 1.25rem !important;
}

.fr-mr-5v,
.fr-mx-5v {
  margin-right: 1.25rem !important;
}

.fr-mt-5v,
.fr-my-5v {
  margin-top: 1.25rem !important;
}

.fr-mb-5v,
.fr-my-5v {
  margin-bottom: 1.25rem !important;
}

.fr-m-6v,
.fr-m-3w {
  margin: 1.5rem !important;
}

.fr-ml-6v,
.fr-ml-3w,
.fr-mx-6v,
.fr-mx-3w {
  margin-left: 1.5rem !important;
}

.fr-mr-6v,
.fr-mr-3w,
.fr-mx-6v,
.fr-mx-3w {
  margin-right: 1.5rem !important;
}

.fr-mt-6v,
.fr-mt-3w,
.fr-my-6v,
.fr-my-3w {
  margin-top: 1.5rem !important;
}

.fr-mb-6v,
.fr-mb-3w,
.fr-my-6v,
.fr-my-3w {
  margin-bottom: 1.5rem !important;
}

.fr-m-7v {
  margin: 1.75rem !important;
}

.fr-ml-7v,
.fr-mx-7v {
  margin-left: 1.75rem !important;
}

.fr-mr-7v,
.fr-mx-7v {
  margin-right: 1.75rem !important;
}

.fr-mt-7v,
.fr-my-7v {
  margin-top: 1.75rem !important;
}

.fr-mb-7v,
.fr-my-7v {
  margin-bottom: 1.75rem !important;
}

.fr-m-8v,
.fr-m-4w {
  margin: 2rem !important;
}

.fr-ml-8v,
.fr-ml-4w,
.fr-mx-8v,
.fr-mx-4w {
  margin-left: 2rem !important;
}

.fr-mr-8v,
.fr-mr-4w,
.fr-mx-8v,
.fr-mx-4w {
  margin-right: 2rem !important;
}

.fr-mt-8v,
.fr-mt-4w,
.fr-my-8v,
.fr-my-4w {
  margin-top: 2rem !important;
}

.fr-mb-8v,
.fr-mb-4w,
.fr-my-8v,
.fr-my-4w {
  margin-bottom: 2rem !important;
}

.fr-m-9v {
  margin: 2.25rem !important;
}

.fr-ml-9v,
.fr-mx-9v {
  margin-left: 2.25rem !important;
}

.fr-mr-9v,
.fr-mx-9v {
  margin-right: 2.25rem !important;
}

.fr-mt-9v,
.fr-my-9v {
  margin-top: 2.25rem !important;
}

.fr-mb-9v,
.fr-my-9v {
  margin-bottom: 2.25rem !important;
}

.fr-m-10v,
.fr-m-5w {
  margin: 2.5rem !important;
}

.fr-ml-10v,
.fr-ml-5w,
.fr-mx-10v,
.fr-mx-5w {
  margin-left: 2.5rem !important;
}

.fr-mr-10v,
.fr-mr-5w,
.fr-mx-10v,
.fr-mx-5w {
  margin-right: 2.5rem !important;
}

.fr-mt-10v,
.fr-mt-5w,
.fr-my-10v,
.fr-my-5w {
  margin-top: 2.5rem !important;
}

.fr-mb-10v,
.fr-mb-5w,
.fr-my-10v,
.fr-my-5w {
  margin-bottom: 2.5rem !important;
}

.fr-m-11v {
  margin: 2.75rem !important;
}

.fr-ml-11v,
.fr-mx-11v {
  margin-left: 2.75rem !important;
}

.fr-mr-11v,
.fr-mx-11v {
  margin-right: 2.75rem !important;
}

.fr-mt-11v,
.fr-my-11v {
  margin-top: 2.75rem !important;
}

.fr-mb-11v,
.fr-my-11v {
  margin-bottom: 2.75rem !important;
}

.fr-m-12v,
.fr-m-6w {
  margin: 3rem !important;
}

.fr-ml-12v,
.fr-ml-6w,
.fr-mx-12v,
.fr-mx-6w {
  margin-left: 3rem !important;
}

.fr-mr-12v,
.fr-mr-6w,
.fr-mx-12v,
.fr-mx-6w {
  margin-right: 3rem !important;
}

.fr-mt-12v,
.fr-mt-6w,
.fr-my-12v,
.fr-my-6w {
  margin-top: 3rem !important;
}

.fr-mb-12v,
.fr-mb-6w,
.fr-my-12v,
.fr-my-6w {
  margin-bottom: 3rem !important;
}

.fr-m-13v {
  margin: 3.25rem !important;
}

.fr-ml-13v,
.fr-mx-13v {
  margin-left: 3.25rem !important;
}

.fr-mr-13v,
.fr-mx-13v {
  margin-right: 3.25rem !important;
}

.fr-mt-13v,
.fr-my-13v {
  margin-top: 3.25rem !important;
}

.fr-mb-13v,
.fr-my-13v {
  margin-bottom: 3.25rem !important;
}

.fr-m-14v,
.fr-m-7w {
  margin: 3.5rem !important;
}

.fr-ml-14v,
.fr-ml-7w,
.fr-mx-14v,
.fr-mx-7w {
  margin-left: 3.5rem !important;
}

.fr-mr-14v,
.fr-mr-7w,
.fr-mx-14v,
.fr-mx-7w {
  margin-right: 3.5rem !important;
}

.fr-mt-14v,
.fr-mt-7w,
.fr-my-14v,
.fr-my-7w {
  margin-top: 3.5rem !important;
}

.fr-mb-14v,
.fr-mb-7w,
.fr-my-14v,
.fr-my-7w {
  margin-bottom: 3.5rem !important;
}

.fr-m-15v {
  margin: 3.75rem !important;
}

.fr-ml-15v,
.fr-mx-15v {
  margin-left: 3.75rem !important;
}

.fr-mr-15v,
.fr-mx-15v {
  margin-right: 3.75rem !important;
}

.fr-mt-15v,
.fr-my-15v {
  margin-top: 3.75rem !important;
}

.fr-mb-15v,
.fr-my-15v {
  margin-bottom: 3.75rem !important;
}

.fr-m-16v,
.fr-m-8w {
  margin: 4rem !important;
}

.fr-ml-16v,
.fr-ml-8w,
.fr-mx-16v,
.fr-mx-8w {
  margin-left: 4rem !important;
}

.fr-mr-16v,
.fr-mr-8w,
.fr-mx-16v,
.fr-mx-8w {
  margin-right: 4rem !important;
}

.fr-mt-16v,
.fr-mt-8w,
.fr-my-16v,
.fr-my-8w {
  margin-top: 4rem !important;
}

.fr-mb-16v,
.fr-mb-8w,
.fr-my-16v,
.fr-my-8w {
  margin-bottom: 4rem !important;
}

.fr-m-17v {
  margin: 4.25rem !important;
}

.fr-ml-17v,
.fr-mx-17v {
  margin-left: 4.25rem !important;
}

.fr-mr-17v,
.fr-mx-17v {
  margin-right: 4.25rem !important;
}

.fr-mt-17v,
.fr-my-17v {
  margin-top: 4.25rem !important;
}

.fr-mb-17v,
.fr-my-17v {
  margin-bottom: 4.25rem !important;
}

.fr-m-18v,
.fr-m-9w {
  margin: 4.5rem !important;
}

.fr-ml-18v,
.fr-ml-9w,
.fr-mx-18v,
.fr-mx-9w {
  margin-left: 4.5rem !important;
}

.fr-mr-18v,
.fr-mr-9w,
.fr-mx-18v,
.fr-mx-9w {
  margin-right: 4.5rem !important;
}

.fr-mt-18v,
.fr-mt-9w,
.fr-my-18v,
.fr-my-9w {
  margin-top: 4.5rem !important;
}

.fr-mb-18v,
.fr-mb-9w,
.fr-my-18v,
.fr-my-9w {
  margin-bottom: 4.5rem !important;
}

.fr-m-19v {
  margin: 4.75rem !important;
}

.fr-ml-19v,
.fr-mx-19v {
  margin-left: 4.75rem !important;
}

.fr-mr-19v,
.fr-mx-19v {
  margin-right: 4.75rem !important;
}

.fr-mt-19v,
.fr-my-19v {
  margin-top: 4.75rem !important;
}

.fr-mb-19v,
.fr-my-19v {
  margin-bottom: 4.75rem !important;
}

.fr-m-20v,
.fr-m-10w {
  margin: 5rem !important;
}

.fr-ml-20v,
.fr-ml-10w,
.fr-mx-20v,
.fr-mx-10w {
  margin-left: 5rem !important;
}

.fr-mr-20v,
.fr-mr-10w,
.fr-mx-20v,
.fr-mx-10w {
  margin-right: 5rem !important;
}

.fr-mt-20v,
.fr-mt-10w,
.fr-my-20v,
.fr-my-10w {
  margin-top: 5rem !important;
}

.fr-mb-20v,
.fr-mb-10w,
.fr-my-20v,
.fr-my-10w {
  margin-bottom: 5rem !important;
}

.fr-m-21v {
  margin: 5.25rem !important;
}

.fr-ml-21v,
.fr-mx-21v {
  margin-left: 5.25rem !important;
}

.fr-mr-21v,
.fr-mx-21v {
  margin-right: 5.25rem !important;
}

.fr-mt-21v,
.fr-my-21v {
  margin-top: 5.25rem !important;
}

.fr-mb-21v,
.fr-my-21v {
  margin-bottom: 5.25rem !important;
}

.fr-m-22v,
.fr-m-11w {
  margin: 5.5rem !important;
}

.fr-ml-22v,
.fr-ml-11w,
.fr-mx-22v,
.fr-mx-11w {
  margin-left: 5.5rem !important;
}

.fr-mr-22v,
.fr-mr-11w,
.fr-mx-22v,
.fr-mx-11w {
  margin-right: 5.5rem !important;
}

.fr-mt-22v,
.fr-mt-11w,
.fr-my-22v,
.fr-my-11w {
  margin-top: 5.5rem !important;
}

.fr-mb-22v,
.fr-mb-11w,
.fr-my-22v,
.fr-my-11w {
  margin-bottom: 5.5rem !important;
}

.fr-m-23v {
  margin: 5.75rem !important;
}

.fr-ml-23v,
.fr-mx-23v {
  margin-left: 5.75rem !important;
}

.fr-mr-23v,
.fr-mx-23v {
  margin-right: 5.75rem !important;
}

.fr-mt-23v,
.fr-my-23v {
  margin-top: 5.75rem !important;
}

.fr-mb-23v,
.fr-my-23v {
  margin-bottom: 5.75rem !important;
}

.fr-m-24v,
.fr-m-12w {
  margin: 6rem !important;
}

.fr-ml-24v,
.fr-ml-12w,
.fr-mx-24v,
.fr-mx-12w {
  margin-left: 6rem !important;
}

.fr-mr-24v,
.fr-mr-12w,
.fr-mx-24v,
.fr-mx-12w {
  margin-right: 6rem !important;
}

.fr-mt-24v,
.fr-mt-12w,
.fr-my-24v,
.fr-my-12w {
  margin-top: 6rem !important;
}

.fr-mb-24v,
.fr-mb-12w,
.fr-my-24v,
.fr-my-12w {
  margin-bottom: 6rem !important;
}

.fr-m-25v {
  margin: 6.25rem !important;
}

.fr-ml-25v,
.fr-mx-25v {
  margin-left: 6.25rem !important;
}

.fr-mr-25v,
.fr-mx-25v {
  margin-right: 6.25rem !important;
}

.fr-mt-25v,
.fr-my-25v {
  margin-top: 6.25rem !important;
}

.fr-mb-25v,
.fr-my-25v {
  margin-bottom: 6.25rem !important;
}

.fr-m-26v,
.fr-m-13w {
  margin: 6.5rem !important;
}

.fr-ml-26v,
.fr-ml-13w,
.fr-mx-26v,
.fr-mx-13w {
  margin-left: 6.5rem !important;
}

.fr-mr-26v,
.fr-mr-13w,
.fr-mx-26v,
.fr-mx-13w {
  margin-right: 6.5rem !important;
}

.fr-mt-26v,
.fr-mt-13w,
.fr-my-26v,
.fr-my-13w {
  margin-top: 6.5rem !important;
}

.fr-mb-26v,
.fr-mb-13w,
.fr-my-26v,
.fr-my-13w {
  margin-bottom: 6.5rem !important;
}

.fr-m-27v {
  margin: 6.75rem !important;
}

.fr-ml-27v,
.fr-mx-27v {
  margin-left: 6.75rem !important;
}

.fr-mr-27v,
.fr-mx-27v {
  margin-right: 6.75rem !important;
}

.fr-mt-27v,
.fr-my-27v {
  margin-top: 6.75rem !important;
}

.fr-mb-27v,
.fr-my-27v {
  margin-bottom: 6.75rem !important;
}

.fr-m-28v,
.fr-m-14w {
  margin: 7rem !important;
}

.fr-ml-28v,
.fr-ml-14w,
.fr-mx-28v,
.fr-mx-14w {
  margin-left: 7rem !important;
}

.fr-mr-28v,
.fr-mr-14w,
.fr-mx-28v,
.fr-mx-14w {
  margin-right: 7rem !important;
}

.fr-mt-28v,
.fr-mt-14w,
.fr-my-28v,
.fr-my-14w {
  margin-top: 7rem !important;
}

.fr-mb-28v,
.fr-mb-14w,
.fr-my-28v,
.fr-my-14w {
  margin-bottom: 7rem !important;
}

.fr-m-29v {
  margin: 7.25rem !important;
}

.fr-ml-29v,
.fr-mx-29v {
  margin-left: 7.25rem !important;
}

.fr-mr-29v,
.fr-mx-29v {
  margin-right: 7.25rem !important;
}

.fr-mt-29v,
.fr-my-29v {
  margin-top: 7.25rem !important;
}

.fr-mb-29v,
.fr-my-29v {
  margin-bottom: 7.25rem !important;
}

.fr-m-30v,
.fr-m-15w {
  margin: 7.5rem !important;
}

.fr-ml-30v,
.fr-ml-15w,
.fr-mx-30v,
.fr-mx-15w {
  margin-left: 7.5rem !important;
}

.fr-mr-30v,
.fr-mr-15w,
.fr-mx-30v,
.fr-mx-15w {
  margin-right: 7.5rem !important;
}

.fr-mt-30v,
.fr-mt-15w,
.fr-my-30v,
.fr-my-15w {
  margin-top: 7.5rem !important;
}

.fr-mb-30v,
.fr-mb-15w,
.fr-my-30v,
.fr-my-15w {
  margin-bottom: 7.5rem !important;
}

.fr-m-31v {
  margin: 7.75rem !important;
}

.fr-ml-31v,
.fr-mx-31v {
  margin-left: 7.75rem !important;
}

.fr-mr-31v,
.fr-mx-31v {
  margin-right: 7.75rem !important;
}

.fr-mt-31v,
.fr-my-31v {
  margin-top: 7.75rem !important;
}

.fr-mb-31v,
.fr-my-31v {
  margin-bottom: 7.75rem !important;
}

.fr-m-32v,
.fr-m-16w {
  margin: 8rem !important;
}

.fr-ml-32v,
.fr-ml-16w,
.fr-mx-32v,
.fr-mx-16w {
  margin-left: 8rem !important;
}

.fr-mr-32v,
.fr-mr-16w,
.fr-mx-32v,
.fr-mx-16w {
  margin-right: 8rem !important;
}

.fr-mt-32v,
.fr-mt-16w,
.fr-my-32v,
.fr-my-16w {
  margin-top: 8rem !important;
}

.fr-mb-32v,
.fr-mb-16w,
.fr-my-32v,
.fr-my-16w {
  margin-bottom: 8rem !important;
}

.fr-m-auto {
  margin: auto;
}

.fr-ml-auto,
.fr-mx-auto {
  margin-left: auto;
}

.fr-mr-auto,
.fr-mx-auto {
  margin-right: auto;
}

.fr-mt-auto,
.fr-my-auto {
  margin-top: auto;
}

.fr-mb-auto,
.fr-my-auto {
  margin-bottom: auto;
}

.fr-m-first-n8v,
.fr-m-first-n4w {
  margin: -2rem !important;
}

.fr-ml-first-n8v,
.fr-ml-first-n4w,
.fr-mx-first-n8v,
.fr-mx-first-n4w {
  margin-left: -2rem !important;
}

.fr-mr-first-n8v,
.fr-mr-first-n4w,
.fr-mx-first-n8v,
.fr-mx-first-n4w {
  margin-right: -2rem !important;
}

.fr-mt-first-n8v,
.fr-mt-first-n4w,
.fr-my-first-n8v,
.fr-my-first-n4w {
  margin-top: -2rem !important;
}

.fr-mb-first-n8v,
.fr-mb-first-n4w,
.fr-my-first-n8v,
.fr-my-first-n4w {
  margin-bottom: -2rem !important;
}

.fr-m-first-n7v {
  margin: -1.75rem !important;
}

.fr-ml-first-n7v,
.fr-mx-first-n7v {
  margin-left: -1.75rem !important;
}

.fr-mr-first-n7v,
.fr-mx-first-n7v {
  margin-right: -1.75rem !important;
}

.fr-mt-first-n7v,
.fr-my-first-n7v {
  margin-top: -1.75rem !important;
}

.fr-mb-first-n7v,
.fr-my-first-n7v {
  margin-bottom: -1.75rem !important;
}

.fr-m-first-n6v,
.fr-m-first-n3w {
  margin: -1.5rem !important;
}

.fr-ml-first-n6v,
.fr-ml-first-n3w,
.fr-mx-first-n6v,
.fr-mx-first-n3w {
  margin-left: -1.5rem !important;
}

.fr-mr-first-n6v,
.fr-mr-first-n3w,
.fr-mx-first-n6v,
.fr-mx-first-n3w {
  margin-right: -1.5rem !important;
}

.fr-mt-first-n6v,
.fr-mt-first-n3w,
.fr-my-first-n6v,
.fr-my-first-n3w {
  margin-top: -1.5rem !important;
}

.fr-mb-first-n6v,
.fr-mb-first-n3w,
.fr-my-first-n6v,
.fr-my-first-n3w {
  margin-bottom: -1.5rem !important;
}

.fr-m-first-n5v {
  margin: -1.25rem !important;
}

.fr-ml-first-n5v,
.fr-mx-first-n5v {
  margin-left: -1.25rem !important;
}

.fr-mr-first-n5v,
.fr-mx-first-n5v {
  margin-right: -1.25rem !important;
}

.fr-mt-first-n5v,
.fr-my-first-n5v {
  margin-top: -1.25rem !important;
}

.fr-mb-first-n5v,
.fr-my-first-n5v {
  margin-bottom: -1.25rem !important;
}

.fr-m-first-n4v,
.fr-m-first-n2w {
  margin: -1rem !important;
}

.fr-ml-first-n4v,
.fr-ml-first-n2w,
.fr-mx-first-n4v,
.fr-mx-first-n2w {
  margin-left: -1rem !important;
}

.fr-mr-first-n4v,
.fr-mr-first-n2w,
.fr-mx-first-n4v,
.fr-mx-first-n2w {
  margin-right: -1rem !important;
}

.fr-mt-first-n4v,
.fr-mt-first-n2w,
.fr-my-first-n4v,
.fr-my-first-n2w {
  margin-top: -1rem !important;
}

.fr-mb-first-n4v,
.fr-mb-first-n2w,
.fr-my-first-n4v,
.fr-my-first-n2w {
  margin-bottom: -1rem !important;
}

.fr-m-first-n3v {
  margin: -0.75rem !important;
}

.fr-ml-first-n3v,
.fr-mx-first-n3v {
  margin-left: -0.75rem !important;
}

.fr-mr-first-n3v,
.fr-mx-first-n3v {
  margin-right: -0.75rem !important;
}

.fr-mt-first-n3v,
.fr-my-first-n3v {
  margin-top: -0.75rem !important;
}

.fr-mb-first-n3v,
.fr-my-first-n3v {
  margin-bottom: -0.75rem !important;
}

.fr-m-first-n2v,
.fr-m-first-n1w {
  margin: -0.5rem !important;
}

.fr-ml-first-n2v,
.fr-ml-first-n1w,
.fr-mx-first-n2v,
.fr-mx-first-n1w {
  margin-left: -0.5rem !important;
}

.fr-mr-first-n2v,
.fr-mr-first-n1w,
.fr-mx-first-n2v,
.fr-mx-first-n1w {
  margin-right: -0.5rem !important;
}

.fr-mt-first-n2v,
.fr-mt-first-n1w,
.fr-my-first-n2v,
.fr-my-first-n1w {
  margin-top: -0.5rem !important;
}

.fr-mb-first-n2v,
.fr-mb-first-n1w,
.fr-my-first-n2v,
.fr-my-first-n1w {
  margin-bottom: -0.5rem !important;
}

.fr-m-first-n1v {
  margin: -0.25rem !important;
}

.fr-ml-first-n1v,
.fr-mx-first-n1v {
  margin-left: -0.25rem !important;
}

.fr-mr-first-n1v,
.fr-mx-first-n1v {
  margin-right: -0.25rem !important;
}

.fr-mt-first-n1v,
.fr-my-first-n1v {
  margin-top: -0.25rem !important;
}

.fr-mb-first-n1v,
.fr-my-first-n1v {
  margin-bottom: -0.25rem !important;
}

.fr-m-first-n1-5v {
  margin: -0.375rem !important;
}

.fr-ml-first-n1-5v,
.fr-mx-first-n1-5v {
  margin-left: -0.375rem !important;
}

.fr-mr-first-n1-5v,
.fr-mx-first-n1-5v {
  margin-right: -0.375rem !important;
}

.fr-mt-first-n1-5v,
.fr-my-first-n1-5v {
  margin-top: -0.375rem !important;
}

.fr-mb-first-n1-5v,
.fr-my-first-n1-5v {
  margin-bottom: -0.375rem !important;
}

.fr-m-first-0 {
  margin: 0 !important;
}

.fr-ml-first-0,
.fr-mx-first-0 {
  margin-left: 0 !important;
}

.fr-mr-first-0,
.fr-mx-first-0 {
  margin-right: 0 !important;
}

.fr-mt-first-0,
.fr-my-first-0 {
  margin-top: 0 !important;
}

.fr-mb-first-0,
.fr-my-first-0 {
  margin-bottom: 0 !important;
}

.fr-m-first-n0-5v {
  margin: -0.125rem !important;
}

.fr-ml-first-n0-5v,
.fr-mx-first-n0-5v {
  margin-left: -0.125rem !important;
}

.fr-mr-first-n0-5v,
.fr-mx-first-n0-5v {
  margin-right: -0.125rem !important;
}

.fr-mt-first-n0-5v,
.fr-my-first-n0-5v {
  margin-top: -0.125rem !important;
}

.fr-mb-first-n0-5v,
.fr-my-first-n0-5v {
  margin-bottom: -0.125rem !important;
}

.fr-m-first-0-5v {
  margin: 0.125rem !important;
}

.fr-ml-first-0-5v,
.fr-mx-first-0-5v {
  margin-left: 0.125rem !important;
}

.fr-mr-first-0-5v,
.fr-mx-first-0-5v {
  margin-right: 0.125rem !important;
}

.fr-mt-first-0-5v,
.fr-my-first-0-5v {
  margin-top: 0.125rem !important;
}

.fr-mb-first-0-5v,
.fr-my-first-0-5v {
  margin-bottom: 0.125rem !important;
}

.fr-m-first-1v {
  margin: 0.25rem !important;
}

.fr-ml-first-1v,
.fr-mx-first-1v {
  margin-left: 0.25rem !important;
}

.fr-mr-first-1v,
.fr-mx-first-1v {
  margin-right: 0.25rem !important;
}

.fr-mt-first-1v,
.fr-my-first-1v {
  margin-top: 0.25rem !important;
}

.fr-mb-first-1v,
.fr-my-first-1v {
  margin-bottom: 0.25rem !important;
}

.fr-m-first-1-5v {
  margin: 0.375rem !important;
}

.fr-ml-first-1-5v,
.fr-mx-first-1-5v {
  margin-left: 0.375rem !important;
}

.fr-mr-first-1-5v,
.fr-mx-first-1-5v {
  margin-right: 0.375rem !important;
}

.fr-mt-first-1-5v,
.fr-my-first-1-5v {
  margin-top: 0.375rem !important;
}

.fr-mb-first-1-5v,
.fr-my-first-1-5v {
  margin-bottom: 0.375rem !important;
}

.fr-m-first-2v,
.fr-m-first-1w {
  margin: 0.5rem !important;
}

.fr-ml-first-2v,
.fr-ml-first-1w,
.fr-mx-first-2v,
.fr-mx-first-1w {
  margin-left: 0.5rem !important;
}

.fr-mr-first-2v,
.fr-mr-first-1w,
.fr-mx-first-2v,
.fr-mx-first-1w {
  margin-right: 0.5rem !important;
}

.fr-mt-first-2v,
.fr-mt-first-1w,
.fr-my-first-2v,
.fr-my-first-1w {
  margin-top: 0.5rem !important;
}

.fr-mb-first-2v,
.fr-mb-first-1w,
.fr-my-first-2v,
.fr-my-first-1w {
  margin-bottom: 0.5rem !important;
}

.fr-m-first-3v {
  margin: 0.75rem !important;
}

.fr-ml-first-3v,
.fr-mx-first-3v {
  margin-left: 0.75rem !important;
}

.fr-mr-first-3v,
.fr-mx-first-3v {
  margin-right: 0.75rem !important;
}

.fr-mt-first-3v,
.fr-my-first-3v {
  margin-top: 0.75rem !important;
}

.fr-mb-first-3v,
.fr-my-first-3v {
  margin-bottom: 0.75rem !important;
}

.fr-m-first-4v,
.fr-m-first-2w {
  margin: 1rem !important;
}

.fr-ml-first-4v,
.fr-ml-first-2w,
.fr-mx-first-4v,
.fr-mx-first-2w {
  margin-left: 1rem !important;
}

.fr-mr-first-4v,
.fr-mr-first-2w,
.fr-mx-first-4v,
.fr-mx-first-2w {
  margin-right: 1rem !important;
}

.fr-mt-first-4v,
.fr-mt-first-2w,
.fr-my-first-4v,
.fr-my-first-2w {
  margin-top: 1rem !important;
}

.fr-mb-first-4v,
.fr-mb-first-2w,
.fr-my-first-4v,
.fr-my-first-2w {
  margin-bottom: 1rem !important;
}

.fr-m-first-5v {
  margin: 1.25rem !important;
}

.fr-ml-first-5v,
.fr-mx-first-5v {
  margin-left: 1.25rem !important;
}

.fr-mr-first-5v,
.fr-mx-first-5v {
  margin-right: 1.25rem !important;
}

.fr-mt-first-5v,
.fr-my-first-5v {
  margin-top: 1.25rem !important;
}

.fr-mb-first-5v,
.fr-my-first-5v {
  margin-bottom: 1.25rem !important;
}

.fr-m-first-6v,
.fr-m-first-3w {
  margin: 1.5rem !important;
}

.fr-ml-first-6v,
.fr-ml-first-3w,
.fr-mx-first-6v,
.fr-mx-first-3w {
  margin-left: 1.5rem !important;
}

.fr-mr-first-6v,
.fr-mr-first-3w,
.fr-mx-first-6v,
.fr-mx-first-3w {
  margin-right: 1.5rem !important;
}

.fr-mt-first-6v,
.fr-mt-first-3w,
.fr-my-first-6v,
.fr-my-first-3w {
  margin-top: 1.5rem !important;
}

.fr-mb-first-6v,
.fr-mb-first-3w,
.fr-my-first-6v,
.fr-my-first-3w {
  margin-bottom: 1.5rem !important;
}

.fr-m-first-7v {
  margin: 1.75rem !important;
}

.fr-ml-first-7v,
.fr-mx-first-7v {
  margin-left: 1.75rem !important;
}

.fr-mr-first-7v,
.fr-mx-first-7v {
  margin-right: 1.75rem !important;
}

.fr-mt-first-7v,
.fr-my-first-7v {
  margin-top: 1.75rem !important;
}

.fr-mb-first-7v,
.fr-my-first-7v {
  margin-bottom: 1.75rem !important;
}

.fr-m-first-8v,
.fr-m-first-4w {
  margin: 2rem !important;
}

.fr-ml-first-8v,
.fr-ml-first-4w,
.fr-mx-first-8v,
.fr-mx-first-4w {
  margin-left: 2rem !important;
}

.fr-mr-first-8v,
.fr-mr-first-4w,
.fr-mx-first-8v,
.fr-mx-first-4w {
  margin-right: 2rem !important;
}

.fr-mt-first-8v,
.fr-mt-first-4w,
.fr-my-first-8v,
.fr-my-first-4w {
  margin-top: 2rem !important;
}

.fr-mb-first-8v,
.fr-mb-first-4w,
.fr-my-first-8v,
.fr-my-first-4w {
  margin-bottom: 2rem !important;
}

.fr-m-first-9v {
  margin: 2.25rem !important;
}

.fr-ml-first-9v,
.fr-mx-first-9v {
  margin-left: 2.25rem !important;
}

.fr-mr-first-9v,
.fr-mx-first-9v {
  margin-right: 2.25rem !important;
}

.fr-mt-first-9v,
.fr-my-first-9v {
  margin-top: 2.25rem !important;
}

.fr-mb-first-9v,
.fr-my-first-9v {
  margin-bottom: 2.25rem !important;
}

.fr-m-first-10v,
.fr-m-first-5w {
  margin: 2.5rem !important;
}

.fr-ml-first-10v,
.fr-ml-first-5w,
.fr-mx-first-10v,
.fr-mx-first-5w {
  margin-left: 2.5rem !important;
}

.fr-mr-first-10v,
.fr-mr-first-5w,
.fr-mx-first-10v,
.fr-mx-first-5w {
  margin-right: 2.5rem !important;
}

.fr-mt-first-10v,
.fr-mt-first-5w,
.fr-my-first-10v,
.fr-my-first-5w {
  margin-top: 2.5rem !important;
}

.fr-mb-first-10v,
.fr-mb-first-5w,
.fr-my-first-10v,
.fr-my-first-5w {
  margin-bottom: 2.5rem !important;
}

.fr-m-first-11v {
  margin: 2.75rem !important;
}

.fr-ml-first-11v,
.fr-mx-first-11v {
  margin-left: 2.75rem !important;
}

.fr-mr-first-11v,
.fr-mx-first-11v {
  margin-right: 2.75rem !important;
}

.fr-mt-first-11v,
.fr-my-first-11v {
  margin-top: 2.75rem !important;
}

.fr-mb-first-11v,
.fr-my-first-11v {
  margin-bottom: 2.75rem !important;
}

.fr-m-first-12v,
.fr-m-first-6w {
  margin: 3rem !important;
}

.fr-ml-first-12v,
.fr-ml-first-6w,
.fr-mx-first-12v,
.fr-mx-first-6w {
  margin-left: 3rem !important;
}

.fr-mr-first-12v,
.fr-mr-first-6w,
.fr-mx-first-12v,
.fr-mx-first-6w {
  margin-right: 3rem !important;
}

.fr-mt-first-12v,
.fr-mt-first-6w,
.fr-my-first-12v,
.fr-my-first-6w {
  margin-top: 3rem !important;
}

.fr-mb-first-12v,
.fr-mb-first-6w,
.fr-my-first-12v,
.fr-my-first-6w {
  margin-bottom: 3rem !important;
}

.fr-m-first-13v {
  margin: 3.25rem !important;
}

.fr-ml-first-13v,
.fr-mx-first-13v {
  margin-left: 3.25rem !important;
}

.fr-mr-first-13v,
.fr-mx-first-13v {
  margin-right: 3.25rem !important;
}

.fr-mt-first-13v,
.fr-my-first-13v {
  margin-top: 3.25rem !important;
}

.fr-mb-first-13v,
.fr-my-first-13v {
  margin-bottom: 3.25rem !important;
}

.fr-m-first-14v,
.fr-m-first-7w {
  margin: 3.5rem !important;
}

.fr-ml-first-14v,
.fr-ml-first-7w,
.fr-mx-first-14v,
.fr-mx-first-7w {
  margin-left: 3.5rem !important;
}

.fr-mr-first-14v,
.fr-mr-first-7w,
.fr-mx-first-14v,
.fr-mx-first-7w {
  margin-right: 3.5rem !important;
}

.fr-mt-first-14v,
.fr-mt-first-7w,
.fr-my-first-14v,
.fr-my-first-7w {
  margin-top: 3.5rem !important;
}

.fr-mb-first-14v,
.fr-mb-first-7w,
.fr-my-first-14v,
.fr-my-first-7w {
  margin-bottom: 3.5rem !important;
}

.fr-m-first-15v {
  margin: 3.75rem !important;
}

.fr-ml-first-15v,
.fr-mx-first-15v {
  margin-left: 3.75rem !important;
}

.fr-mr-first-15v,
.fr-mx-first-15v {
  margin-right: 3.75rem !important;
}

.fr-mt-first-15v,
.fr-my-first-15v {
  margin-top: 3.75rem !important;
}

.fr-mb-first-15v,
.fr-my-first-15v {
  margin-bottom: 3.75rem !important;
}

.fr-m-first-16v,
.fr-m-first-8w {
  margin: 4rem !important;
}

.fr-ml-first-16v,
.fr-ml-first-8w,
.fr-mx-first-16v,
.fr-mx-first-8w {
  margin-left: 4rem !important;
}

.fr-mr-first-16v,
.fr-mr-first-8w,
.fr-mx-first-16v,
.fr-mx-first-8w {
  margin-right: 4rem !important;
}

.fr-mt-first-16v,
.fr-mt-first-8w,
.fr-my-first-16v,
.fr-my-first-8w {
  margin-top: 4rem !important;
}

.fr-mb-first-16v,
.fr-mb-first-8w,
.fr-my-first-16v,
.fr-my-first-8w {
  margin-bottom: 4rem !important;
}

.fr-m-first-17v {
  margin: 4.25rem !important;
}

.fr-ml-first-17v,
.fr-mx-first-17v {
  margin-left: 4.25rem !important;
}

.fr-mr-first-17v,
.fr-mx-first-17v {
  margin-right: 4.25rem !important;
}

.fr-mt-first-17v,
.fr-my-first-17v {
  margin-top: 4.25rem !important;
}

.fr-mb-first-17v,
.fr-my-first-17v {
  margin-bottom: 4.25rem !important;
}

.fr-m-first-18v,
.fr-m-first-9w {
  margin: 4.5rem !important;
}

.fr-ml-first-18v,
.fr-ml-first-9w,
.fr-mx-first-18v,
.fr-mx-first-9w {
  margin-left: 4.5rem !important;
}

.fr-mr-first-18v,
.fr-mr-first-9w,
.fr-mx-first-18v,
.fr-mx-first-9w {
  margin-right: 4.5rem !important;
}

.fr-mt-first-18v,
.fr-mt-first-9w,
.fr-my-first-18v,
.fr-my-first-9w {
  margin-top: 4.5rem !important;
}

.fr-mb-first-18v,
.fr-mb-first-9w,
.fr-my-first-18v,
.fr-my-first-9w {
  margin-bottom: 4.5rem !important;
}

.fr-m-first-19v {
  margin: 4.75rem !important;
}

.fr-ml-first-19v,
.fr-mx-first-19v {
  margin-left: 4.75rem !important;
}

.fr-mr-first-19v,
.fr-mx-first-19v {
  margin-right: 4.75rem !important;
}

.fr-mt-first-19v,
.fr-my-first-19v {
  margin-top: 4.75rem !important;
}

.fr-mb-first-19v,
.fr-my-first-19v {
  margin-bottom: 4.75rem !important;
}

.fr-m-first-20v,
.fr-m-first-10w {
  margin: 5rem !important;
}

.fr-ml-first-20v,
.fr-ml-first-10w,
.fr-mx-first-20v,
.fr-mx-first-10w {
  margin-left: 5rem !important;
}

.fr-mr-first-20v,
.fr-mr-first-10w,
.fr-mx-first-20v,
.fr-mx-first-10w {
  margin-right: 5rem !important;
}

.fr-mt-first-20v,
.fr-mt-first-10w,
.fr-my-first-20v,
.fr-my-first-10w {
  margin-top: 5rem !important;
}

.fr-mb-first-20v,
.fr-mb-first-10w,
.fr-my-first-20v,
.fr-my-first-10w {
  margin-bottom: 5rem !important;
}

.fr-m-first-21v {
  margin: 5.25rem !important;
}

.fr-ml-first-21v,
.fr-mx-first-21v {
  margin-left: 5.25rem !important;
}

.fr-mr-first-21v,
.fr-mx-first-21v {
  margin-right: 5.25rem !important;
}

.fr-mt-first-21v,
.fr-my-first-21v {
  margin-top: 5.25rem !important;
}

.fr-mb-first-21v,
.fr-my-first-21v {
  margin-bottom: 5.25rem !important;
}

.fr-m-first-22v,
.fr-m-first-11w {
  margin: 5.5rem !important;
}

.fr-ml-first-22v,
.fr-ml-first-11w,
.fr-mx-first-22v,
.fr-mx-first-11w {
  margin-left: 5.5rem !important;
}

.fr-mr-first-22v,
.fr-mr-first-11w,
.fr-mx-first-22v,
.fr-mx-first-11w {
  margin-right: 5.5rem !important;
}

.fr-mt-first-22v,
.fr-mt-first-11w,
.fr-my-first-22v,
.fr-my-first-11w {
  margin-top: 5.5rem !important;
}

.fr-mb-first-22v,
.fr-mb-first-11w,
.fr-my-first-22v,
.fr-my-first-11w {
  margin-bottom: 5.5rem !important;
}

.fr-m-first-23v {
  margin: 5.75rem !important;
}

.fr-ml-first-23v,
.fr-mx-first-23v {
  margin-left: 5.75rem !important;
}

.fr-mr-first-23v,
.fr-mx-first-23v {
  margin-right: 5.75rem !important;
}

.fr-mt-first-23v,
.fr-my-first-23v {
  margin-top: 5.75rem !important;
}

.fr-mb-first-23v,
.fr-my-first-23v {
  margin-bottom: 5.75rem !important;
}

.fr-m-first-24v,
.fr-m-first-12w {
  margin: 6rem !important;
}

.fr-ml-first-24v,
.fr-ml-first-12w,
.fr-mx-first-24v,
.fr-mx-first-12w {
  margin-left: 6rem !important;
}

.fr-mr-first-24v,
.fr-mr-first-12w,
.fr-mx-first-24v,
.fr-mx-first-12w {
  margin-right: 6rem !important;
}

.fr-mt-first-24v,
.fr-mt-first-12w,
.fr-my-first-24v,
.fr-my-first-12w {
  margin-top: 6rem !important;
}

.fr-mb-first-24v,
.fr-mb-first-12w,
.fr-my-first-24v,
.fr-my-first-12w {
  margin-bottom: 6rem !important;
}

.fr-m-first-25v {
  margin: 6.25rem !important;
}

.fr-ml-first-25v,
.fr-mx-first-25v {
  margin-left: 6.25rem !important;
}

.fr-mr-first-25v,
.fr-mx-first-25v {
  margin-right: 6.25rem !important;
}

.fr-mt-first-25v,
.fr-my-first-25v {
  margin-top: 6.25rem !important;
}

.fr-mb-first-25v,
.fr-my-first-25v {
  margin-bottom: 6.25rem !important;
}

.fr-m-first-26v,
.fr-m-first-13w {
  margin: 6.5rem !important;
}

.fr-ml-first-26v,
.fr-ml-first-13w,
.fr-mx-first-26v,
.fr-mx-first-13w {
  margin-left: 6.5rem !important;
}

.fr-mr-first-26v,
.fr-mr-first-13w,
.fr-mx-first-26v,
.fr-mx-first-13w {
  margin-right: 6.5rem !important;
}

.fr-mt-first-26v,
.fr-mt-first-13w,
.fr-my-first-26v,
.fr-my-first-13w {
  margin-top: 6.5rem !important;
}

.fr-mb-first-26v,
.fr-mb-first-13w,
.fr-my-first-26v,
.fr-my-first-13w {
  margin-bottom: 6.5rem !important;
}

.fr-m-first-27v {
  margin: 6.75rem !important;
}

.fr-ml-first-27v,
.fr-mx-first-27v {
  margin-left: 6.75rem !important;
}

.fr-mr-first-27v,
.fr-mx-first-27v {
  margin-right: 6.75rem !important;
}

.fr-mt-first-27v,
.fr-my-first-27v {
  margin-top: 6.75rem !important;
}

.fr-mb-first-27v,
.fr-my-first-27v {
  margin-bottom: 6.75rem !important;
}

.fr-m-first-28v,
.fr-m-first-14w {
  margin: 7rem !important;
}

.fr-ml-first-28v,
.fr-ml-first-14w,
.fr-mx-first-28v,
.fr-mx-first-14w {
  margin-left: 7rem !important;
}

.fr-mr-first-28v,
.fr-mr-first-14w,
.fr-mx-first-28v,
.fr-mx-first-14w {
  margin-right: 7rem !important;
}

.fr-mt-first-28v,
.fr-mt-first-14w,
.fr-my-first-28v,
.fr-my-first-14w {
  margin-top: 7rem !important;
}

.fr-mb-first-28v,
.fr-mb-first-14w,
.fr-my-first-28v,
.fr-my-first-14w {
  margin-bottom: 7rem !important;
}

.fr-m-first-29v {
  margin: 7.25rem !important;
}

.fr-ml-first-29v,
.fr-mx-first-29v {
  margin-left: 7.25rem !important;
}

.fr-mr-first-29v,
.fr-mx-first-29v {
  margin-right: 7.25rem !important;
}

.fr-mt-first-29v,
.fr-my-first-29v {
  margin-top: 7.25rem !important;
}

.fr-mb-first-29v,
.fr-my-first-29v {
  margin-bottom: 7.25rem !important;
}

.fr-m-first-30v,
.fr-m-first-15w {
  margin: 7.5rem !important;
}

.fr-ml-first-30v,
.fr-ml-first-15w,
.fr-mx-first-30v,
.fr-mx-first-15w {
  margin-left: 7.5rem !important;
}

.fr-mr-first-30v,
.fr-mr-first-15w,
.fr-mx-first-30v,
.fr-mx-first-15w {
  margin-right: 7.5rem !important;
}

.fr-mt-first-30v,
.fr-mt-first-15w,
.fr-my-first-30v,
.fr-my-first-15w {
  margin-top: 7.5rem !important;
}

.fr-mb-first-30v,
.fr-mb-first-15w,
.fr-my-first-30v,
.fr-my-first-15w {
  margin-bottom: 7.5rem !important;
}

.fr-m-first-31v {
  margin: 7.75rem !important;
}

.fr-ml-first-31v,
.fr-mx-first-31v {
  margin-left: 7.75rem !important;
}

.fr-mr-first-31v,
.fr-mx-first-31v {
  margin-right: 7.75rem !important;
}

.fr-mt-first-31v,
.fr-my-first-31v {
  margin-top: 7.75rem !important;
}

.fr-mb-first-31v,
.fr-my-first-31v {
  margin-bottom: 7.75rem !important;
}

.fr-m-first-32v,
.fr-m-first-16w {
  margin: 8rem !important;
}

.fr-ml-first-32v,
.fr-ml-first-16w,
.fr-mx-first-32v,
.fr-mx-first-16w {
  margin-left: 8rem !important;
}

.fr-mr-first-32v,
.fr-mr-first-16w,
.fr-mx-first-32v,
.fr-mx-first-16w {
  margin-right: 8rem !important;
}

.fr-mt-first-32v,
.fr-mt-first-16w,
.fr-my-first-32v,
.fr-my-first-16w {
  margin-top: 8rem !important;
}

.fr-mb-first-32v,
.fr-mb-first-16w,
.fr-my-first-32v,
.fr-my-first-16w {
  margin-bottom: 8rem !important;
}

.fr-m-first-auto {
  margin: auto;
}

.fr-ml-first-auto,
.fr-mx-first-auto {
  margin-left: auto;
}

.fr-mr-first-auto,
.fr-mx-first-auto {
  margin-right: auto;
}

.fr-mt-first-auto,
.fr-my-first-auto {
  margin-top: auto;
}

.fr-mb-first-auto,
.fr-my-first-auto {
  margin-bottom: auto;
}

.fr-p-0 {
  padding: 0 !important;
}

.fr-pl-0,
.fr-px-0 {
  padding-left: 0 !important;
}

.fr-pr-0,
.fr-px-0 {
  padding-right: 0 !important;
}

.fr-pt-0,
.fr-py-0 {
  padding-top: 0 !important;
}

.fr-pb-0,
.fr-py-0 {
  padding-bottom: 0 !important;
}

.fr-p-0-5v {
  padding: 0.125rem !important;
}

.fr-pl-0-5v,
.fr-px-0-5v {
  padding-left: 0.125rem !important;
}

.fr-pr-0-5v,
.fr-px-0-5v {
  padding-right: 0.125rem !important;
}

.fr-pt-0-5v,
.fr-py-0-5v {
  padding-top: 0.125rem !important;
}

.fr-pb-0-5v,
.fr-py-0-5v {
  padding-bottom: 0.125rem !important;
}

.fr-p-1v {
  padding: 0.25rem !important;
}

.fr-pl-1v,
.fr-px-1v {
  padding-left: 0.25rem !important;
}

.fr-pr-1v,
.fr-px-1v {
  padding-right: 0.25rem !important;
}

.fr-pt-1v,
.fr-py-1v {
  padding-top: 0.25rem !important;
}

.fr-pb-1v,
.fr-py-1v {
  padding-bottom: 0.25rem !important;
}

.fr-p-1-5v {
  padding: 0.375rem !important;
}

.fr-pl-1-5v,
.fr-px-1-5v {
  padding-left: 0.375rem !important;
}

.fr-pr-1-5v,
.fr-px-1-5v {
  padding-right: 0.375rem !important;
}

.fr-pt-1-5v,
.fr-py-1-5v {
  padding-top: 0.375rem !important;
}

.fr-pb-1-5v,
.fr-py-1-5v {
  padding-bottom: 0.375rem !important;
}

.fr-p-2v,
.fr-p-1w {
  padding: 0.5rem !important;
}

.fr-pl-2v,
.fr-pl-1w,
.fr-px-2v,
.fr-px-1w {
  padding-left: 0.5rem !important;
}

.fr-pr-2v,
.fr-pr-1w,
.fr-px-2v,
.fr-px-1w {
  padding-right: 0.5rem !important;
}

.fr-pt-2v,
.fr-pt-1w,
.fr-py-2v,
.fr-py-1w {
  padding-top: 0.5rem !important;
}

.fr-pb-2v,
.fr-pb-1w,
.fr-py-2v,
.fr-py-1w {
  padding-bottom: 0.5rem !important;
}

.fr-p-3v {
  padding: 0.75rem !important;
}

.fr-pl-3v,
.fr-px-3v {
  padding-left: 0.75rem !important;
}

.fr-pr-3v,
.fr-px-3v {
  padding-right: 0.75rem !important;
}

.fr-pt-3v,
.fr-py-3v {
  padding-top: 0.75rem !important;
}

.fr-pb-3v,
.fr-py-3v {
  padding-bottom: 0.75rem !important;
}

.fr-p-4v,
.fr-p-2w {
  padding: 1rem !important;
}

.fr-pl-4v,
.fr-pl-2w,
.fr-px-4v,
.fr-px-2w {
  padding-left: 1rem !important;
}

.fr-pr-4v,
.fr-pr-2w,
.fr-px-4v,
.fr-px-2w {
  padding-right: 1rem !important;
}

.fr-pt-4v,
.fr-pt-2w,
.fr-py-4v,
.fr-py-2w {
  padding-top: 1rem !important;
}

.fr-pb-4v,
.fr-pb-2w,
.fr-py-4v,
.fr-py-2w {
  padding-bottom: 1rem !important;
}

.fr-p-5v {
  padding: 1.25rem !important;
}

.fr-pl-5v,
.fr-px-5v {
  padding-left: 1.25rem !important;
}

.fr-pr-5v,
.fr-px-5v {
  padding-right: 1.25rem !important;
}

.fr-pt-5v,
.fr-py-5v {
  padding-top: 1.25rem !important;
}

.fr-pb-5v,
.fr-py-5v {
  padding-bottom: 1.25rem !important;
}

.fr-p-6v,
.fr-p-3w {
  padding: 1.5rem !important;
}

.fr-pl-6v,
.fr-pl-3w,
.fr-px-6v,
.fr-px-3w {
  padding-left: 1.5rem !important;
}

.fr-pr-6v,
.fr-pr-3w,
.fr-px-6v,
.fr-px-3w {
  padding-right: 1.5rem !important;
}

.fr-pt-6v,
.fr-pt-3w,
.fr-py-6v,
.fr-py-3w {
  padding-top: 1.5rem !important;
}

.fr-pb-6v,
.fr-pb-3w,
.fr-py-6v,
.fr-py-3w {
  padding-bottom: 1.5rem !important;
}

.fr-p-7v {
  padding: 1.75rem !important;
}

.fr-pl-7v,
.fr-px-7v {
  padding-left: 1.75rem !important;
}

.fr-pr-7v,
.fr-px-7v {
  padding-right: 1.75rem !important;
}

.fr-pt-7v,
.fr-py-7v {
  padding-top: 1.75rem !important;
}

.fr-pb-7v,
.fr-py-7v {
  padding-bottom: 1.75rem !important;
}

.fr-p-8v,
.fr-p-4w {
  padding: 2rem !important;
}

.fr-pl-8v,
.fr-pl-4w,
.fr-px-8v,
.fr-px-4w {
  padding-left: 2rem !important;
}

.fr-pr-8v,
.fr-pr-4w,
.fr-px-8v,
.fr-px-4w {
  padding-right: 2rem !important;
}

.fr-pt-8v,
.fr-pt-4w,
.fr-py-8v,
.fr-py-4w {
  padding-top: 2rem !important;
}

.fr-pb-8v,
.fr-pb-4w,
.fr-py-8v,
.fr-py-4w {
  padding-bottom: 2rem !important;
}

.fr-p-9v {
  padding: 2.25rem !important;
}

.fr-pl-9v,
.fr-px-9v {
  padding-left: 2.25rem !important;
}

.fr-pr-9v,
.fr-px-9v {
  padding-right: 2.25rem !important;
}

.fr-pt-9v,
.fr-py-9v {
  padding-top: 2.25rem !important;
}

.fr-pb-9v,
.fr-py-9v {
  padding-bottom: 2.25rem !important;
}

.fr-p-10v,
.fr-p-5w {
  padding: 2.5rem !important;
}

.fr-pl-10v,
.fr-pl-5w,
.fr-px-10v,
.fr-px-5w {
  padding-left: 2.5rem !important;
}

.fr-pr-10v,
.fr-pr-5w,
.fr-px-10v,
.fr-px-5w {
  padding-right: 2.5rem !important;
}

.fr-pt-10v,
.fr-pt-5w,
.fr-py-10v,
.fr-py-5w {
  padding-top: 2.5rem !important;
}

.fr-pb-10v,
.fr-pb-5w,
.fr-py-10v,
.fr-py-5w {
  padding-bottom: 2.5rem !important;
}

.fr-p-11v {
  padding: 2.75rem !important;
}

.fr-pl-11v,
.fr-px-11v {
  padding-left: 2.75rem !important;
}

.fr-pr-11v,
.fr-px-11v {
  padding-right: 2.75rem !important;
}

.fr-pt-11v,
.fr-py-11v {
  padding-top: 2.75rem !important;
}

.fr-pb-11v,
.fr-py-11v {
  padding-bottom: 2.75rem !important;
}

.fr-p-12v,
.fr-p-6w {
  padding: 3rem !important;
}

.fr-pl-12v,
.fr-pl-6w,
.fr-px-12v,
.fr-px-6w {
  padding-left: 3rem !important;
}

.fr-pr-12v,
.fr-pr-6w,
.fr-px-12v,
.fr-px-6w {
  padding-right: 3rem !important;
}

.fr-pt-12v,
.fr-pt-6w,
.fr-py-12v,
.fr-py-6w {
  padding-top: 3rem !important;
}

.fr-pb-12v,
.fr-pb-6w,
.fr-py-12v,
.fr-py-6w {
  padding-bottom: 3rem !important;
}

.fr-p-13v {
  padding: 3.25rem !important;
}

.fr-pl-13v,
.fr-px-13v {
  padding-left: 3.25rem !important;
}

.fr-pr-13v,
.fr-px-13v {
  padding-right: 3.25rem !important;
}

.fr-pt-13v,
.fr-py-13v {
  padding-top: 3.25rem !important;
}

.fr-pb-13v,
.fr-py-13v {
  padding-bottom: 3.25rem !important;
}

.fr-p-14v,
.fr-p-7w {
  padding: 3.5rem !important;
}

.fr-pl-14v,
.fr-pl-7w,
.fr-px-14v,
.fr-px-7w {
  padding-left: 3.5rem !important;
}

.fr-pr-14v,
.fr-pr-7w,
.fr-px-14v,
.fr-px-7w {
  padding-right: 3.5rem !important;
}

.fr-pt-14v,
.fr-pt-7w,
.fr-py-14v,
.fr-py-7w {
  padding-top: 3.5rem !important;
}

.fr-pb-14v,
.fr-pb-7w,
.fr-py-14v,
.fr-py-7w {
  padding-bottom: 3.5rem !important;
}

.fr-p-15v {
  padding: 3.75rem !important;
}

.fr-pl-15v,
.fr-px-15v {
  padding-left: 3.75rem !important;
}

.fr-pr-15v,
.fr-px-15v {
  padding-right: 3.75rem !important;
}

.fr-pt-15v,
.fr-py-15v {
  padding-top: 3.75rem !important;
}

.fr-pb-15v,
.fr-py-15v {
  padding-bottom: 3.75rem !important;
}

.fr-p-16v,
.fr-p-8w {
  padding: 4rem !important;
}

.fr-pl-16v,
.fr-pl-8w,
.fr-px-16v,
.fr-px-8w {
  padding-left: 4rem !important;
}

.fr-pr-16v,
.fr-pr-8w,
.fr-px-16v,
.fr-px-8w {
  padding-right: 4rem !important;
}

.fr-pt-16v,
.fr-pt-8w,
.fr-py-16v,
.fr-py-8w {
  padding-top: 4rem !important;
}

.fr-pb-16v,
.fr-pb-8w,
.fr-py-16v,
.fr-py-8w {
  padding-bottom: 4rem !important;
}

.fr-p-17v {
  padding: 4.25rem !important;
}

.fr-pl-17v,
.fr-px-17v {
  padding-left: 4.25rem !important;
}

.fr-pr-17v,
.fr-px-17v {
  padding-right: 4.25rem !important;
}

.fr-pt-17v,
.fr-py-17v {
  padding-top: 4.25rem !important;
}

.fr-pb-17v,
.fr-py-17v {
  padding-bottom: 4.25rem !important;
}

.fr-p-18v,
.fr-p-9w {
  padding: 4.5rem !important;
}

.fr-pl-18v,
.fr-pl-9w,
.fr-px-18v,
.fr-px-9w {
  padding-left: 4.5rem !important;
}

.fr-pr-18v,
.fr-pr-9w,
.fr-px-18v,
.fr-px-9w {
  padding-right: 4.5rem !important;
}

.fr-pt-18v,
.fr-pt-9w,
.fr-py-18v,
.fr-py-9w {
  padding-top: 4.5rem !important;
}

.fr-pb-18v,
.fr-pb-9w,
.fr-py-18v,
.fr-py-9w {
  padding-bottom: 4.5rem !important;
}

.fr-p-19v {
  padding: 4.75rem !important;
}

.fr-pl-19v,
.fr-px-19v {
  padding-left: 4.75rem !important;
}

.fr-pr-19v,
.fr-px-19v {
  padding-right: 4.75rem !important;
}

.fr-pt-19v,
.fr-py-19v {
  padding-top: 4.75rem !important;
}

.fr-pb-19v,
.fr-py-19v {
  padding-bottom: 4.75rem !important;
}

.fr-p-20v,
.fr-p-10w {
  padding: 5rem !important;
}

.fr-pl-20v,
.fr-pl-10w,
.fr-px-20v,
.fr-px-10w {
  padding-left: 5rem !important;
}

.fr-pr-20v,
.fr-pr-10w,
.fr-px-20v,
.fr-px-10w {
  padding-right: 5rem !important;
}

.fr-pt-20v,
.fr-pt-10w,
.fr-py-20v,
.fr-py-10w {
  padding-top: 5rem !important;
}

.fr-pb-20v,
.fr-pb-10w,
.fr-py-20v,
.fr-py-10w {
  padding-bottom: 5rem !important;
}

.fr-p-21v {
  padding: 5.25rem !important;
}

.fr-pl-21v,
.fr-px-21v {
  padding-left: 5.25rem !important;
}

.fr-pr-21v,
.fr-px-21v {
  padding-right: 5.25rem !important;
}

.fr-pt-21v,
.fr-py-21v {
  padding-top: 5.25rem !important;
}

.fr-pb-21v,
.fr-py-21v {
  padding-bottom: 5.25rem !important;
}

.fr-p-22v,
.fr-p-11w {
  padding: 5.5rem !important;
}

.fr-pl-22v,
.fr-pl-11w,
.fr-px-22v,
.fr-px-11w {
  padding-left: 5.5rem !important;
}

.fr-pr-22v,
.fr-pr-11w,
.fr-px-22v,
.fr-px-11w {
  padding-right: 5.5rem !important;
}

.fr-pt-22v,
.fr-pt-11w,
.fr-py-22v,
.fr-py-11w {
  padding-top: 5.5rem !important;
}

.fr-pb-22v,
.fr-pb-11w,
.fr-py-22v,
.fr-py-11w {
  padding-bottom: 5.5rem !important;
}

.fr-p-23v {
  padding: 5.75rem !important;
}

.fr-pl-23v,
.fr-px-23v {
  padding-left: 5.75rem !important;
}

.fr-pr-23v,
.fr-px-23v {
  padding-right: 5.75rem !important;
}

.fr-pt-23v,
.fr-py-23v {
  padding-top: 5.75rem !important;
}

.fr-pb-23v,
.fr-py-23v {
  padding-bottom: 5.75rem !important;
}

.fr-p-24v,
.fr-p-12w {
  padding: 6rem !important;
}

.fr-pl-24v,
.fr-pl-12w,
.fr-px-24v,
.fr-px-12w {
  padding-left: 6rem !important;
}

.fr-pr-24v,
.fr-pr-12w,
.fr-px-24v,
.fr-px-12w {
  padding-right: 6rem !important;
}

.fr-pt-24v,
.fr-pt-12w,
.fr-py-24v,
.fr-py-12w {
  padding-top: 6rem !important;
}

.fr-pb-24v,
.fr-pb-12w,
.fr-py-24v,
.fr-py-12w {
  padding-bottom: 6rem !important;
}

.fr-p-25v {
  padding: 6.25rem !important;
}

.fr-pl-25v,
.fr-px-25v {
  padding-left: 6.25rem !important;
}

.fr-pr-25v,
.fr-px-25v {
  padding-right: 6.25rem !important;
}

.fr-pt-25v,
.fr-py-25v {
  padding-top: 6.25rem !important;
}

.fr-pb-25v,
.fr-py-25v {
  padding-bottom: 6.25rem !important;
}

.fr-p-26v,
.fr-p-13w {
  padding: 6.5rem !important;
}

.fr-pl-26v,
.fr-pl-13w,
.fr-px-26v,
.fr-px-13w {
  padding-left: 6.5rem !important;
}

.fr-pr-26v,
.fr-pr-13w,
.fr-px-26v,
.fr-px-13w {
  padding-right: 6.5rem !important;
}

.fr-pt-26v,
.fr-pt-13w,
.fr-py-26v,
.fr-py-13w {
  padding-top: 6.5rem !important;
}

.fr-pb-26v,
.fr-pb-13w,
.fr-py-26v,
.fr-py-13w {
  padding-bottom: 6.5rem !important;
}

.fr-p-27v {
  padding: 6.75rem !important;
}

.fr-pl-27v,
.fr-px-27v {
  padding-left: 6.75rem !important;
}

.fr-pr-27v,
.fr-px-27v {
  padding-right: 6.75rem !important;
}

.fr-pt-27v,
.fr-py-27v {
  padding-top: 6.75rem !important;
}

.fr-pb-27v,
.fr-py-27v {
  padding-bottom: 6.75rem !important;
}

.fr-p-28v,
.fr-p-14w {
  padding: 7rem !important;
}

.fr-pl-28v,
.fr-pl-14w,
.fr-px-28v,
.fr-px-14w {
  padding-left: 7rem !important;
}

.fr-pr-28v,
.fr-pr-14w,
.fr-px-28v,
.fr-px-14w {
  padding-right: 7rem !important;
}

.fr-pt-28v,
.fr-pt-14w,
.fr-py-28v,
.fr-py-14w {
  padding-top: 7rem !important;
}

.fr-pb-28v,
.fr-pb-14w,
.fr-py-28v,
.fr-py-14w {
  padding-bottom: 7rem !important;
}

.fr-p-29v {
  padding: 7.25rem !important;
}

.fr-pl-29v,
.fr-px-29v {
  padding-left: 7.25rem !important;
}

.fr-pr-29v,
.fr-px-29v {
  padding-right: 7.25rem !important;
}

.fr-pt-29v,
.fr-py-29v {
  padding-top: 7.25rem !important;
}

.fr-pb-29v,
.fr-py-29v {
  padding-bottom: 7.25rem !important;
}

.fr-p-30v,
.fr-p-15w {
  padding: 7.5rem !important;
}

.fr-pl-30v,
.fr-pl-15w,
.fr-px-30v,
.fr-px-15w {
  padding-left: 7.5rem !important;
}

.fr-pr-30v,
.fr-pr-15w,
.fr-px-30v,
.fr-px-15w {
  padding-right: 7.5rem !important;
}

.fr-pt-30v,
.fr-pt-15w,
.fr-py-30v,
.fr-py-15w {
  padding-top: 7.5rem !important;
}

.fr-pb-30v,
.fr-pb-15w,
.fr-py-30v,
.fr-py-15w {
  padding-bottom: 7.5rem !important;
}

.fr-p-31v {
  padding: 7.75rem !important;
}

.fr-pl-31v,
.fr-px-31v {
  padding-left: 7.75rem !important;
}

.fr-pr-31v,
.fr-px-31v {
  padding-right: 7.75rem !important;
}

.fr-pt-31v,
.fr-py-31v {
  padding-top: 7.75rem !important;
}

.fr-pb-31v,
.fr-py-31v {
  padding-bottom: 7.75rem !important;
}

.fr-p-32v,
.fr-p-16w {
  padding: 8rem !important;
}

.fr-pl-32v,
.fr-pl-16w,
.fr-px-32v,
.fr-px-16w {
  padding-left: 8rem !important;
}

.fr-pr-32v,
.fr-pr-16w,
.fr-px-32v,
.fr-px-16w {
  padding-right: 8rem !important;
}

.fr-pt-32v,
.fr-pt-16w,
.fr-py-32v,
.fr-py-16w {
  padding-top: 8rem !important;
}

.fr-pb-32v,
.fr-pb-16w,
.fr-py-32v,
.fr-py-16w {
  padding-bottom: 8rem !important;
}

.fr-p-first-0 {
  padding: 0 !important;
}

.fr-pl-first-0,
.fr-px-first-0 {
  padding-left: 0 !important;
}

.fr-pr-first-0,
.fr-px-first-0 {
  padding-right: 0 !important;
}

.fr-pt-first-0,
.fr-py-first-0 {
  padding-top: 0 !important;
}

.fr-pb-first-0,
.fr-py-first-0 {
  padding-bottom: 0 !important;
}

.fr-p-first-0-5v {
  padding: 0.125rem !important;
}

.fr-pl-first-0-5v,
.fr-px-first-0-5v {
  padding-left: 0.125rem !important;
}

.fr-pr-first-0-5v,
.fr-px-first-0-5v {
  padding-right: 0.125rem !important;
}

.fr-pt-first-0-5v,
.fr-py-first-0-5v {
  padding-top: 0.125rem !important;
}

.fr-pb-first-0-5v,
.fr-py-first-0-5v {
  padding-bottom: 0.125rem !important;
}

.fr-p-first-1v {
  padding: 0.25rem !important;
}

.fr-pl-first-1v,
.fr-px-first-1v {
  padding-left: 0.25rem !important;
}

.fr-pr-first-1v,
.fr-px-first-1v {
  padding-right: 0.25rem !important;
}

.fr-pt-first-1v,
.fr-py-first-1v {
  padding-top: 0.25rem !important;
}

.fr-pb-first-1v,
.fr-py-first-1v {
  padding-bottom: 0.25rem !important;
}

.fr-p-first-1-5v {
  padding: 0.375rem !important;
}

.fr-pl-first-1-5v,
.fr-px-first-1-5v {
  padding-left: 0.375rem !important;
}

.fr-pr-first-1-5v,
.fr-px-first-1-5v {
  padding-right: 0.375rem !important;
}

.fr-pt-first-1-5v,
.fr-py-first-1-5v {
  padding-top: 0.375rem !important;
}

.fr-pb-first-1-5v,
.fr-py-first-1-5v {
  padding-bottom: 0.375rem !important;
}

.fr-p-first-2v,
.fr-p-first-1w {
  padding: 0.5rem !important;
}

.fr-pl-first-2v,
.fr-pl-first-1w,
.fr-px-first-2v,
.fr-px-first-1w {
  padding-left: 0.5rem !important;
}

.fr-pr-first-2v,
.fr-pr-first-1w,
.fr-px-first-2v,
.fr-px-first-1w {
  padding-right: 0.5rem !important;
}

.fr-pt-first-2v,
.fr-pt-first-1w,
.fr-py-first-2v,
.fr-py-first-1w {
  padding-top: 0.5rem !important;
}

.fr-pb-first-2v,
.fr-pb-first-1w,
.fr-py-first-2v,
.fr-py-first-1w {
  padding-bottom: 0.5rem !important;
}

.fr-p-first-3v {
  padding: 0.75rem !important;
}

.fr-pl-first-3v,
.fr-px-first-3v {
  padding-left: 0.75rem !important;
}

.fr-pr-first-3v,
.fr-px-first-3v {
  padding-right: 0.75rem !important;
}

.fr-pt-first-3v,
.fr-py-first-3v {
  padding-top: 0.75rem !important;
}

.fr-pb-first-3v,
.fr-py-first-3v {
  padding-bottom: 0.75rem !important;
}

.fr-p-first-4v,
.fr-p-first-2w {
  padding: 1rem !important;
}

.fr-pl-first-4v,
.fr-pl-first-2w,
.fr-px-first-4v,
.fr-px-first-2w {
  padding-left: 1rem !important;
}

.fr-pr-first-4v,
.fr-pr-first-2w,
.fr-px-first-4v,
.fr-px-first-2w {
  padding-right: 1rem !important;
}

.fr-pt-first-4v,
.fr-pt-first-2w,
.fr-py-first-4v,
.fr-py-first-2w {
  padding-top: 1rem !important;
}

.fr-pb-first-4v,
.fr-pb-first-2w,
.fr-py-first-4v,
.fr-py-first-2w {
  padding-bottom: 1rem !important;
}

.fr-p-first-5v {
  padding: 1.25rem !important;
}

.fr-pl-first-5v,
.fr-px-first-5v {
  padding-left: 1.25rem !important;
}

.fr-pr-first-5v,
.fr-px-first-5v {
  padding-right: 1.25rem !important;
}

.fr-pt-first-5v,
.fr-py-first-5v {
  padding-top: 1.25rem !important;
}

.fr-pb-first-5v,
.fr-py-first-5v {
  padding-bottom: 1.25rem !important;
}

.fr-p-first-6v,
.fr-p-first-3w {
  padding: 1.5rem !important;
}

.fr-pl-first-6v,
.fr-pl-first-3w,
.fr-px-first-6v,
.fr-px-first-3w {
  padding-left: 1.5rem !important;
}

.fr-pr-first-6v,
.fr-pr-first-3w,
.fr-px-first-6v,
.fr-px-first-3w {
  padding-right: 1.5rem !important;
}

.fr-pt-first-6v,
.fr-pt-first-3w,
.fr-py-first-6v,
.fr-py-first-3w {
  padding-top: 1.5rem !important;
}

.fr-pb-first-6v,
.fr-pb-first-3w,
.fr-py-first-6v,
.fr-py-first-3w {
  padding-bottom: 1.5rem !important;
}

.fr-p-first-7v {
  padding: 1.75rem !important;
}

.fr-pl-first-7v,
.fr-px-first-7v {
  padding-left: 1.75rem !important;
}

.fr-pr-first-7v,
.fr-px-first-7v {
  padding-right: 1.75rem !important;
}

.fr-pt-first-7v,
.fr-py-first-7v {
  padding-top: 1.75rem !important;
}

.fr-pb-first-7v,
.fr-py-first-7v {
  padding-bottom: 1.75rem !important;
}

.fr-p-first-8v,
.fr-p-first-4w {
  padding: 2rem !important;
}

.fr-pl-first-8v,
.fr-pl-first-4w,
.fr-px-first-8v,
.fr-px-first-4w {
  padding-left: 2rem !important;
}

.fr-pr-first-8v,
.fr-pr-first-4w,
.fr-px-first-8v,
.fr-px-first-4w {
  padding-right: 2rem !important;
}

.fr-pt-first-8v,
.fr-pt-first-4w,
.fr-py-first-8v,
.fr-py-first-4w {
  padding-top: 2rem !important;
}

.fr-pb-first-8v,
.fr-pb-first-4w,
.fr-py-first-8v,
.fr-py-first-4w {
  padding-bottom: 2rem !important;
}

.fr-p-first-9v {
  padding: 2.25rem !important;
}

.fr-pl-first-9v,
.fr-px-first-9v {
  padding-left: 2.25rem !important;
}

.fr-pr-first-9v,
.fr-px-first-9v {
  padding-right: 2.25rem !important;
}

.fr-pt-first-9v,
.fr-py-first-9v {
  padding-top: 2.25rem !important;
}

.fr-pb-first-9v,
.fr-py-first-9v {
  padding-bottom: 2.25rem !important;
}

.fr-p-first-10v,
.fr-p-first-5w {
  padding: 2.5rem !important;
}

.fr-pl-first-10v,
.fr-pl-first-5w,
.fr-px-first-10v,
.fr-px-first-5w {
  padding-left: 2.5rem !important;
}

.fr-pr-first-10v,
.fr-pr-first-5w,
.fr-px-first-10v,
.fr-px-first-5w {
  padding-right: 2.5rem !important;
}

.fr-pt-first-10v,
.fr-pt-first-5w,
.fr-py-first-10v,
.fr-py-first-5w {
  padding-top: 2.5rem !important;
}

.fr-pb-first-10v,
.fr-pb-first-5w,
.fr-py-first-10v,
.fr-py-first-5w {
  padding-bottom: 2.5rem !important;
}

.fr-p-first-11v {
  padding: 2.75rem !important;
}

.fr-pl-first-11v,
.fr-px-first-11v {
  padding-left: 2.75rem !important;
}

.fr-pr-first-11v,
.fr-px-first-11v {
  padding-right: 2.75rem !important;
}

.fr-pt-first-11v,
.fr-py-first-11v {
  padding-top: 2.75rem !important;
}

.fr-pb-first-11v,
.fr-py-first-11v {
  padding-bottom: 2.75rem !important;
}

.fr-p-first-12v,
.fr-p-first-6w {
  padding: 3rem !important;
}

.fr-pl-first-12v,
.fr-pl-first-6w,
.fr-px-first-12v,
.fr-px-first-6w {
  padding-left: 3rem !important;
}

.fr-pr-first-12v,
.fr-pr-first-6w,
.fr-px-first-12v,
.fr-px-first-6w {
  padding-right: 3rem !important;
}

.fr-pt-first-12v,
.fr-pt-first-6w,
.fr-py-first-12v,
.fr-py-first-6w {
  padding-top: 3rem !important;
}

.fr-pb-first-12v,
.fr-pb-first-6w,
.fr-py-first-12v,
.fr-py-first-6w {
  padding-bottom: 3rem !important;
}

.fr-p-first-13v {
  padding: 3.25rem !important;
}

.fr-pl-first-13v,
.fr-px-first-13v {
  padding-left: 3.25rem !important;
}

.fr-pr-first-13v,
.fr-px-first-13v {
  padding-right: 3.25rem !important;
}

.fr-pt-first-13v,
.fr-py-first-13v {
  padding-top: 3.25rem !important;
}

.fr-pb-first-13v,
.fr-py-first-13v {
  padding-bottom: 3.25rem !important;
}

.fr-p-first-14v,
.fr-p-first-7w {
  padding: 3.5rem !important;
}

.fr-pl-first-14v,
.fr-pl-first-7w,
.fr-px-first-14v,
.fr-px-first-7w {
  padding-left: 3.5rem !important;
}

.fr-pr-first-14v,
.fr-pr-first-7w,
.fr-px-first-14v,
.fr-px-first-7w {
  padding-right: 3.5rem !important;
}

.fr-pt-first-14v,
.fr-pt-first-7w,
.fr-py-first-14v,
.fr-py-first-7w {
  padding-top: 3.5rem !important;
}

.fr-pb-first-14v,
.fr-pb-first-7w,
.fr-py-first-14v,
.fr-py-first-7w {
  padding-bottom: 3.5rem !important;
}

.fr-p-first-15v {
  padding: 3.75rem !important;
}

.fr-pl-first-15v,
.fr-px-first-15v {
  padding-left: 3.75rem !important;
}

.fr-pr-first-15v,
.fr-px-first-15v {
  padding-right: 3.75rem !important;
}

.fr-pt-first-15v,
.fr-py-first-15v {
  padding-top: 3.75rem !important;
}

.fr-pb-first-15v,
.fr-py-first-15v {
  padding-bottom: 3.75rem !important;
}

.fr-p-first-16v,
.fr-p-first-8w {
  padding: 4rem !important;
}

.fr-pl-first-16v,
.fr-pl-first-8w,
.fr-px-first-16v,
.fr-px-first-8w {
  padding-left: 4rem !important;
}

.fr-pr-first-16v,
.fr-pr-first-8w,
.fr-px-first-16v,
.fr-px-first-8w {
  padding-right: 4rem !important;
}

.fr-pt-first-16v,
.fr-pt-first-8w,
.fr-py-first-16v,
.fr-py-first-8w {
  padding-top: 4rem !important;
}

.fr-pb-first-16v,
.fr-pb-first-8w,
.fr-py-first-16v,
.fr-py-first-8w {
  padding-bottom: 4rem !important;
}

.fr-p-first-17v {
  padding: 4.25rem !important;
}

.fr-pl-first-17v,
.fr-px-first-17v {
  padding-left: 4.25rem !important;
}

.fr-pr-first-17v,
.fr-px-first-17v {
  padding-right: 4.25rem !important;
}

.fr-pt-first-17v,
.fr-py-first-17v {
  padding-top: 4.25rem !important;
}

.fr-pb-first-17v,
.fr-py-first-17v {
  padding-bottom: 4.25rem !important;
}

.fr-p-first-18v,
.fr-p-first-9w {
  padding: 4.5rem !important;
}

.fr-pl-first-18v,
.fr-pl-first-9w,
.fr-px-first-18v,
.fr-px-first-9w {
  padding-left: 4.5rem !important;
}

.fr-pr-first-18v,
.fr-pr-first-9w,
.fr-px-first-18v,
.fr-px-first-9w {
  padding-right: 4.5rem !important;
}

.fr-pt-first-18v,
.fr-pt-first-9w,
.fr-py-first-18v,
.fr-py-first-9w {
  padding-top: 4.5rem !important;
}

.fr-pb-first-18v,
.fr-pb-first-9w,
.fr-py-first-18v,
.fr-py-first-9w {
  padding-bottom: 4.5rem !important;
}

.fr-p-first-19v {
  padding: 4.75rem !important;
}

.fr-pl-first-19v,
.fr-px-first-19v {
  padding-left: 4.75rem !important;
}

.fr-pr-first-19v,
.fr-px-first-19v {
  padding-right: 4.75rem !important;
}

.fr-pt-first-19v,
.fr-py-first-19v {
  padding-top: 4.75rem !important;
}

.fr-pb-first-19v,
.fr-py-first-19v {
  padding-bottom: 4.75rem !important;
}

.fr-p-first-20v,
.fr-p-first-10w {
  padding: 5rem !important;
}

.fr-pl-first-20v,
.fr-pl-first-10w,
.fr-px-first-20v,
.fr-px-first-10w {
  padding-left: 5rem !important;
}

.fr-pr-first-20v,
.fr-pr-first-10w,
.fr-px-first-20v,
.fr-px-first-10w {
  padding-right: 5rem !important;
}

.fr-pt-first-20v,
.fr-pt-first-10w,
.fr-py-first-20v,
.fr-py-first-10w {
  padding-top: 5rem !important;
}

.fr-pb-first-20v,
.fr-pb-first-10w,
.fr-py-first-20v,
.fr-py-first-10w {
  padding-bottom: 5rem !important;
}

.fr-p-first-21v {
  padding: 5.25rem !important;
}

.fr-pl-first-21v,
.fr-px-first-21v {
  padding-left: 5.25rem !important;
}

.fr-pr-first-21v,
.fr-px-first-21v {
  padding-right: 5.25rem !important;
}

.fr-pt-first-21v,
.fr-py-first-21v {
  padding-top: 5.25rem !important;
}

.fr-pb-first-21v,
.fr-py-first-21v {
  padding-bottom: 5.25rem !important;
}

.fr-p-first-22v,
.fr-p-first-11w {
  padding: 5.5rem !important;
}

.fr-pl-first-22v,
.fr-pl-first-11w,
.fr-px-first-22v,
.fr-px-first-11w {
  padding-left: 5.5rem !important;
}

.fr-pr-first-22v,
.fr-pr-first-11w,
.fr-px-first-22v,
.fr-px-first-11w {
  padding-right: 5.5rem !important;
}

.fr-pt-first-22v,
.fr-pt-first-11w,
.fr-py-first-22v,
.fr-py-first-11w {
  padding-top: 5.5rem !important;
}

.fr-pb-first-22v,
.fr-pb-first-11w,
.fr-py-first-22v,
.fr-py-first-11w {
  padding-bottom: 5.5rem !important;
}

.fr-p-first-23v {
  padding: 5.75rem !important;
}

.fr-pl-first-23v,
.fr-px-first-23v {
  padding-left: 5.75rem !important;
}

.fr-pr-first-23v,
.fr-px-first-23v {
  padding-right: 5.75rem !important;
}

.fr-pt-first-23v,
.fr-py-first-23v {
  padding-top: 5.75rem !important;
}

.fr-pb-first-23v,
.fr-py-first-23v {
  padding-bottom: 5.75rem !important;
}

.fr-p-first-24v,
.fr-p-first-12w {
  padding: 6rem !important;
}

.fr-pl-first-24v,
.fr-pl-first-12w,
.fr-px-first-24v,
.fr-px-first-12w {
  padding-left: 6rem !important;
}

.fr-pr-first-24v,
.fr-pr-first-12w,
.fr-px-first-24v,
.fr-px-first-12w {
  padding-right: 6rem !important;
}

.fr-pt-first-24v,
.fr-pt-first-12w,
.fr-py-first-24v,
.fr-py-first-12w {
  padding-top: 6rem !important;
}

.fr-pb-first-24v,
.fr-pb-first-12w,
.fr-py-first-24v,
.fr-py-first-12w {
  padding-bottom: 6rem !important;
}

.fr-p-first-25v {
  padding: 6.25rem !important;
}

.fr-pl-first-25v,
.fr-px-first-25v {
  padding-left: 6.25rem !important;
}

.fr-pr-first-25v,
.fr-px-first-25v {
  padding-right: 6.25rem !important;
}

.fr-pt-first-25v,
.fr-py-first-25v {
  padding-top: 6.25rem !important;
}

.fr-pb-first-25v,
.fr-py-first-25v {
  padding-bottom: 6.25rem !important;
}

.fr-p-first-26v,
.fr-p-first-13w {
  padding: 6.5rem !important;
}

.fr-pl-first-26v,
.fr-pl-first-13w,
.fr-px-first-26v,
.fr-px-first-13w {
  padding-left: 6.5rem !important;
}

.fr-pr-first-26v,
.fr-pr-first-13w,
.fr-px-first-26v,
.fr-px-first-13w {
  padding-right: 6.5rem !important;
}

.fr-pt-first-26v,
.fr-pt-first-13w,
.fr-py-first-26v,
.fr-py-first-13w {
  padding-top: 6.5rem !important;
}

.fr-pb-first-26v,
.fr-pb-first-13w,
.fr-py-first-26v,
.fr-py-first-13w {
  padding-bottom: 6.5rem !important;
}

.fr-p-first-27v {
  padding: 6.75rem !important;
}

.fr-pl-first-27v,
.fr-px-first-27v {
  padding-left: 6.75rem !important;
}

.fr-pr-first-27v,
.fr-px-first-27v {
  padding-right: 6.75rem !important;
}

.fr-pt-first-27v,
.fr-py-first-27v {
  padding-top: 6.75rem !important;
}

.fr-pb-first-27v,
.fr-py-first-27v {
  padding-bottom: 6.75rem !important;
}

.fr-p-first-28v,
.fr-p-first-14w {
  padding: 7rem !important;
}

.fr-pl-first-28v,
.fr-pl-first-14w,
.fr-px-first-28v,
.fr-px-first-14w {
  padding-left: 7rem !important;
}

.fr-pr-first-28v,
.fr-pr-first-14w,
.fr-px-first-28v,
.fr-px-first-14w {
  padding-right: 7rem !important;
}

.fr-pt-first-28v,
.fr-pt-first-14w,
.fr-py-first-28v,
.fr-py-first-14w {
  padding-top: 7rem !important;
}

.fr-pb-first-28v,
.fr-pb-first-14w,
.fr-py-first-28v,
.fr-py-first-14w {
  padding-bottom: 7rem !important;
}

.fr-p-first-29v {
  padding: 7.25rem !important;
}

.fr-pl-first-29v,
.fr-px-first-29v {
  padding-left: 7.25rem !important;
}

.fr-pr-first-29v,
.fr-px-first-29v {
  padding-right: 7.25rem !important;
}

.fr-pt-first-29v,
.fr-py-first-29v {
  padding-top: 7.25rem !important;
}

.fr-pb-first-29v,
.fr-py-first-29v {
  padding-bottom: 7.25rem !important;
}

.fr-p-first-30v,
.fr-p-first-15w {
  padding: 7.5rem !important;
}

.fr-pl-first-30v,
.fr-pl-first-15w,
.fr-px-first-30v,
.fr-px-first-15w {
  padding-left: 7.5rem !important;
}

.fr-pr-first-30v,
.fr-pr-first-15w,
.fr-px-first-30v,
.fr-px-first-15w {
  padding-right: 7.5rem !important;
}

.fr-pt-first-30v,
.fr-pt-first-15w,
.fr-py-first-30v,
.fr-py-first-15w {
  padding-top: 7.5rem !important;
}

.fr-pb-first-30v,
.fr-pb-first-15w,
.fr-py-first-30v,
.fr-py-first-15w {
  padding-bottom: 7.5rem !important;
}

.fr-p-first-31v {
  padding: 7.75rem !important;
}

.fr-pl-first-31v,
.fr-px-first-31v {
  padding-left: 7.75rem !important;
}

.fr-pr-first-31v,
.fr-px-first-31v {
  padding-right: 7.75rem !important;
}

.fr-pt-first-31v,
.fr-py-first-31v {
  padding-top: 7.75rem !important;
}

.fr-pb-first-31v,
.fr-py-first-31v {
  padding-bottom: 7.75rem !important;
}

.fr-p-first-32v,
.fr-p-first-16w {
  padding: 8rem !important;
}

.fr-pl-first-32v,
.fr-pl-first-16w,
.fr-px-first-32v,
.fr-px-first-16w {
  padding-left: 8rem !important;
}

.fr-pr-first-32v,
.fr-pr-first-16w,
.fr-px-first-32v,
.fr-px-first-16w {
  padding-right: 8rem !important;
}

.fr-pt-first-32v,
.fr-pt-first-16w,
.fr-py-first-32v,
.fr-py-first-16w {
  padding-top: 8rem !important;
}

.fr-pb-first-32v,
.fr-pb-first-16w,
.fr-py-first-32v,
.fr-py-first-16w {
  padding-bottom: 8rem !important;
}

:root[data-fr-theme=dark] {
  --shadow-color: rgba(0, 0, 18, 0.32);
}

.fr-placement {
  position: fixed;
  top: 0;
  left: 0;
}

@-moz-document url-prefix() {
  :root[data-fr-scrolling] body {
    position: sticky;
  }
  :root {
    --underline-thickness: calc(0.0625em + 0.25px);
  }
}
.fr-displayed-lg {
  display: none !important;
}

.fr-responsive-img--32x9 {
  aspect-ratio: 3.5555555556 !important;
  -o-object-fit: cover;
     object-fit: cover;
  -o-object-position: 50% 50%;
     object-position: 50% 50%;
}

.fr-responsive-img--16x9 {
  aspect-ratio: 1.7777777778 !important;
  -o-object-fit: cover;
     object-fit: cover;
  -o-object-position: 50% 50%;
     object-position: 50% 50%;
}

.fr-responsive-img--3x2 {
  aspect-ratio: 1.5 !important;
  -o-object-fit: cover;
     object-fit: cover;
  -o-object-position: 50% 50%;
     object-position: 50% 50%;
}

.fr-responsive-img--4x3 {
  aspect-ratio: 1.3333333333 !important;
  -o-object-fit: cover;
     object-fit: cover;
  -o-object-position: 50% 50%;
     object-position: 50% 50%;
}

.fr-responsive-img--1x1 {
  aspect-ratio: 1 !important;
  -o-object-fit: cover;
     object-fit: cover;
  -o-object-position: 50% 50%;
     object-position: 50% 50%;
}

.fr-responsive-img--3x4 {
  aspect-ratio: 0.75 !important;
  -o-object-fit: cover;
     object-fit: cover;
  -o-object-position: 50% 50%;
     object-position: 50% 50%;
}

.fr-responsive-img--2x3 {
  aspect-ratio: 0.6666666667 !important;
  -o-object-fit: cover;
     object-fit: cover;
  -o-object-position: 50% 50%;
     object-position: 50% 50%;
}

.fr-responsive-vid--16x9 {
  aspect-ratio: 1.7777777778 !important;
}

.fr-responsive-vid--4x3 {
  aspect-ratio: 1.3333333333 !important;
}

.fr-responsive-vid--1x1 {
  aspect-ratio: 1 !important;
}

.fr-fi--xs::before,
.fr-fi--xs::after {
  --icon-size: 0.75rem;
}

.fr-fi--sm::before,
.fr-fi--sm::after {
  --icon-size: 1rem;
}

.fr-fi--md::before,
.fr-fi--md::after {
  --icon-size: 1.5rem;
}

.fr-fi--lg::before,
.fr-fi--lg::after {
  --icon-size: 2rem;
}

.fr-artwork-decorative {
  fill: var(--artwork-decorative-blue-france);
}

.fr-artwork-minor {
  fill: var(--artwork-minor-red-marianne);
}

.fr-artwork-major {
  fill: var(--artwork-major-blue-france);
}

.fr-artwork-background {
  fill: var(--artwork-background-grey);
}

.fr-artwork-motif {
  fill: var(--artwork-motif-grey);
}

.fr-artwork--green-tilleul-verveine .fr-artwork-minor {
  fill: var(--artwork-minor-green-tilleul-verveine);
}

.fr-artwork--green-bourgeon .fr-artwork-minor {
  fill: var(--artwork-minor-green-bourgeon);
}

.fr-artwork--green-emeraude .fr-artwork-minor {
  fill: var(--artwork-minor-green-emeraude);
}

.fr-artwork--green-menthe .fr-artwork-minor {
  fill: var(--artwork-minor-green-menthe);
}

.fr-artwork--green-archipel .fr-artwork-minor {
  fill: var(--artwork-minor-green-archipel);
}

.fr-artwork--blue-ecume .fr-artwork-minor {
  fill: var(--artwork-minor-blue-ecume);
}

.fr-artwork--blue-cumulus .fr-artwork-minor {
  fill: var(--artwork-minor-blue-cumulus);
}

.fr-artwork--purple-glycine .fr-artwork-minor {
  fill: var(--artwork-minor-purple-glycine);
}

.fr-artwork--pink-macaron .fr-artwork-minor {
  fill: var(--artwork-minor-pink-macaron);
}

.fr-artwork--pink-tuile .fr-artwork-minor {
  fill: var(--artwork-minor-pink-tuile);
}

.fr-artwork--yellow-tournesol .fr-artwork-minor {
  fill: var(--artwork-minor-yellow-tournesol);
}

.fr-artwork--yellow-moutarde .fr-artwork-minor {
  fill: var(--artwork-minor-yellow-moutarde);
}

.fr-artwork--orange-terre-battue .fr-artwork-minor {
  fill: var(--artwork-minor-orange-terre-battue);
}

.fr-artwork--brown-cafe-creme .fr-artwork-minor {
  fill: var(--artwork-minor-brown-cafe-creme);
}

.fr-artwork--brown-caramel .fr-artwork-minor {
  fill: var(--artwork-minor-brown-caramel);
}

.fr-artwork--brown-opera .fr-artwork-minor {
  fill: var(--artwork-minor-brown-opera);
}

.fr-artwork--beige-gris-galet .fr-artwork-minor {
  fill: var(--artwork-minor-beige-gris-galet);
}

[disabled] .fr-artwork * {
  fill: var(--text-disabled-grey);
}

.fr-h6,
.fr-h5,
.fr-h4,
.fr-h3,
.fr-h2,
.fr-h1,
.fr-display-xs,
.fr-display-sm,
.fr-display-md,
.fr-display-lg,
.fr-display-xl {
  color: var(--text-title-grey);
}

h6,
h5,
h4,
h3,
h2,
h1 {
  color: var(--text-title-grey);
}

@media (min-width: 36em) {
  /*! media sm */
  .fr-hidden-sm {
    display: none !important;
  }
  .fr-unhidden-sm {
    display: inherit !important;
  }
  .fr-sr-only-sm {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap; /* added line */
    border: 0;
    display: block;
  }
  .fr-container-sm {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  .fr-container-sm--fluid {
    padding-left: 0;
    padding-right: 0;
    max-width: none;
    overflow: hidden;
  }
  .fr-grid-row-sm--gutters {
    margin: -0.5rem;
  }
  .fr-grid-row-sm--gutters &gt; [class^=fr-col-],
  .fr-grid-row-sm--gutters &gt; [class*=&quot; fr-col-&quot;],
  .fr-grid-row-sm--gutters &gt; .fr-col {
    padding: 0.5rem;
  }
  .fr-grid-row-sm--no-gutters {
    margin: 0;
  }
  .fr-grid-row-sm--no-gutters &gt; [class^=fr-col-],
  .fr-grid-row-sm--no-gutters &gt; [class*=&quot; fr-col-&quot;],
  .fr-grid-row-sm--no-gutters &gt; .fr-col {
    padding: 0;
  }
  .fr-col-sm {
    flex: 1;
  }
  .fr-col-sm-1 {
    flex: 0 0 8.3333333333%;
    width: 8.3333333333%;
    max-width: 8.3333333333%;
  }
  .fr-col-offset-sm-1:not(.fr-col-offset-sm-1--right) {
    margin-left: 8.3333333333%;
  }
  .fr-col-offset-sm-1--right {
    margin-right: 8.3333333333%;
  }
  .fr-col-sm-2 {
    flex: 0 0 16.6666666667%;
    width: 16.6666666667%;
    max-width: 16.6666666667%;
  }
  .fr-col-offset-sm-2:not(.fr-col-offset-sm-2--right) {
    margin-left: 16.6666666667%;
  }
  .fr-col-offset-sm-2--right {
    margin-right: 16.6666666667%;
  }
  .fr-col-sm-3 {
    flex: 0 0 25%;
    width: 25%;
    max-width: 25%;
  }
  .fr-col-offset-sm-3:not(.fr-col-offset-sm-3--right) {
    margin-left: 25%;
  }
  .fr-col-offset-sm-3--right {
    margin-right: 25%;
  }
  .fr-col-sm-4 {
    flex: 0 0 33.3333333333%;
    width: 33.3333333333%;
    max-width: 33.3333333333%;
  }
  .fr-col-offset-sm-4:not(.fr-col-offset-sm-4--right) {
    margin-left: 33.3333333333%;
  }
  .fr-col-offset-sm-4--right {
    margin-right: 33.3333333333%;
  }
  .fr-col-sm-5 {
    flex: 0 0 41.6666666667%;
    width: 41.6666666667%;
    max-width: 41.6666666667%;
  }
  .fr-col-offset-sm-5:not(.fr-col-offset-sm-5--right) {
    margin-left: 41.6666666667%;
  }
  .fr-col-offset-sm-5--right {
    margin-right: 41.6666666667%;
  }
  .fr-col-sm-6 {
    flex: 0 0 50%;
    width: 50%;
    max-width: 50%;
  }
  .fr-col-offset-sm-6:not(.fr-col-offset-sm-6--right) {
    margin-left: 50%;
  }
  .fr-col-offset-sm-6--right {
    margin-right: 50%;
  }
  .fr-col-sm-7 {
    flex: 0 0 58.3333333333%;
    width: 58.3333333333%;
    max-width: 58.3333333333%;
  }
  .fr-col-offset-sm-7:not(.fr-col-offset-sm-7--right) {
    margin-left: 58.3333333333%;
  }
  .fr-col-offset-sm-7--right {
    margin-right: 58.3333333333%;
  }
  .fr-col-sm-8 {
    flex: 0 0 66.6666666667%;
    width: 66.6666666667%;
    max-width: 66.6666666667%;
  }
  .fr-col-offset-sm-8:not(.fr-col-offset-sm-8--right) {
    margin-left: 66.6666666667%;
  }
  .fr-col-offset-sm-8--right {
    margin-right: 66.6666666667%;
  }
  .fr-col-sm-9 {
    flex: 0 0 75%;
    width: 75%;
    max-width: 75%;
  }
  .fr-col-offset-sm-9:not(.fr-col-offset-sm-9--right) {
    margin-left: 75%;
  }
  .fr-col-offset-sm-9--right {
    margin-right: 75%;
  }
  .fr-col-sm-10 {
    flex: 0 0 83.3333333333%;
    width: 83.3333333333%;
    max-width: 83.3333333333%;
  }
  .fr-col-offset-sm-10:not(.fr-col-offset-sm-10--right) {
    margin-left: 83.3333333333%;
  }
  .fr-col-offset-sm-10--right {
    margin-right: 83.3333333333%;
  }
  .fr-col-sm-11 {
    flex: 0 0 91.6666666667%;
    width: 91.6666666667%;
    max-width: 91.6666666667%;
  }
  .fr-col-offset-sm-11:not(.fr-col-offset-sm-11--right) {
    margin-left: 91.6666666667%;
  }
  .fr-col-offset-sm-11--right {
    margin-right: 91.6666666667%;
  }
  .fr-col-sm-12 {
    flex: 0 0 100%;
    width: 100%;
    max-width: 100%;
  }
  .fr-col-offset-sm-12:not(.fr-col-offset-sm-12--right) {
    margin-left: 100%;
  }
  .fr-col-offset-sm-12--right {
    margin-right: 100%;
  }
  /*! media sm */
}
@media (min-width: 48em) {
  /*! media md */
  h6 {
    font-size: 1.25rem;
    line-height: 1.75rem;
  }
  h5 {
    font-size: 1.375rem;
    line-height: 1.75rem;
  }
  h4 {
    font-size: 1.5rem;
    line-height: 2rem;
  }
  h3 {
    font-size: 1.75rem;
    line-height: 2.25rem;
  }
  h2 {
    font-size: 2rem;
    line-height: 2.5rem;
  }
  h1 {
    font-size: 2.5rem;
    line-height: 3rem;
  }
  .fr-h6 {
    font-size: 1.25rem !important;
    line-height: 1.75rem !important;
  }
  .fr-h5 {
    font-size: 1.375rem !important;
    line-height: 1.75rem !important;
  }
  .fr-h4 {
    font-size: 1.5rem !important;
    line-height: 2rem !important;
  }
  .fr-h3 {
    font-size: 1.75rem !important;
    line-height: 2.25rem !important;
  }
  .fr-h2 {
    font-size: 2rem !important;
    line-height: 2.5rem !important;
  }
  .fr-h1 {
    font-size: 2.5rem !important;
    line-height: 3rem !important;
  }
  .fr-display--xs {
    font-size: 3rem !important;
    line-height: 3.5rem !important;
  }
  .fr-display--sm {
    font-size: 3.5rem !important;
    line-height: 4rem !important;
  }
  .fr-display--md {
    font-size: 4rem !important;
    line-height: 4.5rem !important;
  }
  .fr-display--lg {
    font-size: 4.5rem !important;
    line-height: 5rem !important;
  }
  .fr-display--xl {
    font-size: 5rem !important;
    line-height: 5.5rem !important;
  }
  .fr-hidden-md {
    display: none !important;
  }
  .fr-unhidden-md {
    display: inherit !important;
  }
  .fr-sr-only-md {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap; /* added line */
    border: 0;
    display: block;
  }
  .fr-container-md {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  .fr-container-md--fluid {
    padding-left: 0;
    padding-right: 0;
    max-width: none;
    overflow: hidden;
  }
  .fr-grid-row-md--gutters {
    margin: -0.5rem;
  }
  .fr-grid-row-md--gutters &gt; [class^=fr-col-],
  .fr-grid-row-md--gutters &gt; [class*=&quot; fr-col-&quot;],
  .fr-grid-row-md--gutters &gt; .fr-col {
    padding: 0.5rem;
  }
  .fr-grid-row-md--no-gutters {
    margin: 0;
  }
  .fr-grid-row-md--no-gutters &gt; [class^=fr-col-],
  .fr-grid-row-md--no-gutters &gt; [class*=&quot; fr-col-&quot;],
  .fr-grid-row-md--no-gutters &gt; .fr-col {
    padding: 0;
  }
  .fr-col-md {
    flex: 1;
  }
  .fr-col-md-1 {
    flex: 0 0 8.3333333333%;
    width: 8.3333333333%;
    max-width: 8.3333333333%;
  }
  .fr-col-offset-md-1:not(.fr-col-offset-md-1--right) {
    margin-left: 8.3333333333%;
  }
  .fr-col-offset-md-1--right {
    margin-right: 8.3333333333%;
  }
  .fr-col-md-2 {
    flex: 0 0 16.6666666667%;
    width: 16.6666666667%;
    max-width: 16.6666666667%;
  }
  .fr-col-offset-md-2:not(.fr-col-offset-md-2--right) {
    margin-left: 16.6666666667%;
  }
  .fr-col-offset-md-2--right {
    margin-right: 16.6666666667%;
  }
  .fr-col-md-3 {
    flex: 0 0 25%;
    width: 25%;
    max-width: 25%;
  }
  .fr-col-offset-md-3:not(.fr-col-offset-md-3--right) {
    margin-left: 25%;
  }
  .fr-col-offset-md-3--right {
    margin-right: 25%;
  }
  .fr-col-md-4 {
    flex: 0 0 33.3333333333%;
    width: 33.3333333333%;
    max-width: 33.3333333333%;
  }
  .fr-col-offset-md-4:not(.fr-col-offset-md-4--right) {
    margin-left: 33.3333333333%;
  }
  .fr-col-offset-md-4--right {
    margin-right: 33.3333333333%;
  }
  .fr-col-md-5 {
    flex: 0 0 41.6666666667%;
    width: 41.6666666667%;
    max-width: 41.6666666667%;
  }
  .fr-col-offset-md-5:not(.fr-col-offset-md-5--right) {
    margin-left: 41.6666666667%;
  }
  .fr-col-offset-md-5--right {
    margin-right: 41.6666666667%;
  }
  .fr-col-md-6 {
    flex: 0 0 50%;
    width: 50%;
    max-width: 50%;
  }
  .fr-col-offset-md-6:not(.fr-col-offset-md-6--right) {
    margin-left: 50%;
  }
  .fr-col-offset-md-6--right {
    margin-right: 50%;
  }
  .fr-col-md-7 {
    flex: 0 0 58.3333333333%;
    width: 58.3333333333%;
    max-width: 58.3333333333%;
  }
  .fr-col-offset-md-7:not(.fr-col-offset-md-7--right) {
    margin-left: 58.3333333333%;
  }
  .fr-col-offset-md-7--right {
    margin-right: 58.3333333333%;
  }
  .fr-col-md-8 {
    flex: 0 0 66.6666666667%;
    width: 66.6666666667%;
    max-width: 66.6666666667%;
  }
  .fr-col-offset-md-8:not(.fr-col-offset-md-8--right) {
    margin-left: 66.6666666667%;
  }
  .fr-col-offset-md-8--right {
    margin-right: 66.6666666667%;
  }
  .fr-col-md-9 {
    flex: 0 0 75%;
    width: 75%;
    max-width: 75%;
  }
  .fr-col-offset-md-9:not(.fr-col-offset-md-9--right) {
    margin-left: 75%;
  }
  .fr-col-offset-md-9--right {
    margin-right: 75%;
  }
  .fr-col-md-10 {
    flex: 0 0 83.3333333333%;
    width: 83.3333333333%;
    max-width: 83.3333333333%;
  }
  .fr-col-offset-md-10:not(.fr-col-offset-md-10--right) {
    margin-left: 83.3333333333%;
  }
  .fr-col-offset-md-10--right {
    margin-right: 83.3333333333%;
  }
  .fr-col-md-11 {
    flex: 0 0 91.6666666667%;
    width: 91.6666666667%;
    max-width: 91.6666666667%;
  }
  .fr-col-offset-md-11:not(.fr-col-offset-md-11--right) {
    margin-left: 91.6666666667%;
  }
  .fr-col-offset-md-11--right {
    margin-right: 91.6666666667%;
  }
  .fr-col-md-12 {
    flex: 0 0 100%;
    width: 100%;
    max-width: 100%;
  }
  .fr-col-offset-md-12:not(.fr-col-offset-md-12--right) {
    margin-left: 100%;
  }
  .fr-col-offset-md-12--right {
    margin-right: 100%;
  }
  .fr-m-md-n8v,
  .fr-m-md-n4w {
    margin: -2rem !important;
  }
  .fr-ml-md-n8v,
  .fr-ml-md-n4w,
  .fr-mx-md-n8v,
  .fr-mx-md-n4w {
    margin-left: -2rem !important;
  }
  .fr-mr-md-n8v,
  .fr-mr-md-n4w,
  .fr-mx-md-n8v,
  .fr-mx-md-n4w {
    margin-right: -2rem !important;
  }
  .fr-mt-md-n8v,
  .fr-mt-md-n4w,
  .fr-my-md-n8v,
  .fr-my-md-n4w {
    margin-top: -2rem !important;
  }
  .fr-mb-md-n8v,
  .fr-mb-md-n4w,
  .fr-my-md-n8v,
  .fr-my-md-n4w {
    margin-bottom: -2rem !important;
  }
  .fr-m-md-n7v {
    margin: -1.75rem !important;
  }
  .fr-ml-md-n7v,
  .fr-mx-md-n7v {
    margin-left: -1.75rem !important;
  }
  .fr-mr-md-n7v,
  .fr-mx-md-n7v {
    margin-right: -1.75rem !important;
  }
  .fr-mt-md-n7v,
  .fr-my-md-n7v {
    margin-top: -1.75rem !important;
  }
  .fr-mb-md-n7v,
  .fr-my-md-n7v {
    margin-bottom: -1.75rem !important;
  }
  .fr-m-md-n6v,
  .fr-m-md-n3w {
    margin: -1.5rem !important;
  }
  .fr-ml-md-n6v,
  .fr-ml-md-n3w,
  .fr-mx-md-n6v,
  .fr-mx-md-n3w {
    margin-left: -1.5rem !important;
  }
  .fr-mr-md-n6v,
  .fr-mr-md-n3w,
  .fr-mx-md-n6v,
  .fr-mx-md-n3w {
    margin-right: -1.5rem !important;
  }
  .fr-mt-md-n6v,
  .fr-mt-md-n3w,
  .fr-my-md-n6v,
  .fr-my-md-n3w {
    margin-top: -1.5rem !important;
  }
  .fr-mb-md-n6v,
  .fr-mb-md-n3w,
  .fr-my-md-n6v,
  .fr-my-md-n3w {
    margin-bottom: -1.5rem !important;
  }
  .fr-m-md-n5v {
    margin: -1.25rem !important;
  }
  .fr-ml-md-n5v,
  .fr-mx-md-n5v {
    margin-left: -1.25rem !important;
  }
  .fr-mr-md-n5v,
  .fr-mx-md-n5v {
    margin-right: -1.25rem !important;
  }
  .fr-mt-md-n5v,
  .fr-my-md-n5v {
    margin-top: -1.25rem !important;
  }
  .fr-mb-md-n5v,
  .fr-my-md-n5v {
    margin-bottom: -1.25rem !important;
  }
  .fr-m-md-n4v,
  .fr-m-md-n2w {
    margin: -1rem !important;
  }
  .fr-ml-md-n4v,
  .fr-ml-md-n2w,
  .fr-mx-md-n4v,
  .fr-mx-md-n2w {
    margin-left: -1rem !important;
  }
  .fr-mr-md-n4v,
  .fr-mr-md-n2w,
  .fr-mx-md-n4v,
  .fr-mx-md-n2w {
    margin-right: -1rem !important;
  }
  .fr-mt-md-n4v,
  .fr-mt-md-n2w,
  .fr-my-md-n4v,
  .fr-my-md-n2w {
    margin-top: -1rem !important;
  }
  .fr-mb-md-n4v,
  .fr-mb-md-n2w,
  .fr-my-md-n4v,
  .fr-my-md-n2w {
    margin-bottom: -1rem !important;
  }
  .fr-m-md-n3v {
    margin: -0.75rem !important;
  }
  .fr-ml-md-n3v,
  .fr-mx-md-n3v {
    margin-left: -0.75rem !important;
  }
  .fr-mr-md-n3v,
  .fr-mx-md-n3v {
    margin-right: -0.75rem !important;
  }
  .fr-mt-md-n3v,
  .fr-my-md-n3v {
    margin-top: -0.75rem !important;
  }
  .fr-mb-md-n3v,
  .fr-my-md-n3v {
    margin-bottom: -0.75rem !important;
  }
  .fr-m-md-n2v,
  .fr-m-md-n1w {
    margin: -0.5rem !important;
  }
  .fr-ml-md-n2v,
  .fr-ml-md-n1w,
  .fr-mx-md-n2v,
  .fr-mx-md-n1w {
    margin-left: -0.5rem !important;
  }
  .fr-mr-md-n2v,
  .fr-mr-md-n1w,
  .fr-mx-md-n2v,
  .fr-mx-md-n1w {
    margin-right: -0.5rem !important;
  }
  .fr-mt-md-n2v,
  .fr-mt-md-n1w,
  .fr-my-md-n2v,
  .fr-my-md-n1w {
    margin-top: -0.5rem !important;
  }
  .fr-mb-md-n2v,
  .fr-mb-md-n1w,
  .fr-my-md-n2v,
  .fr-my-md-n1w {
    margin-bottom: -0.5rem !important;
  }
  .fr-m-md-n1v {
    margin: -0.25rem !important;
  }
  .fr-ml-md-n1v,
  .fr-mx-md-n1v {
    margin-left: -0.25rem !important;
  }
  .fr-mr-md-n1v,
  .fr-mx-md-n1v {
    margin-right: -0.25rem !important;
  }
  .fr-mt-md-n1v,
  .fr-my-md-n1v {
    margin-top: -0.25rem !important;
  }
  .fr-mb-md-n1v,
  .fr-my-md-n1v {
    margin-bottom: -0.25rem !important;
  }
  .fr-m-md-n1-5v {
    margin: -0.375rem !important;
  }
  .fr-ml-md-n1-5v,
  .fr-mx-md-n1-5v {
    margin-left: -0.375rem !important;
  }
  .fr-mr-md-n1-5v,
  .fr-mx-md-n1-5v {
    margin-right: -0.375rem !important;
  }
  .fr-mt-md-n1-5v,
  .fr-my-md-n1-5v {
    margin-top: -0.375rem !important;
  }
  .fr-mb-md-n1-5v,
  .fr-my-md-n1-5v {
    margin-bottom: -0.375rem !important;
  }
  .fr-m-md-0 {
    margin: 0 !important;
  }
  .fr-ml-md-0,
  .fr-mx-md-0 {
    margin-left: 0 !important;
  }
  .fr-mr-md-0,
  .fr-mx-md-0 {
    margin-right: 0 !important;
  }
  .fr-mt-md-0,
  .fr-my-md-0 {
    margin-top: 0 !important;
  }
  .fr-mb-md-0,
  .fr-my-md-0 {
    margin-bottom: 0 !important;
  }
  .fr-m-md-n0-5v {
    margin: -0.125rem !important;
  }
  .fr-ml-md-n0-5v,
  .fr-mx-md-n0-5v {
    margin-left: -0.125rem !important;
  }
  .fr-mr-md-n0-5v,
  .fr-mx-md-n0-5v {
    margin-right: -0.125rem !important;
  }
  .fr-mt-md-n0-5v,
  .fr-my-md-n0-5v {
    margin-top: -0.125rem !important;
  }
  .fr-mb-md-n0-5v,
  .fr-my-md-n0-5v {
    margin-bottom: -0.125rem !important;
  }
  .fr-m-md-0-5v {
    margin: 0.125rem !important;
  }
  .fr-ml-md-0-5v,
  .fr-mx-md-0-5v {
    margin-left: 0.125rem !important;
  }
  .fr-mr-md-0-5v,
  .fr-mx-md-0-5v {
    margin-right: 0.125rem !important;
  }
  .fr-mt-md-0-5v,
  .fr-my-md-0-5v {
    margin-top: 0.125rem !important;
  }
  .fr-mb-md-0-5v,
  .fr-my-md-0-5v {
    margin-bottom: 0.125rem !important;
  }
  .fr-m-md-1v {
    margin: 0.25rem !important;
  }
  .fr-ml-md-1v,
  .fr-mx-md-1v {
    margin-left: 0.25rem !important;
  }
  .fr-mr-md-1v,
  .fr-mx-md-1v {
    margin-right: 0.25rem !important;
  }
  .fr-mt-md-1v,
  .fr-my-md-1v {
    margin-top: 0.25rem !important;
  }
  .fr-mb-md-1v,
  .fr-my-md-1v {
    margin-bottom: 0.25rem !important;
  }
  .fr-m-md-1-5v {
    margin: 0.375rem !important;
  }
  .fr-ml-md-1-5v,
  .fr-mx-md-1-5v {
    margin-left: 0.375rem !important;
  }
  .fr-mr-md-1-5v,
  .fr-mx-md-1-5v {
    margin-right: 0.375rem !important;
  }
  .fr-mt-md-1-5v,
  .fr-my-md-1-5v {
    margin-top: 0.375rem !important;
  }
  .fr-mb-md-1-5v,
  .fr-my-md-1-5v {
    margin-bottom: 0.375rem !important;
  }
  .fr-m-md-2v,
  .fr-m-md-1w {
    margin: 0.5rem !important;
  }
  .fr-ml-md-2v,
  .fr-ml-md-1w,
  .fr-mx-md-2v,
  .fr-mx-md-1w {
    margin-left: 0.5rem !important;
  }
  .fr-mr-md-2v,
  .fr-mr-md-1w,
  .fr-mx-md-2v,
  .fr-mx-md-1w {
    margin-right: 0.5rem !important;
  }
  .fr-mt-md-2v,
  .fr-mt-md-1w,
  .fr-my-md-2v,
  .fr-my-md-1w {
    margin-top: 0.5rem !important;
  }
  .fr-mb-md-2v,
  .fr-mb-md-1w,
  .fr-my-md-2v,
  .fr-my-md-1w {
    margin-bottom: 0.5rem !important;
  }
  .fr-m-md-3v {
    margin: 0.75rem !important;
  }
  .fr-ml-md-3v,
  .fr-mx-md-3v {
    margin-left: 0.75rem !important;
  }
  .fr-mr-md-3v,
  .fr-mx-md-3v {
    margin-right: 0.75rem !important;
  }
  .fr-mt-md-3v,
  .fr-my-md-3v {
    margin-top: 0.75rem !important;
  }
  .fr-mb-md-3v,
  .fr-my-md-3v {
    margin-bottom: 0.75rem !important;
  }
  .fr-m-md-4v,
  .fr-m-md-2w {
    margin: 1rem !important;
  }
  .fr-ml-md-4v,
  .fr-ml-md-2w,
  .fr-mx-md-4v,
  .fr-mx-md-2w {
    margin-left: 1rem !important;
  }
  .fr-mr-md-4v,
  .fr-mr-md-2w,
  .fr-mx-md-4v,
  .fr-mx-md-2w {
    margin-right: 1rem !important;
  }
  .fr-mt-md-4v,
  .fr-mt-md-2w,
  .fr-my-md-4v,
  .fr-my-md-2w {
    margin-top: 1rem !important;
  }
  .fr-mb-md-4v,
  .fr-mb-md-2w,
  .fr-my-md-4v,
  .fr-my-md-2w {
    margin-bottom: 1rem !important;
  }
  .fr-m-md-5v {
    margin: 1.25rem !important;
  }
  .fr-ml-md-5v,
  .fr-mx-md-5v {
    margin-left: 1.25rem !important;
  }
  .fr-mr-md-5v,
  .fr-mx-md-5v {
    margin-right: 1.25rem !important;
  }
  .fr-mt-md-5v,
  .fr-my-md-5v {
    margin-top: 1.25rem !important;
  }
  .fr-mb-md-5v,
  .fr-my-md-5v {
    margin-bottom: 1.25rem !important;
  }
  .fr-m-md-6v,
  .fr-m-md-3w {
    margin: 1.5rem !important;
  }
  .fr-ml-md-6v,
  .fr-ml-md-3w,
  .fr-mx-md-6v,
  .fr-mx-md-3w {
    margin-left: 1.5rem !important;
  }
  .fr-mr-md-6v,
  .fr-mr-md-3w,
  .fr-mx-md-6v,
  .fr-mx-md-3w {
    margin-right: 1.5rem !important;
  }
  .fr-mt-md-6v,
  .fr-mt-md-3w,
  .fr-my-md-6v,
  .fr-my-md-3w {
    margin-top: 1.5rem !important;
  }
  .fr-mb-md-6v,
  .fr-mb-md-3w,
  .fr-my-md-6v,
  .fr-my-md-3w {
    margin-bottom: 1.5rem !important;
  }
  .fr-m-md-7v {
    margin: 1.75rem !important;
  }
  .fr-ml-md-7v,
  .fr-mx-md-7v {
    margin-left: 1.75rem !important;
  }
  .fr-mr-md-7v,
  .fr-mx-md-7v {
    margin-right: 1.75rem !important;
  }
  .fr-mt-md-7v,
  .fr-my-md-7v {
    margin-top: 1.75rem !important;
  }
  .fr-mb-md-7v,
  .fr-my-md-7v {
    margin-bottom: 1.75rem !important;
  }
  .fr-m-md-8v,
  .fr-m-md-4w {
    margin: 2rem !important;
  }
  .fr-ml-md-8v,
  .fr-ml-md-4w,
  .fr-mx-md-8v,
  .fr-mx-md-4w {
    margin-left: 2rem !important;
  }
  .fr-mr-md-8v,
  .fr-mr-md-4w,
  .fr-mx-md-8v,
  .fr-mx-md-4w {
    margin-right: 2rem !important;
  }
  .fr-mt-md-8v,
  .fr-mt-md-4w,
  .fr-my-md-8v,
  .fr-my-md-4w {
    margin-top: 2rem !important;
  }
  .fr-mb-md-8v,
  .fr-mb-md-4w,
  .fr-my-md-8v,
  .fr-my-md-4w {
    margin-bottom: 2rem !important;
  }
  .fr-m-md-9v {
    margin: 2.25rem !important;
  }
  .fr-ml-md-9v,
  .fr-mx-md-9v {
    margin-left: 2.25rem !important;
  }
  .fr-mr-md-9v,
  .fr-mx-md-9v {
    margin-right: 2.25rem !important;
  }
  .fr-mt-md-9v,
  .fr-my-md-9v {
    margin-top: 2.25rem !important;
  }
  .fr-mb-md-9v,
  .fr-my-md-9v {
    margin-bottom: 2.25rem !important;
  }
  .fr-m-md-10v,
  .fr-m-md-5w {
    margin: 2.5rem !important;
  }
  .fr-ml-md-10v,
  .fr-ml-md-5w,
  .fr-mx-md-10v,
  .fr-mx-md-5w {
    margin-left: 2.5rem !important;
  }
  .fr-mr-md-10v,
  .fr-mr-md-5w,
  .fr-mx-md-10v,
  .fr-mx-md-5w {
    margin-right: 2.5rem !important;
  }
  .fr-mt-md-10v,
  .fr-mt-md-5w,
  .fr-my-md-10v,
  .fr-my-md-5w {
    margin-top: 2.5rem !important;
  }
  .fr-mb-md-10v,
  .fr-mb-md-5w,
  .fr-my-md-10v,
  .fr-my-md-5w {
    margin-bottom: 2.5rem !important;
  }
  .fr-m-md-11v {
    margin: 2.75rem !important;
  }
  .fr-ml-md-11v,
  .fr-mx-md-11v {
    margin-left: 2.75rem !important;
  }
  .fr-mr-md-11v,
  .fr-mx-md-11v {
    margin-right: 2.75rem !important;
  }
  .fr-mt-md-11v,
  .fr-my-md-11v {
    margin-top: 2.75rem !important;
  }
  .fr-mb-md-11v,
  .fr-my-md-11v {
    margin-bottom: 2.75rem !important;
  }
  .fr-m-md-12v,
  .fr-m-md-6w {
    margin: 3rem !important;
  }
  .fr-ml-md-12v,
  .fr-ml-md-6w,
  .fr-mx-md-12v,
  .fr-mx-md-6w {
    margin-left: 3rem !important;
  }
  .fr-mr-md-12v,
  .fr-mr-md-6w,
  .fr-mx-md-12v,
  .fr-mx-md-6w {
    margin-right: 3rem !important;
  }
  .fr-mt-md-12v,
  .fr-mt-md-6w,
  .fr-my-md-12v,
  .fr-my-md-6w {
    margin-top: 3rem !important;
  }
  .fr-mb-md-12v,
  .fr-mb-md-6w,
  .fr-my-md-12v,
  .fr-my-md-6w {
    margin-bottom: 3rem !important;
  }
  .fr-m-md-13v {
    margin: 3.25rem !important;
  }
  .fr-ml-md-13v,
  .fr-mx-md-13v {
    margin-left: 3.25rem !important;
  }
  .fr-mr-md-13v,
  .fr-mx-md-13v {
    margin-right: 3.25rem !important;
  }
  .fr-mt-md-13v,
  .fr-my-md-13v {
    margin-top: 3.25rem !important;
  }
  .fr-mb-md-13v,
  .fr-my-md-13v {
    margin-bottom: 3.25rem !important;
  }
  .fr-m-md-14v,
  .fr-m-md-7w {
    margin: 3.5rem !important;
  }
  .fr-ml-md-14v,
  .fr-ml-md-7w,
  .fr-mx-md-14v,
  .fr-mx-md-7w {
    margin-left: 3.5rem !important;
  }
  .fr-mr-md-14v,
  .fr-mr-md-7w,
  .fr-mx-md-14v,
  .fr-mx-md-7w {
    margin-right: 3.5rem !important;
  }
  .fr-mt-md-14v,
  .fr-mt-md-7w,
  .fr-my-md-14v,
  .fr-my-md-7w {
    margin-top: 3.5rem !important;
  }
  .fr-mb-md-14v,
  .fr-mb-md-7w,
  .fr-my-md-14v,
  .fr-my-md-7w {
    margin-bottom: 3.5rem !important;
  }
  .fr-m-md-15v {
    margin: 3.75rem !important;
  }
  .fr-ml-md-15v,
  .fr-mx-md-15v {
    margin-left: 3.75rem !important;
  }
  .fr-mr-md-15v,
  .fr-mx-md-15v {
    margin-right: 3.75rem !important;
  }
  .fr-mt-md-15v,
  .fr-my-md-15v {
    margin-top: 3.75rem !important;
  }
  .fr-mb-md-15v,
  .fr-my-md-15v {
    margin-bottom: 3.75rem !important;
  }
  .fr-m-md-16v,
  .fr-m-md-8w {
    margin: 4rem !important;
  }
  .fr-ml-md-16v,
  .fr-ml-md-8w,
  .fr-mx-md-16v,
  .fr-mx-md-8w {
    margin-left: 4rem !important;
  }
  .fr-mr-md-16v,
  .fr-mr-md-8w,
  .fr-mx-md-16v,
  .fr-mx-md-8w {
    margin-right: 4rem !important;
  }
  .fr-mt-md-16v,
  .fr-mt-md-8w,
  .fr-my-md-16v,
  .fr-my-md-8w {
    margin-top: 4rem !important;
  }
  .fr-mb-md-16v,
  .fr-mb-md-8w,
  .fr-my-md-16v,
  .fr-my-md-8w {
    margin-bottom: 4rem !important;
  }
  .fr-m-md-17v {
    margin: 4.25rem !important;
  }
  .fr-ml-md-17v,
  .fr-mx-md-17v {
    margin-left: 4.25rem !important;
  }
  .fr-mr-md-17v,
  .fr-mx-md-17v {
    margin-right: 4.25rem !important;
  }
  .fr-mt-md-17v,
  .fr-my-md-17v {
    margin-top: 4.25rem !important;
  }
  .fr-mb-md-17v,
  .fr-my-md-17v {
    margin-bottom: 4.25rem !important;
  }
  .fr-m-md-18v,
  .fr-m-md-9w {
    margin: 4.5rem !important;
  }
  .fr-ml-md-18v,
  .fr-ml-md-9w,
  .fr-mx-md-18v,
  .fr-mx-md-9w {
    margin-left: 4.5rem !important;
  }
  .fr-mr-md-18v,
  .fr-mr-md-9w,
  .fr-mx-md-18v,
  .fr-mx-md-9w {
    margin-right: 4.5rem !important;
  }
  .fr-mt-md-18v,
  .fr-mt-md-9w,
  .fr-my-md-18v,
  .fr-my-md-9w {
    margin-top: 4.5rem !important;
  }
  .fr-mb-md-18v,
  .fr-mb-md-9w,
  .fr-my-md-18v,
  .fr-my-md-9w {
    margin-bottom: 4.5rem !important;
  }
  .fr-m-md-19v {
    margin: 4.75rem !important;
  }
  .fr-ml-md-19v,
  .fr-mx-md-19v {
    margin-left: 4.75rem !important;
  }
  .fr-mr-md-19v,
  .fr-mx-md-19v {
    margin-right: 4.75rem !important;
  }
  .fr-mt-md-19v,
  .fr-my-md-19v {
    margin-top: 4.75rem !important;
  }
  .fr-mb-md-19v,
  .fr-my-md-19v {
    margin-bottom: 4.75rem !important;
  }
  .fr-m-md-20v,
  .fr-m-md-10w {
    margin: 5rem !important;
  }
  .fr-ml-md-20v,
  .fr-ml-md-10w,
  .fr-mx-md-20v,
  .fr-mx-md-10w {
    margin-left: 5rem !important;
  }
  .fr-mr-md-20v,
  .fr-mr-md-10w,
  .fr-mx-md-20v,
  .fr-mx-md-10w {
    margin-right: 5rem !important;
  }
  .fr-mt-md-20v,
  .fr-mt-md-10w,
  .fr-my-md-20v,
  .fr-my-md-10w {
    margin-top: 5rem !important;
  }
  .fr-mb-md-20v,
  .fr-mb-md-10w,
  .fr-my-md-20v,
  .fr-my-md-10w {
    margin-bottom: 5rem !important;
  }
  .fr-m-md-21v {
    margin: 5.25rem !important;
  }
  .fr-ml-md-21v,
  .fr-mx-md-21v {
    margin-left: 5.25rem !important;
  }
  .fr-mr-md-21v,
  .fr-mx-md-21v {
    margin-right: 5.25rem !important;
  }
  .fr-mt-md-21v,
  .fr-my-md-21v {
    margin-top: 5.25rem !important;
  }
  .fr-mb-md-21v,
  .fr-my-md-21v {
    margin-bottom: 5.25rem !important;
  }
  .fr-m-md-22v,
  .fr-m-md-11w {
    margin: 5.5rem !important;
  }
  .fr-ml-md-22v,
  .fr-ml-md-11w,
  .fr-mx-md-22v,
  .fr-mx-md-11w {
    margin-left: 5.5rem !important;
  }
  .fr-mr-md-22v,
  .fr-mr-md-11w,
  .fr-mx-md-22v,
  .fr-mx-md-11w {
    margin-right: 5.5rem !important;
  }
  .fr-mt-md-22v,
  .fr-mt-md-11w,
  .fr-my-md-22v,
  .fr-my-md-11w {
    margin-top: 5.5rem !important;
  }
  .fr-mb-md-22v,
  .fr-mb-md-11w,
  .fr-my-md-22v,
  .fr-my-md-11w {
    margin-bottom: 5.5rem !important;
  }
  .fr-m-md-23v {
    margin: 5.75rem !important;
  }
  .fr-ml-md-23v,
  .fr-mx-md-23v {
    margin-left: 5.75rem !important;
  }
  .fr-mr-md-23v,
  .fr-mx-md-23v {
    margin-right: 5.75rem !important;
  }
  .fr-mt-md-23v,
  .fr-my-md-23v {
    margin-top: 5.75rem !important;
  }
  .fr-mb-md-23v,
  .fr-my-md-23v {
    margin-bottom: 5.75rem !important;
  }
  .fr-m-md-24v,
  .fr-m-md-12w {
    margin: 6rem !important;
  }
  .fr-ml-md-24v,
  .fr-ml-md-12w,
  .fr-mx-md-24v,
  .fr-mx-md-12w {
    margin-left: 6rem !important;
  }
  .fr-mr-md-24v,
  .fr-mr-md-12w,
  .fr-mx-md-24v,
  .fr-mx-md-12w {
    margin-right: 6rem !important;
  }
  .fr-mt-md-24v,
  .fr-mt-md-12w,
  .fr-my-md-24v,
  .fr-my-md-12w {
    margin-top: 6rem !important;
  }
  .fr-mb-md-24v,
  .fr-mb-md-12w,
  .fr-my-md-24v,
  .fr-my-md-12w {
    margin-bottom: 6rem !important;
  }
  .fr-m-md-25v {
    margin: 6.25rem !important;
  }
  .fr-ml-md-25v,
  .fr-mx-md-25v {
    margin-left: 6.25rem !important;
  }
  .fr-mr-md-25v,
  .fr-mx-md-25v {
    margin-right: 6.25rem !important;
  }
  .fr-mt-md-25v,
  .fr-my-md-25v {
    margin-top: 6.25rem !important;
  }
  .fr-mb-md-25v,
  .fr-my-md-25v {
    margin-bottom: 6.25rem !important;
  }
  .fr-m-md-26v,
  .fr-m-md-13w {
    margin: 6.5rem !important;
  }
  .fr-ml-md-26v,
  .fr-ml-md-13w,
  .fr-mx-md-26v,
  .fr-mx-md-13w {
    margin-left: 6.5rem !important;
  }
  .fr-mr-md-26v,
  .fr-mr-md-13w,
  .fr-mx-md-26v,
  .fr-mx-md-13w {
    margin-right: 6.5rem !important;
  }
  .fr-mt-md-26v,
  .fr-mt-md-13w,
  .fr-my-md-26v,
  .fr-my-md-13w {
    margin-top: 6.5rem !important;
  }
  .fr-mb-md-26v,
  .fr-mb-md-13w,
  .fr-my-md-26v,
  .fr-my-md-13w {
    margin-bottom: 6.5rem !important;
  }
  .fr-m-md-27v {
    margin: 6.75rem !important;
  }
  .fr-ml-md-27v,
  .fr-mx-md-27v {
    margin-left: 6.75rem !important;
  }
  .fr-mr-md-27v,
  .fr-mx-md-27v {
    margin-right: 6.75rem !important;
  }
  .fr-mt-md-27v,
  .fr-my-md-27v {
    margin-top: 6.75rem !important;
  }
  .fr-mb-md-27v,
  .fr-my-md-27v {
    margin-bottom: 6.75rem !important;
  }
  .fr-m-md-28v,
  .fr-m-md-14w {
    margin: 7rem !important;
  }
  .fr-ml-md-28v,
  .fr-ml-md-14w,
  .fr-mx-md-28v,
  .fr-mx-md-14w {
    margin-left: 7rem !important;
  }
  .fr-mr-md-28v,
  .fr-mr-md-14w,
  .fr-mx-md-28v,
  .fr-mx-md-14w {
    margin-right: 7rem !important;
  }
  .fr-mt-md-28v,
  .fr-mt-md-14w,
  .fr-my-md-28v,
  .fr-my-md-14w {
    margin-top: 7rem !important;
  }
  .fr-mb-md-28v,
  .fr-mb-md-14w,
  .fr-my-md-28v,
  .fr-my-md-14w {
    margin-bottom: 7rem !important;
  }
  .fr-m-md-29v {
    margin: 7.25rem !important;
  }
  .fr-ml-md-29v,
  .fr-mx-md-29v {
    margin-left: 7.25rem !important;
  }
  .fr-mr-md-29v,
  .fr-mx-md-29v {
    margin-right: 7.25rem !important;
  }
  .fr-mt-md-29v,
  .fr-my-md-29v {
    margin-top: 7.25rem !important;
  }
  .fr-mb-md-29v,
  .fr-my-md-29v {
    margin-bottom: 7.25rem !important;
  }
  .fr-m-md-30v,
  .fr-m-md-15w {
    margin: 7.5rem !important;
  }
  .fr-ml-md-30v,
  .fr-ml-md-15w,
  .fr-mx-md-30v,
  .fr-mx-md-15w {
    margin-left: 7.5rem !important;
  }
  .fr-mr-md-30v,
  .fr-mr-md-15w,
  .fr-mx-md-30v,
  .fr-mx-md-15w {
    margin-right: 7.5rem !important;
  }
  .fr-mt-md-30v,
  .fr-mt-md-15w,
  .fr-my-md-30v,
  .fr-my-md-15w {
    margin-top: 7.5rem !important;
  }
  .fr-mb-md-30v,
  .fr-mb-md-15w,
  .fr-my-md-30v,
  .fr-my-md-15w {
    margin-bottom: 7.5rem !important;
  }
  .fr-m-md-31v {
    margin: 7.75rem !important;
  }
  .fr-ml-md-31v,
  .fr-mx-md-31v {
    margin-left: 7.75rem !important;
  }
  .fr-mr-md-31v,
  .fr-mx-md-31v {
    margin-right: 7.75rem !important;
  }
  .fr-mt-md-31v,
  .fr-my-md-31v {
    margin-top: 7.75rem !important;
  }
  .fr-mb-md-31v,
  .fr-my-md-31v {
    margin-bottom: 7.75rem !important;
  }
  .fr-m-md-32v,
  .fr-m-md-16w {
    margin: 8rem !important;
  }
  .fr-ml-md-32v,
  .fr-ml-md-16w,
  .fr-mx-md-32v,
  .fr-mx-md-16w {
    margin-left: 8rem !important;
  }
  .fr-mr-md-32v,
  .fr-mr-md-16w,
  .fr-mx-md-32v,
  .fr-mx-md-16w {
    margin-right: 8rem !important;
  }
  .fr-mt-md-32v,
  .fr-mt-md-16w,
  .fr-my-md-32v,
  .fr-my-md-16w {
    margin-top: 8rem !important;
  }
  .fr-mb-md-32v,
  .fr-mb-md-16w,
  .fr-my-md-32v,
  .fr-my-md-16w {
    margin-bottom: 8rem !important;
  }
  .fr-m-md-auto {
    margin: auto;
  }
  .fr-ml-md-auto,
  .fr-mx-md-auto {
    margin-left: auto;
  }
  .fr-mr-md-auto,
  .fr-mx-md-auto {
    margin-right: auto;
  }
  .fr-mt-md-auto,
  .fr-my-md-auto {
    margin-top: auto;
  }
  .fr-mb-md-auto,
  .fr-my-md-auto {
    margin-bottom: auto;
  }
  .fr-p-md-0 {
    padding: 0 !important;
  }
  .fr-pl-md-0,
  .fr-px-md-0 {
    padding-left: 0 !important;
  }
  .fr-pr-md-0,
  .fr-px-md-0 {
    padding-right: 0 !important;
  }
  .fr-pt-md-0,
  .fr-py-md-0 {
    padding-top: 0 !important;
  }
  .fr-pb-md-0,
  .fr-py-md-0 {
    padding-bottom: 0 !important;
  }
  .fr-p-md-0-5v {
    padding: 0.125rem !important;
  }
  .fr-pl-md-0-5v,
  .fr-px-md-0-5v {
    padding-left: 0.125rem !important;
  }
  .fr-pr-md-0-5v,
  .fr-px-md-0-5v {
    padding-right: 0.125rem !important;
  }
  .fr-pt-md-0-5v,
  .fr-py-md-0-5v {
    padding-top: 0.125rem !important;
  }
  .fr-pb-md-0-5v,
  .fr-py-md-0-5v {
    padding-bottom: 0.125rem !important;
  }
  .fr-p-md-1v {
    padding: 0.25rem !important;
  }
  .fr-pl-md-1v,
  .fr-px-md-1v {
    padding-left: 0.25rem !important;
  }
  .fr-pr-md-1v,
  .fr-px-md-1v {
    padding-right: 0.25rem !important;
  }
  .fr-pt-md-1v,
  .fr-py-md-1v {
    padding-top: 0.25rem !important;
  }
  .fr-pb-md-1v,
  .fr-py-md-1v {
    padding-bottom: 0.25rem !important;
  }
  .fr-p-md-1-5v {
    padding: 0.375rem !important;
  }
  .fr-pl-md-1-5v,
  .fr-px-md-1-5v {
    padding-left: 0.375rem !important;
  }
  .fr-pr-md-1-5v,
  .fr-px-md-1-5v {
    padding-right: 0.375rem !important;
  }
  .fr-pt-md-1-5v,
  .fr-py-md-1-5v {
    padding-top: 0.375rem !important;
  }
  .fr-pb-md-1-5v,
  .fr-py-md-1-5v {
    padding-bottom: 0.375rem !important;
  }
  .fr-p-md-2v,
  .fr-p-md-1w {
    padding: 0.5rem !important;
  }
  .fr-pl-md-2v,
  .fr-pl-md-1w,
  .fr-px-md-2v,
  .fr-px-md-1w {
    padding-left: 0.5rem !important;
  }
  .fr-pr-md-2v,
  .fr-pr-md-1w,
  .fr-px-md-2v,
  .fr-px-md-1w {
    padding-right: 0.5rem !important;
  }
  .fr-pt-md-2v,
  .fr-pt-md-1w,
  .fr-py-md-2v,
  .fr-py-md-1w {
    padding-top: 0.5rem !important;
  }
  .fr-pb-md-2v,
  .fr-pb-md-1w,
  .fr-py-md-2v,
  .fr-py-md-1w {
    padding-bottom: 0.5rem !important;
  }
  .fr-p-md-3v {
    padding: 0.75rem !important;
  }
  .fr-pl-md-3v,
  .fr-px-md-3v {
    padding-left: 0.75rem !important;
  }
  .fr-pr-md-3v,
  .fr-px-md-3v {
    padding-right: 0.75rem !important;
  }
  .fr-pt-md-3v,
  .fr-py-md-3v {
    padding-top: 0.75rem !important;
  }
  .fr-pb-md-3v,
  .fr-py-md-3v {
    padding-bottom: 0.75rem !important;
  }
  .fr-p-md-4v,
  .fr-p-md-2w {
    padding: 1rem !important;
  }
  .fr-pl-md-4v,
  .fr-pl-md-2w,
  .fr-px-md-4v,
  .fr-px-md-2w {
    padding-left: 1rem !important;
  }
  .fr-pr-md-4v,
  .fr-pr-md-2w,
  .fr-px-md-4v,
  .fr-px-md-2w {
    padding-right: 1rem !important;
  }
  .fr-pt-md-4v,
  .fr-pt-md-2w,
  .fr-py-md-4v,
  .fr-py-md-2w {
    padding-top: 1rem !important;
  }
  .fr-pb-md-4v,
  .fr-pb-md-2w,
  .fr-py-md-4v,
  .fr-py-md-2w {
    padding-bottom: 1rem !important;
  }
  .fr-p-md-5v {
    padding: 1.25rem !important;
  }
  .fr-pl-md-5v,
  .fr-px-md-5v {
    padding-left: 1.25rem !important;
  }
  .fr-pr-md-5v,
  .fr-px-md-5v {
    padding-right: 1.25rem !important;
  }
  .fr-pt-md-5v,
  .fr-py-md-5v {
    padding-top: 1.25rem !important;
  }
  .fr-pb-md-5v,
  .fr-py-md-5v {
    padding-bottom: 1.25rem !important;
  }
  .fr-p-md-6v,
  .fr-p-md-3w {
    padding: 1.5rem !important;
  }
  .fr-pl-md-6v,
  .fr-pl-md-3w,
  .fr-px-md-6v,
  .fr-px-md-3w {
    padding-left: 1.5rem !important;
  }
  .fr-pr-md-6v,
  .fr-pr-md-3w,
  .fr-px-md-6v,
  .fr-px-md-3w {
    padding-right: 1.5rem !important;
  }
  .fr-pt-md-6v,
  .fr-pt-md-3w,
  .fr-py-md-6v,
  .fr-py-md-3w {
    padding-top: 1.5rem !important;
  }
  .fr-pb-md-6v,
  .fr-pb-md-3w,
  .fr-py-md-6v,
  .fr-py-md-3w {
    padding-bottom: 1.5rem !important;
  }
  .fr-p-md-7v {
    padding: 1.75rem !important;
  }
  .fr-pl-md-7v,
  .fr-px-md-7v {
    padding-left: 1.75rem !important;
  }
  .fr-pr-md-7v,
  .fr-px-md-7v {
    padding-right: 1.75rem !important;
  }
  .fr-pt-md-7v,
  .fr-py-md-7v {
    padding-top: 1.75rem !important;
  }
  .fr-pb-md-7v,
  .fr-py-md-7v {
    padding-bottom: 1.75rem !important;
  }
  .fr-p-md-8v,
  .fr-p-md-4w {
    padding: 2rem !important;
  }
  .fr-pl-md-8v,
  .fr-pl-md-4w,
  .fr-px-md-8v,
  .fr-px-md-4w {
    padding-left: 2rem !important;
  }
  .fr-pr-md-8v,
  .fr-pr-md-4w,
  .fr-px-md-8v,
  .fr-px-md-4w {
    padding-right: 2rem !important;
  }
  .fr-pt-md-8v,
  .fr-pt-md-4w,
  .fr-py-md-8v,
  .fr-py-md-4w {
    padding-top: 2rem !important;
  }
  .fr-pb-md-8v,
  .fr-pb-md-4w,
  .fr-py-md-8v,
  .fr-py-md-4w {
    padding-bottom: 2rem !important;
  }
  .fr-p-md-9v {
    padding: 2.25rem !important;
  }
  .fr-pl-md-9v,
  .fr-px-md-9v {
    padding-left: 2.25rem !important;
  }
  .fr-pr-md-9v,
  .fr-px-md-9v {
    padding-right: 2.25rem !important;
  }
  .fr-pt-md-9v,
  .fr-py-md-9v {
    padding-top: 2.25rem !important;
  }
  .fr-pb-md-9v,
  .fr-py-md-9v {
    padding-bottom: 2.25rem !important;
  }
  .fr-p-md-10v,
  .fr-p-md-5w {
    padding: 2.5rem !important;
  }
  .fr-pl-md-10v,
  .fr-pl-md-5w,
  .fr-px-md-10v,
  .fr-px-md-5w {
    padding-left: 2.5rem !important;
  }
  .fr-pr-md-10v,
  .fr-pr-md-5w,
  .fr-px-md-10v,
  .fr-px-md-5w {
    padding-right: 2.5rem !important;
  }
  .fr-pt-md-10v,
  .fr-pt-md-5w,
  .fr-py-md-10v,
  .fr-py-md-5w {
    padding-top: 2.5rem !important;
  }
  .fr-pb-md-10v,
  .fr-pb-md-5w,
  .fr-py-md-10v,
  .fr-py-md-5w {
    padding-bottom: 2.5rem !important;
  }
  .fr-p-md-11v {
    padding: 2.75rem !important;
  }
  .fr-pl-md-11v,
  .fr-px-md-11v {
    padding-left: 2.75rem !important;
  }
  .fr-pr-md-11v,
  .fr-px-md-11v {
    padding-right: 2.75rem !important;
  }
  .fr-pt-md-11v,
  .fr-py-md-11v {
    padding-top: 2.75rem !important;
  }
  .fr-pb-md-11v,
  .fr-py-md-11v {
    padding-bottom: 2.75rem !important;
  }
  .fr-p-md-12v,
  .fr-p-md-6w {
    padding: 3rem !important;
  }
  .fr-pl-md-12v,
  .fr-pl-md-6w,
  .fr-px-md-12v,
  .fr-px-md-6w {
    padding-left: 3rem !important;
  }
  .fr-pr-md-12v,
  .fr-pr-md-6w,
  .fr-px-md-12v,
  .fr-px-md-6w {
    padding-right: 3rem !important;
  }
  .fr-pt-md-12v,
  .fr-pt-md-6w,
  .fr-py-md-12v,
  .fr-py-md-6w {
    padding-top: 3rem !important;
  }
  .fr-pb-md-12v,
  .fr-pb-md-6w,
  .fr-py-md-12v,
  .fr-py-md-6w {
    padding-bottom: 3rem !important;
  }
  .fr-p-md-13v {
    padding: 3.25rem !important;
  }
  .fr-pl-md-13v,
  .fr-px-md-13v {
    padding-left: 3.25rem !important;
  }
  .fr-pr-md-13v,
  .fr-px-md-13v {
    padding-right: 3.25rem !important;
  }
  .fr-pt-md-13v,
  .fr-py-md-13v {
    padding-top: 3.25rem !important;
  }
  .fr-pb-md-13v,
  .fr-py-md-13v {
    padding-bottom: 3.25rem !important;
  }
  .fr-p-md-14v,
  .fr-p-md-7w {
    padding: 3.5rem !important;
  }
  .fr-pl-md-14v,
  .fr-pl-md-7w,
  .fr-px-md-14v,
  .fr-px-md-7w {
    padding-left: 3.5rem !important;
  }
  .fr-pr-md-14v,
  .fr-pr-md-7w,
  .fr-px-md-14v,
  .fr-px-md-7w {
    padding-right: 3.5rem !important;
  }
  .fr-pt-md-14v,
  .fr-pt-md-7w,
  .fr-py-md-14v,
  .fr-py-md-7w {
    padding-top: 3.5rem !important;
  }
  .fr-pb-md-14v,
  .fr-pb-md-7w,
  .fr-py-md-14v,
  .fr-py-md-7w {
    padding-bottom: 3.5rem !important;
  }
  .fr-p-md-15v {
    padding: 3.75rem !important;
  }
  .fr-pl-md-15v,
  .fr-px-md-15v {
    padding-left: 3.75rem !important;
  }
  .fr-pr-md-15v,
  .fr-px-md-15v {
    padding-right: 3.75rem !important;
  }
  .fr-pt-md-15v,
  .fr-py-md-15v {
    padding-top: 3.75rem !important;
  }
  .fr-pb-md-15v,
  .fr-py-md-15v {
    padding-bottom: 3.75rem !important;
  }
  .fr-p-md-16v,
  .fr-p-md-8w {
    padding: 4rem !important;
  }
  .fr-pl-md-16v,
  .fr-pl-md-8w,
  .fr-px-md-16v,
  .fr-px-md-8w {
    padding-left: 4rem !important;
  }
  .fr-pr-md-16v,
  .fr-pr-md-8w,
  .fr-px-md-16v,
  .fr-px-md-8w {
    padding-right: 4rem !important;
  }
  .fr-pt-md-16v,
  .fr-pt-md-8w,
  .fr-py-md-16v,
  .fr-py-md-8w {
    padding-top: 4rem !important;
  }
  .fr-pb-md-16v,
  .fr-pb-md-8w,
  .fr-py-md-16v,
  .fr-py-md-8w {
    padding-bottom: 4rem !important;
  }
  .fr-p-md-17v {
    padding: 4.25rem !important;
  }
  .fr-pl-md-17v,
  .fr-px-md-17v {
    padding-left: 4.25rem !important;
  }
  .fr-pr-md-17v,
  .fr-px-md-17v {
    padding-right: 4.25rem !important;
  }
  .fr-pt-md-17v,
  .fr-py-md-17v {
    padding-top: 4.25rem !important;
  }
  .fr-pb-md-17v,
  .fr-py-md-17v {
    padding-bottom: 4.25rem !important;
  }
  .fr-p-md-18v,
  .fr-p-md-9w {
    padding: 4.5rem !important;
  }
  .fr-pl-md-18v,
  .fr-pl-md-9w,
  .fr-px-md-18v,
  .fr-px-md-9w {
    padding-left: 4.5rem !important;
  }
  .fr-pr-md-18v,
  .fr-pr-md-9w,
  .fr-px-md-18v,
  .fr-px-md-9w {
    padding-right: 4.5rem !important;
  }
  .fr-pt-md-18v,
  .fr-pt-md-9w,
  .fr-py-md-18v,
  .fr-py-md-9w {
    padding-top: 4.5rem !important;
  }
  .fr-pb-md-18v,
  .fr-pb-md-9w,
  .fr-py-md-18v,
  .fr-py-md-9w {
    padding-bottom: 4.5rem !important;
  }
  .fr-p-md-19v {
    padding: 4.75rem !important;
  }
  .fr-pl-md-19v,
  .fr-px-md-19v {
    padding-left: 4.75rem !important;
  }
  .fr-pr-md-19v,
  .fr-px-md-19v {
    padding-right: 4.75rem !important;
  }
  .fr-pt-md-19v,
  .fr-py-md-19v {
    padding-top: 4.75rem !important;
  }
  .fr-pb-md-19v,
  .fr-py-md-19v {
    padding-bottom: 4.75rem !important;
  }
  .fr-p-md-20v,
  .fr-p-md-10w {
    padding: 5rem !important;
  }
  .fr-pl-md-20v,
  .fr-pl-md-10w,
  .fr-px-md-20v,
  .fr-px-md-10w {
    padding-left: 5rem !important;
  }
  .fr-pr-md-20v,
  .fr-pr-md-10w,
  .fr-px-md-20v,
  .fr-px-md-10w {
    padding-right: 5rem !important;
  }
  .fr-pt-md-20v,
  .fr-pt-md-10w,
  .fr-py-md-20v,
  .fr-py-md-10w {
    padding-top: 5rem !important;
  }
  .fr-pb-md-20v,
  .fr-pb-md-10w,
  .fr-py-md-20v,
  .fr-py-md-10w {
    padding-bottom: 5rem !important;
  }
  .fr-p-md-21v {
    padding: 5.25rem !important;
  }
  .fr-pl-md-21v,
  .fr-px-md-21v {
    padding-left: 5.25rem !important;
  }
  .fr-pr-md-21v,
  .fr-px-md-21v {
    padding-right: 5.25rem !important;
  }
  .fr-pt-md-21v,
  .fr-py-md-21v {
    padding-top: 5.25rem !important;
  }
  .fr-pb-md-21v,
  .fr-py-md-21v {
    padding-bottom: 5.25rem !important;
  }
  .fr-p-md-22v,
  .fr-p-md-11w {
    padding: 5.5rem !important;
  }
  .fr-pl-md-22v,
  .fr-pl-md-11w,
  .fr-px-md-22v,
  .fr-px-md-11w {
    padding-left: 5.5rem !important;
  }
  .fr-pr-md-22v,
  .fr-pr-md-11w,
  .fr-px-md-22v,
  .fr-px-md-11w {
    padding-right: 5.5rem !important;
  }
  .fr-pt-md-22v,
  .fr-pt-md-11w,
  .fr-py-md-22v,
  .fr-py-md-11w {
    padding-top: 5.5rem !important;
  }
  .fr-pb-md-22v,
  .fr-pb-md-11w,
  .fr-py-md-22v,
  .fr-py-md-11w {
    padding-bottom: 5.5rem !important;
  }
  .fr-p-md-23v {
    padding: 5.75rem !important;
  }
  .fr-pl-md-23v,
  .fr-px-md-23v {
    padding-left: 5.75rem !important;
  }
  .fr-pr-md-23v,
  .fr-px-md-23v {
    padding-right: 5.75rem !important;
  }
  .fr-pt-md-23v,
  .fr-py-md-23v {
    padding-top: 5.75rem !important;
  }
  .fr-pb-md-23v,
  .fr-py-md-23v {
    padding-bottom: 5.75rem !important;
  }
  .fr-p-md-24v,
  .fr-p-md-12w {
    padding: 6rem !important;
  }
  .fr-pl-md-24v,
  .fr-pl-md-12w,
  .fr-px-md-24v,
  .fr-px-md-12w {
    padding-left: 6rem !important;
  }
  .fr-pr-md-24v,
  .fr-pr-md-12w,
  .fr-px-md-24v,
  .fr-px-md-12w {
    padding-right: 6rem !important;
  }
  .fr-pt-md-24v,
  .fr-pt-md-12w,
  .fr-py-md-24v,
  .fr-py-md-12w {
    padding-top: 6rem !important;
  }
  .fr-pb-md-24v,
  .fr-pb-md-12w,
  .fr-py-md-24v,
  .fr-py-md-12w {
    padding-bottom: 6rem !important;
  }
  .fr-p-md-25v {
    padding: 6.25rem !important;
  }
  .fr-pl-md-25v,
  .fr-px-md-25v {
    padding-left: 6.25rem !important;
  }
  .fr-pr-md-25v,
  .fr-px-md-25v {
    padding-right: 6.25rem !important;
  }
  .fr-pt-md-25v,
  .fr-py-md-25v {
    padding-top: 6.25rem !important;
  }
  .fr-pb-md-25v,
  .fr-py-md-25v {
    padding-bottom: 6.25rem !important;
  }
  .fr-p-md-26v,
  .fr-p-md-13w {
    padding: 6.5rem !important;
  }
  .fr-pl-md-26v,
  .fr-pl-md-13w,
  .fr-px-md-26v,
  .fr-px-md-13w {
    padding-left: 6.5rem !important;
  }
  .fr-pr-md-26v,
  .fr-pr-md-13w,
  .fr-px-md-26v,
  .fr-px-md-13w {
    padding-right: 6.5rem !important;
  }
  .fr-pt-md-26v,
  .fr-pt-md-13w,
  .fr-py-md-26v,
  .fr-py-md-13w {
    padding-top: 6.5rem !important;
  }
  .fr-pb-md-26v,
  .fr-pb-md-13w,
  .fr-py-md-26v,
  .fr-py-md-13w {
    padding-bottom: 6.5rem !important;
  }
  .fr-p-md-27v {
    padding: 6.75rem !important;
  }
  .fr-pl-md-27v,
  .fr-px-md-27v {
    padding-left: 6.75rem !important;
  }
  .fr-pr-md-27v,
  .fr-px-md-27v {
    padding-right: 6.75rem !important;
  }
  .fr-pt-md-27v,
  .fr-py-md-27v {
    padding-top: 6.75rem !important;
  }
  .fr-pb-md-27v,
  .fr-py-md-27v {
    padding-bottom: 6.75rem !important;
  }
  .fr-p-md-28v,
  .fr-p-md-14w {
    padding: 7rem !important;
  }
  .fr-pl-md-28v,
  .fr-pl-md-14w,
  .fr-px-md-28v,
  .fr-px-md-14w {
    padding-left: 7rem !important;
  }
  .fr-pr-md-28v,
  .fr-pr-md-14w,
  .fr-px-md-28v,
  .fr-px-md-14w {
    padding-right: 7rem !important;
  }
  .fr-pt-md-28v,
  .fr-pt-md-14w,
  .fr-py-md-28v,
  .fr-py-md-14w {
    padding-top: 7rem !important;
  }
  .fr-pb-md-28v,
  .fr-pb-md-14w,
  .fr-py-md-28v,
  .fr-py-md-14w {
    padding-bottom: 7rem !important;
  }
  .fr-p-md-29v {
    padding: 7.25rem !important;
  }
  .fr-pl-md-29v,
  .fr-px-md-29v {
    padding-left: 7.25rem !important;
  }
  .fr-pr-md-29v,
  .fr-px-md-29v {
    padding-right: 7.25rem !important;
  }
  .fr-pt-md-29v,
  .fr-py-md-29v {
    padding-top: 7.25rem !important;
  }
  .fr-pb-md-29v,
  .fr-py-md-29v {
    padding-bottom: 7.25rem !important;
  }
  .fr-p-md-30v,
  .fr-p-md-15w {
    padding: 7.5rem !important;
  }
  .fr-pl-md-30v,
  .fr-pl-md-15w,
  .fr-px-md-30v,
  .fr-px-md-15w {
    padding-left: 7.5rem !important;
  }
  .fr-pr-md-30v,
  .fr-pr-md-15w,
  .fr-px-md-30v,
  .fr-px-md-15w {
    padding-right: 7.5rem !important;
  }
  .fr-pt-md-30v,
  .fr-pt-md-15w,
  .fr-py-md-30v,
  .fr-py-md-15w {
    padding-top: 7.5rem !important;
  }
  .fr-pb-md-30v,
  .fr-pb-md-15w,
  .fr-py-md-30v,
  .fr-py-md-15w {
    padding-bottom: 7.5rem !important;
  }
  .fr-p-md-31v {
    padding: 7.75rem !important;
  }
  .fr-pl-md-31v,
  .fr-px-md-31v {
    padding-left: 7.75rem !important;
  }
  .fr-pr-md-31v,
  .fr-px-md-31v {
    padding-right: 7.75rem !important;
  }
  .fr-pt-md-31v,
  .fr-py-md-31v {
    padding-top: 7.75rem !important;
  }
  .fr-pb-md-31v,
  .fr-py-md-31v {
    padding-bottom: 7.75rem !important;
  }
  .fr-p-md-32v,
  .fr-p-md-16w {
    padding: 8rem !important;
  }
  .fr-pl-md-32v,
  .fr-pl-md-16w,
  .fr-px-md-32v,
  .fr-px-md-16w {
    padding-left: 8rem !important;
  }
  .fr-pr-md-32v,
  .fr-pr-md-16w,
  .fr-px-md-32v,
  .fr-px-md-16w {
    padding-right: 8rem !important;
  }
  .fr-pt-md-32v,
  .fr-pt-md-16w,
  .fr-py-md-32v,
  .fr-py-md-16w {
    padding-top: 8rem !important;
  }
  .fr-pb-md-32v,
  .fr-pb-md-16w,
  .fr-py-md-32v,
  .fr-py-md-16w {
    padding-bottom: 8rem !important;
  }
  /*! media md */
}
@media (min-width: 62em) {
  /*! media lg */
  .fr-hidden-lg {
    display: none !important;
  }
  .fr-unhidden-lg {
    display: inherit !important;
  }
  .fr-sr-only-lg {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap; /* added line */
    border: 0;
    display: block;
  }
  .fr-container,
  .fr-container-sm,
  .fr-container-md {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
  .fr-container-lg {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
  .fr-container-lg--fluid {
    padding-left: 0;
    padding-right: 0;
    max-width: none;
    overflow: hidden;
  }
  .fr-grid-row--gutters,
  .fr-grid-row-sm--gutters,
  .fr-grid-row-md--gutters {
    margin: -0.75rem;
  }
  .fr-grid-row--gutters &gt; [class^=fr-col-],
  .fr-grid-row--gutters &gt; [class*=&quot; fr-col-&quot;],
  .fr-grid-row--gutters &gt; .fr-col,
  .fr-grid-row-sm--gutters &gt; [class^=fr-col-],
  .fr-grid-row-sm--gutters &gt; [class*=&quot; fr-col-&quot;],
  .fr-grid-row-sm--gutters &gt; .fr-col,
  .fr-grid-row-md--gutters &gt; [class^=fr-col-],
  .fr-grid-row-md--gutters &gt; [class*=&quot; fr-col-&quot;],
  .fr-grid-row-md--gutters &gt; .fr-col {
    padding: 0.75rem;
  }
  .fr-grid-row-lg--gutters {
    margin: -0.75rem;
  }
  .fr-grid-row-lg--gutters &gt; [class^=fr-col-],
  .fr-grid-row-lg--gutters &gt; [class*=&quot; fr-col-&quot;],
  .fr-grid-row-lg--gutters &gt; .fr-col {
    padding: 0.75rem;
  }
  .fr-grid-row-lg--no-gutters {
    margin: 0;
  }
  .fr-grid-row-lg--no-gutters &gt; [class^=fr-col-],
  .fr-grid-row-lg--no-gutters &gt; [class*=&quot; fr-col-&quot;],
  .fr-grid-row-lg--no-gutters &gt; .fr-col {
    padding: 0;
  }
  .fr-col-lg {
    flex: 1;
  }
  .fr-col-lg-1 {
    flex: 0 0 8.3333333333%;
    width: 8.3333333333%;
    max-width: 8.3333333333%;
  }
  .fr-col-offset-lg-1:not(.fr-col-offset-lg-1--right) {
    margin-left: 8.3333333333%;
  }
  .fr-col-offset-lg-1--right {
    margin-right: 8.3333333333%;
  }
  .fr-col-lg-2 {
    flex: 0 0 16.6666666667%;
    width: 16.6666666667%;
    max-width: 16.6666666667%;
  }
  .fr-col-offset-lg-2:not(.fr-col-offset-lg-2--right) {
    margin-left: 16.6666666667%;
  }
  .fr-col-offset-lg-2--right {
    margin-right: 16.6666666667%;
  }
  .fr-col-lg-3 {
    flex: 0 0 25%;
    width: 25%;
    max-width: 25%;
  }
  .fr-col-offset-lg-3:not(.fr-col-offset-lg-3--right) {
    margin-left: 25%;
  }
  .fr-col-offset-lg-3--right {
    margin-right: 25%;
  }
  .fr-col-lg-4 {
    flex: 0 0 33.3333333333%;
    width: 33.3333333333%;
    max-width: 33.3333333333%;
  }
  .fr-col-offset-lg-4:not(.fr-col-offset-lg-4--right) {
    margin-left: 33.3333333333%;
  }
  .fr-col-offset-lg-4--right {
    margin-right: 33.3333333333%;
  }
  .fr-col-lg-5 {
    flex: 0 0 41.6666666667%;
    width: 41.6666666667%;
    max-width: 41.6666666667%;
  }
  .fr-col-offset-lg-5:not(.fr-col-offset-lg-5--right) {
    margin-left: 41.6666666667%;
  }
  .fr-col-offset-lg-5--right {
    margin-right: 41.6666666667%;
  }
  .fr-col-lg-6 {
    flex: 0 0 50%;
    width: 50%;
    max-width: 50%;
  }
  .fr-col-offset-lg-6:not(.fr-col-offset-lg-6--right) {
    margin-left: 50%;
  }
  .fr-col-offset-lg-6--right {
    margin-right: 50%;
  }
  .fr-col-lg-7 {
    flex: 0 0 58.3333333333%;
    width: 58.3333333333%;
    max-width: 58.3333333333%;
  }
  .fr-col-offset-lg-7:not(.fr-col-offset-lg-7--right) {
    margin-left: 58.3333333333%;
  }
  .fr-col-offset-lg-7--right {
    margin-right: 58.3333333333%;
  }
  .fr-col-lg-8 {
    flex: 0 0 66.6666666667%;
    width: 66.6666666667%;
    max-width: 66.6666666667%;
  }
  .fr-col-offset-lg-8:not(.fr-col-offset-lg-8--right) {
    margin-left: 66.6666666667%;
  }
  .fr-col-offset-lg-8--right {
    margin-right: 66.6666666667%;
  }
  .fr-col-lg-9 {
    flex: 0 0 75%;
    width: 75%;
    max-width: 75%;
  }
  .fr-col-offset-lg-9:not(.fr-col-offset-lg-9--right) {
    margin-left: 75%;
  }
  .fr-col-offset-lg-9--right {
    margin-right: 75%;
  }
  .fr-col-lg-10 {
    flex: 0 0 83.3333333333%;
    width: 83.3333333333%;
    max-width: 83.3333333333%;
  }
  .fr-col-offset-lg-10:not(.fr-col-offset-lg-10--right) {
    margin-left: 83.3333333333%;
  }
  .fr-col-offset-lg-10--right {
    margin-right: 83.3333333333%;
  }
  .fr-col-lg-11 {
    flex: 0 0 91.6666666667%;
    width: 91.6666666667%;
    max-width: 91.6666666667%;
  }
  .fr-col-offset-lg-11:not(.fr-col-offset-lg-11--right) {
    margin-left: 91.6666666667%;
  }
  .fr-col-offset-lg-11--right {
    margin-right: 91.6666666667%;
  }
  .fr-col-lg-12 {
    flex: 0 0 100%;
    width: 100%;
    max-width: 100%;
  }
  .fr-col-offset-lg-12:not(.fr-col-offset-lg-12--right) {
    margin-left: 100%;
  }
  .fr-col-offset-lg-12--right {
    margin-right: 100%;
  }
  .fr-displayed-lg {
    display: inherit !important;
  }
  /*! media lg */
}
@media (min-width: 78em) {
  /*! media xl */
  .fr-hidden-xl {
    display: none !important;
  }
  .fr-unhidden-xl {
    display: inherit !important;
  }
  .fr-sr-only-xl {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap; /* added line */
    border: 0;
    display: block;
  }
  .fr-container,
  .fr-container-sm,
  .fr-container-md,
  .fr-container-lg {
    max-width: 78rem;
  }
  .fr-container-xl {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
    max-width: 78rem;
  }
  .fr-container-xl--fluid {
    padding-left: 0;
    padding-right: 0;
    max-width: none;
    overflow: hidden;
  }
  .fr-grid-row-xl--gutters {
    margin: -0.75rem;
  }
  .fr-grid-row-xl--gutters &gt; [class^=fr-col-],
  .fr-grid-row-xl--gutters &gt; [class*=&quot; fr-col-&quot;],
  .fr-grid-row-xl--gutters &gt; .fr-col {
    padding: 0.75rem;
  }
  .fr-grid-row-xl--no-gutters {
    margin: 0;
  }
  .fr-grid-row-xl--no-gutters &gt; [class^=fr-col-],
  .fr-grid-row-xl--no-gutters &gt; [class*=&quot; fr-col-&quot;],
  .fr-grid-row-xl--no-gutters &gt; .fr-col {
    padding: 0;
  }
  .fr-col-xl {
    flex: 1;
  }
  .fr-col-xl-1 {
    flex: 0 0 8.3333333333%;
    width: 8.3333333333%;
    max-width: 8.3333333333%;
  }
  .fr-col-offset-xl-1:not(.fr-col-offset-xl-1--right) {
    margin-left: 8.3333333333%;
  }
  .fr-col-offset-xl-1--right {
    margin-right: 8.3333333333%;
  }
  .fr-col-xl-2 {
    flex: 0 0 16.6666666667%;
    width: 16.6666666667%;
    max-width: 16.6666666667%;
  }
  .fr-col-offset-xl-2:not(.fr-col-offset-xl-2--right) {
    margin-left: 16.6666666667%;
  }
  .fr-col-offset-xl-2--right {
    margin-right: 16.6666666667%;
  }
  .fr-col-xl-3 {
    flex: 0 0 25%;
    width: 25%;
    max-width: 25%;
  }
  .fr-col-offset-xl-3:not(.fr-col-offset-xl-3--right) {
    margin-left: 25%;
  }
  .fr-col-offset-xl-3--right {
    margin-right: 25%;
  }
  .fr-col-xl-4 {
    flex: 0 0 33.3333333333%;
    width: 33.3333333333%;
    max-width: 33.3333333333%;
  }
  .fr-col-offset-xl-4:not(.fr-col-offset-xl-4--right) {
    margin-left: 33.3333333333%;
  }
  .fr-col-offset-xl-4--right {
    margin-right: 33.3333333333%;
  }
  .fr-col-xl-5 {
    flex: 0 0 41.6666666667%;
    width: 41.6666666667%;
    max-width: 41.6666666667%;
  }
  .fr-col-offset-xl-5:not(.fr-col-offset-xl-5--right) {
    margin-left: 41.6666666667%;
  }
  .fr-col-offset-xl-5--right {
    margin-right: 41.6666666667%;
  }
  .fr-col-xl-6 {
    flex: 0 0 50%;
    width: 50%;
    max-width: 50%;
  }
  .fr-col-offset-xl-6:not(.fr-col-offset-xl-6--right) {
    margin-left: 50%;
  }
  .fr-col-offset-xl-6--right {
    margin-right: 50%;
  }
  .fr-col-xl-7 {
    flex: 0 0 58.3333333333%;
    width: 58.3333333333%;
    max-width: 58.3333333333%;
  }
  .fr-col-offset-xl-7:not(.fr-col-offset-xl-7--right) {
    margin-left: 58.3333333333%;
  }
  .fr-col-offset-xl-7--right {
    margin-right: 58.3333333333%;
  }
  .fr-col-xl-8 {
    flex: 0 0 66.6666666667%;
    width: 66.6666666667%;
    max-width: 66.6666666667%;
  }
  .fr-col-offset-xl-8:not(.fr-col-offset-xl-8--right) {
    margin-left: 66.6666666667%;
  }
  .fr-col-offset-xl-8--right {
    margin-right: 66.6666666667%;
  }
  .fr-col-xl-9 {
    flex: 0 0 75%;
    width: 75%;
    max-width: 75%;
  }
  .fr-col-offset-xl-9:not(.fr-col-offset-xl-9--right) {
    margin-left: 75%;
  }
  .fr-col-offset-xl-9--right {
    margin-right: 75%;
  }
  .fr-col-xl-10 {
    flex: 0 0 83.3333333333%;
    width: 83.3333333333%;
    max-width: 83.3333333333%;
  }
  .fr-col-offset-xl-10:not(.fr-col-offset-xl-10--right) {
    margin-left: 83.3333333333%;
  }
  .fr-col-offset-xl-10--right {
    margin-right: 83.3333333333%;
  }
  .fr-col-xl-11 {
    flex: 0 0 91.6666666667%;
    width: 91.6666666667%;
    max-width: 91.6666666667%;
  }
  .fr-col-offset-xl-11:not(.fr-col-offset-xl-11--right) {
    margin-left: 91.6666666667%;
  }
  .fr-col-offset-xl-11--right {
    margin-right: 91.6666666667%;
  }
  .fr-col-xl-12 {
    flex: 0 0 100%;
    width: 100%;
    max-width: 100%;
  }
  .fr-col-offset-xl-12:not(.fr-col-offset-xl-12--right) {
    margin-left: 100%;
  }
  .fr-col-offset-xl-12--right {
    margin-right: 100%;
  }
  /*! media xl */
}
@media (hover: hover) and (pointer: fine) {
  :root {
    --brighten: -1;
  }
  a[href]:hover,
  button:not(:disabled):hover,
  input[type=button]:not(:disabled):hover,
  input[type=image]:not(:disabled):hover,
  input[type=reset]:not(:disabled):hover,
  input[type=submit]:not(:disabled):hover {
    background-color: var(--hover-tint);
  }
  a[href]:active,
  button:not(:disabled):active,
  input[type=button]:not(:disabled):active,
  input[type=image]:not(:disabled):active,
  input[type=reset]:not(:disabled):active,
  input[type=submit]:not(:disabled):active {
    background-color: var(--active-tint);
  }
  a[href]:hover,
  a[href]:active {
    --underline-hover-width: var(--underline-max-width);
  }
  .fr-enlarge-link a:hover,
  .fr-enlarge-link a:active {
    background: none;
  }
  .fr-enlarge-link:hover {
    background-color: var(--hover);
  }
  .fr-enlarge-link:active {
    background-color: var(--active);
  }
}
@media all and (-ms-high-contrast: none) and (-ms-high-contrast: none), (-ms-high-contrast: none) and (-ms-high-contrast: active), (-ms-high-contrast: active) and (-ms-high-contrast: none), (-ms-high-contrast: active) and (-ms-high-contrast: active) {
  .fr-enlarge-link {
    background-color: transparent;
  }
  .fr-enlarge-link:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  .fr-enlarge-link:active {
    background-color: rgba(0, 0, 0, 0.1);
  }
}
@media all and (-ms-high-contrast: none), (-ms-high-contrast: active) {
  .fr-enlarge-link [href] {
    text-decoration: none;
  }
  .fr-raw-link[href]::after,
  .fr-raw-link [href]::after {
    content: none;
  }
  [target=_blank]::after {
    background-color: transparent;
    background-size: 100%;
    background-repeat: no-repeat;
    background-image: url(&quot;../icons/system/external-link-line.svg&quot;);
    width: 1rem;
    height: 1rem;
    content: &quot;&quot;;
    vertical-align: sub;
  }
  .fr-responsive-vid::before {
    content: &quot;&quot;;
    display: block;
    padding-bottom: 56.25%;
  }
  ul {
    list-style-type: disc;
  }
  ol {
    list-style-type: decimal;
  }
  ul,
  ol {
    padding-left: 1rem;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
  }
  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    margin: 0 0 1.5rem;
    color: #161616;
  }
  p {
    margin: 0 0 1rem;
  }
  [class^=fr-icon-]::before,
  [class*=&quot; fr-icon-&quot;]::before,
  [class^=fr-fi-]::before,
  [class*=&quot; fr-fi-&quot;]::before {
    background-color: transparent;
    background-size: 100%;
    background-repeat: no-repeat;
    width: 1.5rem;
    height: 1.5rem;
  }
  .fr-icon--xs::before {
    width: 0.75rem;
    height: 0.75rem;
  }
  .fr-icon--sm::before {
    width: 1rem;
    height: 1rem;
  }
  .fr-icon--md::before {
    width: 1.5rem;
    height: 1.5rem;
  }
  .fr-icon--lg::before {
    width: 2rem;
    height: 2rem;
  }
  body {
    background-color: #fff;
    color: #3a3a3a;
  }
  a:not([href]),
  button:disabled,
  input:disabled,
  input[type=checkbox]:disabled,
  input[type=checkbox]:disabled + label,
  input[type=radio]:disabled,
  input[type=radio]:disabled + label,
  textarea:disabled,
  video:not([href]),
  audio:not([href]) {
    color: #929292;
  }
  .fr-artwork-decorative {
    fill: #ececfe;
  }
  .fr-artwork-minor {
    fill: #e1000f;
  }
  .fr-artwork-major {
    fill: #000091;
  }
  .fr-artwork-background {
    fill: #f6f6f6;
  }
  .fr-artwork-motif {
    fill: #e5e5e5;
  }
  .fr-artwork--green-tilleul-verveine .fr-artwork-minor {
    fill: #b7a73f;
  }
  .fr-artwork--green-bourgeon .fr-artwork-minor {
    fill: #68a532;
  }
  .fr-artwork--green-emeraude .fr-artwork-minor {
    fill: #00a95f;
  }
  .fr-artwork--green-menthe .fr-artwork-minor {
    fill: #009081;
  }
  .fr-artwork--green-archipel .fr-artwork-minor {
    fill: #009099;
  }
  .fr-artwork--blue-ecume .fr-artwork-minor {
    fill: #465f9d;
  }
  .fr-artwork--blue-cumulus .fr-artwork-minor {
    fill: #417dc4;
  }
  .fr-artwork--purple-glycine .fr-artwork-minor {
    fill: #a558a0;
  }
  .fr-artwork--pink-macaron .fr-artwork-minor {
    fill: #e18b76;
  }
  .fr-artwork--pink-tuile .fr-artwork-minor {
    fill: #ce614a;
  }
  .fr-artwork--yellow-tournesol .fr-artwork-minor {
    fill: #c8aa39;
  }
  .fr-artwork--yellow-moutarde .fr-artwork-minor {
    fill: #c3992a;
  }
  .fr-artwork--orange-terre-battue .fr-artwork-minor {
    fill: #e4794a;
  }
  .fr-artwork--brown-cafe-creme .fr-artwork-minor {
    fill: #d1b781;
  }
  .fr-artwork--brown-caramel .fr-artwork-minor {
    fill: #c08c65;
  }
  .fr-artwork--brown-opera .fr-artwork-minor {
    fill: #bd987a;
  }
  .fr-artwork--beige-gris-galet .fr-artwork-minor {
    fill: #aea397;
  }
  [disabled] .fr-artwork * {
    fill: #929292;
  }
  .fr-h6,
  .fr-h5,
  .fr-h4,
  .fr-h3,
  .fr-h2,
  .fr-h1,
  .fr-display-xs,
  .fr-display-sm,
  .fr-display-md,
  .fr-display-lg,
  .fr-display-xl {
    color: #161616;
  }
  hr {
    background-image: linear-gradient(0deg, #ddd, #ddd);
  }
  .fr-hr-or::before,
  .fr-hr-or::after {
    background-color: #ddd;
  }
  .fr-hr {
    background-image: linear-gradient(0deg, #ddd, #ddd);
  }
}
@media print {
  body {
    background-color: #fff;
    color: #3a3a3a;
  }
  a:not([href]),
  button:disabled,
  input:disabled,
  input[type=checkbox]:disabled,
  input[type=checkbox]:disabled + label,
  input[type=radio]:disabled,
  input[type=radio]:disabled + label,
  textarea:disabled,
  video:not([href]),
  audio:not([href]) {
    color: #929292;
  }
  .fr-artwork-decorative {
    fill: #ececfe;
  }
  .fr-artwork-minor {
    fill: #e1000f;
  }
  .fr-artwork-major {
    fill: #000091;
  }
  .fr-artwork-background {
    fill: #f6f6f6;
  }
  .fr-artwork-motif {
    fill: #e5e5e5;
  }
  .fr-artwork--green-tilleul-verveine .fr-artwork-minor {
    fill: #b7a73f;
  }
  .fr-artwork--green-bourgeon .fr-artwork-minor {
    fill: #68a532;
  }
  .fr-artwork--green-emeraude .fr-artwork-minor {
    fill: #00a95f;
  }
  .fr-artwork--green-menthe .fr-artwork-minor {
    fill: #009081;
  }
  .fr-artwork--green-archipel .fr-artwork-minor {
    fill: #009099;
  }
  .fr-artwork--blue-ecume .fr-artwork-minor {
    fill: #465f9d;
  }
  .fr-artwork--blue-cumulus .fr-artwork-minor {
    fill: #417dc4;
  }
  .fr-artwork--purple-glycine .fr-artwork-minor {
    fill: #a558a0;
  }
  .fr-artwork--pink-macaron .fr-artwork-minor {
    fill: #e18b76;
  }
  .fr-artwork--pink-tuile .fr-artwork-minor {
    fill: #ce614a;
  }
  .fr-artwork--yellow-tournesol .fr-artwork-minor {
    fill: #c8aa39;
  }
  .fr-artwork--yellow-moutarde .fr-artwork-minor {
    fill: #c3992a;
  }
  .fr-artwork--orange-terre-battue .fr-artwork-minor {
    fill: #e4794a;
  }
  .fr-artwork--brown-cafe-creme .fr-artwork-minor {
    fill: #d1b781;
  }
  .fr-artwork--brown-caramel .fr-artwork-minor {
    fill: #c08c65;
  }
  .fr-artwork--brown-opera .fr-artwork-minor {
    fill: #bd987a;
  }
  .fr-artwork--beige-gris-galet .fr-artwork-minor {
    fill: #aea397;
  }
  [disabled] .fr-artwork * {
    fill: #929292;
  }
  .fr-h6,
  .fr-h5,
  .fr-h4,
  .fr-h3,
  .fr-h2,
  .fr-h1,
  .fr-display-xs,
  .fr-display-sm,
  .fr-display-md,
  .fr-display-lg,
  .fr-display-xl {
    color: #161616;
  }
  h6,
  h5,
  h4,
  h3,
  h2,
  h1 {
    color: #161616;
  }
  hr {
    background-image: linear-gradient(0deg, #ddd, #ddd);
  }
  .fr-hr-or::before,
  .fr-hr-or::after {
    background-color: #ddd;
  }
  .fr-hr {
    background-image: linear-gradient(0deg, #ddd, #ddd);
  }
  .fr-no-print {
    display: none;
  }
  h1,
  h2,
  h3,
  h4 {
    page-break-after: avoid;
    -moz-column-break-after: avoid;
         break-after: avoid;
  }
  p {
    orphans: 3;
    widows: 3;
  }
  .fr-text--sm,
  .fr-text--xs {
    font-size: 1rem !important;
    line-height: 1.5rem !important;
    margin: var(--text-spacing);
  }
}
/*!
 * DSFR v1.11.0 | SPDX-License-Identifier: MIT | License-Filename: LICENSE.md | restricted use (see terms and conditions)
 */
/* ¯¯¯¯¯¯¯¯¯ *\
  BUTTON
\* ˍˍˍˍˍˍˍˍˍ */
.fr-btn {
  --text-spacing: 0;
  --title-spacing: 0;
  display: inline-flex;
  flex-direction: row;
  align-items: center;
  width: -moz-fit-content;
  width: fit-content;
  --underline-img: none;
  --hover-tint: var(--hover);
  font-weight: 500;
  font-size: 1rem;
  line-height: 1.5rem;
  min-height: 2.5rem;
  padding: 0.5rem 1rem;
  background-color: var(--background-action-high-blue-france);
  --idle: transparent;
  --hover: var(--background-action-high-blue-france-hover);
  --active: var(--background-action-high-blue-france-active);
  color: var(--text-inverted-blue-france);
}

.fr-btn::before,
.fr-btn::after {
  display: block;
}

.fr-btn[target=_blank] {
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btn[target=_blank]::after {
  content: &quot;&quot;;
  --icon-size: 1rem;
  margin-right: -0.125rem;
  margin-left: 0.5rem;
}

.fr-btn--align-on-content {
  margin-left: -1rem;
  margin-right: -1rem;
}

.fr-btn[class^=fr-icon-]:not([class*=fr-btn--icon-]),
.fr-btn[class*=&quot; fr-icon-&quot;]:not([class*=fr-btn--icon-]),
.fr-btn[class^=fr-fi-]:not([class*=fr-btn--icon-]),
.fr-btn[class*=&quot; fr-fi-&quot;]:not([class*=fr-btn--icon-]) {
  overflow: hidden;
  white-space: nowrap;
  max-width: 2.5rem;
  max-height: 2.5rem;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}

.fr-btn[class^=fr-icon-]:not([class*=fr-btn--icon-])::before,
.fr-btn[class*=&quot; fr-icon-&quot;]:not([class*=fr-btn--icon-])::before,
.fr-btn[class^=fr-fi-]:not([class*=fr-btn--icon-])::before,
.fr-btn[class*=&quot; fr-fi-&quot;]:not([class*=fr-btn--icon-])::before {
  --icon-size: 1.5rem;
  margin-left: 0;
  margin-right: 0.5rem;
}

.fr-btn--align-on-content[class^=fr-icon-]:not([class*=fr-btn--icon-]),
.fr-btn--align-on-content[class*=&quot; fr-icon-&quot;]:not([class*=fr-btn--icon-]),
.fr-btn--align-on-content[class^=fr-fi-]:not([class*=fr-btn--icon-]),
.fr-btn--align-on-content[class*=&quot; fr-fi-&quot;]:not([class*=fr-btn--icon-]) {
  margin-left: -0.5rem;
  margin-right: -0.5rem;
}

.fr-btn--icon-left[class^=fr-icon-],
.fr-btn--icon-left[class*=&quot; fr-icon-&quot;],
.fr-btn--icon-left[class^=fr-fi-],
.fr-btn--icon-left[class*=&quot; fr-fi-&quot;] {
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btn--icon-left[class^=fr-icon-]::before,
.fr-btn--icon-left[class*=&quot; fr-icon-&quot;]::before,
.fr-btn--icon-left[class^=fr-fi-]::before,
.fr-btn--icon-left[class*=&quot; fr-fi-&quot;]::before {
  --icon-size: 1rem;
  margin-left: -0.125rem;
  margin-right: 0.5rem;
}

.fr-btn--align-on-content.fr-btn--icon-left[class^=fr-icon-],
.fr-btn--align-on-content.fr-btn--icon-left[class*=&quot; fr-icon-&quot;],
.fr-btn--align-on-content.fr-btn--icon-left[class^=fr-fi-],
.fr-btn--align-on-content.fr-btn--icon-left[class*=&quot; fr-fi-&quot;] {
  margin-left: -0.875rem;
  margin-right: -1rem;
}

.fr-btn--icon-right[class^=fr-icon-],
.fr-btn--icon-right[class*=&quot; fr-icon-&quot;],
.fr-btn--icon-right[class^=fr-fi-],
.fr-btn--icon-right[class*=&quot; fr-fi-&quot;] {
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btn--icon-right[class^=fr-icon-]::after,
.fr-btn--icon-right[class*=&quot; fr-icon-&quot;]::after,
.fr-btn--icon-right[class^=fr-fi-]::after,
.fr-btn--icon-right[class*=&quot; fr-fi-&quot;]::after {
  content: &quot;&quot;;
  --icon-size: 1rem;
  margin-right: -0.125rem;
  margin-left: 0.5rem;
}

.fr-btn--icon-right[class^=fr-icon-]::before,
.fr-btn--icon-right[class*=&quot; fr-icon-&quot;]::before,
.fr-btn--icon-right[class^=fr-fi-]::before,
.fr-btn--icon-right[class*=&quot; fr-fi-&quot;]::before {
  content: none;
}

.fr-btn--align-on-content.fr-btn--icon-right[class^=fr-icon-],
.fr-btn--align-on-content.fr-btn--icon-right[class*=&quot; fr-icon-&quot;],
.fr-btn--align-on-content.fr-btn--icon-right[class^=fr-fi-],
.fr-btn--align-on-content.fr-btn--icon-right[class*=&quot; fr-fi-&quot;] {
  margin-left: -1rem;
  margin-right: -0.875rem;
}

.fr-btn--sm {
  font-size: 0.875rem;
  line-height: 1.5rem;
  min-height: 2rem;
  padding: 0.25rem 0.75rem;
}

.fr-btn--sm[target=_blank] {
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btn--sm[target=_blank]::after {
  content: &quot;&quot;;
  --icon-size: 1rem;
  margin-right: -0.125rem;
  margin-left: 0.5rem;
}

.fr-btn--sm.fr-btn--align-on-content {
  margin-left: -0.75rem;
  margin-right: -0.75rem;
}

.fr-btn--sm[class^=fr-icon-]:not([class*=fr-btn--icon-]),
.fr-btn--sm[class*=&quot; fr-icon-&quot;]:not([class*=fr-btn--icon-]),
.fr-btn--sm[class^=fr-fi-]:not([class*=fr-btn--icon-]),
.fr-btn--sm[class*=&quot; fr-fi-&quot;]:not([class*=fr-btn--icon-]) {
  overflow: hidden;
  white-space: nowrap;
  max-width: 2rem;
  max-height: 2rem;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}

.fr-btn--sm[class^=fr-icon-]:not([class*=fr-btn--icon-])::before,
.fr-btn--sm[class*=&quot; fr-icon-&quot;]:not([class*=fr-btn--icon-])::before,
.fr-btn--sm[class^=fr-fi-]:not([class*=fr-btn--icon-])::before,
.fr-btn--sm[class*=&quot; fr-fi-&quot;]:not([class*=fr-btn--icon-])::before {
  --icon-size: 1rem;
  margin-left: 0;
  margin-right: 0.5rem;
}

.fr-btn--sm.fr-btn--align-on-content[class^=fr-icon-]:not([class*=fr-btn--icon-]),
.fr-btn--sm.fr-btn--align-on-content[class*=&quot; fr-icon-&quot;]:not([class*=fr-btn--icon-]),
.fr-btn--sm.fr-btn--align-on-content[class^=fr-fi-]:not([class*=fr-btn--icon-]),
.fr-btn--sm.fr-btn--align-on-content[class*=&quot; fr-fi-&quot;]:not([class*=fr-btn--icon-]) {
  margin-left: -0.5rem;
  margin-right: -0.5rem;
}

.fr-btn--sm.fr-btn--icon-left[class^=fr-icon-],
.fr-btn--sm.fr-btn--icon-left[class*=&quot; fr-icon-&quot;],
.fr-btn--sm.fr-btn--icon-left[class^=fr-fi-],
.fr-btn--sm.fr-btn--icon-left[class*=&quot; fr-fi-&quot;] {
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btn--sm.fr-btn--icon-left[class^=fr-icon-]::before,
.fr-btn--sm.fr-btn--icon-left[class*=&quot; fr-icon-&quot;]::before,
.fr-btn--sm.fr-btn--icon-left[class^=fr-fi-]::before,
.fr-btn--sm.fr-btn--icon-left[class*=&quot; fr-fi-&quot;]::before {
  --icon-size: 1rem;
  margin-left: -0.125rem;
  margin-right: 0.5rem;
}

.fr-btn--sm.fr-btn--align-on-content.fr-btn--icon-left[class^=fr-icon-],
.fr-btn--sm.fr-btn--align-on-content.fr-btn--icon-left[class*=&quot; fr-icon-&quot;],
.fr-btn--sm.fr-btn--align-on-content.fr-btn--icon-left[class^=fr-fi-],
.fr-btn--sm.fr-btn--align-on-content.fr-btn--icon-left[class*=&quot; fr-fi-&quot;] {
  margin-left: -0.625rem;
  margin-right: -0.75rem;
}

.fr-btn--sm.fr-btn--icon-right[class^=fr-icon-],
.fr-btn--sm.fr-btn--icon-right[class*=&quot; fr-icon-&quot;],
.fr-btn--sm.fr-btn--icon-right[class^=fr-fi-],
.fr-btn--sm.fr-btn--icon-right[class*=&quot; fr-fi-&quot;] {
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btn--sm.fr-btn--icon-right[class^=fr-icon-]::after,
.fr-btn--sm.fr-btn--icon-right[class*=&quot; fr-icon-&quot;]::after,
.fr-btn--sm.fr-btn--icon-right[class^=fr-fi-]::after,
.fr-btn--sm.fr-btn--icon-right[class*=&quot; fr-fi-&quot;]::after {
  content: &quot;&quot;;
  --icon-size: 1rem;
  margin-right: -0.125rem;
  margin-left: 0.5rem;
}

.fr-btn--sm.fr-btn--icon-right[class^=fr-icon-]::before,
.fr-btn--sm.fr-btn--icon-right[class*=&quot; fr-icon-&quot;]::before,
.fr-btn--sm.fr-btn--icon-right[class^=fr-fi-]::before,
.fr-btn--sm.fr-btn--icon-right[class*=&quot; fr-fi-&quot;]::before {
  content: none;
}

.fr-btn--sm.fr-btn--align-on-content.fr-btn--icon-right[class^=fr-icon-],
.fr-btn--sm.fr-btn--align-on-content.fr-btn--icon-right[class*=&quot; fr-icon-&quot;],
.fr-btn--sm.fr-btn--align-on-content.fr-btn--icon-right[class^=fr-fi-],
.fr-btn--sm.fr-btn--align-on-content.fr-btn--icon-right[class*=&quot; fr-fi-&quot;] {
  margin-left: -0.75rem;
  margin-right: -0.625rem;
}

.fr-btn--lg {
  font-size: 1.125rem;
  line-height: 1.75rem;
  min-height: 3rem;
  padding: 0.5rem 1.5rem;
}

.fr-btn--lg[target=_blank] {
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btn--lg[target=_blank]::after {
  content: &quot;&quot;;
  --icon-size: 1.5rem;
  margin-right: -0.1875rem;
  margin-left: 0.5rem;
}

.fr-btn--lg.fr-btn--align-on-content {
  margin-left: -1.5rem;
  margin-right: -1.5rem;
}

.fr-btn--lg[class^=fr-icon-]:not([class*=fr-btn--icon-]),
.fr-btn--lg[class*=&quot; fr-icon-&quot;]:not([class*=fr-btn--icon-]),
.fr-btn--lg[class^=fr-fi-]:not([class*=fr-btn--icon-]),
.fr-btn--lg[class*=&quot; fr-fi-&quot;]:not([class*=fr-btn--icon-]) {
  overflow: hidden;
  white-space: nowrap;
  max-width: 3rem;
  max-height: 3rem;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}

.fr-btn--lg[class^=fr-icon-]:not([class*=fr-btn--icon-])::before,
.fr-btn--lg[class*=&quot; fr-icon-&quot;]:not([class*=fr-btn--icon-])::before,
.fr-btn--lg[class^=fr-fi-]:not([class*=fr-btn--icon-])::before,
.fr-btn--lg[class*=&quot; fr-fi-&quot;]:not([class*=fr-btn--icon-])::before {
  --icon-size: 2rem;
  margin-left: 0;
  margin-right: 0.5rem;
}

.fr-btn--lg.fr-btn--align-on-content[class^=fr-icon-]:not([class*=fr-btn--icon-]),
.fr-btn--lg.fr-btn--align-on-content[class*=&quot; fr-icon-&quot;]:not([class*=fr-btn--icon-]),
.fr-btn--lg.fr-btn--align-on-content[class^=fr-fi-]:not([class*=fr-btn--icon-]),
.fr-btn--lg.fr-btn--align-on-content[class*=&quot; fr-fi-&quot;]:not([class*=fr-btn--icon-]) {
  margin-left: -0.5rem;
  margin-right: -0.5rem;
}

.fr-btn--lg.fr-btn--icon-left[class^=fr-icon-],
.fr-btn--lg.fr-btn--icon-left[class*=&quot; fr-icon-&quot;],
.fr-btn--lg.fr-btn--icon-left[class^=fr-fi-],
.fr-btn--lg.fr-btn--icon-left[class*=&quot; fr-fi-&quot;] {
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btn--lg.fr-btn--icon-left[class^=fr-icon-]::before,
.fr-btn--lg.fr-btn--icon-left[class*=&quot; fr-icon-&quot;]::before,
.fr-btn--lg.fr-btn--icon-left[class^=fr-fi-]::before,
.fr-btn--lg.fr-btn--icon-left[class*=&quot; fr-fi-&quot;]::before {
  --icon-size: 1.5rem;
  margin-left: -0.1875rem;
  margin-right: 0.5rem;
}

.fr-btn--lg.fr-btn--align-on-content.fr-btn--icon-left[class^=fr-icon-],
.fr-btn--lg.fr-btn--align-on-content.fr-btn--icon-left[class*=&quot; fr-icon-&quot;],
.fr-btn--lg.fr-btn--align-on-content.fr-btn--icon-left[class^=fr-fi-],
.fr-btn--lg.fr-btn--align-on-content.fr-btn--icon-left[class*=&quot; fr-fi-&quot;] {
  margin-left: -1.3125rem;
  margin-right: -1.5rem;
}

.fr-btn--lg.fr-btn--icon-right[class^=fr-icon-],
.fr-btn--lg.fr-btn--icon-right[class*=&quot; fr-icon-&quot;],
.fr-btn--lg.fr-btn--icon-right[class^=fr-fi-],
.fr-btn--lg.fr-btn--icon-right[class*=&quot; fr-fi-&quot;] {
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btn--lg.fr-btn--icon-right[class^=fr-icon-]::after,
.fr-btn--lg.fr-btn--icon-right[class*=&quot; fr-icon-&quot;]::after,
.fr-btn--lg.fr-btn--icon-right[class^=fr-fi-]::after,
.fr-btn--lg.fr-btn--icon-right[class*=&quot; fr-fi-&quot;]::after {
  content: &quot;&quot;;
  --icon-size: 1.5rem;
  margin-right: -0.1875rem;
  margin-left: 0.5rem;
}

.fr-btn--lg.fr-btn--icon-right[class^=fr-icon-]::before,
.fr-btn--lg.fr-btn--icon-right[class*=&quot; fr-icon-&quot;]::before,
.fr-btn--lg.fr-btn--icon-right[class^=fr-fi-]::before,
.fr-btn--lg.fr-btn--icon-right[class*=&quot; fr-fi-&quot;]::before {
  content: none;
}

.fr-btn--lg.fr-btn--align-on-content.fr-btn--icon-right[class^=fr-icon-],
.fr-btn--lg.fr-btn--align-on-content.fr-btn--icon-right[class*=&quot; fr-icon-&quot;],
.fr-btn--lg.fr-btn--align-on-content.fr-btn--icon-right[class^=fr-fi-],
.fr-btn--lg.fr-btn--align-on-content.fr-btn--icon-right[class*=&quot; fr-fi-&quot;] {
  margin-left: -1.5rem;
  margin-right: -1.3125rem;
}

.fr-btns-group {
  --ul-type: none;
  --ol-type: none;
  --ul-start: 0;
  --ol-start: 0;
  --xl-block: 0;
  --li-bottom: 0;
  --ol-content: none;
  display: flex;
  align-items: stretch;
  flex-wrap: wrap;
  margin-left: -0.5rem;
  margin-right: -0.5rem;
  /**
  * fr-btns-group--inline : aligne les boutons horizontalement dans tout les cas
  * fr-btns-group--inline-(sm/md/lg) : permet de passer en horizontal à partir de la valeur du breakpoint appliqué (sm, md, lg)
  */
  /**
  * fr-btns-group--left : (Défaut) aligne les boutons sur la gauche (en lecture L-t-R)
  */
  /**
  * fr-btns-group--right : aligne les boutons sur la droite
  */
  /**
  * fr-btns-group--center : aligne les boutons au centre du conteneur
  */
  /**
  * fr-btns-group--center : aligne les boutons au centre du conteneur
  */
  /**
  * fr-btns-group--equisized : Fixe la largeur des boutons à celle du plus grand. Géré en grande partie en JS.
  */
  /**
  * fr-btns-group--sm : Fixe les boutons à la taille SM
  */
  /**
  * fr-btns-group--md : (défaut) Fixe les boutons à la taille MD
  */
  /**
  * fr-btns-group--lg : Fixe les boutons à la taille LG (sans modfifieur =&gt; MD)
  */
}

.fr-btns-group &gt; li,
.fr-btns-group &gt; div {
  width: 100%;
  max-width: 100%;
}

.fr-btns-group .fr-btn {
  width: calc(100% - 1rem);
  margin: 0 0.5rem 1rem;
  justify-content: center;
}

.fr-btns-group--inline .fr-btn {
  width: auto;
  max-width: 100%;
  margin-left: 0.5rem;
  margin-right: 0.5rem;
}

.fr-btns-group--inline &gt; li {
  display: inline-flex;
  max-width: 100%;
  width: auto;
}

.fr-btns-group--inline.fr-btns-group--right.fr-btns-group--inline-reverse {
  flex-direction: row-reverse;
  justify-content: flex-start;
}

.fr-btns-group--left,
.fr-btns-group--left li {
  justify-content: flex-start;
  text-align: left;
}

.fr-btns-group--right,
.fr-btns-group--right li {
  justify-content: flex-end;
  text-align: right;
}

.fr-btns-group--center,
.fr-btns-group--center li {
  justify-content: center;
  text-align: center;
}

.fr-btns-group--between,
.fr-btns-group--between li {
  justify-content: space-between;
  text-align: center;
}

.fr-btns-group--equisized {
  --equisized-width: auto;
}

.fr-btns-group--equisized .fr-btn {
  justify-content: center;
  width: var(--equisized-width);
}

.fr-btns-group--sm .fr-btn:not([class^=fr-icon-]):not([class*=&quot; fr-icon-&quot;]):not([class^=fr-fi-]):not([class*=&quot; fr-fi-&quot;]) {
  font-size: 0.875rem;
  line-height: 1.5rem;
  min-height: 2rem;
  padding: 0.25rem 0.75rem;
}

.fr-btns-group--sm:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-icon-],
.fr-btns-group--sm:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-icon-&quot;],
.fr-btns-group--sm:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-fi-],
.fr-btns-group--sm:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-fi-&quot;] {
  font-size: 0.875rem;
  line-height: 1.5rem;
  min-height: 2rem;
  padding: 0.25rem 0.75rem;
  overflow: hidden;
  white-space: nowrap;
  max-width: 2rem;
  max-height: 2rem;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
  justify-content: flex-start;
}

.fr-btns-group--sm:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-icon-]::before,
.fr-btns-group--sm:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-icon-&quot;]::before,
.fr-btns-group--sm:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-fi-]::before,
.fr-btns-group--sm:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-fi-&quot;]::before {
  --icon-size: 1rem;
  margin-left: 0;
  margin-right: 0.5rem;
}

.fr-btns-group--sm.fr-btns-group--icon-left .fr-btn[class^=fr-icon-],
.fr-btns-group--sm.fr-btns-group--icon-left .fr-btn[class*=&quot; fr-icon-&quot;],
.fr-btns-group--sm.fr-btns-group--icon-left .fr-btn[class^=fr-fi-],
.fr-btns-group--sm.fr-btns-group--icon-left .fr-btn[class*=&quot; fr-fi-&quot;] {
  font-size: 0.875rem;
  line-height: 1.5rem;
  min-height: 2rem;
  padding: 0.25rem 0.75rem;
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btns-group--sm.fr-btns-group--icon-left .fr-btn[class^=fr-icon-]::before,
.fr-btns-group--sm.fr-btns-group--icon-left .fr-btn[class*=&quot; fr-icon-&quot;]::before,
.fr-btns-group--sm.fr-btns-group--icon-left .fr-btn[class^=fr-fi-]::before,
.fr-btns-group--sm.fr-btns-group--icon-left .fr-btn[class*=&quot; fr-fi-&quot;]::before {
  --icon-size: 1rem;
  margin-left: -0.125rem;
  margin-right: 0.5rem;
}

.fr-btns-group--sm.fr-btns-group--icon-right .fr-btn[class^=fr-icon-],
.fr-btns-group--sm.fr-btns-group--icon-right .fr-btn[class*=&quot; fr-icon-&quot;],
.fr-btns-group--sm.fr-btns-group--icon-right .fr-btn[class^=fr-fi-],
.fr-btns-group--sm.fr-btns-group--icon-right .fr-btn[class*=&quot; fr-fi-&quot;] {
  font-size: 0.875rem;
  line-height: 1.5rem;
  min-height: 2rem;
  padding: 0.25rem 0.75rem;
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btns-group--sm.fr-btns-group--icon-right .fr-btn[class^=fr-icon-]::after,
.fr-btns-group--sm.fr-btns-group--icon-right .fr-btn[class*=&quot; fr-icon-&quot;]::after,
.fr-btns-group--sm.fr-btns-group--icon-right .fr-btn[class^=fr-fi-]::after,
.fr-btns-group--sm.fr-btns-group--icon-right .fr-btn[class*=&quot; fr-fi-&quot;]::after {
  content: &quot;&quot;;
  --icon-size: 1rem;
  margin-right: -0.125rem;
  margin-left: 0.5rem;
}

.fr-btns-group--sm.fr-btns-group--icon-right .fr-btn[class^=fr-icon-]::before,
.fr-btns-group--sm.fr-btns-group--icon-right .fr-btn[class*=&quot; fr-icon-&quot;]::before,
.fr-btns-group--sm.fr-btns-group--icon-right .fr-btn[class^=fr-fi-]::before,
.fr-btns-group--sm.fr-btns-group--icon-right .fr-btn[class*=&quot; fr-fi-&quot;]::before {
  content: none;
}

.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg) .fr-btn:not([class^=fr-icon-]):not([class*=&quot; fr-icon-&quot;]):not([class^=fr-fi-]):not([class*=&quot; fr-fi-&quot;]) {
  font-size: 1rem;
  line-height: 1.5rem;
  min-height: 2.5rem;
  padding: 0.5rem 1rem;
}

.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg):not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-icon-],
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg):not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-icon-&quot;],
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg):not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-fi-],
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg):not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-fi-&quot;] {
  font-size: 1rem;
  line-height: 1.5rem;
  min-height: 2.5rem;
  padding: 0.5rem 1rem;
  overflow: hidden;
  white-space: nowrap;
  max-width: 2.5rem;
  max-height: 2.5rem;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
  justify-content: flex-start;
}

.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg):not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-icon-]::before,
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg):not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-icon-&quot;]::before,
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg):not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-fi-]::before,
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg):not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-fi-&quot;]::before {
  --icon-size: 1.5rem;
  margin-left: 0;
  margin-right: 0.5rem;
}

.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-left .fr-btn[class^=fr-icon-],
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-left .fr-btn[class*=&quot; fr-icon-&quot;],
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-left .fr-btn[class^=fr-fi-],
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-left .fr-btn[class*=&quot; fr-fi-&quot;] {
  font-size: 1rem;
  line-height: 1.5rem;
  min-height: 2.5rem;
  padding: 0.5rem 1rem;
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-left .fr-btn[class^=fr-icon-]::before,
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-left .fr-btn[class*=&quot; fr-icon-&quot;]::before,
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-left .fr-btn[class^=fr-fi-]::before,
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-left .fr-btn[class*=&quot; fr-fi-&quot;]::before {
  --icon-size: 1rem;
  margin-left: -0.125rem;
  margin-right: 0.5rem;
}

.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-right .fr-btn[class^=fr-icon-],
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-right .fr-btn[class*=&quot; fr-icon-&quot;],
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-right .fr-btn[class^=fr-fi-],
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-right .fr-btn[class*=&quot; fr-fi-&quot;] {
  font-size: 1rem;
  line-height: 1.5rem;
  min-height: 2.5rem;
  padding: 0.5rem 1rem;
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-right .fr-btn[class^=fr-icon-]::after,
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-right .fr-btn[class*=&quot; fr-icon-&quot;]::after,
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-right .fr-btn[class^=fr-fi-]::after,
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-right .fr-btn[class*=&quot; fr-fi-&quot;]::after {
  content: &quot;&quot;;
  --icon-size: 1rem;
  margin-right: -0.125rem;
  margin-left: 0.5rem;
}

.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-right .fr-btn[class^=fr-icon-]::before,
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-right .fr-btn[class*=&quot; fr-icon-&quot;]::before,
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-right .fr-btn[class^=fr-fi-]::before,
.fr-btns-group:not(.fr-btns-group--sm):not(.fr-btns-group--lg).fr-btns-group--icon-right .fr-btn[class*=&quot; fr-fi-&quot;]::before {
  content: none;
}

.fr-btns-group--lg .fr-btn:not([class^=fr-icon-]):not([class*=&quot; fr-icon-&quot;]):not([class^=fr-fi-]):not([class*=&quot; fr-fi-&quot;]) {
  font-size: 1.125rem;
  line-height: 1.75rem;
  min-height: 3rem;
  padding: 0.5rem 1.5rem;
}

.fr-btns-group--lg:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-icon-],
.fr-btns-group--lg:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-icon-&quot;],
.fr-btns-group--lg:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-fi-],
.fr-btns-group--lg:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-fi-&quot;] {
  font-size: 1.125rem;
  line-height: 1.75rem;
  min-height: 3rem;
  padding: 0.5rem 1.5rem;
  overflow: hidden;
  white-space: nowrap;
  max-width: 3rem;
  max-height: 3rem;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
  justify-content: flex-start;
}

.fr-btns-group--lg:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-icon-]::before,
.fr-btns-group--lg:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-icon-&quot;]::before,
.fr-btns-group--lg:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-fi-]::before,
.fr-btns-group--lg:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-fi-&quot;]::before {
  --icon-size: 2rem;
  margin-left: 0;
  margin-right: 0.5rem;
}

.fr-btns-group--lg.fr-btns-group--icon-left .fr-btn[class^=fr-icon-],
.fr-btns-group--lg.fr-btns-group--icon-left .fr-btn[class*=&quot; fr-icon-&quot;],
.fr-btns-group--lg.fr-btns-group--icon-left .fr-btn[class^=fr-fi-],
.fr-btns-group--lg.fr-btns-group--icon-left .fr-btn[class*=&quot; fr-fi-&quot;] {
  font-size: 1.125rem;
  line-height: 1.75rem;
  min-height: 3rem;
  padding: 0.5rem 1.5rem;
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btns-group--lg.fr-btns-group--icon-left .fr-btn[class^=fr-icon-]::before,
.fr-btns-group--lg.fr-btns-group--icon-left .fr-btn[class*=&quot; fr-icon-&quot;]::before,
.fr-btns-group--lg.fr-btns-group--icon-left .fr-btn[class^=fr-fi-]::before,
.fr-btns-group--lg.fr-btns-group--icon-left .fr-btn[class*=&quot; fr-fi-&quot;]::before {
  --icon-size: 1.5rem;
  margin-left: -0.1875rem;
  margin-right: 0.5rem;
}

.fr-btns-group--lg.fr-btns-group--icon-right .fr-btn[class^=fr-icon-],
.fr-btns-group--lg.fr-btns-group--icon-right .fr-btn[class*=&quot; fr-icon-&quot;],
.fr-btns-group--lg.fr-btns-group--icon-right .fr-btn[class^=fr-fi-],
.fr-btns-group--lg.fr-btns-group--icon-right .fr-btn[class*=&quot; fr-fi-&quot;] {
  font-size: 1.125rem;
  line-height: 1.75rem;
  min-height: 3rem;
  padding: 0.5rem 1.5rem;
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btns-group--lg.fr-btns-group--icon-right .fr-btn[class^=fr-icon-]::after,
.fr-btns-group--lg.fr-btns-group--icon-right .fr-btn[class*=&quot; fr-icon-&quot;]::after,
.fr-btns-group--lg.fr-btns-group--icon-right .fr-btn[class^=fr-fi-]::after,
.fr-btns-group--lg.fr-btns-group--icon-right .fr-btn[class*=&quot; fr-fi-&quot;]::after {
  content: &quot;&quot;;
  --icon-size: 1.5rem;
  margin-right: -0.1875rem;
  margin-left: 0.5rem;
}

.fr-btns-group--lg.fr-btns-group--icon-right .fr-btn[class^=fr-icon-]::before,
.fr-btns-group--lg.fr-btns-group--icon-right .fr-btn[class*=&quot; fr-icon-&quot;]::before,
.fr-btns-group--lg.fr-btns-group--icon-right .fr-btn[class^=fr-fi-]::before,
.fr-btns-group--lg.fr-btns-group--icon-right .fr-btn[class*=&quot; fr-fi-&quot;]::before {
  content: none;
}

.fr-fieldset__element &gt; .fr-btns-group {
  margin-bottom: -1rem;
}

.fr-btn--close {
  font-size: 0.875rem;
  line-height: 1.5rem;
  min-height: 2rem;
  padding: 0.25rem 0.75rem;
  overflow: initial;
  max-width: 100%;
  max-height: none;
  display: flex;
  margin-left: auto;
}

.fr-btn--close::after {
  --icon-size: 1rem;
  margin-right: -0.125rem;
  margin-left: 0.5rem;
  flex: 0 0 auto;
  display: inline-block;
  vertical-align: calc((0.75em - var(--icon-size)) * 0.5);
  background-color: currentColor;
  width: var(--icon-size);
  height: var(--icon-size);
  -webkit-mask-size: 100% 100%;
  mask-size: 100% 100%;
  -webkit-mask-image: url(&quot;../../icons/system/close-line.svg&quot;);
  mask-image: url(&quot;../../icons/system/close-line.svg&quot;);
  content: &quot;&quot;;
}

.fr-btn--close::before {
  content: none;
}

.fr-btn--tooltip {
  font-size: 0.875rem;
  line-height: 1.5rem;
  min-height: 2rem;
  padding: 0.25rem 0.75rem;
  overflow: hidden;
  white-space: nowrap;
  max-width: 2rem;
  max-height: 2rem;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}

.fr-btn--tooltip::before {
  --icon-size: 1rem;
  margin-left: 0;
  margin-right: 0.5rem;
  flex: 0 0 auto;
  display: inline-block;
  vertical-align: calc((0.75em - var(--icon-size)) * 0.5);
  background-color: currentColor;
  width: var(--icon-size);
  height: var(--icon-size);
  -webkit-mask-size: 100% 100%;
  mask-size: 100% 100%;
  -webkit-mask-image: url(&quot;../../icons/system/question-line.svg&quot;);
  mask-image: url(&quot;../../icons/system/question-line.svg&quot;);
  content: &quot;&quot;;
}

.fr-btn--fullscreen {
  font-size: 0.875rem;
  line-height: 1.5rem;
  min-height: 2rem;
  padding: 0.25rem 0.75rem;
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btn--fullscreen::after {
  --icon-size: 1rem;
  margin-right: -0.125rem;
  margin-left: 0.5rem;
  flex: 0 0 auto;
  display: inline-block;
  vertical-align: calc((0.75em - var(--icon-size)) * 0.5);
  background-color: currentColor;
  width: var(--icon-size);
  height: var(--icon-size);
  -webkit-mask-size: 100% 100%;
  mask-size: 100% 100%;
  -webkit-mask-image: url(&quot;../../icons/media/fullscreen-line.svg&quot;);
  mask-image: url(&quot;../../icons/media/fullscreen-line.svg&quot;);
  content: &quot;&quot;;
}

.fr-btn--fullscreen::before {
  content: none;
}

.fr-btn--display {
  font-size: 1rem;
  line-height: 1.5rem;
  min-height: 2.5rem;
  padding: 0.5rem 1rem;
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btn--display::before {
  --icon-size: 1rem;
  margin-left: -0.125rem;
  margin-right: 0.5rem;
  flex: 0 0 auto;
  display: inline-block;
  vertical-align: calc((0.75em - var(--icon-size)) * 0.5);
  background-color: currentColor;
  width: var(--icon-size);
  height: var(--icon-size);
  -webkit-mask-size: 100% 100%;
  mask-size: 100% 100%;
  -webkit-mask-image: url(&quot;../../icons/system/fr--theme-fill.svg&quot;);
  mask-image: url(&quot;../../icons/system/fr--theme-fill.svg&quot;);
  content: &quot;&quot;;
}

.fr-btn--account {
  font-size: 0.875rem;
  line-height: 1.5rem;
  min-height: 2rem;
  padding: 0.25rem 0.75rem;
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btn--account::before {
  --icon-size: 1rem;
  margin-left: -0.125rem;
  margin-right: 0.5rem;
  flex: 0 0 auto;
  display: inline-block;
  vertical-align: calc((0.75em - var(--icon-size)) * 0.5);
  background-color: currentColor;
  width: var(--icon-size);
  height: var(--icon-size);
  -webkit-mask-size: 100% 100%;
  mask-size: 100% 100%;
  -webkit-mask-image: url(&quot;../../icons/user/account-circle-fill.svg&quot;);
  mask-image: url(&quot;../../icons/user/account-circle-fill.svg&quot;);
  content: &quot;&quot;;
}

.fr-btn--team {
  font-size: 0.875rem;
  line-height: 1.5rem;
  min-height: 2rem;
  padding: 0.25rem 0.75rem;
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btn--team::before {
  --icon-size: 1rem;
  margin-left: -0.125rem;
  margin-right: 0.5rem;
  flex: 0 0 auto;
  display: inline-block;
  vertical-align: calc((0.75em - var(--icon-size)) * 0.5);
  background-color: currentColor;
  width: var(--icon-size);
  height: var(--icon-size);
  -webkit-mask-size: 100% 100%;
  mask-size: 100% 100%;
  -webkit-mask-image: url(&quot;../../icons/user/team-line.svg&quot;);
  mask-image: url(&quot;../../icons/user/team-line.svg&quot;);
  content: &quot;&quot;;
}

.fr-btn--briefcase {
  font-size: 0.875rem;
  line-height: 1.5rem;
  min-height: 2rem;
  padding: 0.25rem 0.75rem;
  overflow: initial;
  max-width: 100%;
  max-height: none;
}

.fr-btn--briefcase::before {
  --icon-size: 1rem;
  margin-left: -0.125rem;
  margin-right: 0.5rem;
  flex: 0 0 auto;
  display: inline-block;
  vertical-align: calc((0.75em - var(--icon-size)) * 0.5);
  background-color: currentColor;
  width: var(--icon-size);
  height: var(--icon-size);
  -webkit-mask-size: 100% 100%;
  mask-size: 100% 100%;
  -webkit-mask-image: url(&quot;../../icons/business/briefcase-fill.svg&quot;);
  mask-image: url(&quot;../../icons/business/briefcase-fill.svg&quot;);
  content: &quot;&quot;;
}

.fr-btn:disabled,
a.fr-btn:not([href]) {
  color: var(--text-disabled-grey);
  background-color: var(--background-disabled-grey);
  --idle: transparent;
  --hover: var(--background-disabled-grey-hover);
  --active: var(--background-disabled-grey-active);
}

.fr-btn--secondary {
  background-color: transparent;
  --hover: inherit;
  --active: inherit;
  color: var(--text-action-high-blue-france);
  box-shadow: inset 0 0 0 1px var(--border-action-high-blue-france);
}

.fr-btn--secondary:disabled,
a.fr-btn--secondary:not([href]) {
  color: var(--text-disabled-grey);
  box-shadow: inset 0 0 0 1px var(--border-disabled-grey);
  background-color: transparent;
  --hover: inherit;
  --active: inherit;
}

.fr-btn--tertiary,
.fr-btn--account {
  background-color: transparent;
  --hover: inherit;
  --active: inherit;
  color: var(--text-action-high-blue-france);
  box-shadow: inset 0 0 0 1px var(--border-default-grey);
}

.fr-btn--tertiary:disabled,
a.fr-btn--tertiary:not([href]),
a.fr-btn--account:not([href]),
.fr-btn--account:disabled {
  color: var(--text-disabled-grey);
  box-shadow: inset 0 0 0 1px var(--border-disabled-grey);
  background-color: transparent;
  --hover: inherit;
  --active: inherit;
}

.fr-btn--tertiary-no-outline,
.fr-btn--close,
.fr-btn--display,
.fr-btn--fullscreen,
.fr-btn--tooltip,
.fr-btn--briefcase,
.fr-btn--team {
  background-color: transparent;
  --hover: inherit;
  --active: inherit;
  color: var(--text-action-high-blue-france);
}

.fr-btn--tertiary-no-outline:disabled,
a.fr-btn--tertiary-no-outline:not([href]),
a.fr-btn--close:not([href]),
a.fr-btn--display:not([href]),
a.fr-btn--fullscreen:not([href]),
a.fr-btn--tooltip:not([href]),
a.fr-btn--briefcase:not([href]),
a.fr-btn--team:not([href]),
.fr-btn--close:disabled,
.fr-btn--display:disabled,
.fr-btn--fullscreen:disabled,
.fr-btn--tooltip:disabled,
.fr-btn--briefcase:disabled,
.fr-btn--team:disabled {
  color: var(--text-disabled-grey);
  background-color: transparent;
  --hover: inherit;
  --active: inherit;
}

@media (min-width: 36em) {
  /*! media sm */
  .fr-btns-group--inline-sm .fr-btn {
    width: auto;
    max-width: 100%;
    margin-left: 0.5rem;
    margin-right: 0.5rem;
  }
  .fr-btns-group--inline-sm &gt; li {
    display: inline-flex;
    max-width: 100%;
    width: auto;
  }
  .fr-btns-group--inline-sm.fr-btns-group--right.fr-btns-group--inline-reverse {
    flex-direction: row-reverse;
    justify-content: flex-start;
  }
  /*! media sm */
}
@media (min-width: 48em) {
  /*! media md */
  .fr-btns-group--inline-md .fr-btn {
    width: auto;
    max-width: 100%;
    margin-left: 0.5rem;
    margin-right: 0.5rem;
  }
  .fr-btns-group--inline-md &gt; li {
    display: inline-flex;
    max-width: 100%;
    width: auto;
  }
  .fr-btns-group--inline-md.fr-btns-group--right.fr-btns-group--inline-reverse {
    flex-direction: row-reverse;
    justify-content: flex-start;
  }
  /*! media md */
}
@media (min-width: 62em) {
  /*! media lg */
  .fr-btns-group--inline-lg .fr-btn {
    width: auto;
    max-width: 100%;
    margin-left: 0.5rem;
    margin-right: 0.5rem;
  }
  .fr-btns-group--inline-lg &gt; li {
    display: inline-flex;
    max-width: 100%;
    width: auto;
  }
  .fr-btns-group--inline-lg.fr-btns-group--right.fr-btns-group--inline-reverse {
    flex-direction: row-reverse;
    justify-content: flex-start;
  }
  /*! media lg */
}
@media (min-width: 78em) {
  /*! media xl */
  /*! media xl */
}
@media all and (-ms-high-contrast: none), (-ms-high-contrast: active) {
  .fr-btn::before,
  .fr-btn::after {
    background-color: transparent;
    background-size: 100%;
    background-repeat: no-repeat;
    width: 1rem;
    height: 1rem;
  }
  .fr-btn[href] {
    text-decoration: none;
  }
  .fr-btn[class^=fr-icon-]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::before,
  .fr-btn[class^=fr-icon-]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::after,
  .fr-btn[class*=&quot; fr-icon-&quot;]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::before,
  .fr-btn[class*=&quot; fr-icon-&quot;]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::after,
  .fr-btn[class^=fr-fi-]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::before,
  .fr-btn[class^=fr-fi-]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::after,
  .fr-btn[class*=&quot; fr-fi-&quot;]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::before,
  .fr-btn[class*=&quot; fr-fi-&quot;]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::after {
    background-color: transparent;
    background-size: 100%;
    background-repeat: no-repeat;
    width: 1.5rem;
    height: 1.5rem;
  }
  .fr-btn--sm::before,
  .fr-btn--sm::after {
    background-color: transparent;
    background-size: 100%;
    background-repeat: no-repeat;
    width: 0.75rem;
    height: 0.75rem;
  }
  .fr-btn--sm[class^=fr-icon-]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::before,
  .fr-btn--sm[class^=fr-icon-]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::after,
  .fr-btn--sm[class*=&quot; fr-icon-&quot;]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::before,
  .fr-btn--sm[class*=&quot; fr-icon-&quot;]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::after,
  .fr-btn--sm[class^=fr-fi-]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::before,
  .fr-btn--sm[class^=fr-fi-]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::after,
  .fr-btn--sm[class*=&quot; fr-fi-&quot;]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::before,
  .fr-btn--sm[class*=&quot; fr-fi-&quot;]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::after {
    background-color: transparent;
    background-size: 100%;
    background-repeat: no-repeat;
    width: 1rem;
    height: 1rem;
  }
  .fr-btn--lg::before,
  .fr-btn--lg::after {
    background-color: transparent;
    background-size: 100%;
    background-repeat: no-repeat;
    width: 1.5rem;
    height: 1.5rem;
  }
  .fr-btn--lg[class^=fr-icon-]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::before,
  .fr-btn--lg[class^=fr-icon-]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::after,
  .fr-btn--lg[class*=&quot; fr-icon-&quot;]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::before,
  .fr-btn--lg[class*=&quot; fr-icon-&quot;]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::after,
  .fr-btn--lg[class^=fr-fi-]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::before,
  .fr-btn--lg[class^=fr-fi-]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::after,
  .fr-btn--lg[class*=&quot; fr-fi-&quot;]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::before,
  .fr-btn--lg[class*=&quot; fr-fi-&quot;]:not([class^=fr-btn--icon-]):not([class*=&quot; fr-btn--icon-&quot;])::after {
    background-color: transparent;
    background-size: 100%;
    background-repeat: no-repeat;
    width: 2rem;
    height: 2rem;
  }
  .fr-btn--close::before,
  .fr-btn--close::after {
    background-color: transparent;
    background-size: 100%;
    background-repeat: no-repeat;
    background-image: url(&quot;../../icons/system/close-line.svg&quot;);
    width: 1rem;
    height: 1rem;
  }
  .fr-btn--tooltip::before,
  .fr-btn--tooltip::after {
    background-color: transparent;
    background-size: 100%;
    background-repeat: no-repeat;
    background-image: url(&quot;../../icons/system/question-line.svg&quot;);
    width: 1rem;
    height: 1rem;
  }
  .fr-btn--fullscreen::before,
  .fr-btn--fullscreen::after {
    background-color: transparent;
    background-size: 100%;
    background-repeat: no-repeat;
    background-image: url(&quot;../../icons/media/fullscreen-line.svg&quot;);
    width: 1rem;
    height: 1rem;
  }
  .fr-btn--display::before,
  .fr-btn--display::after {
    background-color: transparent;
    background-size: 100%;
    background-repeat: no-repeat;
    background-image: url(&quot;../../icons/system/fr--theme-fill.svg&quot;);
    width: 1rem;
    height: 1rem;
  }
  .fr-btn--briefcase::before,
  .fr-btn--briefcase::after {
    background-color: transparent;
    background-size: 100%;
    background-repeat: no-repeat;
    background-image: url(&quot;../../icons/business/briefcase-fill.svg&quot;);
    width: 1rem;
    height: 1rem;
  }
  .fr-btn--account::before,
  .fr-btn--account::after {
    background-color: transparent;
    background-size: 100%;
    background-repeat: no-repeat;
    background-image: url(&quot;../../icons/user/account-circle-fill.svg&quot;);
    width: 1rem;
    height: 1rem;
  }
  .fr-btn--team::before,
  .fr-btn--team::after {
    background-color: transparent;
    background-size: 100%;
    background-repeat: no-repeat;
    background-image: url(&quot;../../icons/user/team-line.svg&quot;);
    width: 1rem;
    height: 1rem;
  }
  ul.fr-btns-group {
    list-style-type: none;
  }
  ol.fr-btns-group {
    list-style-type: none;
  }
  ul.fr-btns-group,
  ol.fr-btns-group {
    padding-left: 0;
    margin-top: 0;
    margin-bottom: 0;
  }
  .fr-btns-group--sm:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-icon-]::before,
  .fr-btns-group--sm:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-icon-]::after,
  .fr-btns-group--sm:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-icon-&quot;]::before,
  .fr-btns-group--sm:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-icon-&quot;]::after,
  .fr-btns-group--sm:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-fi-]::before,
  .fr-btns-group--sm:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-fi-]::after,
  .fr-btns-group--sm:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-fi-&quot;]::before,
  .fr-btns-group--sm:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-fi-&quot;]::after {
    background-color: transparent;
    background-size: 100%;
    background-repeat: no-repeat;
    width: 1rem;
    height: 1rem;
  }
  .fr-btns-group--lg:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-icon-]::before,
  .fr-btns-group--lg:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-icon-]::after,
  .fr-btns-group--lg:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-icon-&quot;]::before,
  .fr-btns-group--lg:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-icon-&quot;]::after,
  .fr-btns-group--lg:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-fi-]::before,
  .fr-btns-group--lg:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class^=fr-fi-]::after,
  .fr-btns-group--lg:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-fi-&quot;]::before,
  .fr-btns-group--lg:not([class^=fr-btns-group--icon-]):not([class*=&quot; fr-btns-group--icon-&quot;]) .fr-btn[class*=&quot; fr-fi-&quot;]::after {
    background-color: transparent;
    background-size: 100%;
    background-repeat: no-repeat;
    width: 2rem;
    height: 2rem;
  }
  .fr-btn {
    background-color: #000091;
    color: #f5f5fe;
  }
  .fr-btn:hover {
    background-color: #1212ff;
  }
  .fr-btn:active {
    background-color: #2323ff;
  }
  .fr-btn:disabled,
  a.fr-btn:not([href]) {
    color: #929292;
    background-color: #e5e5e5;
  }
  .fr-btn--secondary {
    background-color: transparent;
    color: #000091;
    box-shadow: inset 0 0 0 1px #000091;
  }
  .fr-btn--secondary:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  .fr-btn--secondary:active {
    background-color: rgba(0, 0, 0, 0.1);
  }
  .fr-btn--secondary:disabled,
  a.fr-btn--secondary:not([href]) {
    color: #929292;
    box-shadow: inset 0 0 0 1px #e5e5e5;
    background-color: transparent;
  }
  .fr-btn--secondary:disabled:hover,
  a.fr-btn--secondary:not([href]):hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  .fr-btn--secondary:disabled:active,
  a.fr-btn--secondary:not([href]):active {
    background-color: rgba(0, 0, 0, 0.1);
  }
  .fr-btn--tertiary,
  .fr-btn--account {
    background-color: transparent;
    color: #000091;
    box-shadow: inset 0 0 0 1px #ddd;
  }
  .fr-btn--tertiary:hover,
  .fr-btn--account:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  .fr-btn--tertiary:active,
  .fr-btn--account:active {
    background-color: rgba(0, 0, 0, 0.1);
  }
  .fr-btn--tertiary:disabled,
  a.fr-btn--tertiary:not([href]),
  a.fr-btn--account:not([href]),
  .fr-btn--account:disabled {
    color: #929292;
    box-shadow: inset 0 0 0 1px #e5e5e5;
    background-color: transparent;
  }
  .fr-btn--tertiary:disabled:hover,
  a.fr-btn--tertiary:not([href]):hover,
  a.fr-btn--account:not([href]):hover,
  .fr-btn--account:disabled:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  .fr-btn--tertiary:disabled:active,
  a.fr-btn--tertiary:not([href]):active,
  a.fr-btn--account:not([href]):active,
  .fr-btn--account:disabled:active {
    background-color: rgba(0, 0, 0, 0.1);
  }
  .fr-btn--tertiary-no-outline,
  .fr-btn--close,
  .fr-btn--display,
  .fr-btn--fullscreen,
  .fr-btn--tooltip,
  .fr-btn--briefcase,
  .fr-btn--team {
    background-color: transparent;
    color: #000091;
  }
  .fr-btn--tertiary-no-outline:hover,
  .fr-btn--close:hover,
  .fr-btn--display:hover,
  .fr-btn--fullscreen:hover,
  .fr-btn--tooltip:hover,
  .fr-btn--briefcase:hover,
  .fr-btn--team:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  .fr-btn--tertiary-no-outline:active,
  .fr-btn--close:active,
  .fr-btn--display:active,
  .fr-btn--fullscreen:active,
  .fr-btn--tooltip:active,
  .fr-btn--briefcase:active,
  .fr-btn--team:active {
    background-color: rgba(0, 0, 0, 0.1);
  }
  .fr-btn--tertiary-no-outline:disabled,
  a.fr-btn--tertiary-no-outline:not([href]),
  a.fr-btn--close:not([href]),
  a.fr-btn--display:not([href]),
  a.fr-btn--fullscreen:not([href]),
  a.fr-btn--tooltip:not([href]),
  a.fr-btn--briefcase:not([href]),
  a.fr-btn--team:not([href]),
  .fr-btn--close:disabled,
  .fr-btn--display:disabled,
  .fr-btn--fullscreen:disabled,
  .fr-btn--tooltip:disabled,
  .fr-btn--briefcase:disabled,
  .fr-btn--team:disabled {
    color: #929292;
    background-color: transparent;
  }
  .fr-btn--tertiary-no-outline:disabled:hover,
  a.fr-btn--tertiary-no-outline:not([href]):hover,
  a.fr-btn--close:not([href]):hover,
  a.fr-btn--display:not([href]):hover,
  a.fr-btn--fullscreen:not([href]):hover,
  a.fr-btn--tooltip:not([href]):hover,
  a.fr-btn--briefcase:not([href]):hover,
  a.fr-btn--team:not([href]):hover,
  .fr-btn--close:disabled:hover,
  .fr-btn--display:disabled:hover,
  .fr-btn--fullscreen:disabled:hover,
  .fr-btn--tooltip:disabled:hover,
  .fr-btn--briefcase:disabled:hover,
  .fr-btn--team:disabled:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  .fr-btn--tertiary-no-outline:disabled:active,
  a.fr-btn--tertiary-no-outline:not([href]):active,
  a.fr-btn--close:not([href]):active,
  a.fr-btn--display:not([href]):active,
  a.fr-btn--fullscreen:not([href]):active,
  a.fr-btn--tooltip:not([href]):active,
  a.fr-btn--briefcase:not([href]):active,
  a.fr-btn--team:not([href]):active,
  .fr-btn--close:disabled:active,
  .fr-btn--display:disabled:active,
  .fr-btn--fullscreen:disabled:active,
  .fr-btn--tooltip:disabled:active,
  .fr-btn--briefcase:disabled:active,
  .fr-btn--team:disabled:active {
    background-color: rgba(0, 0, 0, 0.1);
  }
}
@media print {
  .fr-btn {
    background-color: #000091;
    color: #f5f5fe;
  }
  .fr-btn:hover {
    background-color: #1212ff;
  }
  .fr-btn:active {
    background-color: #2323ff;
  }
  .fr-btn:disabled,
  a.fr-btn:not([href]) {
    color: #929292;
    background-color: #e5e5e5;
  }
  .fr-btn--secondary {
    color: #000091;
    box-shadow: inset 0 0 0 1px #000091;
  }
  .fr-btn--secondary:disabled,
  a.fr-btn--secondary:not([href]) {
    color: #929292;
    box-shadow: inset 0 0 0 1px #e5e5e5;
  }
  .fr-btn--tertiary,
  .fr-btn--account {
    color: #000091;
    box-shadow: inset 0 0 0 1px #ddd;
  }
  .fr-btn--tertiary:disabled,
  a.fr-btn--tertiary:not([href]),
  a.fr-btn--account:not([href]),
  .fr-btn--account:disabled {
    color: #929292;
    box-shadow: inset 0 0 0 1px #e5e5e5;
  }
  .fr-btn--tertiary-no-outline,
  .fr-btn--close,
  .fr-btn--display,
  .fr-btn--fullscreen,
  .fr-btn--tooltip,
  .fr-btn--briefcase,
  .fr-btn--team {
    color: #000091;
  }
  .fr-btn--tertiary-no-outline:disabled,
  a.fr-btn--tertiary-no-outline:not([href]),
  a.fr-btn--close:not([href]),
  a.fr-btn--display:not([href]),
  a.fr-btn--fullscreen:not([href]),
  a.fr-btn--tooltip:not([href]),
  a.fr-btn--briefcase:not([href]),
  a.fr-btn--team:not([href]),
  .fr-btn--close:disabled,
  .fr-btn--display:disabled,
  .fr-btn--fullscreen:disabled,
  .fr-btn--tooltip:disabled,
  .fr-btn--briefcase:disabled,
  .fr-btn--team:disabled {
    color: #929292;
  }
  .fr-btn--secondary,
  .fr-btn--tertiary,
  .fr-btn--tertiary-no-outline,
  .fr-btn--close,
  .fr-btn--display,
  .fr-btn--fullscreen,
  .fr-btn--tooltip {
    background-color: transparent;
  }
}
@media print and (-ms-high-contrast: none), print and (-ms-high-contrast: active) {
  .fr-btn--secondary {
    background-color: transparent;
  }
  .fr-btn--secondary:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  .fr-btn--secondary:active {
    background-color: rgba(0, 0, 0, 0.1);
  }
  .fr-btn--secondary:disabled,
  a.fr-btn--secondary:not([href]) {
    background-color: transparent;
  }
  .fr-btn--secondary:disabled:hover,
  a.fr-btn--secondary:not([href]):hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  .fr-btn--secondary:disabled:active,
  a.fr-btn--secondary:not([href]):active {
    background-color: rgba(0, 0, 0, 0.1);
  }
  .fr-btn--tertiary,
  .fr-btn--account {
    background-color: transparent;
  }
  .fr-btn--tertiary:hover,
  .fr-btn--account:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  .fr-btn--tertiary:active,
  .fr-btn--account:active {
    background-color: rgba(0, 0, 0, 0.1);
  }
  .fr-btn--tertiary:disabled,
  a.fr-btn--tertiary:not([href]),
  a.fr-btn--account:not([href]),
  .fr-btn--account:disabled {
    background-color: transparent;
  }
  .fr-btn--tertiary:disabled:hover,
  a.fr-btn--tertiary:not([href]):hover,
  a.fr-btn--account:not([href]):hover,
  .fr-btn--account:disabled:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  .fr-btn--tertiary:disabled:active,
  a.fr-btn--tertiary:not([href]):active,
  a.fr-btn--account:not([href]):active,
  .fr-btn--account:disabled:active {
    background-color: rgba(0, 0, 0, 0.1);
  }
  .fr-btn--tertiary-no-outline,
  .fr-btn--close,
  .fr-btn--display,
  .fr-btn--fullscreen,
  .fr-btn--tooltip,
  .fr-btn--briefcase,
  .fr-btn--team {
    background-color: transparent;
  }
  .fr-btn--tertiary-no-outline:hover,
  .fr-btn--close:hover,
  .fr-btn--display:hover,
  .fr-btn--fullscreen:hover,
  .fr-btn--tooltip:hover,
  .fr-btn--briefcase:hover,
  .fr-btn--team:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  .fr-btn--tertiary-no-outline:active,
  .fr-btn--close:active,
  .fr-btn--display:active,
  .fr-btn--fullscreen:active,
  .fr-btn--tooltip:active,
  .fr-btn--briefcase:active,
  .fr-btn--team:active {
    background-color: rgba(0, 0, 0, 0.1);
  }
  .fr-btn--tertiary-no-outline:disabled,
  a.fr-btn--tertiary-no-outline:not([href]),
  a.fr-btn--close:not([href]),
  a.fr-btn--display:not([href]),
  a.fr-btn--fullscreen:not([href]),
  a.fr-btn--tooltip:not([href]),
  a.fr-btn--briefcase:not([href]),
  a.fr-btn--team:not([href]),
  .fr-btn--close:disabled,
  .fr-btn--display:disabled,
  .fr-btn--fullscreen:disabled,
  .fr-btn--tooltip:disabled,
  .fr-btn--briefcase:disabled,
  .fr-btn--team:disabled {
    background-color: transparent;
  }
  .fr-btn--tertiary-no-outline:disabled:hover,
  a.fr-btn--tertiary-no-outline:not([href]):hover,
  a.fr-btn--close:not([href]):hover,
  a.fr-btn--display:not([href]):hover,
  a.fr-btn--fullscreen:not([href]):hover,
  a.fr-btn--tooltip:not([href]):hover,
  a.fr-btn--briefcase:not([href]):hover,
  a.fr-btn--team:not([href]):hover,
  .fr-btn--close:disabled:hover,
  .fr-btn--display:disabled:hover,
  .fr-btn--fullscreen:disabled:hover,
  .fr-btn--tooltip:disabled:hover,
  .fr-btn--briefcase:disabled:hover,
  .fr-btn--team:disabled:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  .fr-btn--tertiary-no-outline:disabled:active,
  a.fr-btn--tertiary-no-outline:not([href]):active,
  a.fr-btn--close:not([href]):active,
  a.fr-btn--display:not([href]):active,
  a.fr-btn--fullscreen:not([href]):active,
  a.fr-btn--tooltip:not([href]):active,
  a.fr-btn--briefcase:not([href]):active,
  a.fr-btn--team:not([href]):active,
  .fr-btn--close:disabled:active,
  .fr-btn--display:disabled:active,
  .fr-btn--fullscreen:disabled:active,
  .fr-btn--tooltip:disabled:active,
  .fr-btn--briefcase:disabled:active,
  .fr-btn--team:disabled:active {
    background-color: rgba(0, 0, 0, 0.1);
  }
}
/*!
 * DSFR v1.11.0 | SPDX-License-Identifier: MIT | License-Filename: LICENSE.md | restricted use (see terms and conditions)
 */
/* ¯¯¯¯¯¯¯¯¯ *\
  TABLE
\* ˍˍˍˍˍˍˍˍˍ */
.fr-table {
  --table-offset: 1rem;
  --text-spacing: 0;
  --title-spacing: 0;
  position: relative;
  margin-bottom: 2.5rem;
  padding-top: var(--table-offset);
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table::before {
  content: &quot;&quot;;
  display: block;
  width: 100%;
  height: 0;
}

.fr-table:not(.fr-table--no-scroll) table {
  width: 100%;
}

.fr-table table {
  width: 100%;
  display: block;
  overflow: auto;
  border-spacing: 0;
}

.fr-table[data-fr-js-table=true] caption {
  position: absolute;
  top: 0;
}

.fr-table caption {
  position: initial;
  font-size: 1.375rem;
  line-height: 1.75rem;
  margin: var(--title-spacing);
  font-weight: 700;
  text-align: left;
  color: var(--text-title-grey);
}

.fr-table td,
.fr-table th {
  text-align: left;
  vertical-align: middle;
  display: table-cell;
  border: 0;
  padding: 0.75rem;
  font-size: 0.875rem;
  line-height: 1.5rem;
}

.fr-table th {
  font-weight: 700;
}

.fr-table thead {
  background-size: 100% 2px;
  background-position: bottom;
  background-repeat: no-repeat;
  background-image: linear-gradient(0deg, var(--border-plain-grey), var(--border-plain-grey));
  background-color: var(--background-contrast-grey);
  --idle: transparent;
  --hover: var(--background-contrast-grey-hover);
  --active: var(--background-contrast-grey-active);
  color: var(--text-title-grey);
}

.fr-table thead td,
.fr-table thead th {
  font-weight: 700;
  padding-bottom: 0.875rem;
}

/*
* Cache la caption
*/
.fr-table--no-caption {
  padding-top: 0;
}

.fr-table--no-caption caption {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap; /* added line */
  border: 0;
  display: block;
  height: 0;
}

/*
* Fixe le caption en bas du tableau
*/
.fr-table--caption-bottom {
  padding-top: 0;
  margin-bottom: 0;
  margin-top: 1rem;
}

.fr-table--caption-bottom table {
  margin-bottom: calc(var(--table-offset) + 2.75rem);
}

.fr-table--caption-bottom[data-fr-js-table=true] caption {
  position: absolute;
  top: 100%;
  right: 0;
  bottom: 0;
  left: 0;
  margin-top: 1rem;
}

.fr-table--caption-bottom caption {
  margin-top: 1rem;
  height: -moz-min-content;
  height: min-content;
  caption-side: bottom;
}

/*
* pas de scroll ni de shadow
*/
.fr-table--no-scroll {
  min-width: auto;
}

.fr-table--no-scroll table {
  overflow-x: hidden;
}

.fr-table--no-scroll caption {
  max-width: calc(100vw - 2rem);
}

/*
* Fixe la taille des colonnes du tableau
*/
.fr-table--layout-fixed table {
  display: table;
  table-layout: fixed;
}

/* Style bordered, ajoute des bordures entre chaque ligne */
.fr-table--bordered tbody tr {
  background-size: 100% 1px;
  background-position: bottom;
  background-repeat: no-repeat;
  background-image: linear-gradient(0deg, var(--border-default-grey), var(--border-default-grey));
  /* Style bordered, enleve le style even/odd  */
  /* Style bordered, enleve le style even/odd  */
}

/*
* Ombres ajoutées en Js si le contenu est plus grand que le conteneur
*/
.fr-table__shadow {
  /**
  * Modifier ombre à gauche
  **/
  /**
  * Modifier ombre à droite
  **/
  /**
  * Modifier combinaison ombre à gauche et ombre à droite
  **/
}

.fr-table__shadow::before {
  content: &quot;&quot;;
  display: block;
  position: absolute;
  top: var(--table-offset);
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 1;
  box-shadow: inset 0 0 0 0 #161616, inset 0 0 0 0 #161616;
  opacity: 0.32;
  pointer-events: none;
  transition: box-shadow 0.3s;
}

.fr-table__shadow--left::before {
  box-shadow: inset 2rem 0 1rem -2rem #161616, inset 0 0 0 0 #161616;
}

.fr-table__shadow--right::before {
  box-shadow: inset 0 0 0 0 #161616, inset -2rem 0 1rem -2rem #161616;
}

.fr-table__shadow--left.fr-table__shadow--right::before {
  content: &quot;&quot;;
  display: block;
  box-shadow: inset 2rem 0 1rem -2rem #161616, inset -2rem 0 1rem -2rem #161616;
}

/*
* Positionnement ombres sur le tableau sans caption
*/
.fr-table--no-caption .fr-table__shadow::before {
  content: &quot;&quot;;
  display: block;
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}

/*
* Positionnement ombres sur le tableau avec caption en bas
*/
.fr-table--caption-bottom .fr-table__shadow::before {
  content: &quot;&quot;;
  display: block;
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}

:root[data-fr-theme=dark] .fr-table__shadow::before {
  opacity: 1;
}

.fr-table tbody {
  background-color: var(--background-alt-grey);
  --idle: transparent;
  --hover: var(--background-alt-grey-hover);
  --active: var(--background-alt-grey-active);
}

.fr-table tbody tr:nth-child(even) {
  background-color: var(--background-contrast-grey);
  --idle: transparent;
  --hover: var(--background-contrast-grey-hover);
  --active: var(--background-contrast-grey-active);
}

.fr-table--green-tilleul-verveine {
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table--green-tilleul-verveine thead {
  background-image: linear-gradient(0deg, var(--border-plain-green-tilleul-verveine), var(--border-plain-green-tilleul-verveine));
  background-color: var(--background-contrast-green-tilleul-verveine);
  --idle: transparent;
  --hover: var(--background-contrast-green-tilleul-verveine-hover);
  --active: var(--background-contrast-green-tilleul-verveine-active);
}

.fr-table--green-tilleul-verveine tbody {
  background-color: var(--background-alt-green-tilleul-verveine);
  --idle: transparent;
  --hover: var(--background-alt-green-tilleul-verveine-hover);
  --active: var(--background-alt-green-tilleul-verveine-active);
}

.fr-table--green-tilleul-verveine tbody tr:nth-child(even) {
  background-color: var(--background-contrast-green-tilleul-verveine);
  --idle: transparent;
  --hover: var(--background-contrast-green-tilleul-verveine-hover);
  --active: var(--background-contrast-green-tilleul-verveine-active);
}

.fr-table--green-tilleul-verveine.fr-table--bordered tbody tr {
  background-image: linear-gradient(0deg, var(--border-default-green-tilleul-verveine), var(--border-default-green-tilleul-verveine));
}

.fr-table--green-bourgeon {
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table--green-bourgeon thead {
  background-image: linear-gradient(0deg, var(--border-plain-green-bourgeon), var(--border-plain-green-bourgeon));
  background-color: var(--background-contrast-green-bourgeon);
  --idle: transparent;
  --hover: var(--background-contrast-green-bourgeon-hover);
  --active: var(--background-contrast-green-bourgeon-active);
}

.fr-table--green-bourgeon tbody {
  background-color: var(--background-alt-green-bourgeon);
  --idle: transparent;
  --hover: var(--background-alt-green-bourgeon-hover);
  --active: var(--background-alt-green-bourgeon-active);
}

.fr-table--green-bourgeon tbody tr:nth-child(even) {
  background-color: var(--background-contrast-green-bourgeon);
  --idle: transparent;
  --hover: var(--background-contrast-green-bourgeon-hover);
  --active: var(--background-contrast-green-bourgeon-active);
}

.fr-table--green-bourgeon.fr-table--bordered tbody tr {
  background-image: linear-gradient(0deg, var(--border-default-green-bourgeon), var(--border-default-green-bourgeon));
}

.fr-table--green-emeraude {
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table--green-emeraude thead {
  background-image: linear-gradient(0deg, var(--border-plain-green-emeraude), var(--border-plain-green-emeraude));
  background-color: var(--background-contrast-green-emeraude);
  --idle: transparent;
  --hover: var(--background-contrast-green-emeraude-hover);
  --active: var(--background-contrast-green-emeraude-active);
}

.fr-table--green-emeraude tbody {
  background-color: var(--background-alt-green-emeraude);
  --idle: transparent;
  --hover: var(--background-alt-green-emeraude-hover);
  --active: var(--background-alt-green-emeraude-active);
}

.fr-table--green-emeraude tbody tr:nth-child(even) {
  background-color: var(--background-contrast-green-emeraude);
  --idle: transparent;
  --hover: var(--background-contrast-green-emeraude-hover);
  --active: var(--background-contrast-green-emeraude-active);
}

.fr-table--green-emeraude.fr-table--bordered tbody tr {
  background-image: linear-gradient(0deg, var(--border-default-green-emeraude), var(--border-default-green-emeraude));
}

.fr-table--green-menthe {
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table--green-menthe thead {
  background-image: linear-gradient(0deg, var(--border-plain-green-menthe), var(--border-plain-green-menthe));
  background-color: var(--background-contrast-green-menthe);
  --idle: transparent;
  --hover: var(--background-contrast-green-menthe-hover);
  --active: var(--background-contrast-green-menthe-active);
}

.fr-table--green-menthe tbody {
  background-color: var(--background-alt-green-menthe);
  --idle: transparent;
  --hover: var(--background-alt-green-menthe-hover);
  --active: var(--background-alt-green-menthe-active);
}

.fr-table--green-menthe tbody tr:nth-child(even) {
  background-color: var(--background-contrast-green-menthe);
  --idle: transparent;
  --hover: var(--background-contrast-green-menthe-hover);
  --active: var(--background-contrast-green-menthe-active);
}

.fr-table--green-menthe.fr-table--bordered tbody tr {
  background-image: linear-gradient(0deg, var(--border-default-green-menthe), var(--border-default-green-menthe));
}

.fr-table--green-archipel {
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table--green-archipel thead {
  background-image: linear-gradient(0deg, var(--border-plain-green-archipel), var(--border-plain-green-archipel));
  background-color: var(--background-contrast-green-archipel);
  --idle: transparent;
  --hover: var(--background-contrast-green-archipel-hover);
  --active: var(--background-contrast-green-archipel-active);
}

.fr-table--green-archipel tbody {
  background-color: var(--background-alt-green-archipel);
  --idle: transparent;
  --hover: var(--background-alt-green-archipel-hover);
  --active: var(--background-alt-green-archipel-active);
}

.fr-table--green-archipel tbody tr:nth-child(even) {
  background-color: var(--background-contrast-green-archipel);
  --idle: transparent;
  --hover: var(--background-contrast-green-archipel-hover);
  --active: var(--background-contrast-green-archipel-active);
}

.fr-table--green-archipel.fr-table--bordered tbody tr {
  background-image: linear-gradient(0deg, var(--border-default-green-archipel), var(--border-default-green-archipel));
}

.fr-table--blue-ecume {
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table--blue-ecume thead {
  background-image: linear-gradient(0deg, var(--border-plain-blue-ecume), var(--border-plain-blue-ecume));
  background-color: var(--background-contrast-blue-ecume);
  --idle: transparent;
  --hover: var(--background-contrast-blue-ecume-hover);
  --active: var(--background-contrast-blue-ecume-active);
}

.fr-table--blue-ecume tbody {
  background-color: var(--background-alt-blue-ecume);
  --idle: transparent;
  --hover: var(--background-alt-blue-ecume-hover);
  --active: var(--background-alt-blue-ecume-active);
}

.fr-table--blue-ecume tbody tr:nth-child(even) {
  background-color: var(--background-contrast-blue-ecume);
  --idle: transparent;
  --hover: var(--background-contrast-blue-ecume-hover);
  --active: var(--background-contrast-blue-ecume-active);
}

.fr-table--blue-ecume.fr-table--bordered tbody tr {
  background-image: linear-gradient(0deg, var(--border-default-blue-ecume), var(--border-default-blue-ecume));
}

.fr-table--blue-cumulus {
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table--blue-cumulus thead {
  background-image: linear-gradient(0deg, var(--border-plain-blue-cumulus), var(--border-plain-blue-cumulus));
  background-color: var(--background-contrast-blue-cumulus);
  --idle: transparent;
  --hover: var(--background-contrast-blue-cumulus-hover);
  --active: var(--background-contrast-blue-cumulus-active);
}

.fr-table--blue-cumulus tbody {
  background-color: var(--background-alt-blue-cumulus);
  --idle: transparent;
  --hover: var(--background-alt-blue-cumulus-hover);
  --active: var(--background-alt-blue-cumulus-active);
}

.fr-table--blue-cumulus tbody tr:nth-child(even) {
  background-color: var(--background-contrast-blue-cumulus);
  --idle: transparent;
  --hover: var(--background-contrast-blue-cumulus-hover);
  --active: var(--background-contrast-blue-cumulus-active);
}

.fr-table--blue-cumulus.fr-table--bordered tbody tr {
  background-image: linear-gradient(0deg, var(--border-default-blue-cumulus), var(--border-default-blue-cumulus));
}

.fr-table--purple-glycine {
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table--purple-glycine thead {
  background-image: linear-gradient(0deg, var(--border-plain-purple-glycine), var(--border-plain-purple-glycine));
  background-color: var(--background-contrast-purple-glycine);
  --idle: transparent;
  --hover: var(--background-contrast-purple-glycine-hover);
  --active: var(--background-contrast-purple-glycine-active);
}

.fr-table--purple-glycine tbody {
  background-color: var(--background-alt-purple-glycine);
  --idle: transparent;
  --hover: var(--background-alt-purple-glycine-hover);
  --active: var(--background-alt-purple-glycine-active);
}

.fr-table--purple-glycine tbody tr:nth-child(even) {
  background-color: var(--background-contrast-purple-glycine);
  --idle: transparent;
  --hover: var(--background-contrast-purple-glycine-hover);
  --active: var(--background-contrast-purple-glycine-active);
}

.fr-table--purple-glycine.fr-table--bordered tbody tr {
  background-image: linear-gradient(0deg, var(--border-default-purple-glycine), var(--border-default-purple-glycine));
}

.fr-table--pink-macaron {
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table--pink-macaron thead {
  background-image: linear-gradient(0deg, var(--border-plain-pink-macaron), var(--border-plain-pink-macaron));
  background-color: var(--background-contrast-pink-macaron);
  --idle: transparent;
  --hover: var(--background-contrast-pink-macaron-hover);
  --active: var(--background-contrast-pink-macaron-active);
}

.fr-table--pink-macaron tbody {
  background-color: var(--background-alt-pink-macaron);
  --idle: transparent;
  --hover: var(--background-alt-pink-macaron-hover);
  --active: var(--background-alt-pink-macaron-active);
}

.fr-table--pink-macaron tbody tr:nth-child(even) {
  background-color: var(--background-contrast-pink-macaron);
  --idle: transparent;
  --hover: var(--background-contrast-pink-macaron-hover);
  --active: var(--background-contrast-pink-macaron-active);
}

.fr-table--pink-macaron.fr-table--bordered tbody tr {
  background-image: linear-gradient(0deg, var(--border-default-pink-macaron), var(--border-default-pink-macaron));
}

.fr-table--pink-tuile {
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table--pink-tuile thead {
  background-image: linear-gradient(0deg, var(--border-plain-pink-tuile), var(--border-plain-pink-tuile));
  background-color: var(--background-contrast-pink-tuile);
  --idle: transparent;
  --hover: var(--background-contrast-pink-tuile-hover);
  --active: var(--background-contrast-pink-tuile-active);
}

.fr-table--pink-tuile tbody {
  background-color: var(--background-alt-pink-tuile);
  --idle: transparent;
  --hover: var(--background-alt-pink-tuile-hover);
  --active: var(--background-alt-pink-tuile-active);
}

.fr-table--pink-tuile tbody tr:nth-child(even) {
  background-color: var(--background-contrast-pink-tuile);
  --idle: transparent;
  --hover: var(--background-contrast-pink-tuile-hover);
  --active: var(--background-contrast-pink-tuile-active);
}

.fr-table--pink-tuile.fr-table--bordered tbody tr {
  background-image: linear-gradient(0deg, var(--border-default-pink-tuile), var(--border-default-pink-tuile));
}

.fr-table--yellow-tournesol {
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table--yellow-tournesol thead {
  background-image: linear-gradient(0deg, var(--border-plain-yellow-tournesol), var(--border-plain-yellow-tournesol));
  background-color: var(--background-contrast-yellow-tournesol);
  --idle: transparent;
  --hover: var(--background-contrast-yellow-tournesol-hover);
  --active: var(--background-contrast-yellow-tournesol-active);
}

.fr-table--yellow-tournesol tbody {
  background-color: var(--background-alt-yellow-tournesol);
  --idle: transparent;
  --hover: var(--background-alt-yellow-tournesol-hover);
  --active: var(--background-alt-yellow-tournesol-active);
}

.fr-table--yellow-tournesol tbody tr:nth-child(even) {
  background-color: var(--background-contrast-yellow-tournesol);
  --idle: transparent;
  --hover: var(--background-contrast-yellow-tournesol-hover);
  --active: var(--background-contrast-yellow-tournesol-active);
}

.fr-table--yellow-tournesol.fr-table--bordered tbody tr {
  background-image: linear-gradient(0deg, var(--border-default-yellow-tournesol), var(--border-default-yellow-tournesol));
}

.fr-table--yellow-moutarde {
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table--yellow-moutarde thead {
  background-image: linear-gradient(0deg, var(--border-plain-yellow-moutarde), var(--border-plain-yellow-moutarde));
  background-color: var(--background-contrast-yellow-moutarde);
  --idle: transparent;
  --hover: var(--background-contrast-yellow-moutarde-hover);
  --active: var(--background-contrast-yellow-moutarde-active);
}

.fr-table--yellow-moutarde tbody {
  background-color: var(--background-alt-yellow-moutarde);
  --idle: transparent;
  --hover: var(--background-alt-yellow-moutarde-hover);
  --active: var(--background-alt-yellow-moutarde-active);
}

.fr-table--yellow-moutarde tbody tr:nth-child(even) {
  background-color: var(--background-contrast-yellow-moutarde);
  --idle: transparent;
  --hover: var(--background-contrast-yellow-moutarde-hover);
  --active: var(--background-contrast-yellow-moutarde-active);
}

.fr-table--yellow-moutarde.fr-table--bordered tbody tr {
  background-image: linear-gradient(0deg, var(--border-default-yellow-moutarde), var(--border-default-yellow-moutarde));
}

.fr-table--orange-terre-battue {
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table--orange-terre-battue thead {
  background-image: linear-gradient(0deg, var(--border-plain-orange-terre-battue), var(--border-plain-orange-terre-battue));
  background-color: var(--background-contrast-orange-terre-battue);
  --idle: transparent;
  --hover: var(--background-contrast-orange-terre-battue-hover);
  --active: var(--background-contrast-orange-terre-battue-active);
}

.fr-table--orange-terre-battue tbody {
  background-color: var(--background-alt-orange-terre-battue);
  --idle: transparent;
  --hover: var(--background-alt-orange-terre-battue-hover);
  --active: var(--background-alt-orange-terre-battue-active);
}

.fr-table--orange-terre-battue tbody tr:nth-child(even) {
  background-color: var(--background-contrast-orange-terre-battue);
  --idle: transparent;
  --hover: var(--background-contrast-orange-terre-battue-hover);
  --active: var(--background-contrast-orange-terre-battue-active);
}

.fr-table--orange-terre-battue.fr-table--bordered tbody tr {
  background-image: linear-gradient(0deg, var(--border-default-orange-terre-battue), var(--border-default-orange-terre-battue));
}

.fr-table--brown-cafe-creme {
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table--brown-cafe-creme thead {
  background-image: linear-gradient(0deg, var(--border-plain-brown-cafe-creme), var(--border-plain-brown-cafe-creme));
  background-color: var(--background-contrast-brown-cafe-creme);
  --idle: transparent;
  --hover: var(--background-contrast-brown-cafe-creme-hover);
  --active: var(--background-contrast-brown-cafe-creme-active);
}

.fr-table--brown-cafe-creme tbody {
  background-color: var(--background-alt-brown-cafe-creme);
  --idle: transparent;
  --hover: var(--background-alt-brown-cafe-creme-hover);
  --active: var(--background-alt-brown-cafe-creme-active);
}

.fr-table--brown-cafe-creme tbody tr:nth-child(even) {
  background-color: var(--background-contrast-brown-cafe-creme);
  --idle: transparent;
  --hover: var(--background-contrast-brown-cafe-creme-hover);
  --active: var(--background-contrast-brown-cafe-creme-active);
}

.fr-table--brown-cafe-creme.fr-table--bordered tbody tr {
  background-image: linear-gradient(0deg, var(--border-default-brown-cafe-creme), var(--border-default-brown-cafe-creme));
}

.fr-table--brown-caramel {
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table--brown-caramel thead {
  background-image: linear-gradient(0deg, var(--border-plain-brown-caramel), var(--border-plain-brown-caramel));
  background-color: var(--background-contrast-brown-caramel);
  --idle: transparent;
  --hover: var(--background-contrast-brown-caramel-hover);
  --active: var(--background-contrast-brown-caramel-active);
}

.fr-table--brown-caramel tbody {
  background-color: var(--background-alt-brown-caramel);
  --idle: transparent;
  --hover: var(--background-alt-brown-caramel-hover);
  --active: var(--background-alt-brown-caramel-active);
}

.fr-table--brown-caramel tbody tr:nth-child(even) {
  background-color: var(--background-contrast-brown-caramel);
  --idle: transparent;
  --hover: var(--background-contrast-brown-caramel-hover);
  --active: var(--background-contrast-brown-caramel-active);
}

.fr-table--brown-caramel.fr-table--bordered tbody tr {
  background-image: linear-gradient(0deg, var(--border-default-brown-caramel), var(--border-default-brown-caramel));
}

.fr-table--brown-opera {
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table--brown-opera thead {
  background-image: linear-gradient(0deg, var(--border-plain-brown-opera), var(--border-plain-brown-opera));
  background-color: var(--background-contrast-brown-opera);
  --idle: transparent;
  --hover: var(--background-contrast-brown-opera-hover);
  --active: var(--background-contrast-brown-opera-active);
}

.fr-table--brown-opera tbody {
  background-color: var(--background-alt-brown-opera);
  --idle: transparent;
  --hover: var(--background-alt-brown-opera-hover);
  --active: var(--background-alt-brown-opera-active);
}

.fr-table--brown-opera tbody tr:nth-child(even) {
  background-color: var(--background-contrast-brown-opera);
  --idle: transparent;
  --hover: var(--background-contrast-brown-opera-hover);
  --active: var(--background-contrast-brown-opera-active);
}

.fr-table--brown-opera.fr-table--bordered tbody tr {
  background-image: linear-gradient(0deg, var(--border-default-brown-opera), var(--border-default-brown-opera));
}

.fr-table--beige-gris-galet {
  /* Style bordered, ajoute des bordures entre chaque ligne */
  /* Style bordered, ajoute des bordures entre chaque ligne */
}

.fr-table--beige-gris-galet thead {
  background-image: linear-gradient(0deg, var(--border-plain-beige-gris-galet), var(--border-plain-beige-gris-galet));
  background-color: var(--background-contrast-beige-gris-galet);
  --idle: transparent;
  --hover: var(--background-contrast-beige-gris-galet-hover);
  --active: var(--background-contrast-beige-gris-galet-active);
}

.fr-table--beige-gris-galet tbody {
  background-color: var(--background-alt-beige-gris-galet);
  --idle: transparent;
  --hover: var(--background-alt-beige-gris-galet-hover);
  --active: var(--background-alt-beige-gris-galet-active);
}

.fr-table--beige-gris-galet tbody tr:nth-child(even) {
  background-color: var(--background-contrast-beige-gris-galet);
  --idle: transparent;
  --hover: var(--background-contrast-beige-gris-galet-hover);
  --active: var(--background-contrast-beige-gris-galet-active);
}

.fr-table--beige-gris-galet.fr-table--bordered tbody tr {
  background-image: linear-gradient(0deg, var(--border-default-beige-gris-galet), var(--border-default-beige-gris-galet));
}

.fr-table--bordered tbody tr:nth-child(even) {
  background-color: transparent;
  --hover: inherit;
  --active: inherit;
}

@media (min-width: 36em) {
  /*! media sm */
  /*! media sm */
}
@media (min-width: 48em) {
  /*! media md */
  .fr-table caption {
    font-size: 1.5rem;
    line-height: 2rem;
  }
  .fr-table td,
  .fr-table th {
    padding: 1rem;
  }
  .fr-table thead td,
  .fr-table thead th {
    padding-bottom: 1.125rem;
  }
  /*! media md */
}
@media (min-width: 62em) {
  /*! media lg */
  /*! media lg */
}
@media (min-width: 78em) {
  /*! media xl */
  /*! media xl */
}
@media all and (-ms-high-contrast: none), (-ms-high-contrast: active) {
  /**
  * Correctif placement caption
  */
  .fr-table[data-fr-js-table=true] caption {
    position: relative;
  }
  .fr-table caption {
    color: #161616;
  }
  .fr-table thead {
    background-image: linear-gradient(0deg, #3a3a3a, #3a3a3a);
    background-color: #eee;
    color: #161616;
  }
  .fr-table tbody {
    background-color: #f6f6f6;
  }
  .fr-table tbody tr:nth-child(even) {
    background-color: #eee;
  }
  .fr-table--green-tilleul-verveine thead {
    background-image: linear-gradient(0deg, #66673d, #66673d);
    background-color: #fceeac;
  }
  .fr-table--green-tilleul-verveine tbody {
    background-color: #fef7da;
  }
  .fr-table--green-tilleul-verveine tbody tr:nth-child(even) {
    background-color: #fceeac;
  }
  .fr-table--green-tilleul-verveine.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #b7a73f, #b7a73f);
  }
  .fr-table--green-bourgeon thead {
    background-image: linear-gradient(0deg, #447049, #447049);
    background-color: #c9fcac;
  }
  .fr-table--green-bourgeon tbody {
    background-color: #e6feda;
  }
  .fr-table--green-bourgeon tbody tr:nth-child(even) {
    background-color: #c9fcac;
  }
  .fr-table--green-bourgeon.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #68a532, #68a532);
  }
  .fr-table--green-emeraude thead {
    background-image: linear-gradient(0deg, #297254, #297254);
    background-color: #c3fad5;
  }
  .fr-table--green-emeraude tbody {
    background-color: #e3fdeb;
  }
  .fr-table--green-emeraude tbody tr:nth-child(even) {
    background-color: #c3fad5;
  }
  .fr-table--green-emeraude.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #00a95f, #00a95f);
  }
  .fr-table--green-menthe thead {
    background-image: linear-gradient(0deg, #37635f, #37635f);
    background-color: #bafaee;
  }
  .fr-table--green-menthe tbody {
    background-color: #dffdf7;
  }
  .fr-table--green-menthe tbody tr:nth-child(even) {
    background-color: #bafaee;
  }
  .fr-table--green-menthe.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #009081, #009081);
  }
  .fr-table--green-archipel thead {
    background-image: linear-gradient(0deg, #006a6f, #006a6f);
    background-color: #c7f6fc;
  }
  .fr-table--green-archipel tbody {
    background-color: #e5fbfd;
  }
  .fr-table--green-archipel tbody tr:nth-child(even) {
    background-color: #c7f6fc;
  }
  .fr-table--green-archipel.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #009099, #009099);
  }
  .fr-table--blue-ecume thead {
    background-image: linear-gradient(0deg, #2f4077, #2f4077);
    background-color: #e9edfe;
  }
  .fr-table--blue-ecume tbody {
    background-color: #f4f6fe;
  }
  .fr-table--blue-ecume tbody tr:nth-child(even) {
    background-color: #e9edfe;
  }
  .fr-table--blue-ecume.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #465f9d, #465f9d);
  }
  .fr-table--blue-cumulus thead {
    background-image: linear-gradient(0deg, #3558a2, #3558a2);
    background-color: #e6eefe;
  }
  .fr-table--blue-cumulus tbody {
    background-color: #f3f6fe;
  }
  .fr-table--blue-cumulus tbody tr:nth-child(even) {
    background-color: #e6eefe;
  }
  .fr-table--blue-cumulus.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #417dc4, #417dc4);
  }
  .fr-table--purple-glycine thead {
    background-image: linear-gradient(0deg, #6e445a, #6e445a);
    background-color: #fee7fc;
  }
  .fr-table--purple-glycine tbody {
    background-color: #fef3fd;
  }
  .fr-table--purple-glycine tbody tr:nth-child(even) {
    background-color: #fee7fc;
  }
  .fr-table--purple-glycine.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #a558a0, #a558a0);
  }
  .fr-table--pink-macaron thead {
    background-image: linear-gradient(0deg, #8d533e, #8d533e);
    background-color: #fee9e6;
  }
  .fr-table--pink-macaron tbody {
    background-color: #fef4f2;
  }
  .fr-table--pink-macaron tbody tr:nth-child(even) {
    background-color: #fee9e6;
  }
  .fr-table--pink-macaron.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #e18b76, #e18b76);
  }
  .fr-table--pink-tuile thead {
    background-image: linear-gradient(0deg, #a94645, #a94645);
    background-color: #fee9e7;
  }
  .fr-table--pink-tuile tbody {
    background-color: #fef4f3;
  }
  .fr-table--pink-tuile tbody tr:nth-child(even) {
    background-color: #fee9e7;
  }
  .fr-table--pink-tuile.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #ce614a, #ce614a);
  }
  .fr-table--yellow-tournesol thead {
    background-image: linear-gradient(0deg, #716043, #716043);
    background-color: #feecc2;
  }
  .fr-table--yellow-tournesol tbody {
    background-color: #fef6e3;
  }
  .fr-table--yellow-tournesol tbody tr:nth-child(even) {
    background-color: #feecc2;
  }
  .fr-table--yellow-tournesol.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #c8aa39, #c8aa39);
  }
  .fr-table--yellow-moutarde thead {
    background-image: linear-gradient(0deg, #695240, #695240);
    background-color: #feebd0;
  }
  .fr-table--yellow-moutarde tbody {
    background-color: #fef5e8;
  }
  .fr-table--yellow-moutarde tbody tr:nth-child(even) {
    background-color: #feebd0;
  }
  .fr-table--yellow-moutarde.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #c3992a, #c3992a);
  }
  .fr-table--orange-terre-battue thead {
    background-image: linear-gradient(0deg, #755348, #755348);
    background-color: #fee9e5;
  }
  .fr-table--orange-terre-battue tbody {
    background-color: #fef4f2;
  }
  .fr-table--orange-terre-battue tbody tr:nth-child(even) {
    background-color: #fee9e5;
  }
  .fr-table--orange-terre-battue.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #e4794a, #e4794a);
  }
  .fr-table--brown-cafe-creme thead {
    background-image: linear-gradient(0deg, #685c48, #685c48);
    background-color: #f7ecdb;
  }
  .fr-table--brown-cafe-creme tbody {
    background-color: #fbf6ed;
  }
  .fr-table--brown-cafe-creme tbody tr:nth-child(even) {
    background-color: #f7ecdb;
  }
  .fr-table--brown-cafe-creme.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #d1b781, #d1b781);
  }
  .fr-table--brown-caramel thead {
    background-image: linear-gradient(0deg, #845d48, #845d48);
    background-color: #f7ebe5;
  }
  .fr-table--brown-caramel tbody {
    background-color: #fbf5f2;
  }
  .fr-table--brown-caramel tbody tr:nth-child(even) {
    background-color: #f7ebe5;
  }
  .fr-table--brown-caramel.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #c08c65, #c08c65);
  }
  .fr-table--brown-opera thead {
    background-image: linear-gradient(0deg, #745b47, #745b47);
    background-color: #f7ece4;
  }
  .fr-table--brown-opera tbody {
    background-color: #fbf5f2;
  }
  .fr-table--brown-opera tbody tr:nth-child(even) {
    background-color: #f7ece4;
  }
  .fr-table--brown-opera.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #bd987a, #bd987a);
  }
  .fr-table--beige-gris-galet thead {
    background-image: linear-gradient(0deg, #6a6156, #6a6156);
    background-color: #f3ede5;
  }
  .fr-table--beige-gris-galet tbody {
    background-color: #f9f6f2;
  }
  .fr-table--beige-gris-galet tbody tr:nth-child(even) {
    background-color: #f3ede5;
  }
  .fr-table--beige-gris-galet.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #aea397, #aea397);
  }
  .fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #ddd, #ddd);
  }
  .fr-table--bordered tbody tr:nth-child(even) {
    background-color: transparent;
  }
  .fr-table--bordered tbody tr:nth-child(even):hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  .fr-table--bordered tbody tr:nth-child(even):active {
    background-color: rgba(0, 0, 0, 0.1);
  }
}
@media print {
  .fr-table {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table caption {
    color: #161616;
  }
  .fr-table thead {
    background-image: linear-gradient(0deg, #3a3a3a, #3a3a3a);
    background-color: #eee;
    color: #161616;
  }
  .fr-table tbody {
    background-color: #f6f6f6;
  }
  .fr-table tbody tr:nth-child(even) {
    background-color: #eee;
  }
  .fr-table--green-tilleul-verveine {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table--green-tilleul-verveine thead {
    background-image: linear-gradient(0deg, #66673d, #66673d);
    background-color: #fceeac;
  }
  .fr-table--green-tilleul-verveine tbody {
    background-color: #fef7da;
  }
  .fr-table--green-tilleul-verveine tbody tr:nth-child(even) {
    background-color: #fceeac;
  }
  .fr-table--green-tilleul-verveine.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #b7a73f, #b7a73f);
  }
  .fr-table--green-bourgeon {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table--green-bourgeon thead {
    background-image: linear-gradient(0deg, #447049, #447049);
    background-color: #c9fcac;
  }
  .fr-table--green-bourgeon tbody {
    background-color: #e6feda;
  }
  .fr-table--green-bourgeon tbody tr:nth-child(even) {
    background-color: #c9fcac;
  }
  .fr-table--green-bourgeon.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #68a532, #68a532);
  }
  .fr-table--green-emeraude {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table--green-emeraude thead {
    background-image: linear-gradient(0deg, #297254, #297254);
    background-color: #c3fad5;
  }
  .fr-table--green-emeraude tbody {
    background-color: #e3fdeb;
  }
  .fr-table--green-emeraude tbody tr:nth-child(even) {
    background-color: #c3fad5;
  }
  .fr-table--green-emeraude.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #00a95f, #00a95f);
  }
  .fr-table--green-menthe {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table--green-menthe thead {
    background-image: linear-gradient(0deg, #37635f, #37635f);
    background-color: #bafaee;
  }
  .fr-table--green-menthe tbody {
    background-color: #dffdf7;
  }
  .fr-table--green-menthe tbody tr:nth-child(even) {
    background-color: #bafaee;
  }
  .fr-table--green-menthe.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #009081, #009081);
  }
  .fr-table--green-archipel {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table--green-archipel thead {
    background-image: linear-gradient(0deg, #006a6f, #006a6f);
    background-color: #c7f6fc;
  }
  .fr-table--green-archipel tbody {
    background-color: #e5fbfd;
  }
  .fr-table--green-archipel tbody tr:nth-child(even) {
    background-color: #c7f6fc;
  }
  .fr-table--green-archipel.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #009099, #009099);
  }
  .fr-table--blue-ecume {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table--blue-ecume thead {
    background-image: linear-gradient(0deg, #2f4077, #2f4077);
    background-color: #e9edfe;
  }
  .fr-table--blue-ecume tbody {
    background-color: #f4f6fe;
  }
  .fr-table--blue-ecume tbody tr:nth-child(even) {
    background-color: #e9edfe;
  }
  .fr-table--blue-ecume.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #465f9d, #465f9d);
  }
  .fr-table--blue-cumulus {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table--blue-cumulus thead {
    background-image: linear-gradient(0deg, #3558a2, #3558a2);
    background-color: #e6eefe;
  }
  .fr-table--blue-cumulus tbody {
    background-color: #f3f6fe;
  }
  .fr-table--blue-cumulus tbody tr:nth-child(even) {
    background-color: #e6eefe;
  }
  .fr-table--blue-cumulus.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #417dc4, #417dc4);
  }
  .fr-table--purple-glycine {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table--purple-glycine thead {
    background-image: linear-gradient(0deg, #6e445a, #6e445a);
    background-color: #fee7fc;
  }
  .fr-table--purple-glycine tbody {
    background-color: #fef3fd;
  }
  .fr-table--purple-glycine tbody tr:nth-child(even) {
    background-color: #fee7fc;
  }
  .fr-table--purple-glycine.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #a558a0, #a558a0);
  }
  .fr-table--pink-macaron {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table--pink-macaron thead {
    background-image: linear-gradient(0deg, #8d533e, #8d533e);
    background-color: #fee9e6;
  }
  .fr-table--pink-macaron tbody {
    background-color: #fef4f2;
  }
  .fr-table--pink-macaron tbody tr:nth-child(even) {
    background-color: #fee9e6;
  }
  .fr-table--pink-macaron.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #e18b76, #e18b76);
  }
  .fr-table--pink-tuile {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table--pink-tuile thead {
    background-image: linear-gradient(0deg, #a94645, #a94645);
    background-color: #fee9e7;
  }
  .fr-table--pink-tuile tbody {
    background-color: #fef4f3;
  }
  .fr-table--pink-tuile tbody tr:nth-child(even) {
    background-color: #fee9e7;
  }
  .fr-table--pink-tuile.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #ce614a, #ce614a);
  }
  .fr-table--yellow-tournesol {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table--yellow-tournesol thead {
    background-image: linear-gradient(0deg, #716043, #716043);
    background-color: #feecc2;
  }
  .fr-table--yellow-tournesol tbody {
    background-color: #fef6e3;
  }
  .fr-table--yellow-tournesol tbody tr:nth-child(even) {
    background-color: #feecc2;
  }
  .fr-table--yellow-tournesol.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #c8aa39, #c8aa39);
  }
  .fr-table--yellow-moutarde {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table--yellow-moutarde thead {
    background-image: linear-gradient(0deg, #695240, #695240);
    background-color: #feebd0;
  }
  .fr-table--yellow-moutarde tbody {
    background-color: #fef5e8;
  }
  .fr-table--yellow-moutarde tbody tr:nth-child(even) {
    background-color: #feebd0;
  }
  .fr-table--yellow-moutarde.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #c3992a, #c3992a);
  }
  .fr-table--orange-terre-battue {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table--orange-terre-battue thead {
    background-image: linear-gradient(0deg, #755348, #755348);
    background-color: #fee9e5;
  }
  .fr-table--orange-terre-battue tbody {
    background-color: #fef4f2;
  }
  .fr-table--orange-terre-battue tbody tr:nth-child(even) {
    background-color: #fee9e5;
  }
  .fr-table--orange-terre-battue.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #e4794a, #e4794a);
  }
  .fr-table--brown-cafe-creme {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table--brown-cafe-creme thead {
    background-image: linear-gradient(0deg, #685c48, #685c48);
    background-color: #f7ecdb;
  }
  .fr-table--brown-cafe-creme tbody {
    background-color: #fbf6ed;
  }
  .fr-table--brown-cafe-creme tbody tr:nth-child(even) {
    background-color: #f7ecdb;
  }
  .fr-table--brown-cafe-creme.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #d1b781, #d1b781);
  }
  .fr-table--brown-caramel {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table--brown-caramel thead {
    background-image: linear-gradient(0deg, #845d48, #845d48);
    background-color: #f7ebe5;
  }
  .fr-table--brown-caramel tbody {
    background-color: #fbf5f2;
  }
  .fr-table--brown-caramel tbody tr:nth-child(even) {
    background-color: #f7ebe5;
  }
  .fr-table--brown-caramel.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #c08c65, #c08c65);
  }
  .fr-table--brown-opera {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table--brown-opera thead {
    background-image: linear-gradient(0deg, #745b47, #745b47);
    background-color: #f7ece4;
  }
  .fr-table--brown-opera tbody {
    background-color: #fbf5f2;
  }
  .fr-table--brown-opera tbody tr:nth-child(even) {
    background-color: #f7ece4;
  }
  .fr-table--brown-opera.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #bd987a, #bd987a);
  }
  .fr-table--beige-gris-galet {
    /* Style bordered, ajoute des bordures entre chaque ligne */
  }
  .fr-table--beige-gris-galet thead {
    background-image: linear-gradient(0deg, #6a6156, #6a6156);
    background-color: #f3ede5;
  }
  .fr-table--beige-gris-galet tbody {
    background-color: #f9f6f2;
  }
  .fr-table--beige-gris-galet tbody tr:nth-child(even) {
    background-color: #f3ede5;
  }
  .fr-table--beige-gris-galet.fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #aea397, #aea397);
  }
  .fr-table--bordered tbody tr {
    background-image: linear-gradient(0deg, #ddd, #ddd);
    /* Style bordered, enleve le style even/odd  */
  }
  .fr-table td,
  .fr-table th {
    font-size: 1rem;
    line-height: 1.5rem;
  }
}
@media print and (-ms-high-contrast: none), print and (-ms-high-contrast: active) {
  .fr-table--bordered tbody tr:nth-child(even) {
    background-color: transparent;
  }
  .fr-table--bordered tbody tr:nth-child(even):hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  .fr-table--bordered tbody tr:nth-child(even):active {
    background-color: rgba(0, 0, 0, 0.1);
  }
}
/* DSRC config */
.home &gt; * + * {
  margin-block-start: 2em;
}

.home h2 {
  text-align: center;
}

/* DSRC config */
/* Global config */
.dsrc-btn {
  background-color: aqua;
}

/* External libraries overrides */
.rendered_html ul.unstyled {
  list-style: none;
  padding-left: 0;
}
    </style>


<table class="fr-table">
    <tr>
        <th>Projet</th>
        <th>Ville</th>
        <th>Gigs</th>
    </tr>

    <tr>
        <td>🔒 Test Location Permissions</td>
        <td>22 janvier 2024 11:57</td>
        <td>12 rue petit</td>
    </tr>

    <tr>
        <td>🌐 Test Location</td>
        <td>16 janvier 2024 14:12</td>
        <td>29 rue de Nantes</td>
    </tr>

    <tr>
        <td>🧪 Test Géoloc</td>
        <td>16 janvier 2024 12:45</td>
        <td>29 rue de Nantes , 79700 MAULEON</td>
    </tr>

    <tr>
        <td>🧪 Test redirect</td>
        <td>29 décembre 2023 15:12</td>
        <td>1 rue du port</td>
    </tr>

    <tr>
        <td>🌐 Test Location</td>
        <td>29 décembre 2023 11:38</td>
        <td>1 rue du port</td>
    </tr>

</table>
<ul class="fr-btns-group fr-btns-group--inline-sm unstyled">
    <li>
        <button class="fr-btn">Bouton</button>
    </li>
    <li>
        <button class="fr-btn fr-btn--secondary">Bouton Secondaire</button>
    </li>
    <li>
        <button class="fr-btn fr-btn--tertiary">Bouton Tertiaire</button>
    </li>
</ul>





```python

```
