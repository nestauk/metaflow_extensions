# flake8: noqa
import sys

import pytest

from conftest import run_flow
from metaflow_custom.utils import install_setup_py

def test_runs_locally(project):
    """`flow.py` should run without `metaflow_custom` if `myproject` pip installed."""
    install_setup_py(f"{project}/myproject")
    run_flow(f"{project}/myproject/myproject/flow.py")


def test_runs_conda(project):
    run_flow(f"{project}/myproject/myproject/flow.py", environment="conda")


@pytest.mark.aws
def test_runs_batch(project):
    run_flow(
        f"{project}/myproject/myproject/flow.py",
        batch=True,
        metadata="service",
        datastore="s3",
    )
