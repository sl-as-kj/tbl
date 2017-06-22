from   collections import OrderedDict as odict
import numpy as np

from   tbl.screen import Model
from   tbl.view import View, lay_out_columns

#-------------------------------------------------------------------------------

def test_lay_out_0():
    model = Model()
    model.add_col(np.array([ 1,  2,  3]), "foo")
    model.add_col(np.array([ 8,  9, 10]), "bar")
    view = View(model)
    view.left_border   = "|>"
    view.separator     = "||"
    view.right_border  = "<|"

    assert [ tuple(l) for l in lay_out_columns(view) ] == [
        ( 0, 2, "text", "|>"),
        ( 2, 3, "col", 0),
        ( 5, 2, "text", "||"),
        ( 7, 4, "col", 1),
        (11, 2, "text", "<|"),
    ]


