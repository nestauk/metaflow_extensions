# type: ignore
import shutil
from pathlib import Path
from typing import Iterator

import pytest
from _pytest.tmpdir import TempdirFactory

from .utils import install_setup_py, remove_pkg


@pytest.fixture(scope="session")
def temporary_project(tmpdir_factory: TempdirFactory) -> None:
    """Create temporary project `myproject`."""
    temp = tmpdir_factory.mktemp("data-project")
    _create_project(temp)
    yield temp
    shutil.rmtree(temp)


@pytest.fixture
def temporary_installed_project(
    temporary_project: TempdirFactory,
) -> Iterator[TempdirFactory]:
    """Install `{temporary_project}/myproject/setup.py`."""
    install_setup_py(f"{temporary_project}/myproject")
    yield temporary_project
    remove_pkg("myproject")


def _create_project(root: Path) -> None:
    """Copy `tests/myproject` to `root`."""
    src = Path(__file__).parent / "myproject"
    shutil.copytree(src, root / "myproject")
