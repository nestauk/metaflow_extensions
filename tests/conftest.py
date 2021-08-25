import shutil
from pathlib import Path

import pytest

from utils import install_setup_py, remove_pkg  # noqa: I


MYPROJECT_PATH = Path(__file__).parent / "myproject"


@pytest.fixture(scope="session")
def temporary_project(tmpdir_factory):
    """Create temporary project `myproject`."""
    temp = tmpdir_factory.mktemp("data-project")
    shutil.copytree(MYPROJECT_PATH, temp / "myproject")
    yield temp
    shutil.rmtree(temp)


@pytest.fixture
def temporary_installed_project(temporary_project):
    """Install `{temporary_project}/myproject/setup.py`."""
    install_setup_py(f"{temporary_project}/myproject")
    yield temporary_project
    remove_pkg("myproject")
