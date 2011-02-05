#!/bin/bash

USERNAME='postgres'

if [ -z "$1" ]; then
    echo "USAGE: $0 <name-of-database-file>"
    echo "(you can list them with ./aws ls radbackups)"
    exit
fi

filename=radbackups/$1
./aws get $filename $filename
psql -U$USERNAME < $filename
echo "DONE"


