#!/bin/sh

#####################################
# create sym-links of datasets into
# $Detectron/detectron/datasets/data
# $1 is path to Detectron
# $2 is path to datasets

while [ $# -gt 0 ]; do
    case $1 in
    -detectron_path)
        detectron_path=$2
        shift
        ;;
    -dataset_path)
        dataset_path=$2
        shift
        ;;
    *)
        echo "Invalid argument: $1"
        exit 1
    esac
    shift
done

if [ -d "${dataset_path}/caltech_pedestrian" ]; then
    echo "Linking caltech_pedestrian dataset....";
    
    if [ ! -d ${detectron_path}/detectron/datasets/data/caltech_pedestrian ]; then
        mkdir -p ${detectron_path}/detectron/datasets/data/caltech_pedestrian;
    fi
    
    ln -s ${dataset_path}/caltech_pedestrian/train ${detectron_path}/detectron/datasets/data/caltech_pedestrian/train;
    ln -s ${dataset_path}/caltech_pedestrian/test ${detectron_path}/detectron/datasets/data/caltech_pedestrian/test;
    ln -s ${dataset_path}/caltech_pedestrian/JsonAnnotations ${detectron_path}/detectron/datasets/data/caltech_pedestrian/annotations;
fi

