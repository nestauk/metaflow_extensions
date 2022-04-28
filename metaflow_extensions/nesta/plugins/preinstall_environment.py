"""Implements a metaflow environment to run preinstall scripts."""
import sys
from pathlib import Path

from metaflow.metaflow_environment import MetaflowEnvironment
from metaflow.plugins.conda.conda_environment import CondaEnvironment


def bootstrap_wrapper(conda_env_bootstrap_commands):
    """Concatenates {CondaEnvironment and PreinstallEnvironment}.bootstrap_commands."""

    def wrapped_bootstrap_commands(self, step_name):
        from metaflow.metaflow_config import DEFAULT_ENVIRONMENT

        cmds = conda_env_bootstrap_commands(self, step_name)

        if DEFAULT_ENVIRONMENT == "preinstall":
            cmds += PreinstallEnvironment.bootstrap_commands(self, step_name)
        return cmds

    return wrapped_bootstrap_commands


# Force CondaEnvironment to pick up extra PreinstallEnvironment.bootstrap_commands
CondaEnvironment.bootstrap_commands = bootstrap_wrapper(
    CondaEnvironment.bootstrap_commands
)


class PreinstallEnvironment(MetaflowEnvironment):
    """Metaflow Environment to run preinstall scripts.

    This `metaflow_extensions` package sets this as the default environment
    but may be overridden by a `config_${METAFLOW_PROFILE}.json` or by
    redefining the `METAFLOW_DEFAULT_ENVIRONMENT` environment variable.
    By defining it as the default environment it allows composition with
    other `MetaflowEnvironment` instances, e.g. `CondaEnvironment`.

    If using a different `METAFLOW_DEFAULT_ENVIRONMENT`, select this
    environment when you run the flow by passing `--environment preinstall`.
    """

    TYPE = "preinstall"

    @classmethod
    def get_client_info(cls, *args):
        """Client information."""
        return "Preinstall environment (metaflow_extensions)"

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
