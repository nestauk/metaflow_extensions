"""Test functionality of `InstallReqsStep` and `LocalProject`."""
# flake8: noqa
# type: ignore

from conftest import ch_dir, run_flow

flow_name = "{}/myproject/myproject/flow.py".format


def test_runs_locally(temporary_installed_project):
    """`flow.py` should run without `metaflow_custom` if `myproject` pip installed."""
    with ch_dir(temporary_installed_project / "myproject"):
        run_flow(flow_name(temporary_installed_project))


# def test_runs_conda(temporary_project):
#     with ch_dir(temporary_project / "myproject"):
#         run_flow(flow_name(temporary_project), environment="conda")

# @pytest.mark.aws
# def test_runs_batch(project):
#     with ch_dir(project / "myproject"):
#         run_flow(
#             flow_name(project),
#             batch=True,
#             metadata="service",
#             datastore="s3",
#         )
