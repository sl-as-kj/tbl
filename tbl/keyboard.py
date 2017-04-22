from   __future__ import absolute_import, division, print_function, unicode_literals

import contextlib
import select
import sys
import termios
import tty

#-------------------------------------------------------------------------------

TRANSLATION = {
    "\x01"      : "^A",
    "\x02"      : "^B",
    "\x04"      : "^D",
    "\x05"      : "^E",
    "\x06"      : "^F",
    "\x07"      : "^G",
    "\x08"      : "^H",
    "\x0b"      : "^K",
    "\x0c"      : "^L",
    "\x0e"      : "^N",
    "\x10"      : "^P",
    "\x12"      : "^R",
    "\x14"      : "^T",
    "\x15"      : "^U",
    "\x17"      : "^W",
    "\x18"      : "^X",
    "\x1bOP"    : "F1",
    "\x1bOQ"    : "F2",
    "\x1bOR"    : "F3",
    "\x1bOS"    : "F4",
    "\x1b[15~"  : "F5",
    "\x1b[17~"  : "F6",
    "\x1b[18~"  : "F7",
    "\x1b[19~"  : "F8",
    "\x1b[20~"  : "F9",
    "\x1b[21~"  : "F10",
}

@contextlib.contextmanager
def raw_keyboard(file):
    # Save old attributes.
    old_attr = termios.tcgetattr(file)

    attr = termios.tcgetattr(file)
    # Disable character echoing and canonical (line) mode.
    attr[3] &= ~(termios.ECHO | termios.ICANON)
    # Disable minimum read size and timer.
    attr[6][termios.VMIN] = 0
    attr[6][termios.VTIME] = 0
    termios.tcsetattr(file, termios.TCSADRAIN, attr)

    try:
        yield
    finally:
        termios.tcsetattr(file, termios.TCSADRAIN, old_attr)



if __name__ == "__main__":
    with raw_keyboard(sys.stdin):
        while True:
            sel = select.select([sys.stdin], [], [], 0)
            if len(sel[0]) > 0:
                key = sys.stdin.read(8)  # FIXME: Is 8 enough?
                if len(key) > 0:
                    print(TRANSLATION.get(key, key))


