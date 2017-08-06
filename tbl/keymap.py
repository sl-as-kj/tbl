from   functools import partial

from   . import commands, controller, model, view
from   . import screen as scr

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
        "LEFT"          : partial(view.cmd_move_cur, dc=-1),
        "RIGHT"         : partial(view.cmd_move_cur, dc=+1),
        "UP"            : partial(view.cmd_move_cur, dr=-1),
        "DOWN"          : partial(view.cmd_move_cur, dr=+1),
        "LEFTCLICK"     : view.cmd_move_cur_to,
        "S-LEFT"        : partial(view.cmd_scroll, dx=-1),
        "S-RIGHT"       : partial(view.cmd_scroll, dx=+1),
        "M-#"           : view.cmd_toggle_show_row_num,
        "C-k"           : controller.cmd_delete_row,
        "C-x"           : None,
        ("C-x", "C-s")  : model.cmd_save,
        ("C-x", "C-w")  : model.cmd_save_as,
        "C-z"           : controller.cmd_undo,
        "q"             : commands.cmd_quit,
        "RESIZE"        : lambda screen, arg: scr.set_size(screen, arg[0], arg[1]),
    })


