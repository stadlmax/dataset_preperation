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

if [ -d ${dataset_path}/kitti ]; then
    echo "Linking kitti dataset....";
    if [ ! -d ${detectron_path}/detectron/datasets/data/kitti ]; then
        mkdir -p ${detectron_path}/detectron/datasets/data/kitti;
    fi
    
    ln -s ${dataset_path}/kitti/testing ${detectron_path}/detectron/datasets/data/kitti/testing;
    ln -s ${dataset_path}/kitti/training ${detectron_path}/detectron/datasets/data/kitti/training;
    ln -s ${dataset_path}/kitti/JsonAnnotations ${detectron_path}/detectron/datasets/data/kitti/annotations;
fi

