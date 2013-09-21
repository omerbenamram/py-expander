#!/usr/bin/python
import logging

from pyexpander.extract import extract_all, cleanup_temp
from pyexpander.postprocess import process_folder
from pyexpander.transmission import get_environmental_variables_from_transmission


def expand_torrent(torrent_path):
    logging.info('Processing torrent %s' % torrent_path)

    extract_all(torrent_path)
    process_folder(torrent_path)
    cleanup_temp(torrent_path)

    logging.info('Done')


def expand_torrent_from_transmission():
    """
    This main function is designed to be called by transmission.
    """
    try:
        logging.info('Initializing')

        torrent_path = get_environmental_variables_from_transmission()

        expand_torrent(torrent_path)
    except:
        logging.exception("Critical exception occurred: ")
        raise


