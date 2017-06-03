import numpy as np

#-------------------------------------------------------------------------------

def choose_fmt(arr):
    width = max( len(str(a)) for a in arr )
    fmt = lambda v: str(v)[: width] + " " * (width - len(str(v)[: width]))
    fmt.width = width
    return fmt


class State(object):
    # FIXME: Interim.

    def __init__(self, model):
        num_columns = len(model.cols)
        self.vis = [True] * num_columns
        self.fmt = [ choose_fmt(c.arr) for c in model.cols ]
        self.row = 0
        self.x = 0
        self.left_border    = "\u2551 "
        self.separator      = " \u2502 "
        self.right_border   = " \u2551"



