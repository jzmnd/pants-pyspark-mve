"""Plugin to create custom kwargs for `python_artifact()` for use in setup.py"""
from user.python.releaser import gitversion, setupkwargs


def rules():
    return [*gitversion.rules(), *setupkwargs.rules()]
