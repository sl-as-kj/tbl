import itertools

#-------------------------------------------------------------------------------

class Model:
    # FIXME: Interim.

    class Col(object):

        # Counter for the next col ID.
        __ids = itertools.count()

        def __init__(self, arr, name=None):
            self.id     = next(self.__ids)
            self.name   = name
            self.arr    = arr


    def __init__(self):
        # Columns, in order.
        self.__cols         = []
        # Number of rows in the table, or None if no columns so far.
        self.__num_rows     = None


    def add_col(self, arr, name=None, *, position=None):
        """
        Adds a column to the model.

        @param position
          Insertion position into the column order; `None` for end.
        """
        if position is None:
            # Insert at end.
            position = len(self.__cols)

        # Set or check the number of rows from the array length.
        if self.__num_rows is None:
            self.__num_rows = len(arr)
        if len(arr) != self.__num_rows:
            raise ValueError("col is wrong length")

        # Add the col.
        col = self.Col(arr, name=name)
        self.__cols.insert(position, col)


    def get_col(self, col_id):
        """
        Retrieves a column by ID.
        """
        # FIXME: At some point, we'll want a hash for this.
        for col in self.__cols:
            if col.id == col_id:
                return col
        else:
            raise LookupError(col_id)


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
        return iter(self.__cols)



