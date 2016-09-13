import datetime
import os

import logbook
import subliminal
from subliminal.cache import region
from subliminal.cli import dirs, cache_file, MutexLock
from subliminal.subtitle import get_subtitle_path

from .config import LANGUAGES_MAP

logger = logbook.Logger('subtitles')


def find_file_subtitles(path):
    """
    Finds subtitles for the given video file path.

    :param path: The path of the video file to find subtitles to.
    """
    logger.info('Searching subtitles for file: {}'.format(path))
    try:
        # Get required video information.
        video = subliminal.scan_video(path)
        other_languages = []
        subtitle_results = []
        for language, providers in LANGUAGES_MAP.items():
            # Filter providers the user didn't ask for.
            if not providers:
                other_languages.append(language)
            else:
                current_result = subliminal.download_best_subtitles(
                    {video}, languages={language}, providers=providers).values()
                if len(current_result) > 0:
                    subtitle_results.extend(list(current_result)[0])
        # Download all other languages.
        for language in other_languages:
            current_result = subliminal.download_best_subtitles({video}, languages={language}).values()
            if len(current_result) > 0:
                subtitle_results.extend(list(current_result)[0])
        # Handle results.
        if len(subtitle_results) == 0:
            logger.info('No subtitles were found. Moving on...')
        else:
            logger.info('Found {} subtitles. Saving files...'.format(len(subtitle_results)))
            # Save subtitles alongside the video file.
            results_list = list()
            for subtitles in subtitle_results:
                # Filter empty subtitles files.
                if subtitles.content is None:
                    logger.debug('Skipping subtitle {}: no content'.format(subtitles))
                    continue
                subtitles_path = get_subtitle_path(video.name, subtitles.language)
                logger.info('Saving {} to: {}'.format(subtitles, subtitles_path))
                open(subtitles_path, 'wb').write(subtitles.content)
                results_list.append(subtitles_path)
    except ValueError:
        # Subliminal raises a ValueError if the given file is not a video file.
        logger.info('Not a video file. Moving on...')


def configure_subtitles_cache():
    """
    Configure the subliminal cache settings.
    Should be called once when the program starts.
    """
    # Configure the subliminal cache.
    cache_dir = dirs.user_cache_dir
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    cache_file_path = os.path.join(cache_dir, cache_file)
    region.configure('dogpile.cache.dbm', expiration_time=datetime.timedelta(days=30),
                     arguments={'filename': cache_file_path, 'lock_factory': MutexLock})
