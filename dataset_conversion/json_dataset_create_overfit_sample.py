import json
import sys
import os
import argparse
import random

"""
Utilites to create smaller annotation sets for debugging
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description='Modify json annotations to create smaller set'
    )
    parser.add_argument(
        '--train_json',
        dest='train_json_file',
        type=str,
        help="Path to your json train-set.",
        required=True,
        default=""
    )
    parser.add_argument(
        '--test_json',
        dest='test_json_file',
        type=str,
        help="Path to your json test-set.",
        required=True,
        default=""
    )
    parser.add_argument(
        '--size',
        dest='size',
        type=int,
        help='Size of new subsets',
        default=50
    )


    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()


def create_random_subset(json_file, size):
    if not os.path.exists(json_file):
        raise ValueError("FILE {} does not exist!!!".format(json_file))
    json_file_name = json_file.split('.')[0]
    json_file = json.loads(open(json_file).read())


    categories = json_file['categories']
    info = json_file['info']
    images = json_file['images']
    annotations = json_file['annotations']
    licenses = json_file['licenses']

    img_ids = [x['id'] for x in images]
    new_img_ids = random.sample(img_ids, size)

    new_images = [x for x in images if x['id'] in new_img_ids]
    new_annotations = [x for x in annotations if x['image_id'] in new_img_ids]

    new_dataset_dict = {"info": info,
                        "images": new_images,
                        "annotations": new_annotations,
                        "type": "instances",
                        "licenses": licenses,
                        "categories": categories
                        }
    with open(json_file_name + '_overfit.json', 'w') as fp:
        json.dump(new_dataset_dict, fp)
    print("wrote file {}".format(json_file_name + '_overfit.json'))


def main():
    args = parse_args()
    print("Converting with Input: {}\n \t\t {}".format(args.train_json_file, args.test_json_file))
    create_random_subset(args.train_json_file, args.size)
    create_random_subset(args.test_json_file, args.size)


if __name__ == '__main__':
    main()


