__author__ = 'Ohad'


def get_environmental_variables_from_transmission():
    """
    Return the environmental variables passed by tranmission to the script.

    :return: (torrent_dir, torrent_name)
    """
    TARGET_TORRENT_DIR = os.getenv('TR_TORRENT_DIR')
    TARGET_TORRENT_NAME = os.getenv('TR_TORRENT_NAME')
    TARGET_TORRENT_DIR = os.path.realpath(os.path.join(TARGET_TORRENT_DIR, TARGET_TORRENT_NAME))

    return TARGET_TORRENT_DIR, TARGET_TORRENT_NAME

