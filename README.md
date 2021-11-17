# metaflow_extensions (Nesta)

Nesta's plugins for [Metaflow](metaflow.org).

## Install

`pip install git+https://github.com/nestauk/metaflow_extensions`

## Functionality

### Package environment

New default Metaflow environment that adds your project to a Metaflow job package and installs it for each step.

:exclamation: **You do not need to change your flow code,** your code _should_ just work on Batch/Conda like it does locally (subject to other Metaflow settings such `package-suffixes` being sensibly set).

#### Problem

Consider the following directory structure,

```tree
.
├── myproject
│   ├── flows
│   │   └── flow.py
│   ├── utils.py
│   └── __init__.py
└── setup.py
```

and the following flow,

```python
class MyFlow(FlowSpec):
    @step
    def start(self):
        from myproject.utils import super_useful_function
        self.next(self.end)
    @step
    def end(self):
        pass
```

With the normal Metaflow environment (`--environment local`) and not running on AWS this flow works (if `myproject` is pip-installed in your local environment).

With the Conda Metaflow environment (`--environment conda`) and/or running on AWS (`--with batch`) then this flow will fail because the tasktime environment has no to import `myproject` because:

1. On AWS, only files adjacent or below `flow.py` are added to the job package - i.e. `setup.py`, `myproject/__init__.py`, and `myproject/utils.py` don't exist on the AWS machine.
2. On AWS and/or a Conda environment, then `myproject` isn't installed.

#### Solution / usage

Having `metaflow_extensions` installed activates the "project" environment (`metaflow_extensions.plugins.project_environment.ProjectEnvironment`).
This environment:

1. Adds your project to the job package.
2. Automatically adds a decorator that installs your project to each step of your flow.

:bulb: **Tip:** To check what files are being added to the metaflow job package you can run `$python path/to/flow.py package list`

### `run-config` CLI command

New CLI command letting you configure a flow from a YAML file rather than at the command-line.

#### Problem solved

- Make different easy-to-use "profiles", e.g. `dev` for iterating quickly on a local machine, and `prod` for running in production.
- Less risk of incorrectly escaping string sequences on the command line
- YAML config makes it easier for collaborators to know what commands should be run because it's not one long line, and allows comments.

#### Usage

Instead of this:
`python path/to/flow.py --no-pylint --environment conda run --my-json-param '{"key": 2}' --with batch:cpu=10`

You can do this:
`python path/to/flow.py run-config path/to/config.yaml --key dev` to run the `dev` profile,
`python path/to/flow.py run-config path/to/config.yaml --key prod` to run the `prod` profile.

```yaml
# file: path/to/config.yaml
dev:
  preflow_kwargs:
    - datastore: local # faster locally because no overhead of talking to S3
      metadata: local
      monitor: debugMonitor
    - ["no-pylint"]
  flow_kwargs:
    - my-json-param: { key: 1 }
    - []
prod:
  preflow_kwargs:
    - environment: conda
    - ["no-pylint"]
  flow_kwargs:
    - my-json-param: { key: 2 }
      with: "batch:cpu=10"
      namespace: production
    - ["no-test-mode"]
```

You can even use YAML anchors (`&anchor_name`) and merge keys (`<<: *anchor_name`) to reduce repetition across profiles,

```yaml
dev:
  preflow_kwargs:
    - &dev-pre # Create YAML anchor for this array
      datastore: local # faster locally because no overhead of talking to S3
      metadata: local
      monitor: debugMonitor
    - []
  flow_kwargs: &dev-flow
    - my-json-param: { key: 1 }
    - []
prod:
  preflow_kwargs:
    - <<: *dev-pre # Merge anchor (re-use datastore, metadata, monitor set in dev-pre)
      datastore: s3 # Over-ride datastore set in dev-pre
    - []
  flow_kwargs: *dev-flow # Re-use flow_kwargs from dev
```

### Different default Settings

See `metaflow_extensions.config.metaflow_config.py` for details.

List of things changed:

- Default environment
- Default package suffixes

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

Metaflow looks for a package called `metaflow_extensions`.

`metaflow_extensions.config.metaflow_config` overrides `metaflow.metaflow_config`.

`metaflow_extensions.plugins` are available as metaflow imports by defining: `FLOW_DECORATORS`, `STEP_DECORATORS`, `ENVIRONMENTS`, `METADATA_PROVIDERS`, `SIDECARS`, `LOGGING_SIDECARS`, `MONITOR_SIDECARS`, and `get_plugin_cli()`.

(source: https://gitter.im/metaflow_org/community?at=5f99d01ec6fe0131d4bfea36)

This mechanism is current undocumented and is not stable but changes shouldn't be too hard to maintain.
