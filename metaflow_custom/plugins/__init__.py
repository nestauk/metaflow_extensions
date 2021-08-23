"""Define extensions for metaflow to import."""
# https://gitter.im/metaflow_org/community?at=5de7f82d26eeb8518f691e46
from typing import List

FLOW_DECORATORS = []
STEP_DECORATORS = []
ENVIRONMENTS = []


def get_plugin_cli() -> List:
    """Return list of click multi-commands to extend metaflow CLI."""
    return []
