#!/bin/sh

#####################################
#download kitty dataset and process
# pass path/to/datasets into script

cd "$1" 

printf "Download: kitti dataset\n"
if [ ! -d kitti ]; then
    mkdir kitti
fi

cd kitti

wget "https://s3.eu-central-1.amazonaws.com/avg-kitti/data_object_image_2.zip"
unzip data_object_image_2.zip
rm -rf data_object_image_2.zip


wget "https://s3.eu-central-1.amazonaws.com/avg-kitti/data_object_label_2.zip"
unzip data_object_label_2.zip
rm -rf data_object_label_2.zip

cd ..
printf "Download finished.\n"
