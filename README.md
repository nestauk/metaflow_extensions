# metaflow_extensions (Nesta)

Nesta's plugins for [Metaflow](metaflow.org).

## Install

`pip install git+https://github.com/nestauk/metaflow_extensions`

## Use-cases

### "I want to re-use utilities from a parent folder when using Conda/Batch"

For example, say you have the following module structure,

```
├── setup.py
├── common/
│   ├── __init__.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── collections.py
│   │   └── aws.py
│   └── foo/
│       ├── __init__.py
│       └── bar.py
└── pipeline/
    ├── collect/
    │   ├── flow_1.py
    │   ├── ...
    │   ├── flow_N.py
    │   └── requirements.txt
    ├── extract/
    │   ├── flow_1.py
    │   ├── ...
    │   ├── flow_N.py
    │   └── requirements.txt
    └── enrich/
        ├── flow_1.py
        ├── ...
        ├── flow_N.py
        └── requirements.txt
```

and each flow needs access to `common`,

```python
# collect/flow_i.py
class MyFlow(FlowSpec):
    @step
    def start(self):
        from common.utils.aws import super_useful_function

        super_useful_function()
        self.next(self.end)
    @step
    def end(self):
        pass
```

With the normal Metaflow environment (`--environment local` - the default) and not running on a remote compute environment like AWS Batch this flow works (if `common` is pip-installed in your local environment or in your `PYTHONPATH` with any dependencies installed).

With the Conda Metaflow environment (`--environment conda`) and/or running on a remote compute environment like AWS Batch (`--with batch` or `@batch`) then this flow will fail because the tasktime environment (the environment running a single Metaflow step in an isolated conda environment and/or on AWS) has no ability to import `common` because:

1. On AWS, only files adjacent or below `flow_i.py` are added to the job package - it would look like

   ```
    .
    │ # Siblings/children of the flow):
    ├── flow_1.py
    ├── ...
    ├── flow_N.py
    ├── requirements.txt
    │ # Added by Metaflow:
    ├── metaflow_extensions/
    ├── metaflow/
    └── INFO
   ```

   i.e. top-level files such as `setup.py` and `common/` aren't there!

2. On AWS and/or with `--environment conda`, then even if the files were present then `common` isn't installed or on your `PYTHONPATH`.

This libraries' `project` environment solves this problem, you can use it by adding `--environment project` when you run a Metaflow (If using `conda` as well you will need to set the environment variable `METAFLOW_DEFAULT_ENVIRONMENT` to `project`).

When creating a job package, `project` environment will search the parent folders of your flow for a "project root file" - either a `setup.py` or `pyproject.toml` file (you can configure what files it looks for by setting `METAFLOW_PROJECT_FILES` to be a comma-delimited list of files to look for).
If a project root file is found then sibling/children of the project root file (that match `--package-suffixes`) will be added to the job package.

:warning: **Careful:** Files may conflict! E.g. if there is a `requirements.txt` file at the top-level of your project and at the level of your flow, these will conflict!

For example, your code package will look like,

```
.
│ # Siblings/children of the flow:
├── flow_1.py
├── ...
├── flow_N.py
├── requirements.txt # Filename clash! This comes from the flow-level
│ # Added by Metaflow:
├── metaflow_extensions/
├── metaflow/
├── INFO
│ # Siblings/children of the project root file (Added by project environment):
├── setup.py  # Finding this project root file determined what was packaged
├── requirements.txt # Filename clash! This comes from the top-level
├── common/
│   ├── __init__.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── collections.py
│   │   └── aws.py
│   └── foo/
│       ├── __init__.py
│       └── bar.py
└── pipeline/
    ├── ...
```

:bulb: **Tip:** To check what files are being added to the metaflow job package you can run `$python path/to/flow.py package list`

#### My common utilities have dependencies I need to install

Use `project` environment in combination with [`@pip`](#TODO), e.g. by decorating a flow step with `@pip(path=step_requirements.txt)` where `step_requirements.txt` is just `.` to indicate installing at the local directory.

:warning: **Gotchas**:

- When running on your local machine you must run a flow from the directory of your project root file in order for the `.` in `requirements.txt` to install your project!
- If you are running on your local machine but not using `--environment conda` then you can skip using `@pip` because you can install your project package in your development environment yourself. Not skipping this may cause inconsistencies in your environment.

### "I want to install a dependency with pip because it isn't available with Conda"

Use the step decorator `@pip` which can be imported as `from metaflow import pip`.

It is used used similarly to Metaflow's built-in `@conda` decorator.

```python
@pip(path="requirements.txt")
@step
def MyStep(self):
    ...

@pip(libraries={"tqdm": ">1.0.1"})
@step
def MyNextStep(self):
    ...
```

You can read the documentation by either:

1. Reading the [docstrings in the source](metaflow_extensions/plugins/pip_step_decorator.py)
2. `from metaflow import pip; help(pip.args[0])` - Metaflow partially applies decorators which makes accessing docs a little harder.

### "I want to install something on a Batch machine that isn't available via. pip or Conda but I don't want to build and maintain my own Docker image"

The `project` environment has another trick up it's sleeve - preinstall scripts!

Specifically named files in the flow directory (or at the project file level) are run in remote compute environments such as AWS Batch before the flow file begins executing:

- `preinstall.sh` - Will run regardless of flow and step
- `preinstall-<flow name>.sh` - Will run for flow named `<flow name>`
- `preinstall-<flow name>-<step name>.sh` - Will run for flow named `<flow name>` and step named `<step name>`

The bash environment variable `MFPYTHON` is set to the python binary that will be used to execute a flow, this allows e.g. the pre-installation of Python dependencies required at the top-level to provide functionality such as mixins:

`$MFPYTHON -m pip install daps_utils@git+https://github.com/nestauk/daps_utils@dev --quiet 1> /dev/null`

## Examples

Look at `tests/myproject` for some examples.

## For contributors

### Setup

- Install Anaconda (with conda forge enabled)
- Install local package and dev requirements: `pip install -e . -r requirements.txt`
- Install pre-commit hooks: `pre-commit install --install-hooks`

(Look at `.github/workflows/test.yml` if stuck)

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
