import os


def find_executable(filename):
    """
    Searches for a file in paths exported to the PATH environmental variable.

    :param filename: The file to search for.
    :return: The full executable path.
    """
    # Search the system path for the executable
    if os.name == 'nt':
        filename += '.exe'
    for directory in os.getenv('PATH').split(os.pathsep):
        # Ensure the directory in the path is a real directory.
        if os.path.exists(directory):
            files = os.listdir(directory)
            if filename in files:
                return os.path.join(directory, filename)
    raise Exception('{} not found or is not in system PATH'.format(filename))
