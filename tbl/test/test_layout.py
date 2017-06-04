from   collections import OrderedDict as odict
import numpy as np

from   tbl.screen import Model, State, lay_out_cols

#-------------------------------------------------------------------------------

def test_lay_out_0():
    model = Model([
        Model.Col(np.array([ 1,  2,  3]), "foo"),
        Model.Col(np.array([ 8,  9, 10]), "bar"),
    ])
    state = State(model)
    state.left_border   = "|> "
    state.separator     = " || "
    state.right_border  = " <|"

    layout = lay_out_cols(model, state)
    layout = [ tuple(p) for p in layout ]
    assert layout == [
        ( 0, "|> "),
        ( 3, 0),  # col 0
        ( 4, " || "),
        ( 8, 1),  # col 1
        (10, " <|"),
    ]


