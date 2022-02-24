"""Test pip step decorator as independent feature."""
import pytest

from utils import ch_dir, env, run_flow  # noqa: I

flow_name = "{}/myproject/myproject/flows/{}.py".format


def test_runs_local(temporary_installed_project):
    with ch_dir(temporary_installed_project / "myproject"):
        run_flow(
            flow_name(temporary_installed_project, "pip_flow_conda"),
            environment="conda",
        )


def test_runs_conda(temporary_project):
    with ch_dir(temporary_project / "myproject"):
        run_flow(flow_name(temporary_project, "pip_flow_conda"), environment="conda")


@pytest.mark.aws
def test_runs_batch_conda(temporary_project):
    with ch_dir(temporary_project / "myproject"):
        run_flow(
            flow_name(temporary_project, "pip_flow_conda"),
            batch=True,
            environment="conda",
            metadata="local",
            datastore="s3",
            package_suffixes=[".py", ".txt", ".sh"],
        )
