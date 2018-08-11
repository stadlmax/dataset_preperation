#!/bin/sh

#####################################
# reorganize folder structure of 
# vkitti 
# new
# Images
#  ---- clone
#  ---- fog
#  ---- rain
#  ---- morning
#  ---- sunset
#  ---- overcast
# where the corresponding images of each world are moved
# starting from path/to/vkitti

cd "$1"

if [ ! -d Images ]; then
    mkdir Images;
fi
cd Images
imagePath=$PWD

dirlist="clone/ fog/ rain/ morning/ sunset/ overcast/"

cd ..
cd vkitti_1.3.1_rgb

for d in */; do
    cd $d;
    for sd in ${dirlist}; do
        cd $sd;
        for file in *; do
            mv "${file}" "${imagePath}/${d%/}_${sd%/}_${file}";
        done
        cd ..;
        rm -rf $sd
    done
    cd ..;
done

mv vkitti_1.3.1_motgt Annotations
