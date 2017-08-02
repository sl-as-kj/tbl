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

def check_key_map(key_map):
    # Convert single character keys to tuples, for convenience.
    key_map = {
        (k, ) if isinstance(k, str) else tuple( str(s) for s in k ): v
        for k, v in key_map.items()
    }

    # Check prefixes.
    for combo in [ k for k in key_map if len(k) > 1 ]:
        prefix = combo[: -1]
        while len(prefix) > 1:
            if key_map.setdefault(prefix, None) is not None:
                raise ValueError(
                    "combo {} but not prefix {}".format(combo, prefix))
            prefix = prefix[: -1]
            
    return key_map


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


