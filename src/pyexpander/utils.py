import sys
import os


def find_executable(filename):
    """
    Searches for a file in paths exported to the PATH environmental variable
    :param filename: The file to search for.
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
    raise Exception(filename + ' not found or is not in system PATH')

