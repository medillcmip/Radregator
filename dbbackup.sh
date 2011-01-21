
#!/bin/bash

outfile=radbackups/`date "+%Y%m%d".json`

# Dump the data
./manage.py dumpdata auth clipper core tagger users  > $outfile

# And put it somewhere
# This requires ~/.awssecret have "access key \n secret key"
./aws put $outfile $outfile

