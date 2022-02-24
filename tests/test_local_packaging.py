"""Test ProjectEnvironment.add_to_package in tandem with PipStepDecorator."""
from pathlib import Path

import pytest

from utils import ch_dir, env, run_flow  # noqa: I

flow_name = lambda path, flow: Path(  # noqa
    "{}/myproject/myproject/flows/{}.py".format(path, flow)
)


def test_duff_project_runs_locally(temporary_duffproject):
    """Flow should run but `myduffproject` won't have been installed.

    The flow itself should test whether the error handling is working (fixes bug
    https://github.com/nestauk/metaflow_extensions/issues/23)
    """
    with env(METAFLOW_DEFAULT_ENVIRONMENT="project"):
        with ch_dir(temporary_duffproject / "myduffproject"):
            proc = run_flow(
                temporary_duffproject
                / "myduffproject/myduffproject/flows/duff_flow.py",
            )
        assert b"project environment did not find a root file" in proc.stdout


def test_runs_local_projectenv(temporary_project):
    with env(METAFLOW_DEFAULT_ENVIRONMENT="project"):
        # MUST: Run from directory alongside setup.py for `.` in `mine.txt` to
        # work on local machine!
        with ch_dir(temporary_project / "myproject"):
            run_flow(flow_name(temporary_project, "flow"))


def test_runs_conda_projectenv(temporary_project):
    with env(METAFLOW_DEFAULT_ENVIRONMENT="project"):
        # MUST: Run from directory alongside setup.py for `.` in `mine.txt` to
        # work on local machine!
        with ch_dir(temporary_project / "myproject"):
            run_flow(flow_name(temporary_project, "flow"), environment="conda")


@pytest.mark.aws
def test_runs_batch_local_base(temporary_project):
    with env(METAFLOW_DEFAULT_ENVIRONMENT="project"):
        with ch_dir(temporary_project / "myproject"):
            run_flow(
                flow_name(temporary_project, "flow"),
                batch=True,
                environment="conda",
                metadata="local",
                datastore="s3",
                package_suffixes=[".py", ".txt", ".sh"],
            )
