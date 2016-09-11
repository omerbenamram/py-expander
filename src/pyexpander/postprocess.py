import sys
import os
import errno
import shutil
import subprocess

from . import config
from .categorize import get_categorized_path
from .log import get_logger


logger = get_logger('post_process')


def _create_extraction_path(directory_path):
    """
    Verifies that current path exists - if not, creates the path.

    :param directory_path:
    :type directory_path: str, unicode
    """
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            logger.info("Creating directory {}".format(directory_path))

        except OSError as e:
            if e.errno != errno.EEXIST:
                logger.exception("Failed to create directory {}".format(directory_path), e)
                raise
            pass


def process_file(handler, torrent_name, file_path):
    filename = os.path.basename(file_path)
    category_path = get_categorized_path(os.path.join(torrent_name, filename))
    if category_path is not None:
        destination_dir = os.path.join(category_path, torrent_name)

        # Creates target directory (of category path)
        _create_extraction_path(destination_dir)
        destination_path = os.path.join(destination_dir, filename)

        try:
            # Move\Copy all relevant files to their location (keep original files for uploading)
            handler(file_path, destination_path)

            logger.info('{} {} to {}'.format(handler.__name__, file_path, destination_path))
            if sys.platform != 'win32':
                subprocess.check_output(['chmod', config.EXTRACTION_FILES_MASK, '-R', destination_dir])
        except OSError as e:
            logger.exception("Failed to {} {}: {}".format(handler.__name__, file_path, e))


def _handle_directory(directory, handler, torrent_name):
    """
    This is the main directory processing function.
    It's called by the _choose_handler function with the proper handling command for the
    files to process (copy/move).
    It searches for files in the directories matching the known extensions and moves the to
    the relevant path in the destination (/path/category/torrent_name)

    :param directory:
    :param handler:
    :param torrent_name:
    """
    for directory_path, subdirectories, file_names in os.walk(directory):
        logger.info("Processing Directory {}".format(directory_path))
        for filename in file_names:
            process_file(handler, torrent_name, os.path.join(directory_path, filename))


def process_folder(folder):
    """
    This function chooses between copying and moving rars (to conserve the original torrent files)
    :param folder:
    :type folder: str
    """
    torrent_name = os.path.basename(os.path.dirname(folder))
    logger.info('Processing directory {} for torrent {}'.format(folder, torrent_name))

    # If folder has extracted rars...
    listdir = os.listdir(folder)
    if config.EXTRACTION_TEMP_DIR_NAME in listdir:
        _handle_directory(os.path.join(folder, config.EXTRACTION_TEMP_DIR_NAME), shutil.move, torrent_name)

    # If folder has content only
    else:
        _handle_directory(folder, shutil.move, torrent_name)
