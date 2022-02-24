from pathlib import Path

import daps_utils  # This works on batch because preinstall-batch_flow.sh installs it
from metaflow import batch, FlowSpec, step


class MetaflowExtensionsPreinstallFlow(FlowSpec, daps_utils.DapsFlowMixin):
    """Dummy batch flow for showing that bootstrap_command is working."""

    @step
    def start(self):
        """Prepare chunks for batching."""
        self.items = [1]
        self.next(self.b, foreach="items")

    @batch()
    @step
    def b(self):
        """Show that daps_utils is installed via. preinstall."""
        self.something = self.input
        print("non-conda batch task has installed", daps_utils.__version__)

        # Show preinstall has run (it adds a file called 'special-batch-file')
        assert Path("special-batch-file").exists()
        self.next(self.c)

    @step
    def c(self, inputs):
        """Join the chunks."""
        self.next(self.end)

    @step
    def end(self):
        """Done."""
        pass


if __name__ == "__main__":
    MetaflowExtensionsPreinstallFlow()
