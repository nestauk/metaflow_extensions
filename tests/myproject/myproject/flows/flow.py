from metaflow import FlowSpec, step


class MetaflowCustomTestFlow(FlowSpec):
    """Flow for testing metaflow_custom."""

    @step
    def start(self) -> None:
        """Start flow."""
        import myproject

        print(myproject.__path__)

        import toolz

        print(toolz.__path__)

        self.next(self.end)

    @step
    def end(self) -> None:
        """End flow."""
        pass


if __name__ == "__main__":
    MetaflowCustomTestFlow()
