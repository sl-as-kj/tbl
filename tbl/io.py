import csv
from   pathlib import Path

from   .commands import command, CmdResult, CmdError
from   .model import Model

#-------------------------------------------------------------------------------

def make_source(path_str):
    """
    Constructs a source from a path string.
    """
    if "::" in path_str:
        format, path = path_str.split("::", 1)
        path = Path(path)
    else:
        path = Path(path_str)
        format = path.suffix.lstrip(".")
    return {"format": format, "path": path}


def load_csv(source):
    # FIXME: For now, use pandas to load and convert CSV files.
    import pandas as pd
    df = pd.read_csv(source["path"])
    return Model(cols={ n: df[n] for n in df.columns }, source=source)


def dump_csv(mdl):
    with open(mdl.source["path"], "w") as file:
        writer = csv.writer(file)
        # Write header.
        header = [col.name for col in mdl.cols]
        writer.writerow(header)
        # Write rows.
        for row_num in range(mdl.num_rows):
            row = [str(c.arr[row_num]) for c in mdl.cols]
            writer.writerow(row)


SUFFIXES = {
    "csv": (load_csv, dump_csv),
}


def load(source):
    format = source["format"]
    try:
        load, _ = SUFFIXES[format]
    except KeyError:
        raise ValueError(f"unknown format: {format}") from None
    return load(source)


def dump(mdl):
    format = mdl.source["format"]
    try:
        _, dump = SUFFIXES[format]
    except KeyError:
        raise ValueError(f"unknown format: {format}") from None
    return dump(mdl)


#-------------------------------------------------------------------------------
# Commands

@command()
def save(mdl):
    # FIXME: Confirm overwrite.
    dump(mdl)
    return CmdResult(msg="saved: {}".format(mdl.filename))


@command()
def save_as(mdl, filename):
    if filename == "":
        raise CmdError("empty filename")
    path = Path(filename)

    # Choose the format based on the suffix.
    if path.suffix == "":
        raise CmdError(f"can't determine format for '{path}'")
    format = path.suffix.lstrip(".")

    mdl.source = {"format": format, "path": path}

    # FIXME: Confirm overwrite.
    dump(mdl)
    return CmdResult(msg="saved: {}".format(filename))


