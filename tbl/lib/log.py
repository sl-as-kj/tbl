from   contextlib import contextmanager
import logging
import sys

#-------------------------------------------------------------------------------

@contextmanager
def replay(logger=None, handler=None):
    """
    Context manager that captures and replays log messages.

    Installs an additional log handler to `logger` that captures all log
    messages.  At exit, replays them to `handler`.

    @param logger
      The logger to capture logging from; `None` for the root logger.
    @param handler
      The handler to use when replaying messages on exit.
    """
    if logger is None:
        logger = logging.getLogger()
    if handler is None:
        handler = logging.StreamHandler(sys.stderr)

    # Create a log handler that just stores up records.
    records = []
    class Handler(logging.Handler):
        def emit(self, record):
            records.append(record)

    # Install it.
    replay_handler = Handler()
    logger.handlers.append(replay_handler)

    try:
        # Run the context.
        yield

    finally:
        # Remove our handler.
        logger.handlers.remove(replay_handler)
        # Replay the logs.
        for record in records:
            handler.emit(record)


