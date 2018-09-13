import csv
from   pathlib import Path

from   .commands import command, CmdResult, CmdError
from   .model import Model

#-------------------------------------------------------------------------------

def load_model(path, *, suffix=None):
    path = Path(path)
    suffix = path.suffix if suffix is None else suffix

    if suffix == ".csv":
        return load_model_csv(path)
    else:
        raise ValueError(f"can't read {suffix} files")


def load_model_csv(path):
    # FIXME: For now, use pandas to load and convert CSV files.
    import pandas as pd
    mdl = Model(path)
    df = pd.read_csv(path)
    for name in df.columns:
        mdl.add_col(df[name], name)
    return mdl


def _save(mdl, filename):
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


#-------------------------------------------------------------------------------
# Commands

@command()
def save(mdl):
    # FIXME: Confirm overwrite.
    _save(mdl, mdl.filename)
    return CmdResult(msg="saved: {}".format(mdl.filename))


@command()
def save_as(mdl, filename):
    if len(filename) == 0:
        raise CmdError("empty filename")
    # FIXME: Confirm overwrite.
    _save(mdl, filename)
    mdl.filename = filename
    return CmdResult(msg="saved: {}".format(filename))


