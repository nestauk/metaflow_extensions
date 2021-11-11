from contextlib import contextmanager
import shutil
from pathlib import Path

import pytest
import sh

from metaflow_extensions.utils import local_pip_install
from utils import remove_pkg  # noqa: I

MYPROJECT_PATH = Path(__file__).parent / "myproject"


@contextmanager
def temporary_project_maker(tmpdir_factory, project_name):
    project_path = Path(__file__).parent / project_name
    temp = tmpdir_factory.mktemp("data-project")
    shutil.copytree(project_path, temp / project_name)
    sh.git.init(temp)  # to support "daps-utils"-like projects
    yield temp
    shutil.rmtree(temp)


@pytest.fixture(scope="session")
def temporary_project(tmpdir_factory):
    """Create temporary project `myproject`."""
    with temporary_project_maker(tmpdir_factory, "myproject") as temp:
        yield temp


@pytest.fixture(scope="session")
def temporary_duffproject(tmpdir_factory):
    """Create temporary project `myproject`."""
    with temporary_project_maker(tmpdir_factory, "myduffproject") as temp:
        yield temp


@pytest.fixture
def temporary_installed_project(temporary_project):
    """Install `{temporary_project}/myproject/setup.py`."""
    local_pip_install(f"{temporary_project}/myproject")
    sh.git.init(temporary_project)  # to support "daps-utils"-like projects
    yield temporary_project
    remove_pkg("myproject")
