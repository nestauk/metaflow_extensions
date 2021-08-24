from metaflow import FlowSpec, local_only, step


@local_only(reason="myreason")
class MetaflowCustomTestFlow(FlowSpec):
    """Flow for testing metaflow_custom."""

    @step
    def start(self) -> None:
        """Start flow."""
        import myproject

        print(myproject.__path__)

        self.next(self.end)

    @step
    def end(self) -> None:
        """End flow."""
        pass


if __name__ == "__main__":
    MetaflowCustomTestFlow()
