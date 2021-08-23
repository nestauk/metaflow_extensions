"""Test functionality of `run-config` CLI command."""
# flake8: noqa
# type: ignore
import subprocess
import sys
import pytest

from utils import ch_dir, run_flow

flow_name = "{}/myproject/myproject/flow.py".format
config_name = "{}/myproject/myproject/flow_config.yaml".format


def test_runs_locally(temporary_installed_project):
    """`flow.py` should run without `metaflow_custom` if `myproject` pip installed."""
    with ch_dir(temporary_installed_project / "myproject"):
        cmd = [
            sys.executable,
            flow_name(temporary_installed_project),
            "run-config",
            config_name(temporary_installed_project),
        ]
        try:
            out = subprocess.run(cmd, capture_output=True, shell=False, check=True)
        except subprocess.CalledProcessError as e:
            print(e.args)
            print("stdout:", e.stdout)
            print("stderr:", e.stderr)
            raise e
