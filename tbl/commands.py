"""
Command interface

Commands are named, user-accessible operations.  To create a command, decorate a
function with the `@command()` decorator.  The name of the command is
constructed from the function name.

The function may take any of these arguments:

  - `mdl` -- the model
  - `ctl` -- the controller
  - `vw`  -- the view
  - `scr` -- the screen
  - `arg` -- the argument to the UI event

A command have additional parameters; when the command is executed, the user is
prompted for values for these.

For example, this command operates on the model, and an additional argument
named "name":

    ```
    @command()
    def rename(mdl, name):
        ...
    ``` 

The command should perform the appropriate action, and may,

1. Return `CmdResult` to indicate success.  The result object may optionally
   carry a status message to show to the user, and an undo function (of no
   arguments) to add to the undo stack.

1. Return of `None`.  This is treated as a default `CmdResult`.

1. Raise `CmdError`to indicate failure.

To bind a command to a key or key combo, see the `keymap` module.
"""

#-------------------------------------------------------------------------------

import inspect
import logging

__all__ = (
    "CmdError",
    "CmdResult",
    "command",
    "run",
)

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
        assert isinstance(result, CmdResult)
        return result



commands = {}

def command():
    def register(fn):
        params = tuple(inspect.signature(fn).parameters)

        name = fn.__name__.replace("_", "-")
        if name in commands:
            raise ValueError("command name {} already used".format(name))

        commands[name] = Command(name, fn, params)

    return register


#-------------------------------------------------------------------------------

class CmdError(Exception):

    pass



class CmdResult:

    def __init__(self, *, msg=None):
        self.msg = msg


    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.msg)



def run(cmd_name, args, input):
    """
    Runs a command.

    @param args
      Mapping of arguments available for binding to command parameters.  Not
      all arguments must be used.
    @param input
      Function to obtaining arguments for other parameters.  Takes a prompt
      string and returns an argument string.
    """
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
    # FIXME: Confirm if dirty.
    raise KeyboardInterrupt


