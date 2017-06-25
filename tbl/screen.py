from   contextlib import contextmanager
import curses
import curses.textpad
import functools
import logging
import numpy as np
import sys

from   . import view as vw
from   .curses_keyboard import get_key
from   .lib import log
from   .model import Model, save_model
from   .text import pad, palide
import curses.textpad

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
        self.cmd_output = None



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
        win.addstr(y, 0, pad(line[: x], x), Attrs.status)
        y += 1

    render_cmd(win, screen)

    render_view(win, screen.view, model)


def set_cmd(win, screen, cmd):
    screen.cmd_output = cmd
    render_cmd(win, screen)

def render_cmd(win, screen):
    if not screen.cmd_output:
        return

    x = screen.size.x
    y = screen.size.y - screen.cmd_size

    # TODO: understand why code in render_screen() works with pad(str, x)
    # while this throws an error if x-1 is replaced with x below
    # (presumably boundary condition hit here?)

    cmds = screen.cmd_output.splitlines()
    assert len(cmds) == screen.cmd_size
    for cmd in cmds:
        win.addstr(y, 0, pad(cmd, x - 1))
        logging.warning("Trying to render: %s" % cmd)
        # win.addstr(y, 0, pad(line[: x], x), Attrs.status)
        y += 1


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

    # The padding at the left and right of each field value.
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

    # Enable mouse events.
    mouse_mask = curses.BUTTON1_CLICKED | curses.BUTTON1_DOUBLE_CLICKED
    new_mask, _ = curses.mousemask(mouse_mask)
    if new_mask != mouse_mask:
        logging.warning(
            "problem with mouse support: {:x} {:x}"
            .format(mouse_mask, new_mask))

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

class EscapeInterrupt(Exception):
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
    Attrs.cmd = Attrs.normal | curses.A_REVERSE

#-------------------------------------------------------------------------------

def load_test(path):
    import csv
    with open(path) as file:
        reader = csv.reader(file)
        rows = iter(reader)
        names = next(rows)
        arrs = zip(*list(rows))
    model = Model(path)
    for arr, name in zip(arrs, names):
        model.add_col(arr, name)
    return model


def cmd_input(screen, stdscr, prompt=""):
    """
    Prompts for and reads a line of input in the cmd line.
    """

    def _validate(c):
        translate = {127: 8, # BACKSPACE -> C-h
                     10: 7, # ENTER --> C-g
                     343: 7 # RETURN --> C-g
                     }

        # Escape/C-g ==> abort, ala Emacs.
        if c == 27 or c == 7:
            raise EscapeInterrupt()

        return translate.get(c, c)

    # Draw the prompt.
    y = screen.size.y - screen.cmd_size
    stdscr.addstr(y, 0, prompt)
    stdscr.refresh()
    # Create a text input in the rest of the cmd line.
    win = curses.newwin(1, screen.size.x - len(prompt), y, len(prompt))
    box = curses.textpad.Textbox(win)
    # box.stripspaces = True  # as far as I can tell, this does nothing and is on by default anyway.
    curses.curs_set(True)
    # Run it.
    try:
        input = box.edit(_validate).strip()
        result = True, input
    except EscapeInterrupt:
        result = False, None
    finally:
        curses.curs_set(False)

    return result



def next_event(model, view, screen, stdscr):
    """
    Waits for, then processes the next UI event.

    @raise KeyboardInterrupt
      The program should terminate.
    """
    extended_key = False
    key, arg = get_key(stdscr)

    logging.info("key: {!r} {!r}".format(key, arg))

    # clean up cmd box.
    set_cmd(stdscr, screen, None)

    if key == 'C-x':
        extended_key = True
        key, arg = get_key(stdscr)
        logging.info("key: {!r} {!r}".format(key, arg))

    # Process Ctrl-X
    if extended_key:
        # Save.
        if key in ("C-a", "C-s"):
            # save-as
            if key == "C-a":
                success, filename = cmd_input(screen, stdscr,
                                              prompt='Save file (%s): ' % model.filename)
                filename = filename or model.filename
            # regular save.
            else:
                success = True
                filename = model.filename

            if success:
                save_msg = "Saving %s..." % filename
                set_cmd(stdscr, screen, save_msg)
                stdscr.refresh()
                save_model(model, filename)
                save_msg += 'Done.'
                set_cmd(stdscr, screen, save_msg)
                stdscr.refresh()
            pass

        return




    # Cursor movement.
    if key == "LEFT":
        vw.move_cur(view, dc=-1)
    elif key == "RIGHT":
        vw.move_cur(view, dc=+1)
    elif key == "UP":
        vw.move_cur(view, dr=-1)
    elif key == "DOWN":
        vw.move_cur(view, dr=+1)
    elif key == "LEFTCLICK":
        x, y = arg
        vw.move_cur_to_coord(view, x, y)

    # Scrolling.
    elif key == "S-LEFT":
        vw.scroll(view, dx=-1)
    elif key == "S-RIGHT":
        vw.scroll(view, dx=+1)

    elif key == "C-k":
        model.delete_row(view.cur.r, set_undo=True)

    elif key == "C-z":
        model.undo()

    elif key == "M-x":
        input_str = cmd_input(screen, stdscr, "command: ")
        logging.warning (input_str)

    elif key == "q":
        raise KeyboardInterrupt()

    elif key == "RESIZE":
        sx, sy = arg
        set_size(screen, sx, sy)


def main_loop(model, view, screen):
    with log.replay(), curses_screen() as stdscr:
        sy, sx = stdscr.getmaxyx()
        set_size(screen, sx, sy)

        while True:
            # Construct the status bar contents.
            screen.status = vw.get_status(view, model, view.size.y)
            # Render the screen.
            stdscr.erase()
            render_screen(stdscr, screen, model)
            # Process the next UI event.
            try:
                next_event(model, view, screen, stdscr)
            except KeyboardInterrupt:
                break


def main(filename=None):
    logging.basicConfig(filename="log", level=logging.INFO)

    model = load_test(filename or sys.argv[1])
    view = vw.View(model)
    screen = Screen(view)
    main_loop(model, view, screen)


if __name__ == "__main__":
    main()

