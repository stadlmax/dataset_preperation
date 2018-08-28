from pycocotools.coco import COCO
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
        '--json',
        dest='json_files',
        action='append',
        type=str,
        help='Include here the path to the train_json file of your dataset.',
        required=True
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()


def annotation_statistics(annotations, categories, stats=None, area_list=None, category_count=None):
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

    if category_count is None:
        category_count = {}
        category_count['ids'] = {}
        category_count['count'] = {}
        for cat in categories:
            category_count['count'][cat['name']] = 0
            category_count['ids'][cat['id']] = cat['name']

    for anno in annotations:
        category_count['count'][category_count['ids'][anno['category_id']]] += 1
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

    return stats, category_count


def main():
    args = parse_args()
    files = args.json_files

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
        cats = coco.loadCats(coco.getCatIds())
        img_ids = [img['id'] for img in imgs]
        annIds = coco.getAnnIds(imgIds=img_ids, iscrowd=None)
        anns = coco.loadAnns(annIds)
        _, category_count = annotation_statistics(anns, cats, stats, area_list)
        print("File {} has category_count:".format(file))
        print(category_count['count'])

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
