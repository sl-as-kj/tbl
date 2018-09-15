from   .controller import Controller
from   .model import Model
from   .screen import main_loop
from   .view import build_view

__all__ = (
    "show_dataframe",
)

#-------------------------------------------------------------------------------

def show_dataframe(df):
    """
    Shows the interactive curses viewer for a dataframe.
    """
    mdl = Model(cols={ n: df[n] for n in df.columns })
    vw = build_view(mdl)
    ctl = Controller()
    main_loop(mdl, vw, ctl)


