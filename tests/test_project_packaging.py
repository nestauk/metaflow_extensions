"""Tests ability to import and run a local project.

Relies on symlinking in tandem with `PipStepDecorator`.
"""
import pytest

from metaflow_extensions.nesta.utils import ch_dir
from utils import run_flow  # noqa: I

flow_name = "{}/myproject/myproject/flows/{}.py".format


def test_runs_local(temporary_installed_project):
    with ch_dir(temporary_installed_project / "myproject"):
        run_flow(flow_name(temporary_installed_project, "project_packaging_flow"))


def test_runs_conda(temporary_project):
    with ch_dir(temporary_project / "myproject"):
        run_flow(
            flow_name(temporary_project, "project_packaging_flow"),
            environment="conda",
        )


@pytest.mark.aws
def test_runs_batch_local_base(temporary_project):
    with ch_dir(temporary_project / "myproject"):
        run_flow(
            flow_name(temporary_project, "project_packaging_flow"),
            batch=True,
            environment="conda",
            datastore="s3",
            package_suffixes=[".py", ".txt", ".sh"],
        )
