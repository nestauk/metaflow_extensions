from pathlib import Path

import daps_utils  # This works on batch because of bootstrap_command
from metaflow import batch, conda, FlowSpec, step


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
        print("non-conda lib daps_utils installed: ", daps_utils.__version__)

        # Show preinstall has run (it adds a file called 'special-batch-file')
        assert Path("special-batch-file").exists()
        self.next(self.c)

    @step
    def c(self, inputs):
        """Join the chunks."""
        self.next(self.d)

    @step
    def d(self):
        """Prepare more chunks for batching."""
        self.items = [1]
        self.next(self.e, foreach="items")

    @conda(libraries={"sh": "1.14.2"})
    @batch(queue="job-queue-nesta-metaflow-sandbox")
    @step
    def e(self):
        """Show that daps_utils is also installed."""
        # First show that we're in the env
        import sh

        self.something = self.input
        print("conda specific lib sh installed: ", sh.__version__)

        # Next show that daps_utils is not installed
        print("non-conda lib daps_utils installed: ", daps_utils.__version__)

        assert Path("special-batch-file").exists()
        self.next(self.f)

    @step
    def f(self, inputs):
        """Join the chunks."""
        self.next(self.end)

    @step
    def end(self):
        """Done."""
        pass


if __name__ == "__main__":
    BatchFlow()