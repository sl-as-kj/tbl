"""
Command interface

A command is a function whose name starts with `cmd_.` It may have any of these
named parameters:

- `mdl` - the model
- `ctl` - the controller
- `vw`  - the view
- `scr` - the screen
- `arg` - the argument to the UI event

A command may declare additional user-specified parameters using the `param`
decorator.  When the command is executed, the user is prompted for values for
these parameters.  Any other function arguments must be bound.

For example, this command operates on the model, and an additional argument
named "data":

    ```
    @param("name", "column name")
    def rename(mdl, name):
        ...
    ``` 

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
import inspect
import logging

__all__ = (
    "CmdError",
    "CmdResult",
    "command",
    "run",
)

#-------------------------------------------------------------------------------

class CmdError(Exception):

    pass



class InputInterrupt(Exception):

    pass



#-------------------------------------------------------------------------------

class Command:

    def __init__(self, name, fn, params):
        self.name   = name
        self.fn     = fn
        self.params = params


    def __call__(self, args):
        result = self.fn(**args)
        if result is None:
            result = CmdResult()
        return result



commands = {}

def command(name=None):
    assert not callable(name), "you probably meant @command()"

    def register(fn):
        params = tuple(inspect.signature(fn).parameters)

        nonlocal name
        if name is None:
            name = fn.__name__.replace("_", "-")
        if name in commands:
            raise ValueError("command name {} already used".format(name))

        commands[name] = Command(name, fn, params)

    return register


#-------------------------------------------------------------------------------

class CmdResult:

    def __init__(self, *, msg=None):
        self.msg = msg



def run(cmd_name, args, input):
    try:
        cmd = commands[cmd_name]
    except KeyError:
        raise CmdError("unknown command: {}".format(cmd_name))

    # Trim down arguments to those that are parameters of the command.
    args = { n: v for n, v in args.items() if n in cmd.params }
    # Prompt for any additional parameters.
    for param in cmd.params:
        if param not in args:
            prompt = "{} {}: ".format(cmd.name, param)
            args[param] = input(prompt)

    return cmd(args)


#-------------------------------------------------------------------------------

@command()
def quit():
    raise SystemExit(0)


