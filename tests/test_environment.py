"""Test a simple flow can import packages defined in it's environment."""
from utils import run_flow

flow_name = "{}/myproject/myproject/flows/flow.py".format


def test_runs_locally(temporary_installed_project):
    """`flow.py` should run without `metaflow_custom` if `myproject` pip installed."""
    run_flow(flow_name(temporary_installed_project))
