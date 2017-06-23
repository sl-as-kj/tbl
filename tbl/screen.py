from   contextlib import contextmanager
import curses
import functools
import logging
import numpy as np
import sys

from   . import view as vw
from   .curses_keyboard import get_key
from   .lib import log
from   .model import Model
from   .text import pad, palide

#-------------------------------------------------------------------------------

class Screen:
    """
    The display screen, including the table view and UI components.
    """

    def __init__(self, view):
        self.size = vw.Coordinates(80, 25)
        self.view = view
        self.status = "tbl " * 5
        self.status_size = 1
        self.cmd_size = 1



def set_size(screen, sx, sy):
    screen.size.x = sx
    screen.size.y = sy
    screen.view.size.x = sx
    screen.view.size.y = sy - screen.status_size - screen.cmd_size



def render_screen(win, screen, model):
    x = screen.size.x
    y = screen.size.y - screen.status_size - screen.cmd_size
    
    # Draw the status bar.
    status = screen.status.splitlines()
    assert len(status) == screen.status_size
    for line in status:
        logging.info("line: {!r}".format(line))
        win.addstr(y, 0, pad(line[: x], x), Attrs.status)
        y += 1

    render_view(win, screen.view, model)


def render_view(win, view, model):
    """
    Renders `model` with view `view` in curses `win`.
    """
    layout = vw.lay_out_columns(view)
    layout = vw.shift_layout(layout, view.scr.x, view.size.x)

    # Row numbers to draw.  
    num_rows = min(view.size.y, model.num_rows - view.scr.y) 
    # For the time being, we show a contiguous range of rows starting at y.
    rows = np.arange(num_rows) + view.scr.y 

    if view.show_header:
        # Make room for the header.
        rows[1 :] = rows[: -1]
        rows[0] = -1

    pad = " " * view.pad

    # Now, draw.
    for x, w, type, z in layout:
        c, r = view.cur

        # The item may be only partially visible.  Compute the start and stop
        # slice bounds to trim it to the screen.
        if x < 0:
            t0 = -x
            x = 0
        else:
            t0 = None
        if x + w >= view.size.x:
            t1 = view.size.x - x
        else:
            t1 = None

        if type == "text":
            # A fixed text item.
            text = z[t0 : t1]
            if len(z) > 0:
                for y, row in enumerate(rows):
                    attr =  Attrs.cur_row if row == r else Attrs.normal
                    win.addstr(y, x, text, attr)

        elif type == "col":
            # A column from the model.
            col = z
            col_idx = view.order[col]
            fmt = view.get_fmt(col_idx)
            arr = model.get_col(col_idx).arr

            for y, row in enumerate(rows):
                attr = (
                         Attrs.cur_pos if col == c and row == r
                    else Attrs.cur_col if col == c
                    else Attrs.cur_row if              row == r
                    else Attrs.normal
                )
                if row == -1:
                    # Header.
                    text = palide(model.get_col(col_idx).name, w, elide_pos=0.7)
                    attr |= curses.A_UNDERLINE
                else:
                    text = (pad + fmt(arr[row]) + pad)
                win.addstr(y, x, text[t0 : t1], attr)

        else:
            raise NotImplementedError("type: {!r}".format(type))


@contextmanager
def curses_screen():
    """
    Curses context manager.

    Returns the screen window on entry.  Restores the terminal view on exit.
    """
    stdscr = curses.initscr()
    curses.noecho()
    stdscr.keypad(True)
    curses.cbreak()
    curses.curs_set(False)
    curses.raw()
    init_attrs()

    try:
        yield stdscr
    finally:
        curses.noraw()
        curses.curs_set(True)
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()


class Attrs:
    pass
    

def init_attrs():
    curses.start_color()
    curses.use_default_colors()

    Attrs.normal = curses.color_pair(0)

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    Attrs.cur_pos = curses.color_pair(1)

    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    Attrs.cur_col = curses.color_pair(2)

    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    Attrs.cur_row = curses.color_pair(3)

    Attrs.status = Attrs.normal | curses.A_REVERSE


#-------------------------------------------------------------------------------

def load_test(path):
    import csv
    with open(path) as file:
        reader = csv.reader(file)
        rows = iter(reader)
        names = next(rows)
        arrs = zip(*list(rows))
    model = Model()
    for arr, name in zip(arrs, names):
        model.add_col(arr, name)
    view = vw.View(model)
    return model, view


def main(filename=None):
    logging.basicConfig(filename="log", level=logging.INFO)

    model, view = load_test(filename or sys.argv[1])
    screen = Screen(view)

    with log.replay(), curses_screen() as stdscr:
        sy, sx = stdscr.getmaxyx()
        set_size(screen, sx, sy)

        while True:
            screen.status = vw.get_status(view, model, view.size.y)

            stdscr.erase()
            render_screen(stdscr, screen, model)

            c = get_key(stdscr)
            logging.info("getch() -> {!r}".format(c))

            if c == "LEFT":
                vw.move_cur(view, dc=-1)
            elif c == "RIGHT":
                vw.move_cur(view, dc=+1)
            elif c == "UP":
                vw.move_cur(view, dr=-1)
            elif c == "DOWN":
                vw.move_cur(view, dr=+1)

            elif c == "C-k":
                model.delete_row(view.cur.r, set_undo=True)

            elif c == "C-z":
                model.undo()

            elif c == "q":
                break

            # FIXME:
            elif c == curses.KEY_RESIZE:
                sy, sx = stdscr.getmaxyx()
                set_size(screen, sx, sy)

            else:
                continue



if __name__ == "__main__":
    main()

