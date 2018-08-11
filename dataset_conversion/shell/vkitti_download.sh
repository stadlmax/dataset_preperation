#!/bin/sh

#####################################
#download kitty dataset and process
# pass path/to/datasets into script

cd "$1" 

printf "Download: virtual kitti dataset\n"
if [ ! -d vkitti ]; then
    mkdir vkitti
fi
cd vkitti

wget "http://download.europe.naverlabs.com/virtual-kitti-1.3.1/vkitti_1.3.1_motgt.tar.gz"
tar -xzf vkitti_1.3.1_motgt.tar.gz
rm -rf vkitti_1.3.1_motgt.tar.gz

wget "http://download.europe.naverlabs.com/virtual-kitti-1.3.1/vkitti_1.3.1_rgb.tar"
tar xvf vkitti_1.3.1_rgb.tar
rm -rf vkitti_1.3.1_rgb.tar


printf "Download finished.\n"




