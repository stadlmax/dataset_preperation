import json
import sys
import os
import argparse
from conversion_base import CocoConversion


"""
Utilites to combine datasets (currently only vkitti supported intentionally (always works when images are in the same
image directory and the image_names for different datasets are distinct
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description='Remove categories that sould be ignored during testing'
    )
    parser.add_argument(
        '--json',
        dest='json_files',
        action='append',
        type=str,
        help='Include here the path to the train_json file of your dataset that should be combined.',
        required=True
    )

    parser.add_argument(
        '--name',
        dest='name',
        help='name for combined datasets',
        default='dataset_combined'
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()


def create_coco_dataset_dict(new_images, new_annotations, categories, licenses, info):
    dataset_dict = {"info": info,
                    "images": new_images,
                    "annotations": new_annotations,
                    "type": "instances",
                    "licenses": licenses,
                    "categories": categories
                    }

    return dataset_dict


def create_modified_coco_images(image, new_id):
    image['id'] = new_id
    return image


def create_modified_coco_annotation(annotation, new_id, new_img_id):
    annotation['id'] = new_id
    annotation['image_id'] = new_img_id
    return annotation


def main():
    args = parse_args()

    for file in args.json_files:
        if not os.path.exists(file):
            raise ValueError("FILE {} does not exist!!!".format(file))

    anno_dir = os.path.split(args.json_files[0])[0]

    json_files = []
    categories = []
    annotations = []
    images = []
    licenses = []
    info = []

    for file in args.json_files:
        json_file = json.loads(open(file).read())
        json_files.append(json_file)
        categories.append(json_file['categories'])
        annotations.append(json_file['annotations'])
        images.append(json_file['images'])
        licenses.append(json_file['licenses'])
        info.append(json_file['info'])

    image_counter = 0
    annotation_counter = 0

    new_images = []
    new_annotations = []

    # TODO implement checking whether datasets can be combined, i.e. if categories are the same
    # TODO current workaround: simply take first entry of list of files to be combined
    categories = categories[0]
    info = info[0]
    licenses = licenses[0]

    for set in range(len(json_files)):
        for img in images[set]:
            annos_per_im = [x for x in annotations[set] if x['image_id'] == img['id']]
            new_images.append(create_modified_coco_images(img, image_counter))
            for anno in annos_per_im:
                new_annotations.append(create_modified_coco_annotation(anno,
                                                                       annotation_counter,
                                                                       image_counter))
                annotation_counter += 1
            image_counter += 1

    combined_dict = create_coco_dataset_dict(new_images, new_annotations, categories, licenses, info)

    combined_dataset_name = os.path.join(anno_dir, args.name + '.json')

    with open(combined_dataset_name, 'w') as fp:
        json.dump(combined_dict, fp)
    print("wrote file {}".format(combined_dataset_name))


if __name__ == '__main__':
    main()

