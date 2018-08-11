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

if [ -d "${dataset_path}/tt100k" ]; then
    echo "Linking tt100k dataset....";
    
    if [ ! -d ${detectron_path}/detectron/datasets/data/tt100k ]; then
        mkdir -p ${detectron_path}/detectron/datasets/data/tt100k;
    fi
    
    ln -s $dataset_path/tt100k/data/test $detectron_path/detectron/datasets/data/tt100k/test;
    ln -s $dataset_path/tt100k/data/train $detectron_path/detectron/datasets/data/tt100k/train;
    ln -s $dataset_path/tt100k/data/other $detectron_path/detectron/datasets/data/tt100k/other;
    ln -s $dataset_path/tt100k/data/JsonAnnotations $detectron_path/detectron/datasets/data/tt100k/annotations;
fi

