# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(
    0,
    os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        ".."
    ))
)


# -- Project information -----------------------------------------------------
with open("../VERSION") as f1:
    version = release = f1.read().strip()
project = 'dposlib'
copyright = '2016-2019, Toons'
author = 'Toons'

# The master toctree document.
master_doc = 'index'
rst_epilog = u"""
.. |sparkles| replace:: \u2728
.. |exchange| replace:: \U0001f4b1
"""

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    'sphinxcontrib.napoleon',
    'recommonmark'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = ['.rst', '.md']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, maps document names to template names.
html_sidebars = {
    "**": [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
        'support.html'
    ]
}

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "logo": "logo.png",
    "show_powered_by": False,
    "github_user": "Moustikitos",
    "github_repo": "dpos",
    "github_banner": False,
    "github_button": False,
    "travis_button": True,
    "show_related": False,
    "note_bg": "#FFF59C",
    "fixed_sidebar": True
}
