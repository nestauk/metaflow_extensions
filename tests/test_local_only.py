"""Test functionality of `LocalOnly`."""
# flake8: noqa
# type: ignore
from subprocess import CalledProcessError

import pytest

from utils import ch_dir, run_flow

flow_name = "{}/myproject/myproject/local_only_flow.py".format


def test_runs_locally(temporary_installed_project):
    """`flow.py` should run without `metaflow_custom` if `myproject` pip installed."""
    with ch_dir(temporary_installed_project / "myproject"):
        run_flow(flow_name(temporary_installed_project))


def test_fails_with_conda(temporary_project):
    try:
        with ch_dir(temporary_project / "myproject"):
            run_flow(flow_name(temporary_project), environment="conda")
    except CalledProcessError as e:
        stderr = e.stderr.decode()
        assert "This flow can only run locally" in stderr
        assert "myreason" in stderr


@pytest.mark.aws
def test_fails_with_batch(temporary_project):
    try:
        with ch_dir(temporary_project / "myproject"):
            run_flow(
                flow_name(temporary_project),
                batch=True,
                metadata="service",
                datastore="s3",
            )
    except CalledProcessError as e:
        assert "This flow can only run locally, not in batch mode." in e.stderr.decode()
