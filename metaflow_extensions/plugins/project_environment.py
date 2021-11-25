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
from typing import Callable

import click
from metaflow.metaflow_environment import MetaflowEnvironment
from metaflow.plugins.conda.conda_environment import CondaEnvironment
from metaflow.plugins.conda.conda_step_decorator import CondaStepDecorator

from metaflow_extensions.utils import (
    get_conda_python_executable,
    get_pkg_spec,
    install_flow_project,
    is_path_hidden,
    pip_install,
    platform_arch_mismatch,
    up_to_project_root,
    upgrade_pip,
    walk,
    zip_stripped_root,
)


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
        cmds = conda_env_bootstrap_commands(self, step_name)
        cmds += ProjectEnvironment.bootstrap_commands(self, step_name)
        return cmds

    return wrapped_bootstrap_commands


def prepare_step_wrapper(conda_step_prepare_step_environment: Callable) -> Callable:
    """Appends commands after CondaStepDecorator._prepare_step_environment execution.

    In the flow lifecycle this is executed prior to steps being explicitly executed:
    in practice this occurs in conda_step_decorator.package_init and
    runtime_task_create, and it is only executed on local steps (i.e. not batch
    steps). There is some duplication with the task_pre_step method in this
    module as the bootstrap_commands method is executed
    immediately prior to the batch runtime, and is never called locally.

    In short, the difference between task_pre_step
    and bootstrap_wrapper is that:

      * prepare_step_wrapper patches the local conda environment only (it is unable to
        patch the batch conda environment because different of architectures, e.g.
        MacOS on local vs Linux on batch, although patching of the batch environment
        is anyway inconsequential as it is reproduced from conda.dependencies anyway.)
      * bootstrap_wrapper patches the batch conda env only, by definition.

    Arguments:
        conda_step_prepare_step_environment: CondaStepDecorator method to be wrapped

    Returns:
        The wrapped function
    """

    def wrapped_prepare_step_environment(self, *args, **kwargs):
        from metaflow_extensions.config.metaflow_config import (
            PREINSTALL_PKGS,
            DEFAULT_ENVIRONMENT,
        )

        env_id = conda_step_prepare_step_environment(self, *args, **kwargs)
        if DEFAULT_ENVIRONMENT != "project":
            return env_id  # i.e. use default behaviour for non-project environments

        # tl,dr; if this is a batch step, skip it, as package installation
        #        for batch steps is done by bootstrap_wrapper, whereas
        #        prepare_step_wrapper deals with local steps.
        if will_task_be_batch(args[0], self.flow):
            return env_id

        if platform_arch_mismatch(env_id):
            raise AssertionError("Shouldn't be happening!")

        python_exec = get_conda_python_executable(env_id)
        upgrade_pip(python_exec)  # Need newer features for install step

        # Pre-install specified packages if the user has them
        # installed in their local python env
        for pkg_spec in filter(None, map(get_pkg_spec, PREINSTALL_PKGS)):
            pip_install(python_exec, pkg_spec)

        # Install the local project into the current conda env
        install_flow_project(python_exec)
        return env_id

    return wrapped_prepare_step_environment


# XXX - ProjectEnvironment.decospecs is never called if environment=conda!
#       Patch it to add our decospecs too
#       Awaiting fix in PR: https://github.com/Netflix/metaflow/pull/660
CondaEnvironment.decospecs = lambda s: ("conda", *s.base_env.decospecs())

# Force CondaEnvironment to pick up extra ProjectEnvironment.bootstrap_commands
CondaEnvironment.bootstrap_commands = bootstrap_wrapper(
    CondaEnvironment.bootstrap_commands
)

CondaStepDecorator._prepare_step_environment = prepare_step_wrapper(
    CondaStepDecorator._prepare_step_environment
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
        from metaflow_extensions.config.metaflow_config import (
            DEFAULT_PACKAGE_SUFFIXES,
            PROJECT_FILES,
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
        # Import encapsulated to avoid import errors
        from metaflow_extensions.config.metaflow_config import PREINSTALL_PKGS

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
        cmds = [f"chmod +x {fname} && ./{fname}" for fname in preinstalls]

        # Pre-install specified packages if the user have them
        # installed in their local python env
        pip_install = f"{self.executable(step_name)} -m pip install --quiet"
        for pkg_spec in filter(None, map(get_pkg_spec, PREINSTALL_PKGS)):
            cmds += [
                f"{pip_install} --upgrade pip",
                f"{pip_install} {pkg_spec} 1> /dev/null",
            ]

        # Install flow project
        cmds.append(f"{pip_install} pkg_self/.")

        return cmds
