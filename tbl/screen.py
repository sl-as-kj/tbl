from   bisect import *
from   contextlib import contextmanager
import curses
import functools
import logging
import sys

from   . import view
from   .lib import log
from   .model import Model

#-------------------------------------------------------------------------------

def render(win, model, state):
    """
    Renders `model` with view `state` in curses `win`.
    """
    # Get the column layout.
    layout = state.layout

    # Truncate to window size and position.
    layout_x = [ x for x, _ in layout ]
    i0 = bisect_right(layout_x, state.scr.x) - 1
    i1 = bisect_left(layout_x, state.scr.x + state.size.x)
    layout = [ (x - state.scr.x, l) for x, l in layout[i0 : i1] ]

    # Now, draw.
    rows = min(state.size.y - 1, model.num_rows - state.scr.y)
    for r in range(rows):
        win.move(r, 0)
        idx = state.scr.y + r
        for x, v in layout:
            if isinstance(v, int):
                # Got a col ID.
                val = state.get_fmt(v)(model.get_col(v).arr[idx])
            else:
                val = v
            
            if x < 0:
                val = val[-x :]
            if x + len(val) >= state.size.x:
                val = val[: state.size.x - x]

            attr = (
                     Attrs.cur_pos if v == state.cur.c and idx == state.cur.r
                else Attrs.cur_col if v == state.cur.c
                else Attrs.cur_row if                      idx == state.cur.r
                else Attrs.normal
            )
            win.addstr(val, attr)


def advance_column(model, state, forward=True):
    layout = state.layout
    # Select columns only.
    xs = [ x for x, i in layout if isinstance(i, int) ]

    if forward:
        return xs[min(bisect_right(xs, state.scr.x), len(xs) - 1)]
    else:
        return xs[max(bisect_right(xs, state.scr.x - 1) - 1, 0)]
    


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

    scroll_step = 12

    with log.replay(), curses_screen() as stdscr:
        state.size.y, state.size.x = stdscr.getmaxyx()
        render(stdscr, model, state)

        while True:
            c = stdscr.getch()
            logging.info("getch() -> {!r}".format(c))

            if c == curses.KEY_LEFT:
                view.cursor_move(state, dx=-1)
            elif c == curses.KEY_RIGHT:
                view.cursor_move(state, dx=+1)
            elif c == curses.KEY_UP:
                view.cursor_move(state, dy=-1)
            elif c == curses.KEY_DOWN:
                view.cursor_move(state, dy=+1)

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

