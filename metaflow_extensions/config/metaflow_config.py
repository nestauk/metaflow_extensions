"""Metaflow configuration over-rides.

Use `metaflow.from_conf` to set values with the following prioritisation order:
1) System environment variable
2) Your Metaflow profile (JSON config)
3) The value passed to `from_conf`
"""
from typing import Dict

from metaflow.metaflow_config import from_conf

# Override default metaflow environment
DEFAULT_ENVIRONMENT = from_conf("METAFLOW_DEFAULT_ENVIRONMENT", "project")

# Override default package suffixes
_suffix_list = ",".join(
    [
        ".py",  # Source files
        ".yaml",  # Config files
        ".md",  # E.g. when setup.py reads README.md
        ".txt",  # E.g. requirements.txt
    ]
)
DEFAULT_PACKAGE_SUFFIXES = from_conf("METAFLOW_DEFAULT_PACKAGE_SUFFIXES", _suffix_list)

# Path to the client cache
CLIENT_CACHE_PATH = from_conf("METAFLOW_CLIENT_CACHE_PATH", "/tmp/metaflow_client")

# Maximum size (in bytes) of the cache
CLIENT_CACHE_MAX_SIZE = from_conf("METAFLOW_CLIENT_CACHE_MAX_SIZE", "10000")


# XXX - Can remove if https://github.com/Netflix/metaflow/issues/399 resolved
def get_pinned_conda_libs(python_version: str) -> Dict[str, str]:
    """Libraries that metaflow depends on and needs in a conda environment."""
    if python_version.startswith("3.5"):
        return {
            "click": "7.1.2",
            "requests": "2.24.0",
            "boto3": "1.9.88",
            "coverage": "4.5.1",
        }
    else:
        return {
            "click": ">=7.1.2",
            "requests": ">=2.24.0",
            "boto3": ">=1.14.47",
            "coverage": ">=4.5.4",
        }


# Defines root of a project for ProjectEnvironment
_project_files = ["setup.py", "pyproject.toml"]
PROJECT_FILES = from_conf("METAFLOW_PROJECT_FILES", _project_files)
