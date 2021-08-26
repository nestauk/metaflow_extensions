"""Test helpers."""
import logging
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Optional


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
    extend_pythonpath: bool = True,
) -> subprocess.CompletedProcess:
    """Run Metaflow at `path`."""
    path = Path(path)
    cmd = [
        python,
        str(path.name),
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

    # DAPS projects need to be able to import {myproject}
    # which we can figure out from the executable in this test.
    # With that in mind, we specify PYTHONPATH here because {myproject}
    # is not available at the point when daps_utils is imported.
    env = dict(os.environ)
    if extend_pythonpath:
        pythonpath = str(path.parent.parent.parent) + ":" + env.get("PYTHONPATH", "")
        env.update({"PYTHONPATH": pythonpath})

    try:
        out = subprocess.run(
            cmd, capture_output=True, shell=False, check=True, cwd=path.parent, env=env
        )
    except subprocess.CalledProcessError as e:
        logging.error(e.args)
        logging.error(f"stdout:\n {e.stdout.decode()}")
        logging.error(f"stderr:\n {e.stderr.decode()}")
        raise e
    return out


def run_config_flow(
    flow_path: os.PathLike, config_path: os.PathLike
) -> subprocess.CompletedProcess:
    cmd = [
        sys.executable,
        str(flow_path),
        "run-config",
        str(config_path),
    ]

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
