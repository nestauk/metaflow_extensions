"""Tests the `preinstall` Metaflow environment."""
from pathlib import Path

import pytest

from utils import ch_dir, env, run_flow  # noqa: I

flow_name = lambda path, flow: Path(  # noqa
    "{}/myproject/myproject/flows/{}.py".format(path, flow)
)


@pytest.mark.aws
def test_runs_some_batch(temporary_project):
    with ch_dir(temporary_project / "myproject"):
        run_flow(
            flow_name(temporary_project, "batch_flow"),
            datastore="s3",
            package_suffixes=[".py", ".txt", ".sh"],
            environment="project",
        )


@pytest.mark.aws
def test_runs_all_batch_conda(temporary_project):
    with ch_dir(temporary_project / "myproject"):
        with env(METAFLOW_DEFAULT_ENVIRONMENT="project"):
            run_flow(
                flow_name(temporary_project, "batch_flow_with_conda"),
                datastore="s3",
                environment="conda",
                package_suffixes=[".py", ".txt", ".sh"],
                # All steps must run on batch when using conda to preinstall
                # a package that is loaded at the top-level, e.g. to provide mixins!
                # This is because we can't make those modules available in a
                # local conda environment before executing the flow file.
                batch=True,
            )
