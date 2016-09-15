import os
import subprocess
import posixpath

import logbook
from guessit import guessit

from . import config

logger = logbook.Logger('uploader')


def _sync():
    """
    Perform sync action.
    """
    process = subprocess.run('{} sync'.format(config.ACD_CLI_PATH), shell=True)
    if process.returncode != 0:
        logger.error('Bad return code ({}) for sync'.format(process.returncode))
    else:
        logger.info('Sync succeeded!')


def upload_file(file_path):
    """
    Upload the given file to its proper Amazon cloud directory.

    :param: file_path: The file to upload.
    """
    logger.info('Uploading file: {}'.format(file_path))
    fixed_file_path = file_path
    file_parts = os.path.splitext(file_path)
    # Verify file name.
    if len(file_parts) != 2:
        logger.info('File has no extension! Skipping...')
        return
    file_name, file_extension = file_parts
    if file_extension not in config.EXTENSIONS_WHITE_LIST:
        logger.info('File extension is not in white list! Skipping...')
        return
    for black_list_word in config.NAMES_BLACK_LIST:
        if black_list_word in file_name.lower():
            logger.info('File name contains a black listed word ({})! Skipping...'.format(black_list_word))
            return
    language_extension = None
    is_subtitles = file_extension in config.SUBTITLES_EXTENSIONS
    # Fake extension for subtitles in order to help guessit.
    if is_subtitles:
        # Remove language extensions if needed.
        file_parts = os.path.splitext(file_name)
        if len(file_parts) == 2:
            fixed_file_name, language_extension = file_parts
            if language_extension in config.LANGUAGE_EXTENSIONS:
                fixed_file_path = fixed_file_name + config.DEFAULT_VIDEO_EXTENSION
    # Create cloud path based on guessit results.
    cloud_dir = None
    cloud_file = None
    guess_results = guessit(os.path.basename(fixed_file_path))
    video_type = guess_results.get('type')
    title = guess_results.get('title')
    if video_type == 'episode' and title:
        season = guess_results.get('season')
        if season:
            episode = guess_results.get('episode')
            if episode:
                cloud_dir = '{}/{}/Season {:02d}'.format(config.AMAZON_TV_PATH, title, season)
                cloud_file = '{} - S{:02d}E{:02d}'.format(title, season, episode)
    elif video_type == 'movie' and title:
        year = guess_results.get('year')
        if year:
            cloud_dir = '{}/{} ({})'.format(config.AMAZON_MOVIE_PATH, title, year)
            cloud_file = '{} ({})'.format(title, year)
    if cloud_dir and cloud_file:
        if language_extension:
            cloud_file += language_extension
        cloud_file += file_extension
        logger.info('Cloud path: {}'.format(posixpath.join(cloud_dir, cloud_file)))
        # Rename local file before upload.
        base_dir = os.path.dirname(file_path)
        new_path = os.path.join(base_dir, cloud_file)
        os.rename(file_path, new_path)
        # Sync first.
        _sync()
        # Create cloud dirs.
        logger.info('Creating directories...')
        current_dir = ''
        for directory in cloud_dir.split('/'):
            current_dir += '/{}'.format(directory)
            subprocess.run('{} mkdir "{}"'.format(config.ACD_CLI_PATH, current_dir), shell=True)
        # Upload!
        process = subprocess.run('{} upload -o "{}" "{}"'.format(config.ACD_CLI_PATH, new_path, cloud_dir), shell=True)
        # Check results.
        if process.returncode != 0:
            logger.error('Bad return code ({}) for file: {}'.format(process.returncode, file_path))
        else:
            logger.info('Upload succeeded! Deleting original file...')
            # If everything went smoothly, delete the original file and add its name to the original names log.
            if not is_subtitles:
                open(config.ORIGINAL_NAMES_LOG, 'a', encoding='UTF-8').write(file_path + '\n')
            os.remove(new_path)
            # Sync again when done.
            _sync()
    else:
        logger.info('Couldn\'t guess file info. Skipping...')
