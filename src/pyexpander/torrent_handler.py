#!/usr/bin/python
import os
import errno
import shutil
import logging
import re

from pyexpander.extract import extract_all, cleanup_temp
from pyexpander import config
from pyexpander.transmission import get_environmental_variables_from_transmission


VIDEO_EXTENSIONS = ['.mkv', '.avi', '.mov', 'mp4']
MUSIC_EXTENSIONS = ['.flac', '.mp3', '.ogg', '.wav']
SOFTWARE_EXTENSIONS = ['.iso', '.exe']


TV_RE = re.compile("S\d{2}E\d{2}", re.IGNORECASE)


def _create_extraction_path(directory_path):
    """
    Verifies that current path exists - if not, creates the path.

    :param directory_path:
    :type directory_path: str, unicode
    """
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            logging.info("Creating directory %s" % directory_path)

        except OSError as e:
            if e.errno != errno.EEXIST:
                logging.exception("Failed to create directory %s" % directory_path, e)
                raise
            pass


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
    for directory_path, subdirectories, filenames in os.walk(directory):
        logging.info("Processing Directory %s" % directory_path)
        for filename in filenames:
            category_path, file_category = get_categorized_path(filename)

            if category_path is not None:

                original_path = os.path.join(directory_path, filename)
                logging.info("Found %s file %s" % (file_category, original_path))

                destination_dir = os.path.join(category_path, torrent_name)
                _create_extraction_path(destination_dir)  # Creates target directory (of category path)
                destination_path = os.path.join(destination_dir, filename)

                try:
                    # Move\Copy all relevant files to their location (keep original files for uploading)
                    handler(original_path, destination_path)
                    logging.info('%s %s to %s' % (handler.__name__, original_path, destination_path))

                except OSError as e:
                    logging.exception("Failed to %s %s : %s" % (handler.__name__, original_path, e))


def _choose_handler(folder):
    """
    This function chooses between copying and moving rars (to conserve the original torrent files)
    :param folder:
    :type folder: str
    """
    torrent_name = os.path.basename(folder)
    # If folder has extracted rars...
    listdir = os.listdir(folder)
    if config.EXTRACTION_TEMP_DIR_NAME in listdir:
        _handle_directory(os.path.join(folder, config.EXTRACTION_TEMP_DIR_NAME), shutil.move, torrent_name)

    # If folder has content only
    else:
        _handle_directory(folder, shutil.copy, torrent_name)


def _is_tv_show(filename):
    """
    Takes filename "file.ext"
    Returns True if file is TV Show based on S01E01 regex
    """
    if TV_RE.search(filename):
        return True
    return False


def _get_content_type(filename):
    """
    returns 'tv', 'movie', 'music', 'app' for respective filetypes
    :rtype : str
    :param filename:
    "filename.ext"
    """
    base_filename = os.path.basename(filename)
    base_filename.lower()
    extension = os.path.splitext(base_filename)[1]
    if extension in VIDEO_EXTENSIONS:
        if base_filename.find('sample') != -1:
            return "vid-sample"
        if _is_tv_show(base_filename):
            return 'tv'
        else:
            return 'movie'
    if extension in MUSIC_EXTENSIONS:
        return 'music'
    if extension in SOFTWARE_EXTENSIONS:
        return 'app'
    else:
        return None


def get_categorized_path(filename):
    """
    returns destination path for extractions according to the category to which the file belongs
    :param filename:
    "filename.ext"
    :rtype : tuple or None
    """
    try:
        return config.CATEGORY_PATH[_get_content_type(filename)], _get_content_type(filename)

    # If file is not recognized by any of the categories/checks - there would be no entry at the
    # config file
    except KeyError:
        logging.debug("%s is not in any relevant category, ignoring" % filename)
        return None, None


def expand_torrent(torrent_path):
    logging.info('Processing torrent %s' % torrent_path)

    extract_all(torrent_path)
    _choose_handler(torrent_path)
    cleanup_temp(torrent_path)

    logging.info('Done')


def main():
    """
    This main function is designed to be called by transmission.
    """
    try:
        logging.info('Initializing')

        torrent_path = get_environmental_variables_from_transmission()

        expand_torrent(torrent_path)
    except:
        logging.exception("Critical exception occurred: ")
        raise


if __name__ == "__main__":
    main()


