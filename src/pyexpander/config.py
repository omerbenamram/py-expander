"""
Created on Jan 27, 2013

@author: Omer
"""

import os
import sys

CATEGORY_PATH = {'tv': '/path/to/tv/directory',
                 'movie': '/path/to/movies/directory',
                 'app': '/path/to/apps/directory',
                 'music': '/path/to/music/directory'}

LOGFILE = '/path/to/log.log'

EXTRACTION_TEMP_DIR_NAME = '_extracted'



def _find_executable(filename):
    """
    Searches for a file in paths exported to the PATH environmental variable
    :param filename:
    """
    # Search the system path for the executable
    if sys.platform == 'win32':
        filename += '.exe'
    for directory in os.getenv('PATH').split(os.pathsep):
        # Ensure the directory in the path is a real directory
        if os.path.exists(directory):
            files = os.listdir(directory)
            if filename in files:
                # print 'Found ' + filename +' in ' + directory
                return os.path.join(directory, filename)
        else:
            # The directory in the path does not exist
            pass
    raise Exception(filename + 'not found or is not in system PATH')


EXECUTABLE = _find_executable('7z')  # Currently only 7z is supported.

