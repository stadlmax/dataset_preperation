import json
from PIL import Image
import csv
import os
import glob
import random
from conversion_base import CocoConversion


class CocoVkittiConversion(CocoConversion):
    """

    Requires data_dir to be /path/to/vkitti having sub_dirs Annotations and Images

    vkitti has only a few training samples (2126), a 80/20 split is performed to obtain a test set
    yet, also annotations for the full set is created

    creates json for new and original labels

    annotation scheme resembles the annotation-scheme used in the Kitti-Dataset, but has
    additional fields.
    All values (numerical or strings) are separated via spaces,
    each row corresponds to one object. The 15 columns represent:
    #Values    Name      Description
    ----------------------------------------------------------------------------
       1    frame        Frame index in the video (starts from 0)
       1    tid          Track identification number (unique for each object instance)
       1    label        Describes the type of object: 'Car', 'Van', 'Truck',
                         'Pedestrian', 'Person_sitting', 'Cyclist', 'Tram',
                         'Misc' or 'DontCare', like KITTI
       1    truncated    Kitti-like truncation flag
                         (0: not truncated, 1: truncated, 2: heavily truncated, marked as DontCare)
       1    occluded     Integer (0,1,2,3) indicating occlusion state:
                         0 = fully visible, 1 = partly occluded
                         2 = largely occluded, 3 = unknown
       1    alpha        Observation angle of object, ranging [-pi..pi]
       4    bbox         2D bounding box of object in the image (0-based index):
                         contains left, top, right, bottom pixel coordinates
       3    dimensions   3D object dimensions: height, width, length (in meters)
       3    location     3D object location x,y,z in camera coordinates (in meters)
       1    ry           KITTI-like 3D object 'rotation_y', rotation around Y-axis (yaw) in camera coordinates [-pi..pi]
                         (KITTI convention is ry == 0 iff object is aligned with x-axis and pointing right)
       1    rx           rotation around X-axis (pitch) in camera coordinates [-pi..pi]
       1    rz           rotation around Z-axis (roll) in camera coordinates [-pi..pi]
       1    truncr       object 2D truncation ratio in [0..1] (0: no truncation, 1: entirely truncated)
       1    occupr       object 2D occupancy ratio (fraction of non-occluded pixels) in [0..1]
                         (0: fully occluded, 1: fully visible, independent of truncation)
       1    orig_label   original KITTI-like name of the 'type' of the object ignoring the 'DontCare' rules
                         (allows to know original type of DontCare objects)
       1    moving       0/1 flag to indicate whether the object is really moving between this frame and the next one
       1    model        the name of the 3D model used to render the object (can be used for fine-grained recognition)
       1    color        the name of the color of the object


       data
    """

    def create_json_annos(self, caltech_img_bool=False):
        setup_list = ["clone", "morning", "rain", "fog", "overcast", "sunset"]
        world_list = [1,2,6,18,20]
        train_imgs, test_imgs, all_imgs = self.create_train_test_split(part_test=0.2)
        mode_list = ["train", "test", "all"]

        # create dict with mapping dict[mode][world] --> used frames per mode

        self.info = self.create_coco_info()
        self.append_coco_license()  # empty license

        # categories
        categories = ["Car", "Van"]
        categories_new = ["Car", "Van", "DontCare"]
        categories_coco = []
        categories_coco_new = []
        for cat_idx, cat in enumerate(categories, 1):
            self.append_coco_category(cat_idx, cat, "none", categories=categories_coco)
        for cat_idx, cat in enumerate(categories_new, 1):
            self.append_coco_category(cat_idx, cat, "none", categories=categories_coco_new)

        for setup in setup_list:

            for mode in mode_list:
                if mode == "train":
                    imgs = train_imgs
                elif mode == "test":
                    imgs = test_imgs
                else:
                    imgs = all_imgs

                img_id_counter = 0
                images = []
                imgs_frames_per_world = {}
                # create images list by reading images from imgs_dict of current mode and all worlds
                for world in world_list:
                    imgs_split = [img.split("_") for img in imgs]
                    imgs_frames = [int(img[1]) for img in imgs_split if int(img[0]) == world]
                    imgs_frames_per_world[world] = imgs_frames
                    for frame in imgs_frames:
                        file_name = "{:04d}_{}_{:05}.png".format(world, setup, frame)
                        img_path = self.data_dir + "/Images/" + file_name
                        width, height = self.read_image_information(img_path, file_name)
                        if width == -1 and height == -1:
                            continue
                        self.append_coco_image(file_name, height, width, img_id_counter, images)
                        img_id_counter += 1

                ann_id_counter = 0
                annotations = []
                annotations_new = []

                # create annotation list by reading images from annotation.txt for current mode and all worlds
                for world in world_list:
                    ann_id = self.read_world_annotation(world, setup,
                                                        ann_id_counter,
                                                        annotations,
                                                        annotations_new,
                                                        images,
                                                        imgs_frames_per_world[world],
                                                        categories_coco,
                                                        categories_coco_new)

                    ann_id_counter = ann_id

                print("..." + setup + "_" + mode + ": converted {} images".format(img_id_counter))

                dataset_dict = self.create_coco_dataset_dict(images, annotations, categories=categories_coco)
                with open(self.anno_dir + '/vkitti_' + setup + '_' + mode + '.json', 'w') as fp:
                    json.dump(dataset_dict, fp)
                    self.annotation_files.append(self.anno_dir + '/vkitti_' + setup + '_' + mode + '.json')

                dataset_dict = self.create_coco_dataset_dict(images, annotations_new, categories=categories_coco_new)
                with open(self.anno_dir + '/vkitti_new_' + setup + '_' + mode + '.json', 'w') as fp:
                    json.dump(dataset_dict, fp)
                    self.annotation_files.append(self.anno_dir + '/vkitti_new_' + setup + '_' + mode + '.json')

    def create_train_test_split(self, part_test):
        """
        writes train / test split into .txt files
        in the format:
            <world>_<frame>
        """
        images = glob.glob(self.data_dir + "/Images/*_clone_*") # only for clone, but rest is equivalent
        images = [os.path.split(img)[-1] for img in images] # get only file_name
        images = [img.split('_')[0] + '_' + img.split('_')[-1].split('.')[0] for img in images] # remove setup
        num_img = len(images)
        num_test_img = int(num_img * part_test)
        test_imgs = random.sample(images, num_test_img)
        train_imgs = [img for img in images if img not in test_imgs]

        with open(self.anno_dir + '/traintest.txt', 'w') as file:
            for img in images:
                file.write("{}\n".format(img))
        with open(self.anno_dir + '/test.txt', 'w') as file:
            for img in test_imgs:
                file.write("{}\n".format(img))
        with open(self.anno_dir + '/train.txt', 'w') as file:
            for img in train_imgs:
                file.write("{}\n".format(img))
        return train_imgs, test_imgs, images

    def read_world_annotation(self, world, setup, ann_id_counter, annotations, annotations_new,
                              images, imgs_frames, categories, categories_new):
        assert world in [1, 2, 6, 18, 20]
        assert setup in ["clone", "morning", "rain", "fog", "overcast", "sunset"]
        annotation_path = self.data_dir + "/Annotations/{:04d}_{}.txt".format(world, setup)

        if not os.path.exists(annotation_path):
            raise ValueError("Path to annotation does not exist.")

        ann_id = ann_id_counter

        frame_list = imgs_frames

        with open(annotation_path) as file:
            file_csv = csv.reader(file, delimiter=' ')
            next(file_csv)  # skip header
            for row in file_csv:
                frame = int(row[0])
                if frame in frame_list:
                    category_new = row[2]
                    x1, y1, x2, y2 = map(float, row[6:10])
                    category = row[-4]
                    width = x2 - x1
                    height = y2 - y1
                    area = height * width
                    img_id = self.image_to_id(images, "{:04d}_{}_{:05}.png".format(world, setup, frame))
                    if height > 0 and width > 0:
                        bbox = [x1, y1, width, height]
                        segmentation = [[x1, y1,
                                         x1, y1 + height,
                                         x1 + width, y1 + height,
                                         x1 + width, y1]]
                        category_id = self.category_to_index(category, categories)
                        category_id_new = self.category_to_index(category_new, categories_new)
                        annotations.append(self.create_coco_annotation(ann_id,
                                                                       img_id,
                                                                       category_id,
                                                                       segmentation,
                                                                       area,
                                                                       bbox,
                                                                       iscrowd=0))
                        annotations_new.append(self.create_coco_annotation(ann_id,
                                                                           img_id,
                                                                           category_id_new,
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

    def image_to_id(self, images, file_name):
        id = -1
        for image in images:
            if image['file_name'] == file_name:
                id = image['id']
                break
        return id

