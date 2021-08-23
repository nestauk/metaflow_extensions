"""Define extensions for metaflow to import."""
# https://gitter.im/metaflow_org/community?at=5de7f82d26eeb8518f691e46
from typing import List

from .install import InstallReqsStep
from .package import LocalProject
from .local import LocalOnly
from .flow import MyFlowDecorator
from .cli import cli_custom

# FLOW_DECORATORS = [LocalOnly, Spec, InstallReqs]
FLOW_DECORATORS = [LocalOnly, MyFlowDecorator]
STEP_DECORATORS = [InstallReqsStep]
ENVIRONMENTS = [LocalProject]


def get_plugin_cli() -> List:
    """Return list of click multi-commands to extend metaflow CLI."""
    return [cli_custom]
