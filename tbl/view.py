import logging
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
        # Row index of top edge of display.
        self.y0     = 0
        # Col and row index of the cursor position.
        self.x      = 0
        self.y      = 0
        # Window size.
        self.sx     = 80
        self.sy     = 25

        # Decoration characters.
        self.left_border    = "\u2551 "
        self.separator      = " \u2502 "
        self.right_border   = " \u2551"

        self.__layout = None


    def set_size(self, sx, sy):
        self.sx = sx
        self.sy = sy
        self.__layout = None


    def get_fmt(self, col_id):
        """
        Returns the formatter for a column, by name.
        """
        return self.fmt[col_id]


    @property
    def layout(self):
        if self.__layout is None:
            self.__layout = self.__compute_layout()
        return self.__layout


    def __compute_layout(self):
        """
        Computes column layout.

        @return
          A sequence of `[x, item]` pairs describing layout, where `x` is the column
          position and `item` is either a column ID or a string literal.
        """
        layout = []
        x0 = 0

        if self.left_border:
            layout.append([x0, self.left_border])
            x0 += len(self.left_border)

        first_col = True

        for col_id in self.order:
            if first_col:
                first_col = False
            elif self.separator:
                layout.append([x0, self.separator])
                x0 += len(self.separator)

            fmt = self.get_fmt(col_id)
            layout.append([x0, col_id])
            x0 += fmt.width

        if self.right_border:
            layout.append([x0, self.right_border])
            x0 += len(self.right_border)

        return layout



#-------------------------------------------------------------------------------

def cursor_move(dx=0, dy=0):
    def apply(state):
        state.x += dx
        state.x = max(0, min(len(state.order) - 1, state.x))

        state.y += dy
        # FIXME: Need to know max y / number of rows here.
        state.y = max(0, state.y)

        col_idx = state.order[state.x]
        for x, i in state.layout:
            if i == col_idx:
                logging.info("x={}".format(x))
                # Scroll right if necessary.
                state.x0 = max(
                    x + state.get_fmt(col_idx).width - state.sx, state.x0)
                # Scroll left if necessary.
                state.x0 = min(x, state.x0)
                break
        else:
            assert(False)

        state.y0 = min(state.y, state.y0)
        state.y0 = max(state.y - state.sy + 2, state.y0)

    return apply


