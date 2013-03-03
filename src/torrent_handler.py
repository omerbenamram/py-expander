#!/var/packages/python/target/bin/python

"""
Created on Jan 26, 2013

@author: Omer

"""

import os
import errno
import shutil
import subprocess
import logging
import re
import itertools

import config


logging.basicConfig(filename=config.LOGFILE, filemode='ab', level=logging.DEBUG)

VIDEO_EXTENSIONS = ['.mkv', '.avi', '.mov', 'mp4']
MUSIC_EXTENSIONS = ['.flac', '.mp3', '.ogg', '.wav']
SOFTWARE_EXTENSIONS = ['.iso', '.exe']
ARCHIVE_EXTENSIONS = ['.rar', '.zip', '.7z']

TV_RE = re.compile("S\d{2}E\d{2}", re.IGNORECASE)


def _find_target_archives(directory):
    """
    Look for archives in sourcedir + subdirectories.
    Returns archive to extract
    :param directory:
    :type directory: str
    :rtype: list
    """
    archives_list = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            candidate_extension = os.path.splitext(f)[1]
            if candidate_extension in ARCHIVE_EXTENSIONS:
                logging.debug('Found archive %s in %s' % (os.path.join(dirpath, f), directory))
                archives_list.append(os.path.join(dirpath, f))

    #Deals with redundant part01.rar part02.rar etc..
    def _redundant_parts_filter(file_name):
        match = re.search("part(?P<part_num>\d+).rar", file_name, re.IGNORECASE)

        # if parts pattern is not present, leave object unfiltered
        if not match:
            return True

        # if match, return true only if int value is 1
        if int(match.group('part_num')) == 1:
            return True

        logging.debug('%s is redundant - not extracting' % file_name)
        return False

    after_parts_filtration = itertools.ifilter(_redundant_parts_filter, archives_list)

    return list(after_parts_filtration)


def _extract(archive_path, destination):
    """
    Extract archive content to destination
    :param  archive_path:
    :type archive_path: str
    :param  destination:
    :type destination: str
    """
    extract_job = subprocess.Popen([config.EXECUTABLE,  # 7Zip Executable
                                    'e',  # extract to current working dir
                                    '-y',  # assume yes to all (overwrite)
                                    archive_path],
                                   cwd=destination)              # Change current working directory
    # Since 7Zip only works with e flag..

    extract_job.wait()


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


def extract_all(folder):
    """
    recursively extracts all archives in folder.
    recursive extraction is iterative and is saved under

    /foler/config.EXTRACTION_TEMP_DIR_NAME/unpacked_%iteration number

    :param folder:
    """
    current_dir = folder
    archives_to_extract = _find_target_archives(current_dir)

    if len(archives_to_extract) > 0:
        iteration = 1
        extracted_root = os.path.join(folder, config.EXTRACTION_TEMP_DIR_NAME)
        os.mkdir(extracted_root)

        while len(archives_to_extract) > 0:
            current_dir = os.path.join(extracted_root, 'unpacked_%d' % iteration)
            os.mkdir(current_dir)

            for target_archive in archives_to_extract:
                logging.info("Extracting %s to %s" % (target_archive, current_dir))
                _extract(target_archive, current_dir)

            iteration += 1
            archives_to_extract = _find_target_archives(current_dir)

    else:
        logging.info("Found no archives in %s !" % current_dir)


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


