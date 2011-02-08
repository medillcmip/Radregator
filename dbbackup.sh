#!/bin/bash
if [ -z "$1" ]; then
    echo "USAGE: $0 <name-of-database-key>"
    echo "(specify a db key to preced the file name so we don't overwrite other backups)"
    exit
fi

outfile=radbackups/`date "+%Y%m%d"$1.json`

# Dump the data
./manage.py dumpdata > $outfile

# And put it somewhere
# This requires ~/.awssecret have "access key \n secret key"
./aws put $outfile $outfile

