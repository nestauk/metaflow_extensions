"""Test helpers."""
import logging
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional


@contextmanager
def ch_dir(path: os.PathLike) -> None:
    """Context Manager to change directory to `path`."""
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield os.getcwd()
    finally:
        os.chdir(cwd)


def remove_pkg(pkg_name: str) -> None:
    """Uninstall `pkg_name`."""
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "uninstall",
            pkg_name,
            "-y",
            "--quiet",
        ],
        stdout=subprocess.DEVNULL,
        check=True,
    )


def run_flow(
    path: os.PathLike,
    datastore: str = "local",
    metadata: str = "local",
    environment: Optional[str] = None,
    batch: bool = False,
    python: str = sys.executable,
    package_suffixes: Optional[List[str]] = None,
) -> subprocess.CompletedProcess:
    """Run Metaflow at `path`."""
    path = Path(path)
    cmd = [
        python,
        str(path),
        "--datastore",
        str(datastore),
        "--metadata",
        str(metadata),
        "--no-pylint",
    ]

    if environment is not None:
        cmd.extend(["--environment", environment])

    if package_suffixes is not None:
        cmd.extend(["--package-suffixes", ",".join(package_suffixes)])

    cmd.append("run")

    if batch:
        cmd.extend(["--with", "batch"])

    print(cmd)

    try:
        out = subprocess.run(cmd, capture_output=True, shell=False, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(e.args)
        logging.error(f"stdout:\n {e.stdout.decode()}")
        logging.error(f"stderr:\n {e.stderr.decode()}")
        raise e
    return out


@contextmanager
def env(**kwargs) -> None:
    """Context Manager to change env variable."""
    original = dict(os.environ)
    try:
        os.environ.update(kwargs)
        yield
    finally:
        os.environ.clear()
        os.environ.update(original)
