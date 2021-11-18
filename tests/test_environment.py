"""Test a simple flow can import packages defined in it's environment."""
from pathlib import Path

import pytest

from utils import ch_dir, run_flow  # noqa: I

flow_name = lambda path, flow: Path(  # noqa
    "{}/myproject/myproject/flows/{}.py".format(path, flow)
)


def test_runs_locally(temporary_installed_project):
    """Flow should run without `metaflow_extensions` if `myproject` pip installed."""
    run_flow(flow_name(temporary_installed_project, "flow"))


def test_duff_project_runs_locally(temporary_duffproject):
    """Flow should run but `myduffproject` won't have been installed since the project is duff.
    The flow itself should test whether the error handling is working (fixes bug
    https://github.com/nestauk/metaflow_extensions/issues/23)
    """
    with ch_dir(temporary_duffproject / "myduffproject"):
        proc = run_flow(
            temporary_duffproject / "myduffproject/myduffproject/flows/duff_flow.py",
            extend_pythonpath=False,
        )
    assert b"project environment did not find a root file" in proc.stdout


@pytest.mark.parametrize("flow", ["flow", "pip_flow_conda"])
def test_runs_conda(temporary_project, flow):
    """`flow.py` should run due to `LocalProject` default environment."""
    with ch_dir(temporary_project / "myproject"):
        run_flow(flow_name(temporary_project, flow), environment="conda")


@pytest.mark.aws
class TestAwsRuns:
    @pytest.mark.parametrize("flow", ["flow", "batch_flow", "batch_flow_with_conda"])
    def test_runs_all_batch(self, temporary_project, flow):
        """Flows run entirely on batch."""
        kwargs = {"environment": "conda"} if flow.endswith("conda") else {}
        with ch_dir(temporary_project / "myproject"):
            run_flow(
                flow_name(temporary_project, flow),
                batch=True,
                metadata="service",
                datastore="s3",
                **kwargs
            )

    @pytest.mark.parametrize("flow", ["flow", "batch_flow", "batch_flow_with_conda"])
    def test_runs_some_batch(self, temporary_installed_project, flow):
        """Flows run mixture of local and on batch."""
        kwargs = {"environment": "conda"} if flow.endswith("conda") else {}
        with ch_dir(temporary_installed_project / "myproject"):
            run_flow(
                flow_name(temporary_installed_project, "flow"), datastore="s3", **kwargs
            )
