from   __future__ import absolute_import, division, print_function, unicode_literals

import tbl.terminal

#-------------------------------------------------------------------------------

def test_get_size():
    size = tbl.terminal.get_size()
    assert size.columns > 0
    assert size.lines > 0


