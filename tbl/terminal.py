from   __future__ import absolute_import, division, print_function, unicode_literals

from   collections import namedtuple
import fcntl
import os
import struct
import termios

#-------------------------------------------------------------------------------

try:

    from os import terminal_size, get_terminal_size

except ImportError:

    terminal_size = namedtuple("terminal_size", ["columns", "lines"])

    def get_terminal_size(fd):
        winsz = fcntl.ioctl(
            fd, termios.TIOCGWINSZ, " " * struct.calcsize("HHHH"))
        lines, columns, _, _ = struct.unpack("HHHH", winsz)
        return terminal_size(columns, lines)


def get_size(default=terminal_size(80, 25)):
    """
    Returns the terminal size.

    Similar to `shutil.get_terminal_size` (Python 3), but better.
    """
    try:
        columns = int(os.environ["COLUMNS"])
    except (KeyError, ValueError):
        columns = None
    try:
        lines = int(os.environ["LINES"])
    except (KeyError, ValueError):
        lines = None
    if columns and lines:
        return terminal_size(columns, lines)

    # Try to get terminal size for the controlling tty.
    try:
        with open(os.ctermid()) as file:
            size = get_terminal_size(file.fileno())
    except (IOError, OSError):
        pass
    else:
        return terminal_size(columns or size.columns, lines or size.lines)

    # Try to get terminal size from stdin, stdout, or stderr.
    for fd in 0, 1, 2:
        try:
            size = get_terminal_size(fd)
        except (IOError, OSError):
            pass
        else:
            return terminal_size(
                columns or size.columns, lines or size.lines)

    return default


