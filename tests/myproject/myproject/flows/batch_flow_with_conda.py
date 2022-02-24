from pathlib import Path

import tqdm  # This works on batch because of preinstall
from metaflow import batch, conda, FlowSpec, step


class MetaflowExtensionsPreinstallCondaFlow(FlowSpec):
    """Dummy batch flow for showing that bootstrap_command is working."""

    @step
    def start(self):
        """Prepare chunks for batching."""
        self.items = [1]
        self.next(self.b, foreach="items")

    @batch()
    @step
    def b(self):
        """Show that tqdm is installed via. preinstall."""
        self.something = self.input
        print("non-conda lib tqdm installed: ", tqdm.__version__)

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
    @batch()
    @step
    def e(self):
        """Show that tqdm is also installed via. preinstall in Conda."""
        # First show that we're in the env
        import sh

        self.something = self.input
        print("conda specific lib sh installed: ", sh.__version__)

        # Next show that tqdm is not installed
        print("non-conda lib tqdm installed: ", tqdm.__version__)

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
    MetaflowExtensionsPreinstallCondaFlow()
