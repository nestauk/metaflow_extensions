# metaflow_extensions (Nesta)

Nesta's plugins for [Metaflow](metaflow.org).

## Install

`pip install git+https://github.com/nestauk/metaflow_extensions`

## Use-cases

### "I want to re-use utilities from a parent folder when using Conda/Batch"

For example, say you have the following module structure,

```
myproject
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

As of [Metaflow `2.5.2`](https://github.com/Netflix/metaflow/releases/tag/2.5.2), Metaflow follows [symlinks](https://en.wikipedia.org/wiki/Symbolic_link) when creating code packages.
Running `ln -s ../../common/ .` from `pipeline/collect/` will symlink `common/` into that folder meaning that Metaflow will package `common/`, making it importable from the flows in `pipeline/collect/`.
Use this built-in functionality to achieve this use case!
(For Metaflow `<2.5`, `metaflow_extensions<=0.2` provided the `project` environment for making `common/` available in a remote compute environment - this has since been removed)

:bulb: **Tip:** To check what files are being added to the metaflow job package you can run `$python path/to/flow.py package list`

#### My common utilities have dependencies I need to install

Use symlinking (e.g. `ln -s ../../../myproject pkg` from the flow directory) in combination with [`@pip`](#TODO), e.g. by decorating a flow step with `@pip(path=step_requirements.txt)` where `step_requirements.txt` contains `-e pkg/`

Note: If you are running on your local machine but not using `--environment conda` then you can skip using `@pip` because you can install your project package in your development environment yourself.

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

`@pip` executes the underlying `pip` commands from the flow directory to avoid inconsistent behaviour based on where a flow is executed from.

### "I want to install something on a Batch machine that isn't available via. pip or Conda but I don't want to build and maintain my own Docker image"

The `preinstall` environment provided by this library enables you to do this!

Enable it by adding `--environment preinstall` when you run a Metaflow (If using `conda` as well you will need to set the environment variable `METAFLOW_DEFAULT_ENVIRONMENT` to `preinstall`).

Specifically named files in the flow directory are run in remote compute environments such as AWS Batch before the flow file begins executing:

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

Some documentation on the extension mechanism can be found at https://github.com/Netflix/metaflow-extensions-template.

The metaflow extensions mechanism is not currently public or stable, therefore additions to this library should only be made out of necessity and kept as simple as possible!
