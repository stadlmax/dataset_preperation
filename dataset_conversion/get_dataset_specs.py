from pycocotools.coco import COCO
import os
import sys
import glob
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description='check dataset for number of images, classes and annotations'
    )
    parser.add_argument(
        '--ann_dir',
        dest='ann_dir',
        type=str,
        help='Include here the path to the annotations directory of your dataset.',
        default=""
    )

    parser.add_argument(
        '--type',
        dest='data_type',
        type=str,
        help='Include here the type of your dataset.',
        default=""
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()

def main():
    args = parse_args()
    if args.data_type == "coco":
        annotation_files = glob.glob(args.ann_dir + '/instances*.json')
    else:
        annotation_files = glob.glob(args.ann_dir + '/*.json')

    for file in annotation_files:
        coco = COCO(file)
        cats = coco.loadCats(coco.getCatIds())
        imgs = coco.loadImgs(coco.getImgIds())
        img_ids = [img['id'] for img in imgs]
        annIds = coco.getAnnIds(imgIds=img_ids, iscrowd=None)
        anns = coco.loadAnns(annIds)
        print("{} contains {} images and {} annotations from {} classes".format(file, len(img_ids), len(anns),
                                                                                len(cats))
              )


if __name__ == '__main__':
    main()
