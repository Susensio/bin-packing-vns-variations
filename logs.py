import sys
from loguru import logger

FORMAT = (
    '<green>{time:HH:mm:ss.SSS}</green>'
    ' | '
    '<level>{level: <8}</level>'
    ' | '
    '[<cyan>{process.name}</cyan>]'
    '<cyan>{name}</cyan>:'
    '<cyan>{extra[classname]}</cyan>:'
    '<cyan>{function}</cyan>:'
    '<cyan>{line}</cyan>'
    ' - '
    '<level>{message}</level>'
)


def config(level):
    """Levels = 'TRACE', 'DEBUG', 'INFO', 'SUCCESS', 'WARNING', 'ERROR', 'CRITICAL'."""
    logger.remove()
    logger.add(sys.stderr, level=level, format=FORMAT)
    logger.configure(extra={"classname": "None"})


def append_logger(cls):
    """Adds self.logger access from inside a class, otherwise class name won't be printed."""

    def _logger(self):
        return logger.bind(classname=self.__class__.__name__)
    cls.logger = property(_logger)
    return cls
