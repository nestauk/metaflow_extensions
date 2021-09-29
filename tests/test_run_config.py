"""Test functionality of `run-config` CLI command."""
from pathlib import Path

import pytest

from metaflow_custom.plugins.cli import _parse_options, _serialize
from utils import ch_dir, run_config_flow  # noqa: I

flow_name = "{}/myproject/myproject/flows/flow.py".format
config_name = "{}/myproject/myproject/flow_config.yaml".format


def test_runs_locally(temporary_installed_project):
    """`flow.py` should run without `metaflow_custom` if `myproject` pip installed."""
    with ch_dir(temporary_installed_project / "myproject"):
        run_config_flow(
            flow_name(temporary_installed_project),
            config_name(temporary_installed_project),
        )


@pytest.mark.parametrize(
    "options,result",
    [
        (
            ({"foo": {"data": [1.2, 3, "4"]}}, "bar"),
            ["--foo", '\'{"data": [1.2, 3, "4"]}\'', "-b", "-a", "-r"],
        ),
        (
            ({"foo": {"data": [1.2, 3, "4"]}}, ["bar"]),
            ["--foo", '\'{"data": [1.2, 3, "4"]}\'', "--bar"],
        ),
        (({}, []), []),
    ],
)
def test_parse_options(options, result):
    assert list(_parse_options(options)) == result


@pytest.mark.parametrize(
    "obj,result",
    [
        ("identity string", "identity string"),
        (Path("/home"), "/home"),
        ({"Key": 2}, '{"Key": 2}'),
        (None, ""),
    ],
)
def test_serialize(obj, result):
    assert _serialize(obj) == result


@pytest.mark.parametrize(
    "obj",
    [
        object,
        {0: Path()},
    ],
)
def test_serialize_error(obj):
    with pytest.raises(TypeError):
        _serialize(obj)
