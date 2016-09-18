import os
import re
import shutil
import subprocess

import logbook

from . import config
from .utils import find_executable

ARCHIVE_EXTENSIONS = ['.rar', '.zip', '.7z']

logger = logbook.Logger('extractor')


def _extract(archive_path, destination):
    """
    Extract archive content to destination.

    :param  archive_path: The archive to extract.
    :param  destination: The destination to extract to.
    """
    # 'e': extract to current working dir.
    # '-y': assume yes to all (overwrite).
    process_info = [find_executable(config.EXTRACTION_EXECUTABLE), 'e', '-y', archive_path]
    logger.debug('Running {}'.format(process_info))
    # Change current working directory since 7Zip only works with e flag.
    output = subprocess.check_output(process_info, cwd=destination)
    logger.debug('Output: {}'.format(output))


def _find_target_archives(directory):
    """
    Look for archives in source_dir + subdirectories.

    :param directory: The directory to look for archives in.
    :return: The list of archives to extract.
    """
    archives_list = []
    for dir_path, _, file_names in os.walk(directory):
        for f in file_names:
            candidate_extension = os.path.splitext(f)[1]
            if candidate_extension in ARCHIVE_EXTENSIONS:
                logger.debug('Found archive {} in {}'.format(os.path.join(dir_path, f), directory))
                archives_list.append(os.path.join(dir_path, f))
    # Filter out redundant part files.
    filtered_archives_list = []
    for archive_path in archives_list:
        match = re.search('part(?P<part_num>\d+).rar', archive_path, re.IGNORECASE)
        # If parts pattern is not present, or part number is 1, don't filter out the file.
        if not match or int(match.group('part_num')) == 1:
            filtered_archives_list.append(archive_path)
        else:
            logger.debug('{} is redundant - not extracting'.format(archive_path))
    return filtered_archives_list


def extract_all(directory):
    """
    recursively extracts all archives in directory.
    recursive extraction is iterative and is saved under:
    /directory/config.EXTRACTION_TEMP_DIR_NAME/unpacked_{iteration number}

    :param directory: The directory to extract archives from.
    """
    current_dir = directory
    archives_to_extract = _find_target_archives(current_dir)

    if len(archives_to_extract) > 0:
        iteration = 1
        extracted_root = os.path.join(directory, config.EXTRACTION_TEMP_DIR_NAME)
        os.mkdir(extracted_root)

        while len(archives_to_extract) > 0:
            current_dir = os.path.join(extracted_root, 'unpacked_{}'.format(iteration))
            os.mkdir(current_dir)

            for target_archive in archives_to_extract:
                logger.info('Extracting {} to {}'.format(target_archive, current_dir))
                _extract(target_archive, current_dir)

            iteration += 1
            archives_to_extract = _find_target_archives(current_dir)

    else:
        logger.info('Found no archives in {}!'.format(current_dir))


def cleanup_temp(directory):
    """
    This function searches for the subdirectory created for extraction and deletes it.

    :param directory: The directory to clean.
    """
    logger.info('Cleaning up...')
    listdir = os.listdir(directory)
    if config.EXTRACTION_TEMP_DIR_NAME in listdir:
        try:
            logger.info('Going to delete {}'.format(os.path.join(directory, config.EXTRACTION_TEMP_DIR_NAME)))
            shutil.rmtree(os.path.join(directory, config.EXTRACTION_TEMP_DIR_NAME))
        except OSError:
            logger.exception('Failed to delete directory {}!'.format(os.path.join(
                directory, config.EXTRACTION_TEMP_DIR_NAME)))
