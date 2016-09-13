import os

import logbook

logger = logbook.Logger('transmission')


def get_environment_variables_from_transmission():
    """
    Return the environment variables passed by transmission to the script.

    :return: A tuple of format: (full_torrent_path, torrent_name).
    """
    torrent_dir = os.getenv('TR_TORRENT_DIR')
    torrent_name = os.getenv('TR_TORRENT_NAME')

    if torrent_dir is None or torrent_name is None:
        raise Exception('Transmission environment variables were not found.')

    full_path = os.path.join(torrent_dir, torrent_name)

    logger.info('Called from transmission with torrent {}'.format(full_path))

    return full_path
