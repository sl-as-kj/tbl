from   collections import namedtuple
import inspect
import logging

#-------------------------------------------------------------------------------

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

def bind_args(fn, args, input):
    # Got a key binding.  Bind arguments by name.
    sig = inspect.signature(fn)
    args = { 
        k: v 
        for k, v in args.items() 
        if k in sig.parameters 
    }

    # For each parameter, prompt for input.
    for name, prompt in get_params(fn):
        args[name] = input(prompt)

    return args


#-------------------------------------------------------------------------------

def cmd_quit():
    raise KeyboardInterrupt()


