# type: ignore
import os
import shutil
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from subprocess import CalledProcessError
from _pytest.tmpdir import TempdirFactory

import pytest


@contextmanager
def ch_dir(path: os.PathLike) -> None:
    """Context Manager to change directory to `path`."""
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield os.getcwd()
    finally:
        os.chdir(cwd)


def _create_project(root: Path) -> None:
    # Copy `tests/myproject` to `root`
    src = Path(__file__).parent / "myproject"
    shutil.copytree(src, root / "myproject")
    print(src, root)


def run_flow(
    path: os.PathLike,
    datastore="local",
    metadata="local",
    environment=None,
    batch=False,
    python=sys.executable,
) -> None:

    cmd = [
        python,
        str(path),
        "--datastore",
        str(datastore),
        "--metadata",
        str(metadata),
        "--no-pylint",
    ]

    if batch:
        cmd.extend(["--with", "batch"])

    if environment is not None:
        cmd.extend(["--environment", environment])

    cmd.append("run")

    try:
        out = subprocess.run(cmd, capture_output=True, shell=False, check=True)
    except CalledProcessError as e:
        print(e.args)
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)
        raise
    return out


@pytest.fixture(scope="session")
def project(tmpdir_factory: TempdirFactory) -> None:
    """Create temporary project."""
    print(type(tmpdir_factory))
    temp = tmpdir_factory.mktemp("data-project")
    print(temp)

    _create_project(temp)

    yield temp

    shutil.rmtree(temp)
