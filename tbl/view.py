import numpy as np

#-------------------------------------------------------------------------------

def choose_fmt(arr):
    width = max( len(str(a)) for a in arr )
    fmt = lambda v: str(v)[: width] + " " * (width - len(str(v)[: width]))
    fmt.width = width
    return fmt


class State(object):
    # FIXME: Interim.

    def __init__(self, model):
        # Displayed col order.  Also controls col visibility: not all cols
        # need be included.
        self.order  = [ c.id for c in model.cols ]
        # Mapping from col ID to col formatter.
        self.fmt    = { c.id: choose_fmt(c.arr) for c in model.cols }
        # Character coordinate of left edge of display.
        self.x0     = 0
        # Row index of top edge of display.
        self.y0     = 0
        # Col and row index of the cursor position.
        self.x      = 0
        self.y      = 0

        # Decoration characters.
        self.left_border    = "\u2551 "
        self.separator      = " \u2502 "
        self.right_border   = " \u2551"

        self.__layout = None


    def get_fmt(self, name):
        """
        Returns the formatter for a column, by name.
        """
        return self.fmt[name]


    @property
    def layout(self):
        if self.__layout is None:
            self.__layout = self.__compute_layout()
        return self.__layout


    def __compute_layout(self):
        """
        Computes column layout.

        @return
          A sequence of `[x, item]` pairs describing layout, where `x` is the column
          position and `item` is either a column ID or a string literal.
        """
        layout = []
        x0 = 0

        if self.left_border:
            layout.append([x0, self.left_border])
            x0 += len(self.left_border)

        first_col = True

        for col_id in self.order:
            if first_col:
                first_col = False
            elif self.separator:
                layout.append([x0, self.separator])
                x0 += len(self.separator)

            fmt = self.get_fmt(col_id)
            layout.append([x0, col_id])
            x0 += fmt.width

        if self.right_border:
            layout.append([x0, self.right_border])
            x0 += len(self.right_border)

        return layout



