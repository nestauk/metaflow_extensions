import os
from typing import Optional

from metaflow.metaflow_config import METAFLOW_CONFIG


def from_conf(name, default: Optional[str] = None):
    """Get value of `name` from configuration sources, or `default`.

    Prioritisation order:
    1) Env variable
    2) metaflow config JSON
    3) `default`

    Args:
        name: Environment variable name.
        default: Fallback value.

    Returns:
        Value of `name`, if one exists.
    """
    return os.environ.get(name, METAFLOW_CONFIG.get(name, default))


# Path to the client cache
CLIENT_CACHE_PATH = from_conf("METAFLOW_CLIENT_CACHE_PATH", "/tmp/metaflow_client")

# Maximum size (in bytes) of the cache
CLIENT_CACHE_MAX_SIZE = from_conf("METAFLOW_CLIENT_CACHE_MAX_SIZE", "10000")
