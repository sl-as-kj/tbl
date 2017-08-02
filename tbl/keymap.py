from   functools import partial

from   . import commands
from   . import model as mdl
from   .screen import set_size
from   . import view as vw

#-------------------------------------------------------------------------------

def get_default():
    return commands.check_key_map({
        "LEFT"          : partial(vw.move_cur, dc=-1),
        "RIGHT"         : partial(vw.move_cur, dc=+1),
        "UP"            : partial(vw.move_cur, dr=-1),
        "DOWN"          : partial(vw.move_cur, dr=+1),
        "LEFTCLICK"     : lambda arg, view: vw.move_cur_to(view, arg[0], arg[1]),
        "S-LEFT"        : partial(vw.scroll, dx=-1),
        "S-RIGHT"       : partial(vw.scroll, dx=+1),
        "M-#"           : partial(vw.toggle_show_row_num),
        "C-k"           : lambda model, view: model.delete_row(view.cur.r, set_undo=True),
        "C-x"           : None,
        ("C-x", "C-s")  : mdl.cmd_save,
        ("C-x", "C-w")  : mdl.cmd_save_as,
        "C-z"           : lambda model: model.undo(),
        "q"             : commands.cmd_quit,
        "RESIZE"        : lambda arg: set_size(screen, arg[0], arg[1]),
    })


