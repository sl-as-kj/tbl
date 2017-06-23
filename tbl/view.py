import logging
import numpy as np

#-------------------------------------------------------------------------------

class Position(object):
    """
    A location in (col, row) index coordinates.
    """

    def __init__(self, c, r):
        self.c = c
        self.r = r


    def __repr__(self):
        return "{}({!r}, {!r})".format(self.__class__.__name__, self.c, self.r)


    def __iter__(self):
        return iter((self.c, self.r))



class Coordinates(object):
    """
    A location in character (x, y) coordinates.
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y


    def __repr__(self):
        return "{}({!r}, {!r})".format(self.__class__.__name__, self.x, self.y)


    def __iter__(self):
        return iter((self.x, self.y))



#-------------------------------------------------------------------------------

# FIXME: Temporary
def choose_fmt(arr):
    width = max( len(str(a)) for a in arr )
    fmt = lambda v: str(v)[: width] + " " * (width - len(str(v)[: width]))
    fmt.width = width
    return fmt


class View(object):
    # FIXME: Interim.

    def __init__(self, model):
        # Displayed col order.  Also controls col visibility: not all cols
        # need be included.
        self.order  = [ c.id for c in model.cols ]
        # Mapping from col ID to col formatter.
        self.fmt    = { c.id: choose_fmt(c.arr) for c in model.cols }

        # Window size.
        self.size = Coordinates(80, 25)
        # Scroll position, as visible upper-left coordinate.
        self.scr = Coordinates(0, 0)
        # Cursor position.
        self.cur = Position(0, 0)

        self.show_header = True

        # Decoration characters.
        self.left_border    = "\u2551"
        self.separator      = "\u2502"
        self.right_border   = "\u2551"
        self.pad            = 1


    def get_fmt(self, col_id):
        """
        Returns the formatter for a column, by name.
        """
        return self.fmt[col_id]


#-------------------------------------------------------------------------------
# Layout

def lay_out_columns(view):
    """
    Computes the column layout.

    Generates `x, w, type, z` pairs, where,
    - `x` is the starting character position
    - `w` is the width
    - `type` is `"text"` or `"col"`
    - `z` is a string or a column position
    """
    x = 0

    if view.left_border:
        w = len(view.left_border)
        yield x, w, "text", view.left_border
        x += w

    first = True
    for c, col_id in enumerate(view.order):
        if first:
            first = False
        elif view.separator:
            w = len(view.separator)
            yield x, w, "text", view.separator
            x += w

        fmt = view.get_fmt(col_id)
        w = fmt.width + 2 * view.pad
        yield x, w, "col", c
        x += w

    if view.right_border:
        w = len(view.right_border)
        yield x, w, "text", view.right_border
        x += w


def shift_layout(layout, x0, x_size):
    """
    Shifts and filters the layout for scroll position and screen width.

    Shifts `x` positions by `x0`, and filters out entries that are either
    entirely left of `x0` or entirely right of `x0 + x_size`.
    """
    for x, w, type, val in layout:
        x -= x0
        if x + w <= 0:
            continue
        elif x >= x_size:
            break
        else:
            yield x, w, type, val


def locate_in_layout(layout, x0):
    """
    Returns the layout entry containing an x coordinate.
    """
    for x, w, type, val in layout:
        if x <= x0 < x:
            return x, w, type, val
    else:
        return None


def find_col_in_layout(layout, col_id):
    """
    Returns the layout entry for a column.
    """
    for x, w, type, val in layout:
        if type == "col" and val == col_id:
            return x, w, type, val
    else:
        return None


def get_status(view, model, sy):
    """
    Writes the status bar text.
    """
    col = model.get_col(view.order[view.cur.c])
    val = col.arr[view.cur.r]
    return "row {:6d}, {} col '{}' value {!r}".format(
        view.cur.r, col.arr.dtype, col.name, val)


#-------------------------------------------------------------------------------
# Actions

def scroll_to(view, pos):
    """
    Adjusts the scroll position such that `pos` is visible.
    """
    # Find the col in the layout.
    col_idx = view.order[pos.c]
    
    x, w, _, _ = find_col_in_layout(lay_out_columns(view), col_idx)

    # Scroll right if necessary.
    view.scr.x = max(x + w - view.size.x, view.scr.x)
    # Scroll left if necessary.
    view.scr.x = min(x, view.scr.x)

    # Scroll up if necessary.
    view.scr.y = min(view.cur.r, view.scr.y)
    # Scroll down if necessary.
    # FIXME: Need to know the vertical screen layout here.
    view.scr.y = max(view.cur.r - view.size.y + 2, view.scr.y)


def move_cur(view, dc=0, dr=0):
    """
    Moves the cursor position.

    @param dc:
      Change in col position.
    @param dr:
      Change in row position.
    """
    view.cur.c = max(0, min(len(view.order) - 1, view.cur.c + dc))
    view.cur.r = max(0, view.cur.r + dr)
    scroll_to(view, view.cur)



