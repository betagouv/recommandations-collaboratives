from IPython.display import HTML

# Load CSS files as raw text using python
"""
Read a CSS or JS file and load it into Jupyter.
Make sure you trust the code you are loading.

Arg: the file path to the file, relative to the project's static assets folder
Returns: IPython.core.display.HTML object: contains JS/CSS in `data` property
"""


def load_asset(rel_file_path):
    assets_folder = "static/assets/"
    assets_file_path = f"{assets_folder}{rel_file_path}"
    asset_content = open(assets_file_path, "r").read()
    asset = "%s" % asset_content
    return HTML(asset)


# eof
