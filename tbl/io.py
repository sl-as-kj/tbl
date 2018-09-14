import csv
from   pathlib import Path

from   .commands import command, CmdResult, CmdError
from   .model import Model

#-------------------------------------------------------------------------------

def load_csv(source):
    # FIXME: For now, use pandas to load and convert CSV files.
    import pandas as pd
    df = pd.read_csv(source["path"])
    return Model(cols={ n: df[n] for n in df.columns })


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


#-------------------------------------------------------------------------------

SUFFIXES = {
    "csv": (load_csv, dump_csv),
}


def make_source(source_str):
    """
    Constructs a source from a path string.
    """
    if "::" in source_str:
        format, path = source_str.split("::", 1)
        path = Path(path)
    else:
        path = Path(source_str)
        format = path.suffix.lstrip(".")
    return {"format": format, "path": path}


def load(source):
    format = source["format"]
    try:
        load, _ = SUFFIXES[format]
    except KeyError:
        raise ValueError(f"unknown format: {format}") from None
    return load(source)


def dump(source, mdl):
    """
    :raise ValueError:
      The source type is unrecognized.
    :raise NotImplementedError:
      The format used for `mdl` does not support dumping.
    """
    format = source["format"]
    if format is None:
        raise NotImplementedError(f"can't write with format {format}")
    try:
        _, dump = SUFFIXES[format]
    except KeyError:
        raise ValueError(f"unknown format: {format}") from None
    return dump(mdl)


def open(source_str):
    """
    Loads a model based on a source string.
    """
    source = make_source(source_str)
    mdl = load(source)
    mdl.source = source
    return mdl



#-------------------------------------------------------------------------------
# Commands

@command()
def save(mdl):
    # FIXME: Confirm overwrite.
    dump(mdl.source, mdl)
    # FIXME: Include source in message.
    return CmdResult(msg="saved")


@command()
def save_as(mdl, filename):
    if filename == "":
        raise CmdError("empty filename")

    mdl.source = make_source(filename)
    return save(mdl)


