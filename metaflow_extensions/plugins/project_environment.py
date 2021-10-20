"""Implements a metaflow environment to package up a local project.

Implementation notes:
- MetaflowEnvironment.add_to_package runs in the runtime (orchestrating)
  environment and defines a list of tuples to add to the job package.
- Flow path is used as a starting point to search for setup.py file. It is
  inferred by inspecting the arguments to the current process, the first
  argument being the flow path.
"""
import sys
from itertools import filterfalse
from pathlib import Path

import click
from metaflow.metaflow_environment import MetaflowEnvironment
from metaflow.plugins.conda.conda_environment import CondaEnvironment

from metaflow_extensions.utils import (
    is_path_hidden,
    up_to_project_root,
    walk,
    zip_stripped_root,
)

# XXX - ProjectEnvironment.decospecs is never called if environment=conda!
#       Patch it to add our decospecs too
#       Awaiting fix in PR: https://github.com/Netflix/metaflow/pull/660
CondaEnvironment.decospecs = lambda s: ("conda", *s.base_env.decospecs())


class ProjectEnvironment(MetaflowEnvironment):
    """Metaflow Environment to package up a local project.

    This `metaflow_extensions` package sets this as the default environment
    but may be overridden by a `config_${METAFLOW_PROFILE}.json` or by
    redefining the `METAFLOW_DEFAULT_ENVIRONMENT` environment variable.
    By defining it as the default environment it allows composition with
    other `MetaflowEnvironment` instances, e.g. `CondaEnvironment`.

    If using a different `METAFLOW_DEFAULT_ENVIRONMENT`, select this
    environment when you run the flow by passing `--environment project`.
    """

    TYPE = "project"

    def decospecs(self):
        """Add `install_project` decorator to every step."""
        return ("install_project",)

    def add_to_package(self):
        """Add project (if project root exists to define it) to the job package."""
        # Import encapsulated to avoid import errors
        from metaflow_extensions.config.metaflow_config import (
            DEFAULT_PACKAGE_SUFFIXES,
            PROJECT_FILES,
        )

        flow_path = Path(sys.argv[0])
        path = up_to_project_root(flow_path)
        if path:
            paths = filterfalse(is_path_hidden, walk(path, DEFAULT_PACKAGE_SUFFIXES))
            return list(zip_stripped_root(path, paths))
        else:
            click.secho(
                "project environment did not find a root file, "
                f"(valid: {PROJECT_FILES})",
                "no local project added.",
                bg="red",
            )
            return []

    @classmethod
    def get_client_info(cls, *args):
        """Client information."""
        return "Local project environment (metaflow_extensions)"
