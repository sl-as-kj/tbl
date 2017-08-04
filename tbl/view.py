import logging
import math
import numpy as np

from   .lib import *

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
        # Number of rows.
        self.num_rows = model.num_rows

        # Window size.
        self.size = Coordinates(80, 25)
        # Scroll position, as visible upper-left coordinate.
        self.scr = Coordinates(0, 0)
        # Cursor position.
        self.cur = Position(0, 0)

        self.show_header = True
        self.show_row_num = True

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

def lay_out_columns(vw):
    """
    Computes the column layout.

    Generates `x, w, type, z` pairs, where,
    - `x` is the starting character position
    - `w` is the width
    - `type` is `"text"` or `"col"`
    - `z` is a string or a column position
    """
    x = 0

    first = True

    if vw.show_row_num:
        digits = int(math.log10(vw.num_rows)) + 1
        w = digits + 2 * vw.pad
        yield x, w, "row_num", digits
        x += w

    if vw.left_border:
        w = len(vw.left_border)
        yield x, w, "text", vw.left_border
        x += w

    for c, col_id in enumerate(vw.order):
        if first:
            first = False
        elif vw.separator:
            w = len(vw.separator)
            yield x, w, "text", vw.separator
            x += w

        fmt = vw.get_fmt(col_id)
        w = fmt.width + 2 * vw.pad
        yield x, w, "col", c
        x += w

    if vw.right_border:
        w = len(vw.right_border)
        yield x, w, "text", vw.right_border
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
        if x <= x0 < x + w:
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


def get_status(vw, model, sy):
    """
    Writes the status bar text.
    """
    col = model.get_col(vw.order[vw.cur.c])
    val = col.arr[vw.cur.r]
    return "row {:6d}, {} col '{}' value {!r}".format(
        vw.cur.r, col.arr.dtype, col.name, val)


#-------------------------------------------------------------------------------
# Actions

def scroll_to(vw, x=None, y=None):
    """
    Scrolls the vw to a scroll position.
    """
    vw.scr.x = clip(0, if_none(x, vw.scr.x), vw.size.x - 1)
    vw.scr.y = clip(0, if_none(y, vw.scr.y), vw.size.y - 1)


def scroll(vw, dx=0, dy=0):
    """
    Scrolls the view by offsets.
    """
    scroll_to(vw.scr.x + dx, vw.scr.y + dy)


def scroll_to_pos(vw, pos):
    """
    Scrolls the view such that `pos` is visible.
    """
    # Find the col in the layout.
    col_idx = vw.order[pos.c]
    
    x, w, _, _ = find_col_in_layout(lay_out_columns(vw), col_idx)

    # Scroll right if necessary.
    vw.scr.x = max(x + w - vw.size.x, vw.scr.x)
    # Scroll left if necessary.
    vw.scr.x = min(x, vw.scr.x)

    # Scroll up if necessary.
    vw.scr.y = min(vw.cur.r, vw.scr.y)
    # Scroll down if necessary.
    vw.scr.y = max(vw.cur.r - vw.size.y, vw.scr.y)


def move_cur_to(vw, c=None, r=None):
    vw.cur.c = clip(0, if_none(c, vw.cur.c), len(vw.order) - 1)
    vw.cur.r = clip(0, if_none(r, vw.cur.r), vw.num_rows - 1)
    scroll_to_pos(vw, vw.cur)
    

def move_cur(vw, dc=0, dr=0):
    """
    Moves the cursor position.

    @param dc:
      Change in col position.
    @param dr:
      Change in row position.
    """
    move_cur_to(vw, vw.cur.c + dc, vw.cur.r + dr)


def move_cur_to_coord(vw, x, y):
    """
    Moves the cursor to the position matching coordinates `x, y`.

    Does nothing if the coordinates don't correspond to a position, _e.g._
    the position is on a column separator.
    """
    _, _, type, c = locate_in_layout(lay_out_columns(vw), vw.scr.x + x)
    if type == "col":
        # FIXME: Compute row number correctly.
        r = vw.scr.y + y - 1
        move_cur_to(vw, c, r)

    
def toggle_show_row_num(vw):
    vw.show_row_num = not vw.show_row_num


