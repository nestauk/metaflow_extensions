"""Utility functions."""
import logging
import os
import shlex
import subprocess
from contextlib import contextmanager
from typing import Tuple, Union


@contextmanager
def ch_dir(path: os.PathLike) -> None:
    """Context Manager to change directory to `path`."""
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield os.getcwd()
    finally:
        os.chdir(cwd)


def is_mflow_conda_environment(argv, default_env) -> bool:
    """True if current process is a Metaflow Conda environment."""
    joined_argv = " ".join(argv)
    return (
        default_env == "conda"
        or "--environment conda" in joined_argv
        or "--with conda" in joined_argv
    )


def pip(
    executable: str, *pip_cmds: str, **subprocess_kwargs
) -> subprocess.CompletedProcess:
    """Execute pip for the given python executable."""
    process = subprocess.run(
        [executable, "-m", "pip", *pip_cmds], check=True, **subprocess_kwargs
    )
    return process


def pip_install(
    executable: str, paths: Union[str, Tuple[str, ...]], *args
) -> subprocess.CompletedProcess:
    """`pip install` local package at `path`."""
    logging.info(f"pip installing {paths} for {executable}.")

    if isinstance(paths, str):
        paths = (paths,)

    return pip(
        executable,
        "install",
        *map(shlex.quote, paths),
        # "--quiet",
        *map(shlex.quote, args),
        stdout=subprocess.DEVNULL,
    )
