import numpy as np

from   . import model, view
from   .commands import *

# FIXME: Track dirty state.

#-------------------------------------------------------------------------------

class Controller:

    def __init__(self):
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
def delete_row(mdl, vw, ctl):
    row_num = vw.cur.r
    row     = model.delete_row(mdl, row_num)
    undo    = lambda: model.insert_row(mdl, row_num, row)
    ctl.undo.append(undo)

    # Make sure selection is still valid.
    # FIXME: Abstract this propertly.
    vw.layout = view.Layout(mdl, vw)
    view.move_cur_to(vw)


