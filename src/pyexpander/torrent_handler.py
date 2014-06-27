#!/usr/bin/python2.7
import os
import sys
import shutil

from pyexpander.extract import extract_all, cleanup_temp
from pyexpander.log import get_logger
from pyexpander.postprocess import process_folder, process_file
from pyexpander.transmission import get_environmental_variables_from_transmission


logger = get_logger('handler')


def expand_torrent(torrent_path):
    logger.info('Processing torrent %s' % torrent_path)

    if os.path.isdir(torrent_path):
        torrent_path = os.path.join(os.path.abspath(torrent_path), '')
        extract_all(torrent_path)
        process_folder(torrent_path)
        cleanup_temp(torrent_path)
    else:
        process_file(shutil.copy, os.path.basename(torrent_path), torrent_path)

    logger.info('Done')


def expand_torrent_from_transmission():
    """
    This main function is designed to be called by transmission.
    """
    torrent_path = get_environmental_variables_from_transmission()

    expand_torrent(torrent_path)


def expand_torrent_main():
    """
    This main function is designed to be called from commandline.
    If an argument is provided, the script will try to expand it.
    Else, we assume transmission is calling the script.
    """
    try:
        if len(sys.argv) == 2:
            torrent_path = sys.argv[1]
            expand_torrent(torrent_path)
        else:
            expand_torrent_from_transmission()
    except:
        logger.exception("Critical exception occurred: ")
        raise
