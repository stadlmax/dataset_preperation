#!/bin/sh

#####################################
#download tt100k dataset and process
# pass path/to/datasets into script

cd "$1" 

printf "Download:TT100K dataset\n"
if [ ! -d tt100k ]; then
    mkdir tt100k
fi

cd tt100k

wget "http://cg.cs.tsinghua.edu.cn/traffic-sign/data_model_code/data.zip"
wget "http://cg.cs.tsinghua.edu.cn/traffic-sign/data_model_code/code.zip"
unzip code.zip
unzip data.zip
#contains
#    train: all train pictures
#    test: all test pictures
#    other: some data that exclude from train and test
#    marks: standard traffic sign picture that are used for data agumentation
#    annotations.json: json file which contains the annotations of the pictures
#    results: results of our model and fast-rcnn
 
rm data.zip
rm code.zip
cd ..
printf "Download finished.\n"
