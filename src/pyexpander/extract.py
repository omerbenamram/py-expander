import shutil
import os
import re
import subprocess

from . import config
from .log import get_logger
from .utils import find_executable


logger = get_logger('extractor')


ARCHIVE_EXTENSIONS = ['.rar', '.zip', '.7z']


def _extract(archive_path, destination):
    """
    Extract archive content to destination
    :param  archive_path:
    :type archive_path: str
    :param  destination:
    :type destination: str
    """
    # 'e': extract to current working dir
    # '-y': assume yes to all (overwrite)
    process_info = [find_executable(config.EXTRACTION_EXECUTABLE), 'e', '-y', archive_path]

    logger.debug('Running {}'.format(process_info))

    # Change current working directory since 7Zip only works with e flag.
    output = subprocess.check_output(process_info, cwd=destination)

    logger.debug('Output: {}'.format(output))


def _find_target_archives(directory):
    """
    Look for archives in source_dir + subdirectories.
    Returns archive to extract
    :param directory:
    :type directory: str
    :rtype: list
    """
    archives_list = []
    for dir_path, _, file_names in os.walk(directory):
        for f in file_names:
            candidate_extension = os.path.splitext(f)[1]
            if candidate_extension in ARCHIVE_EXTENSIONS:
                logger.debug('Found archive {} in {}'.format(os.path.join(dir_path, f), directory))
                archives_list.append(os.path.join(dir_path, f))

    # Deals with redundant part01.rar part02.rar etc..
    def _redundant_parts_filter(file_name):
        match = re.search("part(?P<part_num>\d+).rar", file_name, re.IGNORECASE)

        # if parts pattern is not present, leave object unfiltered
        if not match:
            return True

        # if match, return true only if int value is 1
        if int(match.group('part_num')) == 1:
            return True

        logger.debug('{} is redundant - not extracting'.format(file_name))
        return False

    after_parts_filtration = filter(_redundant_parts_filter, archives_list)

    return list(after_parts_filtration)


def extract_all(folder):
    """
    recursively extracts all archives in folder.
    recursive extraction is iterative and is saved under

    /folder/config.EXTRACTION_TEMP_DIR_NAME/unpacked_%iteration number

    :param folder:
    """
    current_dir = folder
    archives_to_extract = _find_target_archives(current_dir)

    if len(archives_to_extract) > 0:
        iteration = 1
        extracted_root = os.path.join(folder, config.EXTRACTION_TEMP_DIR_NAME)
        os.mkdir(extracted_root)

        while len(archives_to_extract) > 0:
            current_dir = os.path.join(extracted_root, 'unpacked_{}'.format(iteration))
            os.mkdir(current_dir)

            for target_archive in archives_to_extract:
                logger.info("Extracting {} to {}".format(target_archive, current_dir))
                _extract(target_archive, current_dir)

            iteration += 1
            archives_to_extract = _find_target_archives(current_dir)

    else:
        logger.info("Found no archives in {}!".format(current_dir))


def cleanup_temp(folder):
    """
    This function searches for the subdirectory created for extraction and deletes it.

    :param folder:
    """
    logger.info('Cleaning up...')

    listdir = os.listdir(folder)

    if config.EXTRACTION_TEMP_DIR_NAME in listdir:
        try:
            logger.info('Going to delete {}'.format(os.path.join(folder, config.EXTRACTION_TEMP_DIR_NAME)))
            shutil.rmtree(os.path.join(folder, config.EXTRACTION_TEMP_DIR_NAME))
        except OSError:
            logger.exception("Failed to delete directory {}!".format(os.path.join(
                folder, config.EXTRACTION_TEMP_DIR_NAME)))
