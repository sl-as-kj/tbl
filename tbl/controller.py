import numpy as np

from   . import model
from   .commands import *
from .view import move_cur_to

# FIXME: Track dirty state.

#-------------------------------------------------------------------------------

class Controller:

    def __init__(self, mdl):
        self.mdl = mdl
        self.undo = []



#-------------------------------------------------------------------------------
# Commands

@command()
def undo(ctl):
    try:
        cmd = ctl.undo.pop()
    except IndexError:
        raise CmdError("nothing to undo")
    else:
        cmd()


@command()
def delete_row(ctl, vw):
    row_num = vw.cur.r
    row     = model.delete_row(ctl.mdl, row_num)
    undo    = lambda: model.insert_row(ctl.mdl, row_num, row)
    ctl.undo.append(undo)

    # move currently selected row one up if this was the last row.
    # Alex, is this the right place for this?
    if row_num >= ctl.mdl.num_rows:
        move_cur_to(vw, r=ctl.mdl.num_rows - 1)



