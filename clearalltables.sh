#!/bin/bash

#requires the .pgpass file to be set in the user's home directory
#http://developer.postgresql.org/pgdocs/postgres/libpq-pgpass.html
#make sure you're pg_hba.conf file local auth method is set to 
#http://developer.postgresql.org/pgdocs/postgres/auth-pg-hba-conf.html
if [ -z "$1" ]; then
    echo "USAGE: $0 <db_name> <username>"
    echo "Please specify the name of the database to restore"
    exit
fi

if [ -z "$2" ]; then
    echo "USAGE: $0 <db_name> <username>"
    echo "Please specify the user name"
    exit
fi
DBNAME=$1
USERNAME=$2

psql $DBNAME $USERNAME < dropalltables.sql
