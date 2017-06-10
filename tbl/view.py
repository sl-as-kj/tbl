import logging
import numpy as np

#-------------------------------------------------------------------------------

def choose_fmt(arr):
    width = max( len(str(a)) for a in arr )
    fmt = lambda v: str(v)[: width] + " " * (width - len(str(v)[: width]))
    fmt.width = width
    return fmt


class Position(object):
    """
    A location in (col, row) index coordinates.
    """

    def __init__(self, c, r):
        self.c = c
        self.r = r


    def __iter__(self):
        return iter((c, r))



class Coordinates(object):
    """
    A location in character (x, y) coordinates.
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y


    def __iter__(self):
        return iter((x, y))



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
        # Cursor position.
        self.cur = Position(0, 0)
        # Window size.
        self.size = Coordinates(80, 25)

        # Decoration characters.
        self.left_border    = "\u2551"
        self.separator      = "\u2502"
        self.right_border   = "\u2551"
        self.pad            = " "


    def get_fmt(self, col_id):
        """
        Returns the formatter for a column, by name.
        """
        return self.fmt[col_id]


    @property
    def layout(self):
        """
        The column layout.

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
            x0 += fmt.width + 2 * len(self.pad)

        if self.right_border:
            layout.append([x0, self.right_border])
            x0 += len(self.right_border)

        return layout



#-------------------------------------------------------------------------------

def scroll_to(state, pos):
    """
    Adjusts the scroll position such that `pos` is visible.
    """
    # Find the col in the layout.
    col_idx = state.order[pos.c]
    for x, i in state.layout:
        if i == col_idx:
            break
    else:
        assert(False)

    # Scroll right if necessary.
    state.scr.x = max(
        x + state.get_fmt(col_idx).width - state.size.x, 
        state.scr.x)
    # Scroll left if necessary.
    state.scr.x = min(x, state.scr.x)

    # Scroll up if necessary.
    state.scr.y = min(state.cur.r, state.scr.y)
    # Scroll down if necessary.
    # FIXME: Need to know the vertical screen layout here.
    state.scr.y = max(state.cur.r - state.size.y + 2, state.scr.y)


def move_cur(state, dc=0, dr=0):
    """
    Moves the cursor position.

    @param dc:
      Change in col position.
    @param dr:
      Change in row position.
    """
    state.cur.c = max(0, min(len(state.order) - 1, state.cur.c + dc))
    state.cur.r = max(0, state.cur.r + dr)
    scroll_to(state, state.cur)


