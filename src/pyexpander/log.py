import logbook
from logbook import Logger

from pyexpander import config


filehandler = logbook.RotatingFileHandler(config.LOGFILE, level=logbook.DEBUG)


def get_logger(name):
    """
    Return the logger for the given name.

    :param name: The name of the logger.
    :return: A logbook Logger.
    """
    logger = Logger(name, level=logbook.DEBUG)
    logger.handlers.append(filehandler)
    return logger