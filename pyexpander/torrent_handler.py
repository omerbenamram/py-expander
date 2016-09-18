#!/usr/local/bin/python3.5
import os
import shutil
import sys

import logbook

from pyexpander import config
from pyexpander.extract import extract_all, cleanup_temp
from pyexpander.postprocess import process_directory, process_file
from pyexpander.subtitles import configure_subtitles_cache
from pyexpander.transmission import get_environment_variables_from_transmission

logger = logbook.Logger('handler')


def _get_log_handlers():
    """
    Initializes all relevant log handlers.

    :return: A list of log handlers.
    """
    return [
        logbook.NullHandler(),
        logbook.StreamHandler(sys.stdout, level=logbook.DEBUG, bubble=True),
        logbook.RotatingFileHandler(config.LOGFILE, level=logbook.DEBUG, max_size=5 * 1024 * 1024, bubble=True)
    ]


def expand_torrent(torrent_path):
    """
    Perform torrent expansion steps - extraction, moving to relevant directory and cleanup.

    :param torrent_path: The torrent path to expand.
    """
    logger.info('Processing torrent {}'.format(torrent_path))
    torrent_path = os.path.abspath(torrent_path)

    if os.path.isdir(torrent_path):
        # Make sure the path ends with a separator.
        torrent_path = os.path.join(torrent_path, '')
        extract_all(torrent_path)
        process_directory(torrent_path)
        cleanup_temp(torrent_path)
    else:
        process_file(shutil.move, os.path.splitext(os.path.basename(torrent_path))[0], torrent_path)
    logger.info('Done!')


def expand_torrent_from_transmission():
    """
    Expand a torrent when called directly from transmission (by using environment variables).
    """
    torrent_path = get_environment_variables_from_transmission()
    expand_torrent(torrent_path)


def main():
    """
    This function is designed to be called from command line.
    If an argument (either as the full path, or as a base dir and a file) is provided,
    the script will try to expand it.
    Else, we assume transmission is calling the script.
    """
    with logbook.NestedSetup(_get_log_handlers()).applicationbound():
        logger.info('Py-expander started!')
        try:
            # Set subliminal cache first.
            if config.SHOULD_FIND_SUBTITLES:
                logger.debug('Setting subtitles cache...')
                configure_subtitles_cache()
            # Parse input arguments.
            if len(sys.argv) == 3:
                directory = sys.argv[1]
                filename = sys.argv[2]
                if directory == config.DEFAULT_PATH:
                    torrent_path = os.path.join(directory, filename)
                    logger.info('Input is a file: {}'.format(torrent_path))
                else:
                    torrent_path = directory
                    logger.info('Input is a dir: {}'.format(torrent_path))
                expand_torrent(torrent_path)
            elif len(sys.argv) == 2:
                expand_torrent(sys.argv[1])
            else:
                expand_torrent_from_transmission()
        except:
            logger.exception('Critical exception occurred!')
            raise


if __name__ == '__main__':
    main()
