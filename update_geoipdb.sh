#!/bin/bash

TEMP_FOLDER="/var/tmp/geoipupdate"
UPLOAD_FOLDER="/var/config/rest/downloads"
GEOIP_FILE=$1
GEOIP_MD5="$1.md5"

mkdir -p $TEMP_FOLDER

if [ -f "$UPLOAD_FOLDER/$GEOIP_FILE" ] && [ -f "$UPLOAD_FOLDER/$GEOIP_MD5" ]; then
  mv $UPLOAD_FOLDER/$GEOIP_FILE $TEMP_FOLDER
  mv $UPLOAD_FOLDER/$GEOIP_MD5 $TEMP_FOLDER
else
  echo "Could not find $UPLOAD_FOLDER/$GEOIP_FILE and $UPLOAD_FOLDER/$GEOIP_MD5"
  exit 1s
fi

cd $TEMP_FOLDER

# Test the file integrity
if md5sum --status -c $GEOIP_MD5; then
  unzip $GEOIP_FILE
  for filename in *.rpm; do
      echo "Updating $filename"
      geoip_update_data -f "$filename"
  done
else
  echo "Invalid md5"
fi

if [ -d $TEMP_FOLDER ];then
  rm -rf $TEMP_FOLDER
fi