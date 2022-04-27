"""Test utility functions."""
import sys
from unittest import mock

import pytest

from metaflow_extensions.utils import is_mflow_conda_environment, pip_install


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
        # "--quiet",
        *out_args,
    )
