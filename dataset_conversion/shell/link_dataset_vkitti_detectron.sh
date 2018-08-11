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

if [ -d "${dataset_path}/vkitti" ]; then
    echo "Linking vkitti dataset....";
    if [ ! -d ${detectron_path}/detectron/datasets/data/vkitti ]; then
        mkdir -p ${detectron_path}/detectron/datasets/data/vkitti;
    fi
    
    ln -s ${dataset_path}/vkitti/Images ${detectron_path}/detectron/datasets/data/vkitti/Images;
    ln -s ${dataset_path}/vkitti/JsonAnnotations ${detectron_path}/detectron/datasets/data/vkitti/annotations;
fi

