import os
import sys
import shutil

from pyexpander import config
from pyexpander.extract import extract_all, cleanup_temp
from pyexpander.log import get_logger
from pyexpander.postprocess import process_folder, process_file
from pyexpander.transmission import get_environmental_variables_from_transmission


logger = get_logger('handler')


def expand_torrent(torrent_path):
    logger.info('Processing torrent %s' % torrent_path)
    torrent_path = os.path.abspath(torrent_path)

    if os.path.isdir(torrent_path):
        torrent_path = os.path.join(torrent_path, '')
        extract_all(torrent_path)
        process_folder(torrent_path)
        cleanup_temp(torrent_path)
    else:
        process_file(shutil.move, os.path.splitext(os.path.basename(torrent_path))[0], torrent_path)

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
    If an argument (either as the full path, or as a base dir and a file) is provided,
    the script will try to expand it.
    Else, we assume transmission is calling the script.
    """
    logger.info("Py-expander started!")
    try:		
        if len(sys.argv) == 3:
            folder = sys.argv[1]
            filename = sys.argv[2]
            if folder == config.DEFAULT_PATH:
                torrent_path = os.path.join(folder, filename)
                logger.info("Input is a file: %s" % torrent_path)
            else:
                torrent_path = folder
                logger.info("Input is a dir: %s" % torrent_path)
            expand_torrent(torrent_path)
        elif len(sys.argv) == 2:
            expand_torrent(sys.argv[1])
        else:
            expand_torrent_from_transmission()
    except:
        logger.exception("Critical exception occurred: ")
        raise

if __name__ == '__main__':
    expand_torrent_main()