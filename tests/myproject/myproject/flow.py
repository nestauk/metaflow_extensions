from metaflow import FlowSpec, step


class MetaflowCustomTestFlow(FlowSpec):
    """Flow for testing metaflow_custom."""

    @step
    def start(self):
        """Start flow."""
        import myproject
        import toolz
        self.next(self.end)

    @step
    def end(self):
        """End flow."""
        pass


if __name__ == "__main__":
    MetaflowCustomTestFlow()
