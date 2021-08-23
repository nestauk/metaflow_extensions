"""Define extensions for metaflow to import."""
from typing import List

FLOW_DECORATORS = []
STEP_DECORATORS = []
ENVIRONMENTS = []
METADATA_PROVIDERS = []
SIDECARS = []
LOGGING_SIDECARS = []
MONITOR_SIDECARS = []


def get_plugin_cli() -> List:
    """Return list of click multi-commands to extend metaflow CLI."""
    return []
