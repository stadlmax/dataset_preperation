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

if [ -d "${dataset_path}/coco" ]; then
    echo "Linking coco dataset....";
    
    if [ ! -d ${detectron_path}/detectron/datasets/data/coco ]; then
        mkdir -p ${detectron_path}/detectron/datasets/data/coco;
    fi
    
    ln -s ${dataset_path}/coco/coco_test2014 ${detectron_path}/detectron/datasets/data/coco/;
    ln -s ${dataset_path}/coco/coco_train2014 ${detectron_path}/detectron/datasets/data/coco/;
    ln -s ${dataset_path}/coco/coco_val2014 ${detectron_path}/detectron/datasets/data/coco/;
    ln -s ${dataset_path}/coco/annotations ${detectron_path}/detectron/datasets/data/coco/annotations;
fi

