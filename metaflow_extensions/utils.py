"""Utility functions."""
import logging
import os
import platform
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Tuple, Union


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
    path = Path(path)
    return any(part.startswith(".") for part in path.parts)


def zip_stripped_root(
    root: os.PathLike, paths: Iterable[str]
) -> Iterator[Tuple[str, str]]:
    """Return tuples of path and path with `root` stripped for paths in `path`."""
    return map(
        lambda item: (item, str(Path("pkg_self") / Path(item).relative_to(root))), paths
    )


def is_mflow_conda_environment() -> bool:
    """True if current process is a Metaflow Conda environment."""
    from metaflow.metaflow_config import DEFAULT_ENVIRONMENT

    joined_argv = " ".join(sys.argv)
    return (
        DEFAULT_ENVIRONMENT == "conda"
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
        "--quiet",
        *map(shlex.quote, args),
        stdout=subprocess.DEVNULL,
    )


def local_pip_install(project_path: Path, executable: str = sys.executable) -> None:
    """`pip install` local package at `project_path`."""
    pip_install(executable, str(project_path))


def upgrade_pip(executable: str = sys.executable) -> None:
    """Upgrade pip."""
    pip_install(executable, "pip", "--upgrade")


def _parse_pkg_spec(pkg_details: str) -> Tuple[Optional[str], Optional[str]]:
    """Determine package name and package spec from the output of pip freeze.

    For example:
       * foo @ git+https://path/to/foo.git -> foo, git+https://path/to/foo.git
       * foo==1.2.3                        -> foo, foo==1.2.3

    Arguments:
        pkg_details: A single line of output from pip freeze.

    Returns:
        Tuple containing package name and package spec.
    """
    pkg_name, pkg_spec = None, None
    # First format: foo @ git+https://path/to/foo.git
    try:
        pkg_name, pkg_spec = pkg_details.split(" @ ")
    except ValueError:
        pass
    # Second format: foo==1.2.3
    try:
        pkg_name, _ = pkg_details.split("==")
        pkg_spec = pkg_details
    except ValueError:
        # Other format is '-e git+ssh' which are local
        # packages and so can't be supported anyway
        pass
    return pkg_name, pkg_spec


def parse_subprocess_stdout(
    subprocess_output: subprocess.CompletedProcess,
) -> Iterator[str]:
    """Split and decode subprocess output."""
    yield from map(bytes.decode, subprocess_output.stdout.splitlines())


def get_pkg_spec(pkg_name: str) -> Optional[str]:
    """Retrieves the package spec for the local package name, if it exists."""
    subprocess_output = pip(sys.executable, "freeze", capture_output=True)
    pkgs_details = parse_subprocess_stdout(subprocess_output)
    for _pkg_name, pkg_spec in map(_parse_pkg_spec, pkgs_details):
        if _pkg_name == pkg_name:
            return pkg_spec
    return None


def get_conda_envs_directory(subprocess_output: subprocess.CompletedProcess) -> str:
    """Parse the conda environment directory from conda info output."""
    for line in parse_subprocess_stdout(subprocess_output):
        try:
            _, envs_directory = line.split("envs directories : ")
        except ValueError:
            continue
        else:
            return envs_directory
    raise ValueError("Could not parse conda environment directory.")


def get_conda_python_executable(env_id: str) -> str:
    """Resolve the pip for this conda."""
    subprocess_output = subprocess.run(
        ["conda", "info"], check=True, capture_output=True
    )
    envs_directory = get_conda_envs_directory(subprocess_output)
    python_exec = str(Path(envs_directory) / env_id / "bin" / "python")
    return python_exec


def platform_arch_mismatch(env_id: str) -> bool:
    """Determine whether the conda env's arch matches with the local arch."""
    _, _, arch, _ = env_id.split("_")
    if platform.system() == "Linux":
        return not arch.startswith("linux")
    elif platform.system() == "Darwin":
        return not arch.startswith("osx")
    else:
        raise ValueError(f"Platform '{platform.system()}' is not supported")


def install_flow_project(executable: str = sys.executable) -> Optional[Path]:
    """Install the project corresponding to the currently running flow."""
    flow_path = Path(sys.argv[0])
    project_root = up_to_project_root(flow_path)
    if project_root:
        upgrade_pip(executable)  # Need newer features for install step
        local_pip_install(project_root, executable)
    return project_root
