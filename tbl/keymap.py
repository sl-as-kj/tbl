from   functools import partial

from   . import commands
from   . import model as mdl
from   . import screen as scr
from   . import view

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


def get_default():
    return check_key_map({
        "LEFT"          : partial(view.move_cur, dc=-1),
        "RIGHT"         : partial(view.move_cur, dc=+1),
        "UP"            : partial(view.move_cur, dr=-1),
        "DOWN"          : partial(view.move_cur, dr=+1),
        "LEFTCLICK"     : lambda arg, vw: view.move_cur_to(vw, arg[0], arg[1]),
        "S-LEFT"        : partial(view.scroll, dx=-1),
        "S-RIGHT"       : partial(view.scroll, dx=+1),
        "M-#"           : partial(view.toggle_show_row_num),
        "C-k"           : lambda model, vw: model.delete_row(vw.cur.r, set_undo=True),
        "C-x"           : None,
        ("C-x", "C-s")  : mdl.cmd_save,
        ("C-x", "C-w")  : mdl.cmd_save_as,
        "C-z"           : lambda model: model.undo(),
        "q"             : commands.cmd_quit,
        "RESIZE"        : lambda screen, arg: scr.set_size(screen, arg[0], arg[1]),
    })


