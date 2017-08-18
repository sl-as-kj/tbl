import math

from   .commands import command, CmdError, CmdResult
from   .lib import clip, if_none

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

class View(object):
    """
    Owns the followin state:

    - The order and visibility of columns in the display.
    - Each displayed column's formatter (but not name or contents).
    - The display size of the table.
    - The scroll state of the table in the display.
    - The cursor position.
    - Selection.

    """

    class Col:

        def __init__(self, col_id, fmt):
            self.col_id     = col_id
            self.fmt        = fmt
            self.visible    = True



    def __init__(self):
        # Overall dimensions.
        self.screen_size = Coordinates(80, 25)

        # FIXME: Move to controller:
        # Height of status bar.
        self.status_size = 1
        # Status bar text.
        self.status = "?" * 16
        # Height of cmd region.
        self.cmd_size = 1
        # Output or error text in cmd region.
        self.error = None
        self.output = None

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

        self.cols           = []
        self.layout         = None


    def add_column(self, col_id, fmt, position=None):
        if position is None:
            position = len(self.cols)
        self.cols.insert(position, self.Col(col_id, fmt))
        return position


    def set_screen_size(self, sx, sy):
        self.screen_size.x = sx
        self.screen_size.y = sy


    @property
    def size(self):
        return Coordinates(
            self.screen_size.x,
            self.screen_size.y - self.status_size - self.cmd_size
        )



#-------------------------------------------------------------------------------
# Layout

# FIXME: Roll behavior into class.

class Layout:

    def __init__(self, mdl, vw):
        cols = lay_out_cols(mdl, vw)
        self.cols       = list(cols)
        self.num_rows   = mdl.num_rows



def lay_out_cols(mdl, vw):
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
        digits = int(math.log10(mdl.num_rows)) + 1
        w = digits + 2 * vw.pad
        yield x, w, "row_num", digits
        x += w

    if vw.left_border:
        w = len(vw.left_border)
        yield x, w, "text", vw.left_border
        x += w

    for c, col in enumerate(vw.cols):
        if col.visible:
            if first:
                first = False
            elif vw.separator:
                w = len(vw.separator)
                yield x, w, "text", vw.separator
                x += w

            w = col.fmt.width + 2 * vw.pad
            yield x, w, "col", c
            x += w

    if vw.right_border:
        w = len(vw.right_border)
        yield x, w, "text", vw.right_border
        x += w


def shift_layout_cols(layout, x0, x_size):
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


def find_col_in_layout(layout, col_idx):
    """
    Returns the layout entry for a column.
    """
    for x, w, type, val in layout:
        if type == "col" and val == col_idx:
            return x, w, type, val
    else:
        return None


#-------------------------------------------------------------------------------

def get_status(vw, mdl):
    """
    Writes the status bar text.

    @return
      The left- and right-justified portions of the text.
    """
    col     = mdl.cols[vw.cur.c]
    row_num = vw.cur.r
    val     = col.arr[vw.cur.r]
    dtype   = col.arr.dtype

    hidden = sum( not c.visible for c in vw.cols )
    hidden = " [{} cols hidden]".format(hidden) if hidden > 0 else ""

    return (
        "{} [{}]".format(val, dtype) + hidden,
        "{} {:6d}".format(col.name, row_num)
    )


#-------------------------------------------------------------------------------
# Actions

def scroll_to(vw, x=None, y=None):
    """
    Scrolls the vw to a scroll position.
    """
    vw.scr.x = clip(0, if_none(x, vw.scr.x), vw.size.x - 1)
    vw.scr.y = clip(0, if_none(y, vw.scr.y), vw.size.y - 1)


def scroll_to_pos(vw, pos):
    """
    Scrolls the view such that `pos` is visible.
    """
    # Find the col in the layout.
    x, w, _, _ = find_col_in_layout(vw.layout.cols, pos.c)

    # Scroll right if necessary.
    vw.scr.x = max(x + w - vw.size.x, vw.scr.x)
    # Scroll left if necessary.
    vw.scr.x = min(x, vw.scr.x)

    # Scroll up if necessary.
    vw.scr.y = min(vw.cur.r, vw.scr.y)
    # Scroll down if necessary.
    sy = vw.size.y - (1 if vw.show_header else 0)
    vw.scr.y = max(vw.cur.r - sy + 1, vw.scr.y)


def move_cur_to(vw, c=None, r=None):
    vw.cur.c = clip(0, if_none(c, vw.cur.c), len(vw.cols) - 1)
    assert vw.cols[vw.cur.c].visible
    vw.cur.r = clip(0, if_none(r, vw.cur.r), vw.layout.num_rows - 1)
    scroll_to_pos(vw, vw.cur)


def move_cur_to_coord(vw, x, y):
    """
    Moves the cursor to the position matching coordinates `x, y`.

    Does nothing if the coordinates don't correspond to a position, _e.g._
    the position is on a column separator.
    """
    _, _, type, c = locate_in_layout(vw.layout.cols, vw.scr.x + x)
    if type == "col":
        # FIXME: Compute row number correctly.
        r = vw.scr.y + y - 1
        move_cur_to(vw, c, r)

    
def _next_visible(cols, c):
    return next( c for c in range(c + 1, len(cols)) if cols[c].visible )
        

def _prev_visible(cols, c):
    return next( c for c in range(c - 1, -1, -1) if cols[c].visible )

             
def hide_col(vw, c):
    if vw.cols[c].visible:
        vw.cols[c].visible = False
    else:
        raise CmdError("column already hidden")

    # If we hide a column to the left of the current col, move to the left.
    if vw.cur.c == c:
        try:
            vw.cur.c = _next_visible(vw.cols, c)
        except StopIteration:
            vw.cur.c = _prev_visible(vw.cols, c)
        # FIXME: What if we hide the last column?


#-------------------------------------------------------------------------------
# Commands

@command()
def move_left(vw):
    try:
        c = _prev_visible(vw.cols, vw.cur.c)
    except StopIteration:
        pass
    else:
        move_cur_to(vw, c=c)


@command()
def move_right(vw):
    try:
        c = _next_visible(vw.cols, vw.cur.c)
    except StopIteration:
        pass
    else:
        move_cur_to(vw, c=c)


@command()
def move_up(vw):
    move_cur_to(vw, r=vw.cur.r - 1)


@command()
def move_down(vw):
    move_cur_to(vw, r=vw.cur.r + 1)


@command()
def scroll_left(vw):
    scroll_to(vw, vw.scr.x - 1)


@command()
def scroll_right(vw):
    scroll_to(vw, vw.scr.x + 1)


@command()
def toggle_show_row_num(vw):
    vw.show_row_num = not vw.show_row_num


@command()
def hide_column_name(vw, mdl, name):
    try:
        col, = ( c for c in mdl.cols if c.name == name )
    except ValueError:
        raise CmdError("no column: {}".format(name))
    hide_col(vw, col.id)
    return CmdResult(msg="column hidden: {}".format(name))


@command()
def hide_column(vw, mdl):
    c = vw.cur.c
    hide_col(vw, c)
    col = mdl.get_col(c)
    return CmdResult(msg="column hidden: {}".format(col.name))


