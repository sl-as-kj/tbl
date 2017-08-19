import numpy as np

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

        # (x, y) coordinates of the upper-left visible 
        self.scr = Coordinates(0, 0)
        # (c, r) coordinates of the cursor position.
        self.cur = Position(0, 0)

        self.show_header = True
        self.show_row_num = True

        # Decoration characters.
        self.left_border    = "\u2551"
        self.separator      = "\u2502"
        self.right_border   = "\u2551"
        self.pad            = 1

        # FIXME: Determine this properly.
        row_num_fmt         = lambda n: format(n, "04d")
        row_num_fmt.width   = 4
        self.row_num_fmt    = row_num_fmt

        self.cols           = []
        self.num_rows       = 0
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
    """
    The transformation between (col, row) position and (x, y) coordinates.
    """

    def __init__(self, vw):
        """
        Computes the column layout.

        Generates `x, w, type, z` pairs, where,
        - `x` is the starting character position
        - `w` is the width
        - `type` is `"text"` or `"col"`
        - `z` is a string or a column position
        """
        cols = []  # (x, width, c), c=None for row number
        text = []  # (x, width, text)

        x = -vw.scr.x
        xs = vw.size.x

        def add_col(w, c):
            nonlocal x
            if 0 < x + w and x < xs:
                cols.append((x, w, c))
            x += w

        def add_text(t):
            nonlocal x
            w = len(t)
            if 0 < x + w and x < xs:
                text.append((x, w, t))
            x += w

        need_sep = False

        if vw.left_border:
            add_text(vw.left_border)

        if vw.show_row_num:
            add_col(vw.row_num_fmt.width + 2 * vw.pad, None)
            need_sep = True

        for c, col in enumerate(vw.cols):
            if vw.separator and need_sep:
                add_text(vw.separator)
            add_col(col.fmt.width + 2 * vw.pad, c)
            need_sep = True
            
        if vw.right_border:
            add_text(vw.right_border)

        self.cols = cols
        self.text = text


    def locate_col(self, x0):
        """
        Returns the layout entry containing an x coordinate.
        """
        for x, w, c in self.cols:
            if x <= x0 < x + w:
                return x, w, c
        else:
            raise LookupError("no col at x: {}".format(x0))


    def get_col(self, c):
        """
        Returns the layout entry for a column.
        """
        for x, w, c_ in self.cols:
            if c_ == c:
                return x, w



def _rendered_cols(vw, mdl):
    """
    Helper function to set up columns for rendering.
    """
    # Draw columns.
    for x, w, c in vw.layout.cols:
        # The item may be only partially visible.  Compute the start and stop
        # slice bounds to trim it to the screen.
        xp = max(x, 0)
        sx = vw.size.x - xp
        trim = slice(-x if x < 0 else None, sx if sx < w else None)

        if c is None:
            # Row number.
            fmt = vw.row_num_fmt
            arr = np.arange(mdl.num_rows)  # FIXME
            name = "row #"
        else:
            fmt = vw.cols[c].fmt
            col = mdl.get_col(c)
            arr = col.arr
            name = col.name
    
        yield c, xp, w, trim, name, fmt, arr


def _rendered_text(vw, mdl):
    """
    Helper function to set up text decorations for rendering.
    """
    for x, w, text in vw.layout.text:
        # The item may be only partially visible.  Compute the start and stop
        # slice bounds to trim it to the screen.
        xp = max(x, 0)
        sx = vw.size.x - xp
        trim = slice(-x if x < 0 else None, sx if sx < w else None)

        text = text[trim]
        if len(text) > 0:
            yield xp, w, text


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
    try:
        c = vw.layout.locate_col(vw.scr.x + x)
    except LookupError:
        pass
    else:
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


