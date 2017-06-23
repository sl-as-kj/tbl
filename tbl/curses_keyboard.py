"""
Curses keyboard handling.
"""

#-------------------------------------------------------------------------------

ESC = 27

KEYS = {
      0:    "C-SPACE",
      1:    "C-a",
      2:    "C-b",
      3:    "C-c",
      4:    "C-d",
      5:    "C-e",
      6:    "C-f",
      7:    "C-g",
      9:    "TAB",
     10:    "RETURN",
     11:    "C-k",
     12:    "C-l",
     14:    "C-n",
     15:    "C-o",
     16:    "C-p",
     17:    "C-q",
     18:    "C-r",
     19:    "C-s",
     20:    "C-t",
     21:    "C-u",
     22:    "C-v",
     23:    "C-w",
     24:    "C-x",
     25:    "C-y",
     26:    "C-z",
     27:    "ESC",
     32:    "SPACE",
    127:    "BACKSPACE",
    258:    "DOWN",
    259:    "UP",
    260:    "LEFT",
    261:    "RIGHT",
    262:    "HOME",
    265:    "F1",
    266:    "F2",
    267:    "F3",
    268:    "F4",
    269:    "F5",
    270:    "F6",
    271:    "F7",
    272:    "F8",
    273:    "F9",
    274:    "F10",
    275:    "F11",
    276:    "F12",
    330:    "DELETE",
    338:    "PAGEDOWN",
    339:    "PAGEUP",
    343:    "ENTER",
    360:    "END",
}        

META_KEYS = {
     98:    "M-LEFT",   # M-b
    102:    "M-RIGHT",  # M-f 
}

def get_key(stdscr):
    meta = False
    while True:
        c = stdscr.getch()
        if c == ESC:
            if meta:
                return "M-ESC"
            else:
                meta = True
                continue
        elif meta:
            return META_KEYS.get(c, "M-" + KEYS.get(c, chr(c)))
        else:
            return KEYS.get(c, chr(c))



#-------------------------------------------------------------------------------
# Testing

import curses

def main():
    stdscr = curses.initscr()
    curses.noecho()
    stdscr.keypad(True)
    # curses.cbreak()
    curses.raw()
    curses.curs_set(False)

    try:
        while True:
            key = get_key(stdscr)
            stdscr.addstr(10, 10, key + "    ")
            if key == "q":
                break
    finally:
        curses.curs_set(True)
        curses.noraw()
        # curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()


if __name__ == "__main__":
    main()
