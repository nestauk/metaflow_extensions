# metaflow_custom (Nesta)

Nesta's plugins for [Metaflow](metaflow.org).

## Install

`pip install git+https://github.com/nestauk/metaflow_custom`

## Functionality

## For contributors

### Setup

- Install Anaconda (with conda forge enabled)
- Install local package and dev requirements: `pip install -e . -r requirements.txt`
- Install pre-commit hooks: `pre-commit install --install-hooks`

### Tests

- Run local tests with `pytest`
- Run AWS tests with `pytest -m aws` (requires relevant metaflow configuration)
- Run all tests with `pytest -m ""`

### How the metaflow extension mechanism works

Metaflow looks for a package called `metaflow_custom`.

`metaflow_custom.config.metaflow_config` overrides `metaflow.metaflow_config`.

`metaflow_custom.plugins` are available as metaflow imports by defining: `FLOW_DECORATORS`, `STEP_DECORATORS`, `ENVIRONMENTS`, `METADATA_PROVIDERS`, `SIDECARS`, `LOGGING_SIDECARS`, `MONITOR_SIDECARS`, and `get_plugin_cli()`.

(source: https://gitter.im/metaflow_org/community?at=5f99d01ec6fe0131d4bfea36)

This mechanism is current undocumented and is not stable but changes shouldn't be too hard to maintain.
