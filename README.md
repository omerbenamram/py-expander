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

* Currently only 7-Zip is supported.
