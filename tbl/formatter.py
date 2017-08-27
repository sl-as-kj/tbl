import logging

try:
    from fixfmt.numpy import choose_formatter

except ImportError:
    # Not available.
    logging.warning("fixfmt not available")

    def choose_formatter(arr):
        width = max( len(str(a)) for a in arr )
        fmt = lambda v: str(v)[: width] + " " * (width - len(str(v)[: width]))
        fmt.width = width
        return fmt

