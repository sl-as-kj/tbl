import itertools
import numpy as np
import csv
import logging

from   .commands import param

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


    def get_col(self, col_id):
        """
        Retrieves a column by ID.
        """
        # FIXME: At some point, we'll want a hash for this.
        for col in self.cols:
            if col.id == col_id:
                return col
        else:
            raise LookupError(col_id)


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

    return lambda: delete_row(mdl, row_num)


#-------------------------------------------------------------------------------

def save_model(mdl, filename):
    """
    Save the model to a file.
    TODO: This needs a lot of work to preserve
    formatting, etc.
    :param mdl:
    :param filename:
    :param new_filename:
    :return:
    """
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        # write header
        header = [col.name for col in mdl.cols]
        writer.writerow(header)
        # write rows.
        for row_num in range(mdl.num_rows):
            row = [str(c.arr[row_num]) for c in mdl.cols]
            writer.writerow(row)


def cmd_save(mdl):
    save_model(mdl, mdl.filename)


@param("filename", "save file as")
def cmd_save_as(mdl, filename):
    if len(filename) > 0:
        save_model(mdl, filename)
        mdl.filename = filename


