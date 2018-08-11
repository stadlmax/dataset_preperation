from detectron.pycocotools.coco import COCO
import os
import sys
import glob
import argparse
import statistics

sizes = [8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 128]
step = 8
max_size = 128

def parse_args():
    parser = argparse.ArgumentParser(
        description='determine dataset statistics'
    )
    parser.add_argument(
        '--train_json',
        dest='train_json',
        type=str,
        help='Include here the path to the train_json file of your dataset.',
        default=""
    )

    parser.add_argument(
        '--test_json',
        dest='test_json',
        type=str,
        help='Include here the path to the test_json file of your dataset.',
        default=""
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()


def annotation_statistics(annotations, stats=None, area_list=None):
    if stats is None:
        stats = {
            "else": 0,
            "max": -1,
            "min": 1e10,
            "num": 0,
            "area_sum": 0.0,
            "mean": 0.0,
        }
        for size in sizes:
            stats[size] = 0

    for anno in annotations:
        area = anno["area"]
        for size in sizes:
            if 1.0 * (size - step) * (size - step) <= area < 1.0 * size * size:
                stats[size] += 1
        if area >= 1.0 * max_size * max_size:
            stats["else"] += 1
        stats["num"] += 1
        stats["area_sum"] += area
        if area > stats["max"]:
            stats["max"] = area
        if area < stats["min"]:
            stats["min"] = area
        if area_list is not None:
            area_list.append(area)

    return stats

def main():
    args = parse_args()
    files = [args.train_json, args.test_json]

    stats = {
        "else": 0,
        "max": -1,
        "min": 1e10,
        "num": 0,
        "area_sum": 0.0,
        "mean": 0.0,
    }
    for size in sizes:
        stats[size]  = 0

    area_list = []

    for file in files:
        coco = COCO(file)
        imgs = coco.loadImgs(coco.getImgIds())
        img_ids = [img['id'] for img in imgs]
        annIds = coco.getAnnIds(imgIds=img_ids, iscrowd=None)
        anns = coco.loadAnns(annIds)
        annotation_statistics(anns, stats, area_list)

    stats["max"] = stats["max"] ** 0.5
    stats["min"] = stats["min"] ** 0.5
    mean_area = stats["area_sum"] / stats["num"]
    stats["mean"] = mean_area ** 0.5
    med = statistics.median(area_list)
    smaller = 0
    greater = 0
    for area in area_list:
        if area > mean_area:
            greater += 1
        else:
            smaller += 1

    print(stats)
    print("median: {}".format(med**0.5))
    print("smaller than mean: {}, greater: {}".format(smaller, greater))


if __name__ == '__main__':
    main()
