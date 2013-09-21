#!/usr/bin/python
__author__ = 'omerba'

import os
import errno
import shutil
import subprocess
import logging
import re
import itertools

from pyexpander import config


logging.basicConfig(filename=config.LOGFILE, filemode='ab', level=logging.DEBUG)

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


def _choose_handler(folder, torrent_name):
    """
    This function chooses between copying and moving rars (to conserve the original torrent files)
    :param folder:
    :type folder: str
    """

    # If folder has extracted rars...
    listdir = os.listdir(folder)
    if config.EXTRACTION_TEMP_DIR_NAME in listdir:
        _handle_directory(os.path.join(folder, config.EXTRACTION_TEMP_DIR_NAME), shutil.move, torrent_name)

    # If folder has content only
    else:
        _handle_directory(folder, shutil.copy, torrent_name)


def _cleanup_temp(folder):
    """
    This function searches for the subdirectory created for extraction and deletes it.

    :param folder:
    """
    logging.info('Cleaning up...')

    listdir = os.listdir(folder)

    if config.EXTRACTION_TEMP_DIR_NAME in listdir:
        try:
            logging.info('Going to delete %s' % (os.path.join(folder, config.EXTRACTION_TEMP_DIR_NAME)))
            shutil.rmtree(os.path.join(folder, config.EXTRACTION_TEMP_DIR_NAME))
        except OSError:
            logging.exception("Failed to delete directory %s ! " %
                              (os.path.join(folder, config.EXTRACTION_TEMP_DIR_NAME)))


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
        return None


def main():
    """
    This main function is designed to be called by transmission.

    """
    try:
        logging.info('Initializing')

        #Get environmental values from transmission
        #Path should be $TR_TORRENT_DIR/$TR_TORRENT_NAME

        TORRENT_DIR, TORRENT_NAME = config.get_environmental_variables_from_transmission()

        extract_all(TORRENT_DIR)
        _choose_handler(TORRENT_DIR, TORRENT_NAME)
        _cleanup_temp(TORRENT_DIR)
        logging.info('Done!')
    except:
        logging.exception("Critical exception occurred: ")
        raise


if __name__ == "__main__":
    main()


