"""Test pip step decorator as independent feature."""
import pytest

from utils import ch_dir, env, run_flow  # noqa: I

flow_name = "{}/myproject/myproject/flows/pip_flow_conda.py".format


def test_runs_local_base(temporary_project):
    with env(METAFLOW_DEFAULT_ENVIRONMENT="local"):
        with ch_dir(temporary_project / "myproject"):
            run_flow(flow_name(temporary_project), environment="conda")


@pytest.mark.aws
def test_runs_batch_local_base(temporary_project):
    with env(METAFLOW_DEFAULT_ENVIRONMENT="local"):
        with ch_dir(temporary_project / "myproject"):
            run_flow(
                flow_name(temporary_project),
                batch=True,
                environment="conda",
                metadata="local",
                datastore="s3",
            )
