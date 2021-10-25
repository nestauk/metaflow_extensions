"""Utility functions."""
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Tuple


def has_project_file(path: Path) -> bool:
    """True if `path` contains metaflow project file."""
    # Import encapsulated to avoid import errors
    from metaflow_extensions.config.metaflow_config import PROJECT_FILES

    return any((path / file).exists() for file in PROJECT_FILES)


def up_to_project_root(init_path: Path) -> Optional[Path]:
    """Walk up until project root found."""
    path = init_path.resolve()
    while not has_project_file(path):
        path = path.parent
        if path == Path("/"):
            return None
    return path


def walk(root: os.PathLike, addl_suffixes: List[str]) -> Iterator[str]:
    """Recursive walk through `root`, yield paths with suffixes in `addl_suffixes`."""
    suffixes = tuple(addl_suffixes)
    for path, _, files in os.walk(root):
        yield from (
            os.path.join(path, file) for file in files if file.endswith(suffixes)
        )


def is_path_hidden(path: os.PathLike) -> bool:
    """True if `path` contains a hidden component."""
    return "/." in path or Path(path).name.startswith(".")


def zip_stripped_root(
    root: os.PathLike, paths: Iterable[str]
) -> Iterator[Tuple[str, str]]:
    """Return tuples of path and path with `root` stripped for paths in `path`."""
    return map(lambda item: (item, item.replace(str(root), "", 1)), paths)


def running_in_local_env() -> bool:
    """True if runtime environment is/will be the same as task-time environment."""
    return not any(
        arg.startswith("batch") or arg.startswith("conda") for arg in sys.argv
    )


def local_pip_install(project_path: Path) -> None:
    """`pip install` local package at `project_path`."""
    logging.info(f"pip installing @ {project_path} for {sys.executable}.")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            str(project_path),
            "--quiet",
            # Needed to avoid temporary copies of large dirs like `outputs/`
            "--use-feature",
            "in-tree-build",
        ],
        stdout=subprocess.DEVNULL,
        check=True,
    )


def upgrade_pip() -> None:
    """Upgrade pip."""
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "pip",
            "--upgrade",
            "--quiet",
        ],
        stdout=subprocess.DEVNULL,
        check=True,
    )
