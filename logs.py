import sys
from loguru import logger


FORMAT = (
    '<green>{time:HH:mm:ss.SSS}</green>'
    ' | '
    '<level>{level: <8}</level>'
    ' | '
    '<cyan>{name}</cyan>:'
    # '<cyan>{extra[classname]}</cyan>:'
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


# class ClassLogger:
#     def __init__(self):
#         self.logger = logger.bind(classname=self.__class__.__name__)

#     def __post_init__(self):
#         self.logger = logger.bind(classname=self.__class__.__name__)
