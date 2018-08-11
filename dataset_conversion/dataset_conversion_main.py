import argparse
import sys

from tt100k_conversion import CocoTt100kConversion
from kitti_conversion import CocoKittiConversion
from vkitti_conversion import CocoVkittiConversion
from caltech_pedestrian_conversion import CocoCaltechPedestrianConversion


def parse_args():
    parser = argparse.ArgumentParser(
        description='Convert a dataset to ms-coco-style format'
    )
    parser.add_argument(
        '--data_dir',
        dest='data_dir',
        type=str,
        help='Include here the path to the root directory where your dataset is stored',
        default=""
    )

    parser.add_argument(
        '--type',
        dest='dataset_type',
        type=str,
        help='Include here the type of your dataset you want to convert. At the moment, supported datasets are: '
             'tt100k, caltech_pedestrian, kitti, vkitti',
        default=""
    )

    parser.add_argument(
        '--check',
        dest='check_bool',
        type= bool,
        help='Set bool to false for disabling check_json_annos',
        default=False
    )

    parser.add_argument(
        '--plot',
        dest='plot_bool',
        help='Set bool to false for disabling ploting example annotations',
        default=False
    )

    parser.add_argument(
        '--caltech_img_bool',
        dest='caltech_img_bool',
        help='Set bool to false for disabling the conversion of .seq video files if the converted images already exist',
        default=True
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()


def main():
    args = parse_args()
    im_dir = ""
    json_file = ""

    if args.dataset_type is None or args.dataset_type is None:
        return
    if args.dataset_type == 'tt100k':
        dataset = CocoTt100kConversion(args.data_dir)
        im_dir = args.data_dir + '/train'
        json_file = args.data_dir + '/JsonAnnotations/tt100k_train.json'

    elif args.dataset_type == 'caltech_pedestrian':
        dataset = CocoCaltechPedestrianConversion(args.data_dir)
        im_dir = args.data_dir + '/train'
        json_file = args.data_dir + '/JsonAnnotations/caltech_original_train.json'

    elif args.dataset_type == 'kitti':
        dataset = CocoKittiConversion(args.data_dir)
        im_dir = args.data_dir + '/training/image_2'
        json_file = args.data_dir + '/JsonAnnotations/kitti_train.json'

    elif args.dataset_type == 'vkitti':
        dataset = CocoVkittiConversion(args.data_dir)
        im_dir = args.data_dir + '/Images'
        json_file = args.data_dir + '/JsonAnnotations/vkitti_clone_train.json'

    else:
        raise ValueError("Specified type of dataset is not supported.")

    dataset.create_json_annos(caltech_img_bool=args.caltech_img_bool)

    if args.check_bool and im_dir != "" and json_file != "":
        dataset.check_json_annos(args.plot_bool, im_dir, json_file)


if __name__ == '__main__':
    main()

