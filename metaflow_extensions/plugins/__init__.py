"""Define extensions for metaflow to import."""
from typing import List

from .install_step_decorator import InstallProjectStepDecorator
from .project_environment import ProjectEnvironment


FLOW_DECORATORS = []
STEP_DECORATORS = [InstallProjectStepDecorator]
ENVIRONMENTS = [ProjectEnvironment]
METADATA_PROVIDERS = []
SIDECARS = {}
LOGGING_SIDECARS = {}
MONITOR_SIDECARS = {}


def get_plugin_cli() -> List:
    """Return list of click multi-commands to extend metaflow CLI."""
    return []
