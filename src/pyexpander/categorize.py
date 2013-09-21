import os
import guessit

from pyexpander import config
from pyexpander.log import get_logger


logger = get_logger('categorize')


MUSIC_EXTENSIONS = ['.flac', '.mp3', '.ogg', '.wav']
SOFTWARE_EXTENSIONS = ['.iso', '.exe']


def get_path_video(filename):
    guess = guessit.guess_video_info(filename)

    if guess[u'type'] == u'episode':
        series = guess.get(u'series', u'').title()
        season = guess.get(u'season', u'')

        return config.TV_PATH.format(series=series, season=season)
    elif guess[u'type'] == u'movie':
        title = guess.get(u'title', u'').title()
        year = guess.get(u'year', u'')

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
    :param filename:
    "filename.ext"
    :rtype : tuple or None
    """
    categorized_path = get_path_non_video(filename) or get_path_video(filename)

    if categorized_path is not None:
        logger.debug("Categorized path for %s is %s" % (filename, categorized_path))
    else:
        # file is not recognized by any of the categories/checks.
        logger.debug("%s is not in any relevant category, ignoring" % filename)

    return categorized_path
