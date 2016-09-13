import babelfish

# Directories settings.
TV_PATH = '/tv/directory'
MOVIE_PATH = '/movies/directory'
APP_PATH = '/apps/directory'
MUSIC_PATH = '/music/directory'
DEFAULT_PATH = '/'

# Log settings.
LOGFILE = '/var/log/pyexp.log'

# Extraction settings.
EXTRACTION_FILES_MASK = '770'
EXTRACTION_TEMP_DIR_NAME = '_extracted'
EXTRACTION_EXECUTABLE = '7z'

# Subtitle settings.
SHOULD_FIND_SUBTITLES = True
# A map between each language and its favorite subliminal providers (None for all providers).
LANGUAGES_MAP = {
    babelfish.Language('heb'): ['subscenter'],
    babelfish.Language('eng'): []
}
