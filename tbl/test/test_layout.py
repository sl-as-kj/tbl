from   collections import OrderedDict as odict
import numpy as np

from   tbl.screen import Model
from   tbl.view import State

#-------------------------------------------------------------------------------

def test_lay_out_0():
    model = Model()
    model.add_col(np.array([ 1,  2,  3]), "foo")
    model.add_col(np.array([ 8,  9, 10]), "bar")
    state = State(model)
    state.left_border   = "|>"
    state.separator     = "||"
    state.right_border  = "<|"

    layout = [ tuple(p) for p in state.layout ]
    assert layout == [
        ( 0, "|>"),
        ( 2, 0),  # col 0
        ( 5, "||"),
        ( 7, 1),  # col 1
        (11, "<|"),
    ]


