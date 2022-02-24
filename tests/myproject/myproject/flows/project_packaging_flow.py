from metaflow import FlowSpec, pip, step


class MetaflowExtensionsProjectPackageFlow(FlowSpec):
    """Dummy flow for testing `ProjectEnvironment.add_to_package` and
    `PipStepDecorator` to achieve local packaging.
    """

    @pip(path="requirements-project_packaging_flow.txt")
    @step
    def start(self):
        """Start flow."""
        import myproject

        print(myproject.__path__)

        import toolz

        print(toolz.__path__)

        self.next(self.end)

    @step
    def end(self):
        """End flow."""
        pass


if __name__ == "__main__":
    MetaflowExtensionsProjectPackageFlow()
