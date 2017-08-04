from   contextlib import contextmanager
import curses
import curses.textpad
import functools
from   functools import partial
import logging
import numpy as np
import os
import sys

from   . import commands, keymap
from   . import model as mdl
from   . import view
from   .curses_keyboard import get_key
from   .lib import log
from   .model import Model
from   .text import pad, palide
import curses.textpad

#-------------------------------------------------------------------------------

class Screen:
    """
    The display screen, including the table view and UI components.
    """

    def __init__(self, vw):
        self.size = view.Coordinates(80, 25)
        self.vw = vw
        self.status = "tbl " * 5
        self.status_size = 1
        self.cmd_size = 1
        self.cmd_output = None



def set_size(screen, sx, sy):
    screen.size.x = sx
    screen.size.y = sy
    screen.vw.size.x = sx
    screen.vw.size.y = sy - screen.status_size - screen.cmd_size


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
    render_view(win, screen.vw, model)


def render_cmd(win, screen):
    if not screen.cmd_output:
        return

    x = screen.size.x
    y = screen.size.y - screen.cmd_size

    cmds = screen.cmd_output.splitlines()
    assert len(cmds) <= screen.cmd_size
    for cmd in cmds:
        # FIXME: Writing the bottom-right corner causes an error, which is
        # why we use x - 1.
        win.addstr(y, 0, pad(cmd, x - 1))
        y += 1


def render_view(win, vw, model):
    """
    Renders `model` with view `vw` in curses `win`.
    """
    layout = view.lay_out_columns(vw)
    layout = view.shift_layout(layout, vw.scr.x, vw.size.x)

    # Row numbers to draw.  
    num_rows = min(vw.size.y, model.num_rows - vw.scr.y) 
    # For the time being, we show a contiguous range of rows starting at y.
    rows = np.arange(num_rows) + vw.scr.y 

    if vw.show_header:
        # Make room for the header.
        rows[1 :] = rows[: -1]
        rows[0] = -1

    # The padding at the left and right of each field value.
    pad = " " * vw.pad

    # Now, draw.
    for x, w, type, z in layout:
        c, r = vw.cur

        # The item may be only partially visible.  Compute the start and stop
        # slice bounds to trim it to the screen.
        if x < 0:
            t0 = -x
            x = 0
        else:
            t0 = None
        if x + w >= vw.size.x:
            t1 = vw.size.x - x
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
            col_idx = vw.order[col]
            fmt = vw.get_fmt(col_idx)
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

        elif type == "row_num":
            fmt_str = "0{}d".format(z)
            for y, row in enumerate(rows):
                attr = Attrs.cur_row if row == r else Attrs.normal
                if row == -1:
                    # Header
                    pass
                else:
                    win.addstr(y, x, pad + format(row, fmt_str) + pad, attr)

        else:
            raise NotImplementedError("type: {!r}".format(type))


@contextmanager
def curses_screen():
    """
    Curses context manager.

    Returns the screen window on entry.  Restores the terminal view on exit.
    """
    # Disable the curses ESC translation delay.
    # FIXME: It might be possible to set the ESCDELAY variable in libncurses.so
    # directly with ctypes.
    os.environ["ESCDELAY"] = "0"

    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)
    curses.raw()

    stdscr.keypad(True)
    stdscr.notimeout(True)
    stdscr.nodelay(True)

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
        stdscr.nodelay(False)
        stdscr.notimeout(False)
        stdscr.keypad(False)

        curses.noraw()
        curses.curs_set(True)
        curses.nocbreak()
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


class EscapeInterrupt(Exception):

    pass



def cmd_input(screen, stdscr, prompt=""):
    """
    Prompts for and reads a line of input in the cmd line.

    @return
      The input text.
    @raise EscapeInterrupt
      User cancelled the edit with C-c or C-g.
    """
    def translate(c):
        if c in {3, 7}:  # C-g
            raise EscapeInterrupt()
        else:
            return {
                127: curses.KEY_BACKSPACE,
            }.get(c, c)

    # Draw the prompt.
    y = screen.size.y - screen.cmd_size
    stdscr.addstr(y, 0, prompt)
    stdscr.refresh()
    # Create a text input in the rest of the cmd line.
    win = curses.newwin(1, screen.size.x - len(prompt), y, len(prompt))
    box = curses.textpad.Textbox(win)
    curses.curs_set(True)
    # Run it.
    try:
        result = box.edit(translate)
    finally:
        curses.curs_set(False)
    # Not sure why, but edit() always leaves a space at the end.
    if len(result) > 0:
        assert result[-1] == " "
        return result[: -1]
    else:
        return result


#-------------------------------------------------------------------------------

def next_event(model, vw, screen, stdscr, key_map):
    """
    Waits for, then processes the next UI event according to key_map.

    Handles multi-character key combos.

    @raise KeyboardInterrupt
      The program should terminate.
    """
    # Accumulate prefix keys.
    prefix = ()

    # Loop until we have a complete combo.
    while True:
        screen.cmd_output = " ".join(prefix)
        render_cmd(stdscr, screen)

        key, arg = get_key(stdscr)
        logging.debug("key: {!r} {!r}".format(key, arg))
        screen.cmd_output = None

        combo = prefix + (key, )
        try:
            fn = key_map[combo]

        except KeyError:
            # Unknown combo.
            # FIXME: Indicate this in the UI: flash?
            logging.debug("unknown combo: {}".format(" ".join(combo)))
            return None

        else:
            if fn is None:
                # It's a prefix.
                prefix = combo
            else:
                # Got a key binding.  Bind arguments by name.
                logging.debug("known combo: {}".format(" ".join(combo)))
                try:
                    args = commands.bind_args(
                        fn, 
                        {
                            "model" : model, 
                            "vw"  : vw, 
                            "screen": screen, 
                            "arg"   : arg,
                        },
                        lambda p: cmd_input(screen, stdscr, prompt=p + ": ")
                    )
                except EscapeInterrupt:
                    return None
                return fn(**args)


def main_loop(model, vw, screen):
    key_map = keymap.get_default()

    with log.replay(), curses_screen() as stdscr:
        sy, sx = stdscr.getmaxyx()
        set_size(screen, sx, sy)

        while True:
            # Construct the status bar contents.
            screen.status = view.get_status(vw, model, vw.size.y)
            # Render the screen.
            stdscr.erase()
            render_screen(stdscr, screen, model)
            # Process the next UI event.
            try:
                next_event(model, vw, screen, stdscr, key_map)
            except KeyboardInterrupt:
                break


def main(filename=None):
    logging.basicConfig(filename="log", level=logging.DEBUG)

    model = load_test(filename or sys.argv[1])
    vw = view.View(model)
    screen = Screen(vw)
    main_loop(model, vw, screen)


if __name__ == "__main__":
    main()

