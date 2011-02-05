#!/bin/bash

USERNAME='postgres'
DBNAME='localfourth'
outfile=radbackups/`date "+%Y%m%d".sql`


# Dump the data
pg_dump -U$USERNAME $DBNAME  > $outfile

# And put it somewhere
# This requires ~/.awssecret have "access key \n secret key"
./aws put $outfile $outfile

