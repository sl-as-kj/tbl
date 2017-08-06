import numpy as np

from   . import model
from   .commands import *

#-------------------------------------------------------------------------------

class Controller:

    def __init__(self, mdl):
        self.mdl = mdl
        self.undo = []


#-------------------------------------------------------------------------------

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


