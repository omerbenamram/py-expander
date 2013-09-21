import os
from pyexpander.log import get_logger


logger = get_logger('transmission')


def get_environmental_variables_from_transmission():
    """
    Return the environmental variables passed by tranmission to the script.

    :return: (full_torrent_path, torrent_name)
    """
    torrent_dir = os.getenv('TR_TORRENT_DIR')
    torrent_name = os.getenv('TR_TORRENT_NAME')
    full_path = os.path.realpath(os.path.join(torrent_dir, torrent_name))

    logger.info('Called from transmission with torrent %s' % full_path)

    return full_path

