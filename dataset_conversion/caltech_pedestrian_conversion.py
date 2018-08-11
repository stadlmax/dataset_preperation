from __future__ import print_function, division

import json
from PIL import Image
import os
import glob
import cv2 as cv
from collections import defaultdict
from scipy.io import loadmat

from conversion_base import CocoConversion


class CocoCaltechPedestrianConversion(CocoConversion):
    """
    based on https://github.com/mitmul/caltech-pedestrian-dataset-converter
    based on https://github.com/dbcollection/caltech_pedestrian_extractor

    requires datadir to be path to /path/to/caltech_pedestrian
    """

    def create_json_annos(self, caltech_img_bool=True):
        print("\n Converting images ...\n")
        if caltech_img_bool: # converts if not explicitly set to False
            self.convert_seqs()
        self.create_json_annos_original()
        self.create_json_annos_new()

    def create_json_annos_new(self):
        # create annotation for new annotations
        # located in annotations/anno_test_1xnew
        # located in annotations/anno_train_1xnew
        types = ["person", "ignore", "people"]

        img_id_counter = 0
        ann_id_counter = 0
        ann_id_counter_v = 0

        for mode in ['test', 'train']:
            img_count = 1
            images = []
            images_v = []
            annotations = []
            annotations_v = []
            dir = self.data_dir + "/annotations/anno_" + mode + "_1xnew"
            for file in glob.glob(dir + "/*.txt"):
                set, video, frame, data = self.read_txt_annotation(file, os.path.split(file)[-1])
                img_file_name, width, height = self.read_frame_image(set, video, frame)
                if img_file_name == "" and width == 0 and height == 0:
                    continue

                self.append_coco_image(img_file_name, height, width, img_id_counter, images)
                self.append_coco_image(img_file_name, height, width, img_id_counter, images_v)

                for data_dict in data:
                    pos = data_dict["pos"]
                    posv = data_dict["posv"]
                    category = data_dict["category"]
                    category_id = self.category_to_index(category, self.categories)

                    x = float(pos[0]) - 1
                    y = float(pos[1]) - 1
                    width = float(pos[2])
                    height = float(pos[3])
                    segmentation = [[x, y,
                                     x, y + height,
                                     x + width, y + height,
                                     x + width, y]]
                    area = width * height
                    bbox = [x, y, width, height]
                    iscrowd = 0

                    self.append_coco_annotation(ann_id_counter, img_id_counter, category_id,
                                                segmentation, area,
                                                bbox, iscrowd, annotations)
                    ann_id_counter += 1

                    if isinstance(posv, int) or isinstance(posv, float):
                        posv = [0, 0, 0, 0]

                    x = float(posv[0])
                    y = float(posv[1])
                    width = float(posv[2])
                    height = float(posv[3])
                    segmentation = [[x, y,
                                     x, y + height,
                                     x + width, y + height,
                                     x + width, y]]
                    area = width * height
                    bbox = [x, y, width, height]
                    iscrowd = 0
                    if x > 0 and y > 0 and height > 0 and width > 0:
                        self.append_coco_annotation(ann_id_counter_v, img_id_counter, category_id,
                                                    segmentation, area,
                                                    bbox, iscrowd, annotations_v)
                        ann_id_counter_v += 1

                img_count += 1
                img_id_counter += 1

            print("...new " + mode + ": converted {} images".format(img_count))
            dataset_dict = self.create_coco_dataset_dict(images, annotations)
            dataset_dict_v = self.create_coco_dataset_dict(images_v, annotations_v)
            with open(self.anno_dir + '/caltech_new' + '_' + mode + '.json', 'w') as fp:
                json.dump(dataset_dict, fp)
                self.annotation_files.append(self.anno_dir + '/caltech_new' + '_' + mode + '.json')
            with open(self.anno_dir + '/caltech_new' + '_' + mode + 'v.json', 'w') as fp:
                json.dump(dataset_dict_v, fp)
                self.annotation_files.append(self.anno_dir + '/caltech_new' + '_' + mode + 'v.json')

    def create_json_annos_original(self):
        print("\n Converting annotations ...\n")
        data_full = self.read_frame_annotations_into_dict()

        print("\n Converting annotations into MS-COCO-Style ... \n")
        train_sets = [0, 1, 2, 3, 4, 5]
        test_sets = [6, 7, 8, 9, 10]
        videos = [15, 6, 12, 13, 12, 13, 19, 12, 11, 12, 12]
        frame_start = 30
        frame_step = 30
        frame_start_dense = 4
        frame_step_dense = 4

        self.info = self.create_coco_info()
        self.append_coco_license()  # empty license
        types = ["person", "person?", "people"]

        # create annotations for case of original annotations
        # meaning set00 - set05 for training, every 30th frame
        # meaning set06 - set10 for testing, every 30th frame

        # also create annotation for dense sampling
        # meaning set00 -set05 for training, very 4th frame

        for type_idx, type in enumerate(types, 1):
            self.append_coco_category(type_idx, type, "none")

        ann_id_counter = 0
        ann_id_counter_v = 0
        img_id_counter = 0
        for ann_type in ["original", "dense"]:
            if ann_type == "original":
                start = frame_start
                step = frame_step
            else:
                start = frame_start_dense
                step = frame_step_dense

            for mode in ["train", "test"]:
                img_count = 1
                images = []
                images_v = []
                annotations = []
                annotations_v = []
                dir = self.data_dir + "/" + mode

                if mode == "train":
                    mode_sets = train_sets
                else:
                    mode_sets = test_sets

                for set in mode_sets:
                    for video in range(videos[set]):
                        num_frames = len(glob.glob(dir + "/set{:02d}_V{:03d}_*.jpg".format(set, video)))
                        for frame in range(start, num_frames, step):
                            img_file_name, width, height = self.read_frame_image(set, video, frame)
                            data = self.read_frame_annotations(set, video, frame, data_full)
                            self.append_coco_image(img_file_name, height, width, img_id_counter, images)
                            self.append_coco_image(img_file_name, height, width, img_id_counter, images_v)

                            for data_dict in data:
                                pos = data_dict["pos"]
                                posv = data_dict["posv"]
                                category = data_dict["category"]
                                category_id = self.category_to_index(category, self.categories)

                                x = pos[0]
                                y = pos[1]
                                width = pos[2]
                                height = pos[3]
                                segmentation = [[x, y,
                                                 x, y + height,
                                                 x + width, y + height,
                                                 x + width, y]]
                                area = width * height
                                bbox = [x, y, width, height]
                                iscrowd = 0

                                self.append_coco_annotation(ann_id_counter, img_id_counter, category_id,
                                                            segmentation, area,
                                                            bbox, iscrowd, annotations)
                                ann_id_counter += 1

                                if isinstance(posv, int):
                                    posv = [0, 0, 0, 0]

                                x = posv[0]
                                y = posv[1]
                                width = posv[2]
                                height = posv[3]
                                segmentation = [[x, y,
                                                 x, y + height,
                                                 x + width, y + height,
                                                 x + width, y]]
                                area = width * height
                                bbox = [x, y, width, height]
                                iscrowd = 0
                                if x > 0 and y > 0 and height > 0 and width > 0:
                                    self.append_coco_annotation(ann_id_counter_v, img_id_counter, category_id,
                                                                segmentation, area,
                                                                bbox, iscrowd, annotations_v)
                                    ann_id_counter_v += 1

                            img_count += 1
                            img_id_counter += 1

                print("..." + ann_type + ' ' + mode + ": converted {} images".format(img_count))

                dataset_dict = self.create_coco_dataset_dict(images, annotations)
                dataset_dict_v = self.create_coco_dataset_dict(images_v, annotations_v)
                with open(self.anno_dir + '/caltech_' + ann_type + '_' + mode + '.json', 'w') as fp:
                    json.dump(dataset_dict, fp)
                    self.annotation_files.append(self.anno_dir + '/caltech_' + ann_type + '_' + mode + '.json')
                with open(self.anno_dir + '/caltech_' + ann_type + '_' + mode + 'v.json', 'w') as fp:
                    json.dump(dataset_dict_v, fp)
                    self.annotation_files.append(self.anno_dir + '/caltech_' + ann_type + '_' + mode + 'v.json')

    @staticmethod
    def save_img(out_dir, dname, fn, i, frame):
        if not os.path.exists('{}/{}_{}_{}.jpg'.format(  # changed to jpg format
                                                        out_dir, os.path.basename(dname),
                                                        os.path.basename(fn).split('.')[0], i)):
            cv.imwrite('{}/{}_{}_{}.jpg'.format(  # changed to jpg format
                out_dir, os.path.basename(dname),
                os.path.basename(fn).split('.')[0], i), frame)

    def convert_seqs(self):
        print("\nconverting training images ...")
        for dname in sorted(glob.glob(self.data_dir + '/set0[0-5]')):
            for fn in sorted(glob.glob('{}/*.seq'.format(dname))):
                cap = cv.VideoCapture(fn)
                i = 0
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    out_dir = self.data_dir + '/train' #for set00 to set05
                    if not os.path.exists(out_dir):
                        os.makedirs(out_dir)
                    self.save_img(out_dir, dname, fn, i, frame)
                    i += 1
                print(fn)

        print("\nconverting testing images ....")
        for dname in sorted(glob.glob(self.data_dir + '/set0[6-9]') + glob.glob(self.data_dir + '/set10')):
            for fn in sorted(glob.glob('{}/*.seq'.format(dname))):
                cap = cv.VideoCapture(fn)
                i = 0
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    out_dir = self.data_dir + '/test' #for set06 to set10
                    if not os.path.exists(out_dir):
                        os.makedirs(out_dir)
                    self.save_img(out_dir, dname, fn, i, frame)
                    i += 1
                print(fn)

    def read_frame_image(self, set, video, frame):
        if 0 <= set <= 5:
            img_dir_path = self.data_dir + '/train'
        elif set <= 10:
            img_dir_path = self.data_dir + '/test'
        else:
            raise ValueError("Invalid set argument, must be within [0, 10]")

        img_file_name = 'set{:02d}_V{:03d}_{}.jpg'.format(set, video, frame)
        img_path = img_dir_path + '/' + img_file_name
        if not os.path.exists(img_path):
            print("IMAGE {} does not exist, continuing ... ".format(img_file_name))
            return "", 0, 0
        img_file = Image.open(img_path)
        width, height = img_file.size

        return img_file_name, width, height

    def read_frame_annotations(self, set, video, frame, data_full):
        """ returns image infomation and bbox / category information corresponding to image in of set_video_frame"""
        datum_list = data_full["set{:02d}".format(set)]["V{:03d}".format(video)][
            'frames'][frame-1]
        data = []

        for datum in datum_list:
            data.append({'pos': datum['pos'],
                         'posv': datum['posv'],
                         'category': datum['lbl']}
                        )
        return data

    def read_frame_annotations_into_dict(self):
        all_obj = 0
        data = defaultdict(dict)
        for dname in sorted(glob.glob(self.data_dir + '/annotations/set*')):
            set_name = os.path.basename(dname)
            data[set_name] = defaultdict(dict)
            for anno_fn in sorted(glob.glob('{}/*.vbb'.format(dname))):
                vbb = loadmat(anno_fn)
                nFrame = int(vbb['A'][0][0][0][0][0])
                objLists = vbb['A'][0][0][1][0]
                maxObj = int(vbb['A'][0][0][2][0][0])
                objInit = vbb['A'][0][0][3][0]
                objLbl = [str(v[0]) for v in vbb['A'][0][0][4][0]]
                objStr = vbb['A'][0][0][5][0]
                objEnd = vbb['A'][0][0][6][0]
                objHide = vbb['A'][0][0][7][0]
                altered = int(vbb['A'][0][0][8][0][0])
                log = vbb['A'][0][0][9][0]
                logLen = int(vbb['A'][0][0][10][0][0])

                video_name = os.path.splitext(os.path.basename(anno_fn))[0]
                data[set_name][video_name]['nFrame'] = nFrame
                data[set_name][video_name]['maxObj'] = maxObj
                data[set_name][video_name]['log'] = log.tolist()
                data[set_name][video_name]['logLen'] = logLen
                data[set_name][video_name]['altered'] = altered
                data[set_name][video_name]['frames'] = defaultdict(list)

                n_obj = 0
                for frame_id, obj in enumerate(objLists):
                    if len(obj) > 0:
                        for id, pos, occl, lock, posv in zip(
                                obj['id'][0], obj['pos'][0], obj['occl'][0],
                                obj['lock'][0], obj['posv'][0]):
                            keys = obj.dtype.names
                            id = int(id[0][0]) - 1  # MATLAB is 1-origin
                            pos = pos[0].tolist()
                            occl = int(occl[0][0])
                            lock = int(lock[0][0])
                            posv = posv[0].tolist()

                            datum = dict(zip(keys, [id, pos, occl, lock, posv]))
                            datum['lbl'] = str(objLbl[datum['id']])
                            datum['str'] = int(objStr[datum['id']])
                            datum['end'] = int(objEnd[datum['id']])
                            datum['hide'] = int(objHide[datum['id']])
                            datum['init'] = int(objInit[datum['id']])
                            data[set_name][video_name][
                                'frames'][frame_id].append(datum)
                            n_obj += 1

                print(dname, anno_fn, n_obj)
                all_obj += n_obj
        return data

    def read_txt_annotation(self, file_path, file_name):
        name = file_name.split('.')[0]
        set = int(name.split('_')[0][-2:])
        video = int(name.split('_')[1][-3:])
        frame = int(name.split('_')[2][1:])
        txt_annotations = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                next(file)
                for line in file:
                    category = line.split(' ')[0]
                    pos = line.split(' ')[1:5]
                    posv = line.split(' ')[6:10]
                    txt_annotations.append({
                        'category': category,
                        'pos': pos,
                        'posv': posv,
                    })
        return set, video, frame, txt_annotations