from   bisect import *
from   contextlib import contextmanager
import curses
import functools
import logging
import sys

from   .model import Model
from   .view import State, lay_out_cols

#-------------------------------------------------------------------------------

def render(win, model, state):
    """
    Renders `model` with view `state` in curses `win`.
    """
    # Compute the column layout.
    layout = lay_out_cols(model, state)

    max_y, max_x = win.getmaxyx()

    # Truncate to window size and position.
    layout_x = [ x for x, _ in layout ]
    i0 = bisect_right(layout_x, state.x0) - 1
    i1 = bisect_left(layout_x, state.x0 + max_x)
    layout = [ (x - state.x0, l) for x, l in layout[i0 : i1] ]

    # Now, draw.
    rows = min(max_y - 1, model.num_rows - state.y0)
    for r in range(rows):
        win.move(r, 0)
        idx = state.y0 + r
        for x, v in layout:
            if isinstance(v, int):
                # Got a col ID.
                v = state.get_fmt(v)(model.get_col(v).arr[idx])
            
            if x < 0:
                v = v[-x :]
            if x + len(v) >= max_x:
                v = v[: max_x - x]

            win.addstr(v)


def advance_column(model, state, forward=True):
    layout = lay_out_cols(model, state)
    # Select columns only.
    xs = [ x for x, i in layout if isinstance(i, int) ]

    if forward:
        return xs[min(bisect_right(xs, state.x0), len(xs) - 1)]
    else:
        return xs[max(bisect_right(xs, state.x0 - 1) - 1, 0)]
    


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

    try:
        yield stdscr
    finally:
        curses.curs_set(True)
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()


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
    state = State(model)
    return model, state


def main():
    logging.basicConfig(filename="log", level=logging.INFO)

    model, state = load_test(sys.argv[1])

    with curses_screen() as stdscr:
        render(stdscr, model, state)
        stdscr.refresh()

        while True:
            c = stdscr.getch()
            logging.info("getch() -> {!r}".format(c))
            if c == curses.KEY_LEFT:
                state.x0 = advance_column(model, state, forward=False)
            elif c == curses.KEY_SLEFT:
                if state.x0 > 0:
                    state.x0 -= 1
            elif c == curses.KEY_RIGHT:
                state.x0 = advance_column(model, state, forward=True)
            elif c == curses.KEY_SRIGHT:
                state.x0 += 1
            elif c == curses.KEY_UP:
                if state.y0 > 0:
                    state.y0 -= 1
            elif c == curses.KEY_DOWN:
                if state.y0 < model.num_rows - 1:
                    state.y0 += 1
            elif c == ord('q'):
                break
            else:
                continue
            stdscr.erase()
            render(stdscr, model, state)
            stdscr.refresh()



if __name__ == "__main__":
    main()

