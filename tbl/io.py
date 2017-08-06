import csv
import logging

from   .commands import param

#-------------------------------------------------------------------------------

def save(mdl, filename):
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
    save(mdl, mdl.filename)


@param("filename", "save file as")
def cmd_save_as(mdl, filename):
    if len(filename) > 0:
        save(mdl, filename)
        mdl.filename = filename


