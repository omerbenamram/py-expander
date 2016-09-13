import errno
import os
import shutil
import subprocess

import logbook

from . import config
from .categorize import get_categorized_path
from .subtitles import find_file_subtitles

logger = logbook.Logger('post_process')


def _create_destination_path(directory_path):
    """
    Verifies that current path exists and if it doesn't, creates the path.

    :param directory_path: The directory path to create.
    """
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            logger.info('Creating directory {}'.format(directory_path))
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                logger.exception('Failed to create directory {}'.format(directory_path))
                raise


def process_file(handler, torrent_name, file_path):
    """
    Processes a single file with the given handler.

    :param handler: The handler to use.
    :param torrent_name: The relevant torrent name.
    :param file_path: The file path to process.
    """
    filename = os.path.basename(file_path)
    category_path = get_categorized_path(os.path.join(torrent_name, filename))
    if category_path is not None:
        destination_dir = os.path.join(category_path, torrent_name)
        # Creates target directory (of category path).
        _create_destination_path(destination_dir)
        destination_path = os.path.join(destination_dir, filename)
        try:
            # Move\Copy all relevant files to their location (keep original files for uploading).
            handler(file_path, destination_path)
            logger.info('{} {} to {}'.format(handler.__name__, file_path, destination_path))
            if os.name != 'nt':
                subprocess.check_output(['chmod', config.EXTRACTION_FILES_MASK, '-R', destination_dir])
            # Get subtitles.
            if config.SHOULD_FIND_SUBTITLES:
                find_file_subtitles(destination_path)
        except OSError as e:
            logger.exception('Failed to {} {}: {}'.format(handler.__name__, file_path, e))


def _handle_directory(directory, handler, torrent_name):
    """
    The main directory processing function.
    It's called by the _choose_handler function with the proper handling command for the
    files to process (copy/move).
    It searches for files in the directories matching the known extensions and moves them to
    the relevant path in the destination (/path/category/torrent_name).

    :param directory: The directory to process.
    :param handler: The handler to use.
    :param torrent_name: The relevant torrent name.
    """
    for directory_path, _, file_names in os.walk(directory):
        logger.info('Processing Directory {}'.format(directory_path))
        for filename in file_names:
            process_file(handler, torrent_name, os.path.join(directory_path, filename))


def process_directory(directory):
    """
    Chooses between copying and moving RARs (to conserve the original torrent files).

    :param directory: The directory to process.
    """
    torrent_name = os.path.basename(os.path.dirname(directory))
    logger.info('Processing directory {} for torrent {}'.format(directory, torrent_name))
    # If directory has extracted RARs.
    directories_list = os.listdir(directory)
    if config.EXTRACTION_TEMP_DIR_NAME in directories_list:
        _handle_directory(os.path.join(directory, config.EXTRACTION_TEMP_DIR_NAME), shutil.move, torrent_name)
    # If directory has content only.
    else:
        _handle_directory(directory, shutil.move, torrent_name)
