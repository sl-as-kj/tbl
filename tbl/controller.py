import numpy as np

from   . import model
from   .commands import CmdError, CmdResult

#-------------------------------------------------------------------------------

class Controller:

    def __init__(self, mdl):
        self.mdl = mdl
        self.undo = []


#-------------------------------------------------------------------------------

def cmd_undo(ctl):
    try:
        cmd = ctl.undo.pop()
    except IndexError:
        raise CmdError("nothing to undo")
    else:
        cmd()


def cmd_delete_row(mdl, vw):
    row_num = vw.cur.r
    row     = model.delete_row(mdl, row_num)
    undo    = lambda: model.insert_row(mdl, row_num, row)
    return CmdResult(undo=undo)


