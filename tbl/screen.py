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
    layout = lay_out_cols(state)

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
                val = state.get_fmt(v)(model.get_col(v).arr[idx])
            else:
                val = v
            
            if x < 0:
                val = val[-x :]
            if x + len(val) >= max_x:
                val = val[: max_x - x]

            attr = (
                     Attrs.cur_pos if v == state.x and idx == state.y
                else Attrs.cur_col if v == state.x
                else Attrs.cur_row if                  idx == state.y
                else Attrs.normal
            )
            win.addstr(val, attr)


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
    state = State(model)
    return model, state


def main():
    logging.basicConfig(filename="log", level=logging.INFO)

    model, state = load_test(sys.argv[1])

    with curses_screen() as stdscr:
        render(stdscr, model, state)

        while True:
            c = stdscr.getch()
            logging.info("getch() -> {!r}".format(c))
            if c == curses.KEY_LEFT:
                if state.x > 0:
                    state.x -= 1
            elif c == curses.KEY_RIGHT:
                if state.x < len(state.order) - 1:
                    state.x += 1

            elif c == curses.KEY_SLEFT:
                state.x0 = advance_column(model, state, forward=False)
            elif c == curses.KEY_SRIGHT:
                state.x0 = advance_column(model, state, forward=True)

            elif c == curses.KEY_UP:
                if state.y > 0:
                    state.y -= 1
                    if state.y0 > state.y:
                        state.y0 = state.y
            elif c == curses.KEY_DOWN:
                if state.y < model.num_rows - 1:
                    state.y += 1
                # FIXME: Scroll down if necessary.

            elif c == ord('q'):
                break
            else:

                continue
            stdscr.erase()
            render(stdscr, model, state)



if __name__ == "__main__":
    main()

