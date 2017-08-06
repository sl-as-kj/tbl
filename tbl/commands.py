"""
Command interface

A command is a function whose name starts with `cmd_.` It may have any of these
named parameters:

- `mdl` - the model
- `ctl` - the controller
- `vw`  - the view
- `scr` - the screen
- `arg` - the argument to the UI event

If any other parameters are unbound, the user will be prompted for (string)
values for each, before invoking the command.

The command should perform the appropriate action, and may either,

1. Return `CmdResult` to indicate success.  The result object may optionally
   carry a status message to show to the user, and an undo function (of no
   arguments) to add to the undo stack.

   A return of `None` is treated as a default `CmdResult`.

1. Raise `CmdError`to indicate failure.

To bind a command to a key or key combo, see the `keymap` module.
"""

#-------------------------------------------------------------------------------

from   collections import namedtuple
import logging

__all__ = (
    "CmdError",
    "CmdResult",
)

#-------------------------------------------------------------------------------

class CmdError(Exception):

    pass



class InputInterrupt(Exception):

    pass



#-------------------------------------------------------------------------------

Param = namedtuple("Param", ("name", "prompt"))

def param(name, prompt):
    def wrapper(fn):
        try:
            params = fn.__params__
        except AttributeError:
            params = fn.__params__ = []
        params.append(Param(name, prompt))
        return fn

    return wrapper


def get_params(fn):
    return getattr(fn, "__params__", [])


#-------------------------------------------------------------------------------

class CmdResult:

    def __init__(self, *, msg=None):
        self.msg = msg



#-------------------------------------------------------------------------------

def cmd_quit():
    raise KeyboardInterrupt()


