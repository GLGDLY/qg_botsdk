# -*- coding: utf-8 -*-
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


project = "qg_botsdk"
copyright = "2022, GLGDLY"
author = "GLGDLY"
version = "latest"
release = "latest"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autosectionlabel", "myst_parser"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
myst_footnote_transition = False

language = "zh_CN"
show_authors = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_title = "qg_botsdk 帮助文档"
html_logo = "_static/robot.png"
html_favicon = "_static/favicon.ico"
html_show_copyright = True
html_show_sphinx = False
html_theme_options = {
    "source_repository": "https://github.com/GLGDLY/qg_botsdk/",
    "source_branch": "master",
    "source_directory": "docs/",
}
