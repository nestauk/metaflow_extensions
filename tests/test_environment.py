"""Test a simple flow can import packages defined in it's environment."""
import pytest

from utils import ch_dir, run_flow  # noqa: I

flow_name = "{}/myproject/myproject/flows/flow.py".format


def test_runs_locally(temporary_installed_project):
    """Flow should run without `metaflow_extensions` if `myproject` pip installed."""
    run_flow(flow_name(temporary_installed_project))


def test_duff_project_runs_locally(temporary_duffproject):
    """Flow should run but `myduffproject` won't have been installed since the project is duff.
    The flow itself should test whether the error handling is working (fixes bug
    https://github.com/nestauk/metaflow_extensions/issues/23)
    """
    with ch_dir(temporary_duffproject / "myduffproject"):
        run_flow(
            temporary_duffproject / "myduffproject/myduffproject/flows/duff_flow.py"
        )


def test_runs_conda(temporary_project):
    """`flow.py` should run due to `LocalProject` default environment."""
    with ch_dir(temporary_project / "myproject"):
        run_flow(flow_name(temporary_project), environment="conda")


@pytest.mark.aws
def test_runs_batch(temporary_project):
    """`flow.py` should run due to `LocalProject` default environment."""
    with ch_dir(temporary_project / "myproject"):
        run_flow(
            flow_name(temporary_project),
            batch=True,
            metadata="service",
            datastore="s3",
        )
