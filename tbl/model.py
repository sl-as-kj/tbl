import itertools
import numpy as np

#-------------------------------------------------------------------------------

class Model:
    # FIXME: Interim.

    class Col:

        # Counter for the next col ID.
        __ids = itertools.count()

        def __init__(self, arr, name=None):
            self.id     = next(self.__ids)
            self.name   = name
            self.arr    = arr


    def __init__(self, filename):
        # Columns, in order.
        self.cols       = []
        # Number of rows in the table, or None if no columns so far.
        # FIXME: Make a property?
        self.num_rows   = None
        self.filename   = filename


    def add_col(self, arr, name=None, *, position=None):
        """
        Adds a column to the model.

        @param position
          Insertion position into the column order; `None` for end.
        """
        arr = np.asarray(arr)
        if position is None:
            # Insert at end.
            position = len(self.cols)

        # Set or check the number of rows from the array length.
        if self.num_rows is None:
            self.num_rows = len(arr)
        if len(arr) != self.num_rows:
            raise ValueError("col is wrong length")

        # Add the col.
        col = self.Col(arr, name=name)
        self.cols.insert(position, col)


    def get_col_idx(self, col_id):
        """
        Returns the column index of a column by ID.
        """
        # FIXME: At some point, we'll want a hash for this.
        for i, col in enumerate(self.cols):
            if col.id == col_id:
                return i
        else:
            raise LookupError(col_id)
        

    def get_col(self, col_id):
        """
        Retrieves a column by ID.
        """
        return self.cols[self.get_col_idx(col_id)]


    @property
    def num_cols(self):
        return len(self.cols)



#-------------------------------------------------------------------------------

def delete_row(mdl, row_num):
    """
    Deletes a row; returns a sequence with the row's values.
    """
    assert 0 <= row_num < mdl.num_rows

    row = tuple( c.arr[row_num] for c in mdl.cols )
    for col in mdl.cols:
        col.arr = np.delete(col.arr, row_num)
    mdl.num_rows -= 1

    return row


def insert_row(mdl, row_num, row):
    """
    Inserts a sequence of values as a row at `row_num`.
    """
    assert 0 <= row_num <= mdl.num_rows
    assert len(row) == len(mdl.cols)
    
    for col, val in zip(mdl.cols, row):
        col.arr = np.insert(col.arr, row_num, val)
    mdl.num_rows += 1


def set_col_idx(mdl, col_id, col_idx):
    """
    Reorders columns so that `col_id` is at position `col_idx`.
    """
    old_idx = mdl.get_col_idx(col_id)
    mdl.cols.insert(col_idx, mdl.cols.pop(old_idx))
    return old_idx


