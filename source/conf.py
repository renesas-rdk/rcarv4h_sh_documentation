# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
from typing import Any

try:
    from sphinx_polyversion.api import load as polyversion_load
except ImportError:
    polyversion_load = None

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'R-Car V4H Sparrow Hawk User Manual'
copyright = '2026, Renesas Electronics Corporation'
author = 'Renesas Electronics Corporation'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['myst_parser', 'sphinxcontrib.spelling', 'sphinx_copybutton', 'sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = []

# -- sphinx-polyversion context ---------------------------------------------
if polyversion_load is not None:
    try:
        polyversion_load(globals())
    except Exception:
        # Keep standard Sphinx builds working outside sphinx-polyversion.
        pass

html_context: dict[str, Any] = globals().get('html_context', {})
poly_current = html_context.get('current')
poly_release = getattr(poly_current, 'name', None)
release = poly_release or os.getenv('READTHEDOCS_VERSION', os.getenv('DOCS_VERSION', '1.0'))
version = release.lstrip('v')

# Kernel of the R-Car V4H SH image. Change KERNEL_VERSION here when the kernel is
# updated and every prose and table occurrence follows. Substitutions are not
# expanded inside code blocks, so the few occurrences in shell examples still have
# to be edited by hand.
KERNEL_VERSION = '6.18.39'
KERNEL_LOCALVERSION = '-arm64-renesas'
KERNEL_RELEASE = KERNEL_VERSION + KERNEL_LOCALVERSION

rst_prolog = f"""
.. |kernel_version| replace:: {KERNEL_VERSION}
.. |kernel_release| replace:: ``{KERNEL_RELEASE}``
.. |modules_path| replace:: ``/usr/lib/modules/{KERNEL_RELEASE}/``
.. |modules_build_path| replace:: ``rcar-utils/workspace/kernel-modules/usr/lib/modules/{KERNEL_RELEASE}/``
"""


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    # Sub-pages of a section page live one level deeper than the default 4,
    # so the sidebar needs an extra level to keep showing them.
    'navigation_depth': 5,
}
html_static_path = ['_static']
html_copy_source = False

# Relative to html_static_path
html_css_files = ['custom.css']
html_js_files = ['version-switcher.js']

html_favicon = '../renesas_favicon.png'

# -- Options for LaTeX output --------------------------------------------------
latex_engine = 'lualatex'

latex_elements = {
    'figure_align': 'H',  # Force all figures to stay in place (no floating)
    'passoptionstopackages': r'''
\PassOptionsToPackage{svgnames}{xcolor}
''',
    'fontpkg': r'''
\usepackage{fontspec}
\setsansfont{Carlito}
\setromanfont{Caladea}
\setmonofont{DejaVu Sans Mono}
\renewcommand{\familydefault}{\sfdefault}
''',
    'preamble': r'''
\usepackage[titles]{tocloft}
\cftsetpnumwidth {1.25cm}\cftsetrmarg{1.5cm}
\setlength{\cftchapnumwidth}{0.75cm}
\setlength{\cftsecindent}{\cftchapnumwidth}
\setlength{\cftsecnumwidth}{1.25cm}
''',
    "sphinxsetup": r"""
        verbatimwrapslines=true,     % keep wrapping long lines
        verbatimcontinued=,          % hide the wrap marker
        verbatimvisiblespace=,       % also hide the little visible-space glyph before breaks
    """,
'fncychap': r'\usepackage[Bjornstrup]{fncychap}',
'printindex': r'\footnotesize\raggedright\printindex',
}

latex_documents = [
    ('index',
     'R-Car_V4H_Sparrow_Hawk_User_Manual.tex',
     r'R-Car V4H Sparrow Hawk\\User Manual',
     'Renesas Electronics Corporation',
     'manual'),
]

# Spell checker configuration
spelling_lang = 'en_US'
spelling_word_list_filename = '../spelling_wordlist.txt'
# Do not accept words just because they are importable Python modules on the
# build machine (e.g. "netplan", "cairo" on Ubuntu hosts); keep results
# identical between host and container builds.
spelling_ignore_importable_modules = False

# Copybutton configuration (keep comment lines, remove $/# prompts)
copybutton_prompt_text = r'^(?:[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+:[^$]*\$ |\$ )'
copybutton_prompt_is_regexp = True
copybutton_only_copy_prompt_lines = False
copybutton_remove_prompts = True
