import json
from itertools import chain
from os import PathLike
from pathlib import Path
from shlex import quote
from typing import Any, Dict, Iterable, List, Tuple

import click
from metaflow.exception import MetaflowException

Config = Dict[str, Any]


class MetaflowConfigNotFound(MetaflowException):  # noqa: D
    headline = "Config file not found"

    def __init__(self, name):  # noqa: D
        msg = "*%s*" % name
        super().__init__(msg)


@click.group()
def cli_custom(ctx):
    """Plugin CLI group."""
    pass


@cli_custom.command(help="Custom command")
@click.argument("config-path")
@click.option("--key", default=None, help="Key in `config-path`")
@click.pass_context
def run_config(ctx, config_path, key):
    """Plugin command: run-config.

    Implementation parses the YAML config, and then calls the main metaflow
    entry-point with the run command.
    This is perhaps a bit hacky but keeps assumptions and code to a minimum
    which will help if Metaflow implementation details change from under us.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise MetaflowConfigNotFound(config_path)

    config = _parse_config(config_path)[key] if key else _parse_config(config_path)

    # XXX: Hack to avoid double
    #      "Metaflow <version> executing <flow_name> for user:<user>"
    _erase_last_output_line()

    # Import must be encapsulated to avoid partial imports
    from metaflow.cli import start

    start.main(
        [
            *_parse_options(config["preflow_kwargs"]),
            "run",
            *_parse_options(config["flow_kwargs"]),
            *_add_run_id(config_path, key),  # TODO: what about key
            # TODO: add run-id-file
        ],
        obj=ctx.obj,
        auto_envvar_prefix="METAFLOW",
    )


def _add_run_id(config_path: Path, key=None) -> Tuple[str, str]:
    run_id_path = config_path.with_suffix(".run_id")
    if key:
        run_id_path = run_id_path.with_name(f"{run_id_path.stem}_{key}.run_id")
    return ("--run-id-file", str(run_id_path))


def _parse_config(path: PathLike) -> Config:
    # Import needs to be encapsulated to avoid running in task-time
    # environments without the package installed
    import yaml

    return yaml.safe_load(Path(path).open())


def _serialise(x: Any) -> str:
    """Serialise `x` to `str` falling back on JSON."""
    if isinstance(x, str):
        return x
    if isinstance(x, Path):
        return str(x)
    else:
        return json.dumps(x)


def _parse_options(options: Tuple[Dict[str, Any], List[str]]) -> Iterable[str]:
    r"""Parse and quote `options` to be passed to metaflow.

    ```
    ({"foo": {"data": [1.2, 3, "4"]}}, "bar")
     =>
     '--foo', '\'{"data": [1.2, 3, "4"]}\'', '--bar'
    ```

    Args:
        options: Two-tuple of options to parse and quote.
                 First item is a dictionary of key-value pairs.
                 Second item is a list of flags

    Returns:
        Iterable of command-line arguments.
    """
    params, flags = options

    parsed_params = chain.from_iterable(
        (f"--{k}", _serialise(v)) for k, v in params.items()
    )
    parsed_flags = (f"--{k}" for k in flags)
    return map(quote, [*parsed_params, *parsed_flags])


ERASE_LAST_LINE = "\033[F"
ERASE_TO_EOL = "\033[K"


def _erase_last_output_line():
    """Remove last line of terminal output."""
    click.secho(f"{ERASE_LAST_LINE}{ERASE_TO_EOL}", nl=False)
