from metaflow import FlowSpec, step


class MetaflowExtensionsTestFlow(FlowSpec):
    """Flow for testing metaflow_extensions."""

    @step
    def start(self):
        """Start flow."""
        try:
            import myduffproject
        except ModuleNotFoundError:
            pass
        else:
            raise ValueError(f"{myduffproject} should not have been found!")

        self.next(self.end)

    @step
    def end(self):
        """End flow."""
        pass


if __name__ == "__main__":
    MetaflowExtensionsTestFlow()
