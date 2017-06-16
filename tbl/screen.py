from   contextlib import contextmanager
import curses
import functools
import logging
import numpy as np
import sys

from   . import view
from   .lib import log
from   .model import Model
from   .text import palide

#-------------------------------------------------------------------------------

def render(win, model, state):
    """
    Renders `model` with view `state` in curses `win`.
    """
    layout = view.lay_out_columns(state)
    layout = view.shift_layout(layout, state.scr.x, state.size.x)

    # Row numbers to draw.  
    num_rows = min(state.size.y - 1, model.num_rows - state.scr.y) 
    # For the time being, we show a contiguous range of rows staritng at y.
    rows = np.arange(num_rows) + state.scr.y 

    if state.show_header:
        # Make room for the header.
        rows[1 :] = rows[: -1]
        rows[0] = -1

    pad = " " * state.pad

    # Now, draw.
    for x, w, type, z in layout:
        c, r = state.cur

        # The item may be only partially visible.  Compute the start and stop
        # slice bounds to trim it to the screen.
        if x < 0:
            t0 = -x
            x = 0
        else:
            t0 = None
        if x + w >= state.size.x:
            t1 = state.size.x - x
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
            col_idx = state.order[col]
            fmt = state.get_fmt(col_idx)
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
                    text = palide(model.get_col(col_idx).name, w)
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

    Returns the screen window on entry.  Restores the terminal state on exit.
    """
    stdscr = curses.initscr()
    curses.noecho()
    stdscr.keypad(True)
    curses.cbreak()
    curses.curs_set(False)

    init_attrs()

    try:
        yield stdscr
    finally:
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
    state = view.State(model)
    return model, state


def main():
    logging.basicConfig(filename="log", level=logging.INFO)

    model, state = load_test(sys.argv[1])

    with log.replay(), curses_screen() as stdscr:
        state.size.y, state.size.x = stdscr.getmaxyx()
        render(stdscr, model, state)

        while True:
            c = stdscr.getch()
            logging.info("getch() -> {!r}".format(c))

            if c == curses.KEY_LEFT:
                view.move_cur(state, dc=-1)
            elif c == curses.KEY_RIGHT:
                view.move_cur(state, dc=+1)
            elif c == curses.KEY_UP:
                view.move_cur(state, dr=-1)
            elif c == curses.KEY_DOWN:
                view.move_cur(state, dr=+1)

            elif c == ord('q'):
                break

            elif c == curses.KEY_RESIZE:
                sy, sx = stdscr.getmaxyx()
                state.set_size(sx, sy)

            else:
                continue

            stdscr.erase()
            render(stdscr, model, state)



if __name__ == "__main__":
    main()

