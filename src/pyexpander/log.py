__author__ = 'ohadr'


import logbook
from logbook import Logger


#TODO: log to file. logging.basicConfig(filename=config.LOGFILE, filemode='ab', level=logging.DEBUG)
def get_logger(name):
    """
    Return the logger for the given name.

    :param name: The name of the logger.
    :return: A logbook Logger.
    """
    return Logger(name)