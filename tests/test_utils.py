import sys
from pathlib import Path
from uuid import uuid4

import pytest

from metaflow_custom.utils import (
    has_project_file,
    is_path_hidden,
    running_in_local_env,
    up_to_project_root,
    walk,
    zip_stripped_root,
)
from tests.conftest import MYPROJECT_PATH


NONEXISTENT_PATH = Path(f"/{uuid4()}/foo/bar/baz")


def test_has_project_file():
    assert has_project_file(MYPROJECT_PATH)
    assert not has_project_file(NONEXISTENT_PATH)


def test_up_to_project_root():
    assert up_to_project_root(MYPROJECT_PATH / "myproject") == MYPROJECT_PATH
    assert up_to_project_root(NONEXISTENT_PATH) is None


def test_walk():
    expected_files_rel = [
        "setup.py",
        "myproject/__init__.py",
        "myproject/flows/flow.py",
    ]
    expected_files_abs = set(str(MYPROJECT_PATH / file) for file in expected_files_rel)
    actual_files = set(walk(MYPROJECT_PATH, [".py"]))

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
    "root,strip_paths",
    [
        ("/prefix", ["/ab", "a"]),
        ("", ["/ab", "a"]),
        ("/", ["/ab", "a"]),
    ],
)
def test_zip_stripped_root(root, strip_paths):
    paths = list(map(lambda p: root + p, strip_paths))
    result = list(zip_stripped_root(root, paths))
    assert result == list(zip(paths, strip_paths))


@pytest.mark.parametrize(
    "argv,is_local",
    [
        (["file", "conda"], False),
        (["file", "batch"], False),
        (["file", "conda:stuff"], False),
        (["file", "batch:stuff"], False),
        (["file", "prefix:conda"], True),
        (["file", "prefix:batch"], True),
    ],
)
def test_running_in_local_env(argv, is_local):
    tmp = sys.argv.copy()
    try:
        sys.argv = argv
        assert running_in_local_env() is is_local
    finally:
        sys.argv = tmp
