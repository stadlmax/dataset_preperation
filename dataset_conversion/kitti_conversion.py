import json
from PIL import Image
import random
import os
import csv

from conversion_base import CocoConversion


class CocoKittiConversion(CocoConversion):
    """ based on https://github.com/nghiattran/vod-converter

    Requires data_dir to be /path/to/kitti having sub_dirs training and testing

    as no testing-labels are available
    a 75/25 train/test split is used on the training-data
    kitti has 7481 training images (7518 testing images)
    this results in
        5611 training images
        1870 testing images
    indices are saved under train.txt and test.txt in data_dir

    Description of fields from Kitti dataset dev kit: (link)[]
    The label files contain the following information, which can be read and
    written using the matlab tools (readLabels.m, writeLabels.m) provided within
    this devkit. All values (numerical or strings) are separated via spaces,
    each row corresponds to one object. The 15 columns represent:
    #Values    Name      Description
    ----------------------------------------------------------------------------
       1    type         Describes the type of object: 'Car', 'Van', 'Truck',
                         'Pedestrian', 'Person_sitting', 'Cyclist', 'Tram',
                         'Misc' or 'DontCare'
       1    truncated    Float from 0 (non-truncated) to 1 (truncated), where
                         truncated refers to the object leaving image boundaries
       1    occluded     Integer (0,1,2,3) indicating occlusion state:
                         0 = fully visible, 1 = partly occluded
                         2 = largely occluded, 3 = unknown
       1    alpha        Observation angle of object, ranging [-pi..pi]
       4    bbox         2D bounding box of object in the image (0-based index):
                         contains left, top, right, bottom pixel coordinates
       3    dimensions   3D object dimensions: height, width, length (in meters)
       3    location     3D object location x,y,z in camera coordinates (in meters)
       1    rotation_y   Rotation ry around Y-axis in camera coordinates [-pi..pi]
       1    score        Only for results: Float, indicating confidence in
                         detection, needed for p/r curves, higher is better.
    """

    def create_json_annos(self, caltech_img_bool=False):

        self.info = self.create_coco_info()
        self.append_coco_license() #empty license

        # categories
        categories = ["Car", "Van", "Truck", "Pedestrian",
                      "Person_sitting", "Cyclist", "Tram",
                      "Misc", "DontCare"]
        for cat_idx, cat in enumerate(categories, 1):
            self.append_coco_category(cat_idx, cat, "none")

        # perform train / test split
        test_ids, train_ids = self.create_train_test_split(part_test=0.25)

        # create annotations
        ann_id_counter = 0
        for mode in ["train", "test"]:
            if mode == "train":
                ids = train_ids
            else:
                ids = test_ids

            images = []
            annotations = []
            img_count = 0
            for img_id in ids:
                img_file_name = "{:06d}.png".format(img_id)
                ann_file_name = "{:06d}.txt".format(img_id)
                img_file_path = self.data_dir + "/training/image_2/" + img_file_name
                ann_file_path = self.data_dir + "/training/label_2/" + ann_file_name

                # append the images information for each id
                width, height = self.read_image_information(img_file_path, img_file_name)
                if width == -1 and height == -1:
                    continue
                self.append_coco_image(img_file_name, height, width, img_id, images)

                # append the annotations information for each id
                ann_id_new = self.read_image_annotation(ann_file_path, ann_id_counter, annotations)
                ann_id_counter = ann_id_new
                img_count += 1

            print("..." + mode + ": converted {} images".format(img_count))

            dataset_dict = self.create_coco_dataset_dict(images, annotations)
            with open(self.anno_dir + '/kitti_' + mode + '.json', 'w') as fp:
                json.dump(dataset_dict, fp)
                self.annotation_files.append(self.anno_dir + '/kitti_' + mode + '.json')

    def create_train_test_split(self, part_test):
        num_img = 7481
        num_test_img = int(num_img * part_test)
        test_ids = random.sample(range(num_img), num_test_img)
        train_ids = [id for id in range(num_img) if id not in test_ids]

        with open(self.anno_dir + '/test.txt', 'w') as file:
            for id in test_ids:
                file.write("{:06d}\n".format(id))
        with open(self.anno_dir + '/train.txt', 'w') as file:
            for id in train_ids:
                file.write("{:06d}\n".format(id))
        return test_ids, train_ids

    def read_image_annotation(self, annotation_path, ann_id_counter, annotations):
        """ gets path to annotation.txt (e.g. 0000111.txt) """
        if not os.path.exists(annotation_path):
            raise ValueError("Path to annotation does not exist.")
        ann_file = os.path.split(annotation_path)[-1]
        image_id = int(ann_file.split('.')[0])
        ann_id = ann_id_counter

        with open(annotation_path) as file:
            file_csv = csv.reader(file, delimiter=' ')
            for row in file_csv:
                x1, y1, x2, y2 = map(float, row[4:8])
                category = row[0]
                width = x2 - x1
                height = y2 - y1
                area = height * width
                if height > 0 and width > 0:
                    bbox = [x1,y1,width, height]
                    segmentation = [[x1, y1,
                                     x1, y1 + height,
                                     x1 + width, y1 + height,
                                     x1 + width, y1]]
                    category_id = self.category_to_index(category, self.categories)
                    annotations.append(self.create_coco_annotation(ann_id,
                                                                   image_id,
                                                                   category_id,
                                                                   segmentation,
                                                                   area,
                                                                   bbox,
                                                                   iscrowd=0))
                    ann_id += 1

        return ann_id

    def read_image_information(self, img_path, file_name):
        if not os.path.exists(img_path):
            print("IMAGE {} does not exist, continuing ... ".format(file_name))
            return -1, -1
        with Image.open(img_path) as image:
            return image.width, image.height


