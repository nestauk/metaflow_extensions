"""Metaflow configuration over-rides.

Use `metaflow.from_conf` to set values with the following prioritisation order:
1) System environment variable
2) Your Metaflow profile (JSON config)
3) The value passed to `from_conf`
"""
from metaflow.metaflow_config import from_conf

# Path to the client cache
CLIENT_CACHE_PATH = from_conf("METAFLOW_CLIENT_CACHE_PATH", "/tmp/metaflow_client")

# Maximum size (in bytes) of the cache
CLIENT_CACHE_MAX_SIZE = from_conf("METAFLOW_CLIENT_CACHE_MAX_SIZE", "10000")

# Defines root of a project for ProjectEnvironment
_project_files = ["setup.py", "pyproject.toml"]
PROJECT_FILES = from_conf("METAFLOW_PROJECT_FILES", _project_files)
