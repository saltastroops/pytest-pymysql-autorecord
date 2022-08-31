import os
import sys
sys.path.insert(0, os.path.abspath("../src"))

project = 'pytest-pymysql-snapshot-mock'
copyright = '2022, Southern African Large Telescope (SALT)'
author = 'Southern African Large Telescope (SALT)'
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_nb"
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
html_static_path = ['_static']
default_role = 'py:obj'
myst_enable_extensions = [
    "colon_fence"
]
myst_url_schemes = ("http", "https")
html_theme = "sphinx_book_theme"
html_sidebars = {
    "**": ["sbt-sidebar-nav.html"]
}
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/reference/', None),
    'matplotlib': ('https://matplotlib.org/', None),
    'astropy': ('https://docs.astropy.org/en/stable/', None),
    "pytest": ('https://docs.pytest.org/en/stable/', None)
}
