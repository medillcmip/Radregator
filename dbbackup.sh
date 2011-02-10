#!/bin/bash
#requires the .pgpass file to be set in the user's home directory
#http://developer.postgresql.org/pgdocs/postgres/libpq-pgpass.html
#make sure you're pg_hba.conf file local auth method is set to 
#http://developer.postgresql.org/pgdocs/postgres/auth-pg-hba-conf.html
if [ -z "$1" ]; then
    echo "USAGE: $0 <app_namespace> <db_name> <username>"
    echo "(specify a unique namespace specifying where the backup originates from (e.g. local_shane or testing_1))"
    exit
fi

if [ -z "$2" ]; then
    echo "USAGE: $0 <app_namespace> <db_name> <username>"
    echo "Please specify the name of the database to dump"
    exit
fi

if [ -z "$3" ]; then
    echo "USAGE: $0 <app_namespace> <db_name> <username>"
    echo "Please specify the user name"
    exit
fi

DBNAME=$2
USERNAME=$3
outfile=radbackups/`date "+%Y%m%d"$1.sql`

# Dump the data
pg_dump -U$USERNAME $DBNAME > $outfile

# And put it somewhere
# This requires ~/.awssecret have "access key \n secret key"
./aws put $outfile $outfile

# remove all traces of files
rm radbackups/*
