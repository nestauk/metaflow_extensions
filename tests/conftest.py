import shutil
import sys
from contextlib import contextmanager
from pathlib import Path

import pytest

from metaflow_extensions.nesta.utils import pip_install

from utils import remove_pkg  # noqa: I

MYPROJECT_PATH = Path(__file__).parent / "myproject"


@contextmanager
def temporary_project_maker(tmpdir_factory, project_name):
    project_path = Path(__file__).parent / project_name
    temp = tmpdir_factory.mktemp("data-project")
    shutil.copytree(project_path, temp / project_name, symlinks=True)
    pip_install(sys.executable, "tqdm")
    yield temp
    remove_pkg("tqdm")
    shutil.rmtree(temp)


@pytest.fixture(scope="session")
def temporary_project(tmpdir_factory):
    """Create temporary project `myproject`."""
    with temporary_project_maker(tmpdir_factory, "myproject") as temp:
        yield temp


@pytest.fixture
def temporary_installed_project(temporary_project):
    """Clean up any installation of `myproject` in the main environment."""
    yield temporary_project
    remove_pkg("myproject")
