import itertools

#-------------------------------------------------------------------------------

class Model:
    # FIXME: Interim.

    class Col(object):

        def __init__(self, arr, name=None):
            self.name   = name
            self.arr    = arr


    def __init__(self, cols):
        # Mapping from column ID to column, and a list giving column ID orders.
        # We use this instead of an OrderedDict so that the order is easier
        # to manipulate.
        self.__cols         = {}
        self.__col_order    = []

        # Counter for the next col ID.
        self.__col_ids      = itertools.count()

        # Number of rows in the table, or None if no columns so far.
        self.__num_rows     = None

        for col in cols:
            self.add_col(col)


    def add_col(self, col, position=None):
        """
        Adds a column to the model.

        @param position
          Insertion position into the column order; `None` for end.
        """
        if position is None:
            # Insert at end.
            position = len(self.__col_order)

        if self.__num_rows is None:
            # First col, so set number of rows.
            self.__num_rows = len(col.arr)
        if len(col.arr) != self.__num_rows:
            raise ValueError("col is wrong length")

        # Assign a col ID, and add the col.
        col_id = next(self.__col_ids)
        self.__cols[col_id] = col
        self.__col_order.insert(position, col_id)
        assert len(self.__cols) == len(self.__col_order)


    @property
    def num_cols(self):
        return len(self.__cols)


    @property
    def num_rows(self):
        if self.__num_rows is None:
            raise RuntimeError("no cols yet")
        else:
            return self.__num_rows


    @property
    def cols(self):
        """
        Columns in the model, in order.
        """
        return ( self.__cols[i] for i in self.__col_order )



