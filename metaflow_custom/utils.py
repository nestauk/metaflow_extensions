import sys


def running_in_local_env() -> bool:
    """True if runtime environment is/will be the same as task-time environment."""
    return not any(
        arg.startswith("batch") or arg.startswith("conda") for arg in sys.argv
    )
