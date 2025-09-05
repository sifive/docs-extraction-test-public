# -- Project information -----------------------------------------------------
project = 'Github Doc extraction to Confluence'
copyright = '2025, Venu'
author = 'Venu'
release = 'V1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinxcontrib.confluencebuilder"
]

templates_path = ['_templates']
exclude_patterns = []
language = 'en'

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'
html_static_path = ['_static']

# -- Confluence configuration ------------------------------------------------
confluence_publish = True
confluence_space_key = "GDE"
confluence_parent_page = "Github Docs Extraction"
confluence_server_url = "https://sifive-sandbox-851.atlassian.net/wiki/"

# Authentication should be passed securely via environment variables in CI
# Example (in GitHub Actions):
# confluence_server_user = os.getenv("CONFLUENCE_SERVER_USER")
# confluence_server_pass = os.getenv("CONFLUENCE_SERVER_PASS")

