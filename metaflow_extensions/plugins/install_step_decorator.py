"""Implements a step decorator to install a project package if not running locally.

Implementation notes:
- StepDecorator.task_pre_step runs just before a step begins executing in the
  tasktime environment (not the runtime environment) - e.g. the function will
  run on batch, not on the machine orchestrating the batch run.
- Flow path is used as a starting point to search for a directory containing a
  file in `METAFLOW_PROJECT_FILES`. It is inferred by inspecting the arguments
  to the current process, the first argument being the flow path.
- `fail_loudly` defaults to false because ProjectEnvironment adds it to
  every step, and as ProjectEnvironment is intended to replace the
  default environment, we may not always be in a project context.
"""
from metaflow.decorators import StepDecorator

from metaflow_extensions.utils import (
    install_flow_project,
    is_task_running_in_local_env,
)


class InstallProjectStepDecorator(StepDecorator):
    """Step decorator to install project package if not running locally.

    To use, add this decorator to your step:
    ```python
    @install_project
    @step
    def MyStep(self):
        ...
    ```

    Project package is defined as the closest folder adjacent or above the
    executing flow containing a file in
    `metaflow_extensions.config.metaflow_config.PROJECT_FILES`.

    Parameters:
        fail_loudly (bool): If True, then fail if a project package couldn't
                            be found. Defaults to False.
    """

    name = "install_project"

    defaults = {"fail_loudly": False}

    def task_pre_step(self, *args):
        """If not running locally, install project package if one exists."""
        if is_task_running_in_local_env():
            return
        project_root = install_flow_project()
        if not project_root and self.attributes["fail_loudly"]:
            raise FileNotFoundError(
                f"Could not find pip-installable file @ {project_root}"
            )
