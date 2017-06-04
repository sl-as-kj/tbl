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
        # Displayed col order.  Also controls col visibility: not all cols
        # need be included.
        self.order  = [ c.id for c in model.cols ]
        # Mapping from col ID to col formatter.
        self.fmt    = { c.id: choose_fmt(c.arr) for c in model.cols }
        # Character coordinate of left edge of display.
        self.x0     = 0
        # Row index of top edge of displa.
        self.y0     = 0
        
        # Decoration characters.
        self.left_border    = "\u2551 "
        self.separator      = " \u2502 "
        self.right_border   = " \u2551"


    def get_fmt(self, name):
        """
        Returns the formatter for a column, by name.
        """
        return self.fmt[name]



#-------------------------------------------------------------------------------

def lay_out_cols(model, state):
    """
    Computes column layout.

    @return
      A sequence of `[x, item]` pairs describing layout, where `x` is the column
      position and `item` is either a column ID or a string literal.
    """
    layout = []
    x0 = 0

    if state.left_border:
        layout.append([x0, state.left_border])
        x0 += len(state.left_border)

    first_col = True

    for col_id in state.order:
        if first_col:
            first_col = False
        elif state.separator:
            layout.append([x0, state.separator])
            x0 += len(state.separator)

        fmt = state.get_fmt(col_id)
        layout.append([x0, col_id])
        x0 += fmt.width

    if state.right_border:
        layout.append([x0, state.right_border])
        x0 += len(state.right_border)

    return layout


