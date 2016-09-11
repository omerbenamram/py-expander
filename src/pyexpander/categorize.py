import os
from guessit import guessit

from . import config
from .log import get_logger


logger = get_logger('categorize')


MUSIC_EXTENSIONS = ['.flac', '.mp3', '.ogg', '.wav']
SOFTWARE_EXTENSIONS = ['.iso', '.exe']


def get_path_video(filename):
    guess = guessit(filename)

    if guess['type'] == 'episode':
        series = guess.get('series', '').title()
        season = guess.get('season', '')

        return config.TV_PATH.format(series=series, season=season)
    elif guess['type'] == 'movie':
        title = guess.get('title', '').title()
        year = guess.get('year', '')

        return config.MOVIE_PATH.format(title=title, year=year)
    else:
        return None


def get_path_non_video(filename):
    base_filename = os.path.basename(filename)
    base_filename.lower()
    extension = os.path.splitext(base_filename)[1]

    if extension in MUSIC_EXTENSIONS:
        return config.MUSIC_PATH
    if extension in SOFTWARE_EXTENSIONS:
        return config.APP_PATH
    else:
        return None


def get_categorized_path(filename):
    """
    returns destination path for extractions according to the category to which the file belongs
    :param filename: The name of the file.
    :rtype : str
    """
    categorized_path = get_path_non_video(filename) or get_path_video(filename)

    if categorized_path is not None:
        logger.debug("Categorized path for {} is {}".format(filename, categorized_path))
    else:
        # file is not recognized by any of the categories/checks.
        logger.debug("{} is not in any relevant category, ignoring".format(filename))

    return categorized_path
