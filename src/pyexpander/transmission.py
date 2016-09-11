import os
from .log import get_logger


logger = get_logger('transmission')


def get_environmental_variables_from_transmission():
    """
    Return the environmental variables passed by transmission to the script.

    :return: (full_torrent_path, torrent_name)
    """
    torrent_dir = os.getenv('TR_TORRENT_DIR')
    torrent_name = os.getenv('TR_TORRENT_NAME')

    if torrent_dir is None or torrent_name is None:
        raise Exception('Transmission environment variables were not found.')

    full_path = os.path.join(torrent_dir, torrent_name)

    logger.info('Called from transmission with torrent {}'.format(full_path))

    return full_path
