import os
import re

from pyexpander import config
from pyexpander.log import get_logger


logger = get_logger('categorize')


VIDEO_EXTENSIONS = ['.mkv', '.avi', '.mov', 'mp4']
MUSIC_EXTENSIONS = ['.flac', '.mp3', '.ogg', '.wav']
SOFTWARE_EXTENSIONS = ['.iso', '.exe']


TV_RE = re.compile("S\d{2}E\d{2}", re.IGNORECASE)


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
        logger.debug("%s is not in any relevant category, ignoring" % filename)
        return None, None
