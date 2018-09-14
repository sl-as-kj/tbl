import csv
from   pathlib import Path

from   .commands import command, CmdResult, CmdError
from   .model import Model

#-------------------------------------------------------------------------------

class Source:
    """
    Method for loading, and optionally dumping, a table.

    This class is for documentation purposes only.  Source classes don't need to
    inherit from it.
    """

    # Mapping from source names to source types.
    TYPES = {}

    # Mapping from file suffixes to source types.
    FILE_SUFFIXES = {}


    def __str__(self):
        """
        User-visible representation of the source.
        """

    @classmethod
    def parse(Class, source_str):
        """
        Parses a source from the source string.
        """

    def load(self) -> Model:
        """
        Reads a model.
        """

    def dump(self, mdl: Model):
        """
        Writes a model.

        :raise NotImplemented:
        """
        


class CSVSource(Source):

    def __init__(self, path):
        self.__path = Path(path)


    def __str__(self):
        return str(self.__path)


    @classmethod
    def parse(Class, source_str):
        return Class(source_str)


    def load(self):
        # FIXME: For now, use pandas to load and convert CSV files.
        import pandas as pd
        df = pd.read_csv(self.__path)
        return Model(cols={ n: df[n] for n in df.columns })


    def dump(self, mdl):
        with open(self.__path, "w") as file:
            writer = csv.writer(file)
            # Write header.
            header = [ col.name for col in mdl.cols ]
            writer.writerow(header)
            # Write rows.
            for row_num in range(mdl.num_rows):
                row = [ str(c.arr[row_num]) for c in mdl.cols ]
                writer.writerow(row)



Source.TYPES["csv"] = CSVSource
Source.FILE_SUFFIXES[".csv"] = CSVSource


#-------------------------------------------------------------------------------

def make_source(source_str):
    """
    Constructs a source from a path string.
    """
    if "::" in source_str:
        source_name, source_str = source_str.split("::", 1)
        try:
            Src = Source.TYPES[source_name]
        except KeyError:
            raise ValueError(f"unknown source type: {source_name}") from None
        return Src.parse(source_str)

    else:
        # Assume it's a path, and take the path from the file suffix.
        path = Path(source_str)
        try:
            Src = Source.FILE_SUFFIXES[path.suffix]
        except KeyError:
            raise ValueError(
                f"unknown source for suffix: {path.suffix}") from None
        else:
            return Src(path)


def open(source_str):
    """
    Loads a model based on a source string.
    """
    source = make_source(source_str)
    mdl = source.load()
    mdl.source = source
    return mdl


#-------------------------------------------------------------------------------
# Commands

@command()
def save(mdl):
    # FIXME: Confirm overwrite.
    mdl.source.dump(mdl)
    return CmdResult(msg=f"saved: {mdl.source}")


@command()
def save_as(mdl, source_str):
    if source_str == "":
        raise CmdError("no source given")

    mdl.source = make_source(source_str)
    return save(mdl)


