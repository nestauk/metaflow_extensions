import sys
from pathlib import Path
from unittest import mock
from uuid import uuid4

import pytest

from metaflow_extensions.utils import (
    _parse_pkg_spec,
    get_conda_envs_directory,
    get_conda_python_executable,
    get_pkg_spec,
    has_project_file,
    is_mflow_conda_environment,
    is_path_hidden,
    parse_subprocess_stdout,
    pip_install,
    platform_arch_mismatch,
    up_to_project_root,
    walk,
    zip_stripped_root,
)
from tests.conftest import MYPROJECT_PATH

from utils import ch_dir, env  # noqa: I

NONEXISTENT_PATH = Path(f"/{uuid4()}/foo/bar/baz")


def test_has_project_file():
    assert has_project_file(MYPROJECT_PATH)
    assert not has_project_file(NONEXISTENT_PATH)


def test_up_to_project_root_absolute(tmp_path):
    assert up_to_project_root(MYPROJECT_PATH / "myproject") == MYPROJECT_PATH
    assert up_to_project_root(NONEXISTENT_PATH) is None


def test_up_to_project_root_relative(tmp_path):
    with ch_dir(tmp_path):
        assert not up_to_project_root(Path("."))

    myproject_path_relative = MYPROJECT_PATH.relative_to(Path.cwd())
    assert up_to_project_root(myproject_path_relative / "myproject") == MYPROJECT_PATH


def test_walk():
    expected_files_rel = [
        "setup.py",
        "myproject/__init__.py",
        "myproject/__initplus__.py",
        "myproject/flows/flow.py",
        "myproject/flows/batch_flow.py",
        "myproject/flows/batch_flow_with_conda.py",
        "myproject/flows/pip_flow_conda.py",
        "myproject/flows/requirements.txt",
    ]
    expected_files_abs = set(str(MYPROJECT_PATH / file) for file in expected_files_rel)
    actual_files = set(walk(MYPROJECT_PATH, [".py", ".txt"]))
    print(actual_files)
    assert len(actual_files ^ expected_files_abs) == 0


@pytest.mark.parametrize(
    "path,is_hidden",
    [
        (".hidden", True),
        ("not_hidden", False),
        ("/foo/.bar/baz.ext", True),
        ("foo/bar/baz.ext", False),
        ("/", False),
    ],
)
def test_is_path_hidden(path, is_hidden):
    assert is_path_hidden(path) is is_hidden


@pytest.mark.parametrize(
    "root,paths,strip_paths",
    [
        ("/prefix", ["/prefix/ab", "/prefix/a"], ["pkg_self/ab", "pkg_self/a"]),
        ("", ["ab", "a"], ["pkg_self/ab", "pkg_self/a"]),
        ("/", ["/ab", "/a"], ["pkg_self/ab", "pkg_self/a"]),
    ],
)
def test_zip_stripped_root(root, paths, strip_paths):
    result = list(zip_stripped_root(root, paths))
    assert result == list(zip(paths, strip_paths))


@pytest.mark.parametrize(
    "argv,default_env,is_conda",
    [
        # True
        (["file", "--environment", "conda"], "local", True),
        (["file", "--with", "conda"], "local", True),
        (["file", "run"], "conda", True),
        # False
        (["file", "conda"], "local", False),
        (["file", "batch"], "local", False),
        (["file", "conda:stuff"], "local", False),
        (["file", "batch:stuff"], "local", False),
        (["file", "--environment", "other"], "local", False),
    ],
)
def test_is_mflow_conda_environment(argv, default_env, is_conda):
    tmp = sys.argv.copy()
    with mock.patch("metaflow.metaflow_config.DEFAULT_ENVIRONMENT", default_env):
        try:
            sys.argv = argv
            assert is_mflow_conda_environment() is is_conda
        finally:
            sys.argv = tmp


@pytest.mark.ci_only
def test_get_pkg_spec():
    pkg_spec = get_pkg_spec("daps-utils")
    git_path, _hash = pkg_spec.split("@")
    assert git_path.endswith(
        "nestauk/daps_utils"
    )  # different forms depending on git/https scheme
    assert len(_hash) == 40


def test_daps_utils_spec_daps_utils_not_installed():
    assert get_pkg_spec("something-that-doesnt-exist") is None


@pytest.mark.ci_only
def test_get_conda_python_executable():
    python_exec = get_conda_python_executable("foo")
    assert Path(python_exec).exists(), "Make sure conda env 'foo' exists"
    assert python_exec.endswith("/python")


@mock.patch("metaflow_extensions.utils.platform")
@pytest.mark.parametrize(
    "env_id,platform,is_mismatch",
    [
        ("foo_bar_linux32_abcd", "Linux", False),
        ("foo_bar_linux64_abcd", "Linux", False),
        ("foo_bar_osx32_abcd", "Linux", True),
        ("foo_bar_osx64_abcd", "Linux", True),
        ("foo_bar_linux32_abcd", "Darwin", True),
        ("foo_bar_linux64_abcd", "Darwin", True),
        ("foo_bar_osx32_abcd", "Darwin", False),
        ("foo_bar_osx64_abcd", "Darwin", False),
    ],
)
def test_platform_arch_mismatch_linux(mocked_platform, env_id, platform, is_mismatch):
    mocked_platform.system.return_value = platform
    assert platform_arch_mismatch(env_id) == is_mismatch


@pytest.mark.parametrize(
    "platform",
    ["Windows", "MacOS", "ChromeOS", "Foo", "Bar"],
)
@mock.patch("metaflow_extensions.utils.platform")
def test_platform_arch_mismatch_other_system(mocked_platform, platform):
    mocked_platform.system.return_value = platform
    for system in ["foo", "bar", "baz", "linux32", "linux64", "osx32", "osx64"]:
        env_id = f"foo_bar_{system}_abcd"
        with pytest.raises(ValueError):
            platform_arch_mismatch(env_id)


def test_parse_subprocess_stdout():
    subprocess_output = mock.Mock()
    subprocess_output.stdout = b"foo\nbar\nbaz"
    assert list(parse_subprocess_stdout(subprocess_output)) == ["foo", "bar", "baz"]


def test__parse_pkg_spec():
    assert _parse_pkg_spec("foo @ git+https://path/to/foo.git") == (
        "foo",
        "git+https://path/to/foo.git",
    )
    assert _parse_pkg_spec("foo==1.2.3") == ("foo", "foo==1.2.3")


def test_get_conda_envs_directory():
    subprocess_output = mock.Mock()
    subprocess_output.stdout = (
        b"          package cache : /foo/bar/anaconda3/pkgs\n"
        b"                          /foo/bar/.conda/pkgs\n"
        b"       envs directories : /foo/bar/envs\n"
        b"                          /Users/jklinger/.conda/envs\n"
        b"               platform : osx-64"
    )
    assert get_conda_envs_directory(subprocess_output) == "/foo/bar/envs"


@pytest.mark.parametrize(
    "paths,args,out_paths,out_args",
    [
        ("tqdm", (), ("tqdm",), ()),
        ("tqdm==1.2.3", (), ("tqdm==1.2.3",), ()),
        ("tqdm ==1.2.3", (), ("'tqdm ==1.2.3'",), ()),
        (("tqdm ==1.2.3",), (), ("'tqdm ==1.2.3'",), ()),
        (
            ("tqdm ==1.2.3", "uren == 4.5.6"),
            (),
            ("'tqdm ==1.2.3'", "'uren == 4.5.6'"),
            (),
        ),
        (
            ("tqdm ==1.2.3", "uren == 4.5.6"),
            ("--log", "path with space"),
            ("'tqdm ==1.2.3'", "'uren == 4.5.6'"),
            ("--log", "'path with space'"),
        ),
    ],
)
@mock.patch(  # Don't execute subprocess just return input args
    "metaflow_extensions.utils.pip", lambda *pip_args, **subproc_kwargs: pip_args
)
def test_pip_install(paths, args, out_paths, out_args):
    assert pip_install("python", paths, *args)[2:] == (
        *out_paths,
        "--quiet",
        *out_args,
    )
