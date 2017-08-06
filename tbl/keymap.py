"""
Mapping from key combos to commands

A key map is a mapping from keys or key combos to command names.  The keys may
be single key codes, or sequence of key codes for key combos.  The values are
commands.  A value of `PREFIX` indicates a prefix key; each prefix of a a key
combo must be tagged as a prefix in this way.
"""

#-------------------------------------------------------------------------------

from   functools import partial

from   . import commands, controller, io, model, view
from   . import screen as scr

#-------------------------------------------------------------------------------

PREFIX = object()

def build_key_map(key_map):
    # Convert single character keys to tuples, as a convenience.
    key_map = {
        (k, ) if isinstance(k, str) else tuple( str(s) for s in k ): v
        for k, v in key_map.items()
    }

    # Check prefixes.
    for combo in [ k for k in key_map if len(k) > 1 ]:
        prefix = combo[: -1]
        while len(prefix) > 1:
            if key_map.setdefault(prefix, None) is not PREFIX:
                raise ValueError(
                    "combo {} but not prefix {}".format(combo, prefix))
            prefix = prefix[: -1]
            
    return key_map


def get_default():
    """
    Returns the default key map.
    """
    return build_key_map({
        "LEFT"          : "move-left",
        "RIGHT"         : "move-right",
        "UP"            : "move-up",
        "DOWN"          : "move-down",
        "S-LEFT"        : "scroll-left",
        "S-RIGHT"       : "scroll-right",

        "C-b"           : "move-left",   # back
        "C-f"           : "move-right",  # forward
        "C-k"           : "delete-row",
        "C-p"           : "move-up",     # previous
        "C-n"           : "move-down",   # next
        "C-x"           : PREFIX,
        ("C-x", "C-s")  : "save",
        ("C-x", "C-w")  : "save-as",
        "C-z"           : "undo",

        "M-#"           : "toggle-show-row-num",
        "M-x"           : "command",

        "q"             : "quit",
    })


