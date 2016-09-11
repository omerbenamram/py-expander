import sys
import logbook
from logbook import Logger

from . import config


file_handler = logbook.RotatingFileHandler(config.LOGFILE, level=logbook.DEBUG)
console_handler = logbook.StreamHandler(sys.stdout, level=logbook.INFO, bubble=True)

file_handler.push_application()
console_handler.push_application()


def get_logger(name):
    """
    Return the logger for the given name.

    :param name: The name of the logger.
    :return: A logbook Logger.
    """
    logger = Logger(name, level=logbook.DEBUG)
    return logger
