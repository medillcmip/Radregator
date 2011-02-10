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

psql -t $DBNAME $USERNAME -c "SELECT 'DROP TABLE ' || n.nspname || '.' ||
c.relname || ' CASCADE;' FROM pg_catalog.pg_class AS c LEFT JOIN
pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace WHERE relkind =
'r' AND n.nspname NOT IN ('pg_catalog', 'pg_toast') AND
pg_catalog.pg_table_is_visible(c.oid)" > radbackups/droptables

psql $DBNAME $USERNAME -f radbackups/droptables
