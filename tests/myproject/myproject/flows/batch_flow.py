import daps_utils  # This works on batch because of bootstrap_command
from metaflow import batch, FlowSpec, step


class BatchFlow(FlowSpec, daps_utils.DapsFlowMixin):
    """Dummy batch flow for showing that bootstrap_command is working."""

    @step
    def start(self):
        """Start the flow."""
        self.next(self.a)

    @step
    def a(self):
        """Prepare chunks for batching."""
        self.items = [1]
        self.next(self.b, foreach="items")

    @batch(queue="job-queue-nesta-metaflow-test")
    @step
    def b(self):
        """Show that daps_utils is installed, and that preinstall is run."""
        self.something = self.input
        # Show daps_utils is installed
        print("non-conda batch task has installed", daps_utils.__version__)
        # Show preinstall has run (it adds a file called 'special-batch-file')
        from pathlib import Path

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
    BatchFlow()
