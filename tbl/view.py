import logging
import numpy as np

#-------------------------------------------------------------------------------

def choose_fmt(arr):
    width = max( len(str(a)) for a in arr )
    fmt = lambda v: str(v)[: width] + " " * (width - len(str(v)[: width]))
    fmt.width = width
    return fmt


class Coordinates(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y


class State(object):
    # FIXME: Interim.

    def __init__(self, model):
        # Displayed col order.  Also controls col visibility: not all cols
        # need be included.
        self.order  = [ c.id for c in model.cols ]
        # Mapping from col ID to col formatter.
        self.fmt    = { c.id: choose_fmt(c.arr) for c in model.cols }

        # Scroll position, as visible upper-left coordinate.
        self.scr = Coordinates(0, 0)
        # Col and row index of the cursor position.
        self.cur = Coordinates(0, 0)
        # Window size.
        self.size = Coordinates(80, 25)

        # Decoration characters.
        self.left_border    = "\u2551 "
        self.separator      = " \u2502 "
        self.right_border   = " \u2551"

        self.__layout = None


    def get_fmt(self, col_id):
        """
        Returns the formatter for a column, by name.
        """
        return self.fmt[col_id]


    @property
    def layout(self):
        # FIXME: ...?
        return self.__compute_layout()


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

def scroll_to_cursor(state):
    """
    Adjusts the scroll position such that the cursor is visible.
    """


def cursor_move(dx=0, dy=0):
    def apply(state):
        # Move horizontally.
        state.cur.x = max(0, min(len(state.order) - 1, state.cur.x + dx))

        # Move vertically.
        state.cur.y = max(0, state.cur.y + dy)
        # FIXME: Need to know max y / number of rows here.

        col_idx = state.order[state.cur.x]
        for x, i in state.layout:
            if i == col_idx:
                logging.info("x={}".format(x))
                # Scroll right if necessary.
                state.scr.x = max(
                    x + state.get_fmt(col_idx).width - state.size.x, 
                    state.scr.x)
                # Scroll left if necessary.
                state.scr.x = min(x, state.scr.x)
                break
        else:
            assert(False)

        state.scr.y = min(state.cur.y, state.scr.y)
        state.scr.y = max(state.cur.y - state.size.y + 2, state.scr.y)

    return apply


