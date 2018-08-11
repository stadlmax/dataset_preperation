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

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()


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

    car_id = -1
    van_id = -1
    for cats in categories:
        if cats['name'] == "Car":
            car_id = cats['id']
            continue
        elif cats['name'] == 'Van':
            van_id = cats['id']
            continue

    # for testing kitti on vkitti: convert VAN into CAR and only keep CAR and DontCare
    for anno in annotations:
        if anno['id'] == van_id:
            anno['id'] = car_id

    new_cat_names = ['Car', 'Van']

    print("Creating new annotations with following categories {}".format(new_cat_names))

    new_categories = [x for x in categories if x['name'] in new_cat_names]
    new_categories_ids = [x['id'] for x in new_categories]
    new_annotations =[x for x in annotations if x['category_id'] in new_categories_ids]

    new_dataset_dict = {"info": info,
                        "images": images,
                        "annotations": new_annotations,
                        "type": "instances",
                        "licenses": licenses,
                        "categories": new_categories
                        }

    with open(json_file_name + '_ignore_complete.json', 'w') as fp:
        json.dump(new_dataset_dict, fp)
    print("wrote file {}".format(json_file_name + '_ignore_complete.json'))


if __name__ == '__main__':
    main()