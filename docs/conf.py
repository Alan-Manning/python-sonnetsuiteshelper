import os

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.ifconfig",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
]
source_suffix = ".rst"
master_doc = "index"
project = "sonnetsuiteshelper"
year = "2023"
author = "Alan Manning"
copyright = f"{year}, {author}"
version = release = "0.4.5"

pygments_style = "trac"
templates_path = ["."]
extlinks = {
    "issue": ("https://github.com/Alan-Manning/python-sonnetsuiteshelper/issues/%s", "#"),
    "pr": ("https://github.com/Alan-Manning/python-sonnetsuiteshelper/pull/%s", "PR #"),
}
# on_rtd is whether we are on readthedocs.org
on_rtd = os.environ.get("READTHEDOCS", None) == "True"

# if not on_rtd:  # only set the theme if we are building docs locally
html_theme = "sphinx_rtd_theme"

html_use_smartypants = True
html_last_updated_fmt = "%b %d, %Y"
html_split_index = False
html_sidebars = {
    "**": ["searchbox.html", "globaltoc.html", "sourcelink.html"],
}
html_short_title = f"{project}-{version}"

autodoc_default_options = {"members": None, "undoc-members": None, "private-members": None, "show-inheritance": None}

napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_use_ivar = True
napoleon_use_param = False
napoleon_use_rtype = False
napoleon_preprocess_types = True
# napoleon_type_aliases = None
napoleon_custom_sections = [("KwArgs", "Keyword Arguments")]

# old
# napoleon_numpy_docstring = True
# # napoleon_include_init_with_doc = True
# napoleon_use_ivar = True
# napoleon_use_param = False
# napoleon_use_rtype = True
# # napoleon_preprocess_types = False
# # napoleon_type_aliases = True
# napoleon_custom_sections = [("KwArgs", "Keyword Arguments")]
