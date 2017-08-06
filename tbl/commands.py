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

    def __init__(self, *, msg=None, undo=None):
        self.msg = msg
        self.undo = undo



#-------------------------------------------------------------------------------

def cmd_quit():
    raise KeyboardInterrupt()


