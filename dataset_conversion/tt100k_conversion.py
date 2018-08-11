import json
from PIL import Image
import os

from conversion_base import CocoConversion


class CocoTt100kConversion(CocoConversion):
    """
    requires datadir to be /path/to/tt100k/data
    """

    def create_json_annos(self, caltech_img_bool=False):
        """
           TT100K JSON STYLE
           { "imgs": imgs,
             "types": types
           }

           imgs = {
               "id":
           }

           image = {
               "path": str
               "objects": [object]
           }

           object = {
               "category": str
               "bbox": {"xmin", "ymin", "ymax", "xmax"}
               "ellipse_org": ..., optional
               "ellipse": ..., optinal
               "polygon". ..., optional
           }

           types = [type] where type: str
           """

        print("Converting TT100k dataset .... ")

        file_dir = self.data_dir + "/annotations.json"
        if not os.path.exists(file_dir):
            raise ValueError("FILE {} does not exist!!!".format(file_dir))
        annos = json.loads(open(file_dir).read())

        self.info = self.create_coco_info()
        self.append_coco_license() #empty license

        types = annos["types"]
        for type_idx, type in enumerate(types, 1):
            self.append_coco_category(type_idx, type, "none")

        ann_id_counter = 0
        for set in ["train", "test", "other"]:
            img_count = 0
            images = []
            annotations = []

            # create json for specific set
            ids_path = self.data_dir + "/" + set + "/ids.txt"
            if not os.path.exists(ids_path):
                raise ValueError("FILE {} does not exist!!!".format(ids_path))
            ids = open(ids_path).read().splitlines()
            for imgid in ids:
                img = annos["imgs"][imgid]
                file_name = img['path'].split('/')[1]
                img_path = self.data_dir + "/" + set + "/" + file_name
                if not os.path.exists(img_path):
                    print("IMAGE {} does not exist, continuing ... ".format(file_name))
                    continue
                img_file = Image.open(img_path)
                img_count += 1
                width, height = img_file.size
                image_id = int(file_name.split('.')[0])
                self.append_coco_image(file_name, height, width, image_id, images)

                for obj in img['objects']:
                    category = obj["category"]
                    bbox_tt100k = obj["bbox"]

                    # tt100k: format [xmin, ymin, ymax, xmax] as dict

                    # coco: box coordinates are measured from the top left image corner and are 0-indexed
                    # format [x,y,width, height]

                    id = ann_id_counter
                    ann_id_counter += 1
                    category_id = self.category_to_index(category, self.categories)
                    x = bbox_tt100k['xmin'] # left corner
                    y = bbox_tt100k['ymin'] # top left corner
                    width = bbox_tt100k['xmax'] - x
                    height = bbox_tt100k['ymax']- y
                    segmentation = [[x, y,
                                     x, y + height,
                                     x + width, y + height,
                                     x + width, y]]
                    area = width * height
                    bbox = [x, y, width, height]
                    iscrowd = 0
                    self.append_coco_annotation(id, image_id, category_id, segmentation, area,
                                                bbox, iscrowd, annotations)

            print("..." + set + ": converted {} images".format(img_count))

            dataset_dict = self.create_coco_dataset_dict(images, annotations)
            with open(self.anno_dir + '/tt100k_' + set + '.json', 'w') as fp:
                json.dump(dataset_dict, fp)
                self.annotation_files.append(self.anno_dir + '/tt100k_' + set + '.json')