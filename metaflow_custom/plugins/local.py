import sys

from metaflow.decorators import FlowDecorator
from metaflow.exception import MetaflowException

from metaflow_custom.utils import running_in_local_env


class LocalOnly(FlowDecorator):
    """Decorator prevents a flow being run on batch or separate conda environment."""

    name = "local_only"
    defaults = {"reason": None, "disallow": None}

    def flow_init(self, flow, graph, environment, datastore, logger, echo, options):
        """Print reason for only running locally, and raise Error if not obeyed."""
        reason = self.attributes.get("reason")
        reason_msg = f" Reason: *{reason}*" if reason else ""
        echo(
            f"Running in local only mode due to LocalOnly decorator.{reason_msg}",
            fg="magenta",
            highlight="green",
        )

        disallow = self.attributes.get("disallow")
        if disallow is None and not running_in_local_env():
            raise MetaflowException(
                "This flow can only run locally "
                "(when the runtime and tasktime environments are the same."
            )

        if disallow and any(_phrase_segment_in_command(s) for s in disallow):
            raise MetaflowException(
                "This flow can only run locally." f"{disallow} in {sys.argv}."
            )


def _phrase_segment_in_command(s: str) -> bool:
    return any(s in arg for arg in sys.argv)
