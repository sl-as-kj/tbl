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
    i0 = bisect_right(layout_x, state.x) - 1
    i1 = bisect_left(layout_x, state.x + max_x)
    layout = [ (x - state.x, l) for x, l in layout[i0 : i1] ]

    fmts = [ state.get_fmt(c.name) for c in model.cols ]

    # FIXME: This is wrong; use IDs.
    cols = list(model.cols)

    # Now, draw.
    rows = min(max_y - 1, model.num_rows - state.row)
    for r in range(rows):
        win.move(r, 0)
        for x, v in layout:
            if isinstance(v, int):
                v = fmts[v](cols[v].arr[state.row + r])
            
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
        return xs[min(bisect_right(xs, state.x), len(xs) - 1)]
    else:
        return xs[max(bisect_right(xs, state.x - 1) - 1, 0)]
    


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
                state.x = advance_column(model, state, forward=False)
            elif c == curses.KEY_SLEFT:
                if state.x > 0:
                    state.x -= 1
            elif c == curses.KEY_RIGHT:
                state.x = advance_column(model, state, forward=True)
            elif c == curses.KEY_SRIGHT:
                state.x += 1
            elif c == curses.KEY_UP:
                if state.row > 0:
                    state.row -= 1
            elif c == curses.KEY_DOWN:
                if state.row < model.num_rows - 1:
                    state.row += 1
            elif c == ord('q'):
                break
            else:
                continue
            stdscr.erase()
            render(stdscr, model, state)
            stdscr.refresh()



if __name__ == "__main__":
    main()

