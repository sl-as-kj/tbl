import itertools
import numpy as np
import csv
import logging

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
        self.__cols         = []
        # Number of rows in the table, or None if no columns so far.
        self.__num_rows     = None

        self.__undo_info = []
        self.filename = filename


    def add_col(self, arr, name=None, *, position=None):
        """
        Adds a column to the model.

        @param position
          Insertion position into the column order; `None` for end.
        """
        arr = np.asarray(arr)
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

    def delete_row(self, row_num, set_undo=False):
        """
        delete a row from the model
        :param row_num:
        :return:
        """

        # do not allow deletion of the last row for now.
        if self.__num_rows <= 1:
            return

        row = [c.arr[row_num] for c in self.__cols]
        for c in self.__cols:
            c.arr = np.delete(c.arr, row_num)

        self.__num_rows -= 1

        if set_undo:
            self.__undo_info.append((self.insert_row, {'row_num': row_num, 'row': row}))

    def insert_row(self, row_num, row, set_undo=False):
        """
        insert a row
        :param row_num: where to insert the row.
        :param row: list of things to insert into each column
        :return:
        """
        if len(row) != self.num_cols:
            raise ValueError("row is wrong length")

        for c_idx,c in enumerate(self.__cols):
            c.arr = np.insert(c.arr, row_num, row[c_idx])
        self.__num_rows += 1
        if set_undo:
            self.__undo_info.append((self.delete_row, {'row_num': row_num}))


    def undo(self):
        """
        simplest undo: pop the undo info from the undo stack and execute it.
        :return:
        """
        if not len(self.__undo_info):
            return

        func, kwargs = self.__undo_info.pop()
        func(**kwargs)


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


def save_model(model, filename, new_filename=True):
    """
    Save the model to a file.
    TODO: This needs a lot of work to preserve
    formatting, etc.
    :param model:
    :param filename:
    :param new_filename:
    :return:
    """
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        # write header
        header = [col.name for col in model.cols]
        logging.warning(header)
        writer.writerow(header)
        # write rows.
        for row_num in range(model.num_rows):
            row = [str(c.arr[row_num]) for c in model.cols]
            writer.writerow(row)

    if new_filename:
        model.filename = filename