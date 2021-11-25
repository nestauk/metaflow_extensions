"""Metaflow environment to package up a local project & run preinstall scripts.

Implementation notes:
- MetaflowEnvironment.add_to_package runs in the runtime (orchestrating)
  environment and defines a list of tuples to add to the job package.
- Flow path is used as a starting point to search for a project root. It is
  inferred by inspecting the arguments to the current process, the first
  argument being the flow path.
"""
import sys
from itertools import filterfalse
from pathlib import Path

from metaflow.metaflow_environment import MetaflowEnvironment
from metaflow.plugins.conda.conda_environment import CondaEnvironment


def will_task_be_batch(step_name: str, flow: object) -> bool:
    """Returns `True` if `step_name` of `flow` will run on batch."""
    from metaflow.plugins.aws.batch.batch_decorator import BatchDecorator

    step_decos = getattr(flow, step_name).decorators
    return any(isinstance(deco, BatchDecorator) for deco in step_decos)


def bootstrap_wrapper(conda_env_bootstrap_commands):
    """Concatenates {CondaEnvironment and ProjectEnvironment}.bootstrap_commands.

    In the flow lifecycle this called directly before the conda step is
    explicitly executed: in practice this occurs in metaflow's batch.py
    (i.e. it is only executed on batch steps). There is some duplication with
    the prepare_step_wrapper method in this module, which can be read in the
    docstring therein.

    Arguments:
        conda_env_bootstrap_commands: CondaEnvironment method to be wrapped

    Returns:
        The wrapped function
    """

    def wrapped_bootstrap_commands(self, step_name):
        from metaflow.metaflow_config import DEFAULT_ENVIRONMENT

        cmds = conda_env_bootstrap_commands(self, step_name)

        if DEFAULT_ENVIRONMENT == "project":
            cmds += ProjectEnvironment.bootstrap_commands(self, step_name)
        return cmds

    return wrapped_bootstrap_commands


# Force CondaEnvironment to pick up extra ProjectEnvironment.bootstrap_commands
CondaEnvironment.bootstrap_commands = bootstrap_wrapper(
    CondaEnvironment.bootstrap_commands
)


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

    def add_to_package(self):
        """Add project (if project root exists to define it) to the job package."""
        # Import encapsulated to avoid import errors
        import click
        from metaflow.metaflow_config import DEFAULT_PACKAGE_SUFFIXES
        from metaflow_extensions.nesta.config.metaflow_config import PROJECT_FILES
        from metaflow_extensions.nesta.utils import (
            is_path_hidden,
            up_to_project_root,
            walk,
            zip_stripped_root,
        )

        flow_path = Path(sys.argv[0]).resolve()
        path = up_to_project_root(flow_path)
        if path:
            paths = filterfalse(is_path_hidden, walk(path, DEFAULT_PACKAGE_SUFFIXES))
            return list(zip_stripped_root(path, paths))
        else:
            click.secho(
                "project environment did not find a root file, "
                f"(valid: {PROJECT_FILES}, flow path: {flow_path})"
                "no local project added.",
                bg="red",
            )
            return []

    @classmethod
    def get_client_info(cls, *args):
        """Client information."""
        return "Local project environment (metaflow_extensions)"

    def bootstrap_commands(self, step_name):
        """Run before any step decorators are initialized."""
        # Identify python binary and make it usable in preinstall scripts
        # through MFPYTHON environment variable.
        cmds = [
            # `true` 'swallows' the python wrapper that Metaflow puts around
            # these commands that will break exports
            "true"
            # find python executable. For conda this lives under
            # `metaflow_<flow name>_<architecture>_<conda hash>/bin/python`
            " && export MFPYTHON=$(find . -name python)"
            # if python executable not found, conda isn't being used so just
            #  use `python`
            " && export MFPYTHON=${MFPYTHON:-python}"
        ]

        # Run any pre-install scripts
        flow_name = Path(sys.argv[0]).stem
        flow_dir = Path(sys.argv[0]).parent

        preinstalls = (
            "preinstall.sh",
            f"preinstall-{flow_name}.sh",
            f"preinstall-{flow_name}-{step_name}.sh",
        )
        preinstalls = list(
            filter(lambda fname: (flow_dir / fname).exists(), preinstalls)
        )
        for fname in preinstalls:
            cmds.extend([f"chmod +x {fname}", f"./{fname}"])

        print("Bootstrap commands added by preinstall environment:", cmds)
        return cmds
