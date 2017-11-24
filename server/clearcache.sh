# !/usr/bin/sh

if [ "$0" != "./clearcache.sh" ]
then 
    echo "Run this script from /server/ directory only!"
else
    # Remove database and imagedata.json from same folder
    rm data.db
    rm imagedata.json
    # Remove all cheque images
    rm static/img/*.jpg
fi