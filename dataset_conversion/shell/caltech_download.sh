#!/bin/sh

#####################################
#download caltech dataset and process
# pass path/to/datasets into script

cd "$1" 

printf "Download: caltech_pedestrian dataset\n"
if [ ! -d caltech_pedestrian ]; then
    mkdir caltech_pedestrian 
fi

cd caltech_pedestrian

wget "http://www.vision.caltech.edu.s3-us-west-2.amazonaws.com/Image_Datasets/CaltechPedestrians/datasets/USA/annotations.zip"
unzip annotations.zip
rm annotations.zip

for i in $(seq -f "%02g" 0 10); do
wget "http://www.vision.caltech.edu.s3-us-west-2.amazonaws.com/Image_Datasets/CaltechPedestrians/datasets/USA/set${i}.tar"; 
tar xvf set${i}.tar;
rm set${i}.tar;
done

wget http://datasets.d2.mpi-inf.mpg.de/caltech_new_annos/Caltech_new_annotations.zip
unzip Caltech_new_annotations.zip
rm Caltech_new_annotations.zip

sudo mv ./anno_test_1xnew ./annotations
sudo mv ./anno_train_1xnew ./annotations

cd ..
printf "Download finished!.\n"
