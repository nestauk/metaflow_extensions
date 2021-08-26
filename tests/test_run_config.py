"""Test functionality of `run-config` CLI command."""
from utils import ch_dir, run_config_flow  # noqa: I202

flow_name = "{}/myproject/myproject/flows/flow.py".format
config_name = "{}/myproject/myproject/flow_config.yaml".format


def test_runs_locally(temporary_installed_project):
    """`flow.py` should run without `metaflow_custom` if `myproject` pip installed."""
    with ch_dir(temporary_installed_project / "myproject"):
        run_config_flow(
            flow_name(temporary_installed_project),
            config_name(temporary_installed_project),
        )
