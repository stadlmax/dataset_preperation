import json
import sys
import os
import argparse
from conversion_base import CocoConversion


"""
Utilites to remove categories that should be ignored during testing
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description='Remove categories that sould be ignored during testing'
    )
    parser.add_argument(
        '--json',
        dest='json_file',
        type=str,
        help="Path to your json test-set.",
        default=""
    )

    parser.add_argument(
        '--remove',
        dest='remove_txt',
        type=str,
        help='Path to a .txt-file where you list your categories to be removed.',
        default=""
    )

    parser.add_argument(
        '--keep',
        dest='keep_txt',
        type=str,
        help='path to a.txt-file where you list your categories to be kept.',
        default=""
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()


def create_ignore_coco_annotation(old_coco_annotation, ignore_flag=0):
    if ignore_flag == 0:
        return old_coco_annotation

    else:
        id = old_coco_annotation['id']
        image_id = old_coco_annotation['image_id']
        category_id = old_coco_annotation['category_id']
        segmentation = old_coco_annotation['segmentation']
        area = old_coco_annotation['area']
        bbox = old_coco_annotation['bbox']
        iscrowd = old_coco_annotation['iscrowd']
        ignore = ignore_flag

        annotation = {"id": id,
                      "image_id": image_id,
                      "category_id": category_id,
                      "segmentation": segmentation,
                      "area": area,
                      "bbox": bbox,
                      "iscrowd": iscrowd,
                      "ignore": ignore}
        return annotation


def main():
    args = parse_args()

    if not os.path.exists(args.json_file):
        raise ValueError("FILE {} does not exist!!!".format(args.json_file))
    json_file = json.loads(open(args.json_file).read())
    json_file_name = args.json_file.split('.')[0]

    categories = json_file['categories']
    cat_names = [x['name'] for x in categories]
    info = json_file['info']
    images = json_file['images']
    annotations = json_file['annotations']
    licenses = json_file['licenses']

    if args.remove_txt != "":
        if not os.path.exists(args.remove_txt):
            raise ValueError("FILE {} does not exist!!!".format(args.remove_txt))
        with open(args.remove_txt) as file:
            for line in file:
                remove_cats = line.split(',')
                break # only read first line
        new_cat_names = [str(x) for x in cat_names if x not in remove_cats]

    elif args.keep_txt != "":
        if not os.path.exists(args.keep_txt):
            raise ValueError("FILE {} does not exist!!!".format(args.keep_txt))
        with open(args.keep_txt) as file:
            for line in file:
                keep_cats = line.split(',')
                break # only read first line
        new_cat_names = [str(x) for x in keep_cats if x in cat_names]
    else:
        raise ValueError("You have to specify either remove.txt or keep.txt!")

    print("Creating new annotations with following categories {}".format(new_cat_names))

    new_categories = [x for x in categories if x['name'] in new_cat_names]
    new_categories_ids = [x['id'] for x in new_categories]
    new_annotations =[x for x in annotations if x['category_id'] in new_categories_ids]

    new_annotations_partial = [create_ignore_coco_annotation(x, ignore_flag=1) if x['category_id'] in new_categories_ids
                               else create_ignore_coco_annotation(x) for x in annotations]

    new_dataset_dict = {"info": info,
                        "images": images,
                        "annotations": new_annotations,
                        "type": "instances",
                        "licenses": licenses,
                        "categories": new_categories
                        }

    new_dataset_dict_partial = {"info": info,
                                "images": images,
                                "annotations": new_annotations_partial,
                                "type": "instances",
                                "licenses": licenses,
                                "categories": categories
                                }

    with open(json_file_name + '_ignore_complete.json', 'w') as fp:
        json.dump(new_dataset_dict, fp)
    print("wrote file {}".format(json_file_name + '_ignore_complete.json'))
    with open(json_file_name + '_ignore.json', 'w') as fp:
        json.dump(new_dataset_dict_partial, fp)
    print("wrote file {}".format(json_file_name + '_ignore.json'))


if __name__ == '__main__':
    main()

