import sys

from metaflow import conda, conda_base, FlowSpec, pip, step


@conda_base(libraries={"tqdm": "4.62.0"})
class MetaflowExtensionsTestFlow(FlowSpec):
    """Flow for testing metaflow_extensions."""

    @step
    def start(self):
        """Start flow."""
        import tqdm

        print(tqdm.__path__)
        print(sys.executable)
        assert tqdm.__version__ == "4.62.0", tqdm.__version__

        self.next(self.conda_pip)

    @conda(libraries={"tqdm": "4.60.0"})
    @pip(libraries={"tqdm": "4.59.0"})
    @step
    def conda_pip(self):
        import tqdm

        print(tqdm.__path__)
        print(sys.executable)
        assert tqdm.__version__ == "4.59.0", tqdm.__version__

        self.next(self.pip_conda)

    @conda(libraries={"tqdm": "4.60.0"})
    @pip(libraries={"tqdm": "4.59.0"})
    @step
    def pip_conda(self):
        import tqdm

        print(tqdm.__path__)
        print(sys.executable)
        assert tqdm.__version__ == "4.59.0", tqdm.__version__

        self.next(self.no_deco)

    @step
    def no_deco(self):
        import tqdm

        print(tqdm.__path__)
        print(sys.executable)
        assert tqdm.__version__ == "4.62.0", tqdm.__version__

        self.next(self.pip)

    @pip(path="requirements.txt")
    @step
    def pip(self):
        """End flow."""
        import tqdm

        print(tqdm.__path__)
        print(sys.executable)
        assert tqdm.__version__ == "4.61.0", tqdm.__version__

        self.next(self.end)

    @conda(libraries={"tqdm": "4.62.0"})
    @step
    def end(self):
        """End flow."""
        import tqdm

        print(tqdm.__path__)
        print(sys.executable)
        assert tqdm.__version__ == "4.62.0", tqdm.__version__


if __name__ == "__main__":
    MetaflowExtensionsTestFlow()
