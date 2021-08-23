import os

from metaflow.metaflow_config import METAFLOW_CONFIG


def from_conf(name, default=None):
    """Get value of key `name` from configuration sources, or `default`.

    Prioritisation order:
    1) Env variable
    2) metaflow config JSON
    3) `default`
    """
    return os.environ.get(name, METAFLOW_CONFIG.get(name, default))


# Override default metaflow environment
DEFAULT_ENVIRONMENT = from_conf("METAFLOW_DEFAULT_ENVIRONMENT", "localproject")

# Override default package suffixes
DEFAULT_PACKAGE_SUFFIXES = from_conf(
    "METAFLOW_DEFAULT_PACKAGE_SUFFIXES",
    ",".join(
        [
            ".py",  # Source files
            ".yaml",  # Config
            ".md",  # setup.py reads README.md
            ".txt",  # E.g. requirements.txt
            # "PKG-INFO",
            ".env.shared",  # Gets cookiecutter metadata
            ".run_id",  # For cookiecutter getters
        ]
    ),
)

# Path to the client cache
CLIENT_CACHE_PATH = from_conf("METAFLOW_CLIENT_CACHE_PATH", "/tmp/metaflow_client")
# Maximum size (in bytes) of the cache
CLIENT_CACHE_MAX_SIZE = from_conf("METAFLOW_CLIENT_CACHE_MAX_SIZE", 10000)
