"""
General-purpose code.
"""

# FIXME: We shouldn't have a catch-all package!

#-------------------------------------------------------------------------------

def if_none(val, default):
    """
    Returns `val`, or `default` if `val` is `None`.
    """
    return default if val is None else val


def clip(min_val, val, max_val):
    """
    Returns `val` clipped to `min_val` and `max_val`.
    """
    return max(min_val, min(val, max_val))


