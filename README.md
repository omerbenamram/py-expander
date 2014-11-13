py-expander
===========

A python script designed to post-process Transmission torrents.

The script extracts files recursively (if extract is necessary)
and the moves the files to pre-configured folders based on their type.
If no rars are present in the download - the script will copy the files.

The script relies on the 'guessit' package to detect movies/tv downloads.

Original torrent files are conserved for upload.

I recommend using this script with couchpotato/sickbeard/headphones since they
provide additional awesome post-processing features!

* Currently only 7-Zip is supported. (Make sure to use the version with the rar plugin, or compile from source with 'make all')

Usage
===========
Install the script as follows:

	$ python setup.py develop

Edit the configuration with your folders

	$ vim config.py

That's it.

The script can be used from the command line:

	$ pyexpand /download/The.Wire.S01E01.HDTV

or for transmission:

	$ vim /var/lib/transmission/settings.json
	..
	 "script-torrent-done-enabled": true,
     "script-torrent-done-filename": "pyexpand",
    ..

* Make sure that the transmission user can run `pyexpand`. If not:

	$ ln -s /usr/local/bin/pyexpand /usr/bin/pyexpand
