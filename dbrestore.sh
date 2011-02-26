#!/bin/bash

#requires the .pgpass file to be set in the user's home directory
#http://developer.postgresql.org/pgdocs/postgres/libpq-pgpass.html
#make sure you're pg_hba.conf file local auth method is set to 
#http://developer.postgresql.org/pgdocs/postgres/auth-pg-hba-conf.html
if [ -z "$1" ]; then
    echo "USAGE: $0 <backup_filename> <db_name> <username>"
    echo "(specify the name of the file to retrieve)"
    exit
fi

if [ -z "$2" ]; then
    echo "USAGE: $0 <backup_filename> <db_name> <username>"
    echo "Please specify the name of the database to restore"
    exit
fi

if [ -z "$3" ]; then
    echo "USAGE: $0 <backup_filename> <db_name> <username>"
    echo "Please specify the user name"
    exit
fi
DBNAME=$2
USERNAME=$3
filename=lfradbackups/$1
./aws get $filename $filename
psql $DBNAME $USERNAME < $filename
rm lfradbackups/*
echo "DONE"
