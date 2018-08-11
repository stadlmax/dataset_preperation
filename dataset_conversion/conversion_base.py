from pycocotools.coco import COCO
import datetime
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

plt.rcParams['figure.figsize'] = (10.0, 8.0) # set default size of plots
plt.rcParams['image.interpolation'] = 'nearest'

"""
ms coco style
{
    "info": info, optional
    "images": [image]
    "annotations": [annotation]
    "licenses": licence, optinal
    "categories": categories, for object detection
}

    info = {
        "year": int
        "version": str
        "description": str
        "contributor": str
        "url": str
        "date_created": datetime
    }

    licence = {
        "id": id
        "name": str
        "url": str
    }

    image = {
        "file_name": str
        "height": int
        "width": int
        "id": int #use number from file-name
        "licencce": int, optional
        "flickr_url": str, optinal
        "coco_url": str, optional
        "date_captured": datetime
    }

    annotation = {
        "id": int,
        "image_id" : int,
        "category_id" : int,
        "segmentation": RLE or [polygon],
        "area" : float,
        "bbox" : [x,y,width,height],
        "iscrowd" : 0 or 1,
        }
    if iscrowd == 0: polyongs used (single object, several polyongs may be needed due to occlusions)
    if iscrowd == 1: RLE coding of binary mask (for larger objects, like groups of people)

    categories = [{
        "id" : int,
        "name" : str,
        "supercategory" : str,
        }]

"""


class CocoConversion(object):

    def __init__(self, data_dir):
        if not os.path.exists(data_dir):
            raise ValueError("PATH {} does not exist!!!".format(data_dir))
        self.data_dir = data_dir
        self.info = None
        self.licenses = []
        self.categories = []
        self.annotation_files = []
        if not os.path.exists(data_dir + "/JsonAnnotations"):
            os.makedirs(data_dir + "/JsonAnnotations")
        self.anno_dir = data_dir + "/JsonAnnotations"

    @staticmethod
    def category_to_index(category, categories):
        category_id = -1
        for type in categories:
            if type['name'] == category:
                category_id = type['id']
        return category_id

    @staticmethod
    def create_coco_category(id, type, supercategory):
        category = {"id": id,
                    "name": type,
                    "supercategory": supercategory}
        return category

    def append_coco_category(self, id, type, supercategory, categories=None):
        if categories is None:
            self.categories.append(self.create_coco_category(id, type, supercategory))
        else:
            categories.append(self.create_coco_category(id, type, supercategory))

    @staticmethod
    def create_coco_image(file_name, height, width, id):
        image = {"file_name": file_name,
                 "height": height,
                 "width": width,
                 "id": id}
        return image

    def append_coco_image(self, file_name, height, width, id, images):
        images.append(self.create_coco_image(file_name, height, width, id))

    @staticmethod
    def create_coco_annotation(id, image_id, category_id, segmentation, area, bbox, iscrowd):
        annotation = {"id": id,
                      "image_id": image_id,
                      "category_id": category_id,
                      "segmentation": segmentation,
                      "area": area,
                      "bbox": bbox,
                      "iscrowd": iscrowd}
        return annotation

    def append_coco_annotation(self, id, image_id, category_id, segmentation, area, bbox, iscrowd, annotations):
        annotations.append(self.create_coco_annotation(id, image_id, category_id, segmentation,
                                                       area, bbox, iscrowd))

    def create_coco_info(self, description="", url="", version=0, year=0, contributor="",
                         date_created=datetime.datetime.utcnow().isoformat(' ')):
        info = {
            "description": description,
            "url": url,
            "version": version,
            "year": year,
            "contributor": contributor,
            "date_created": date_created
        }
        self.info = info
        return info

    @staticmethod
    def create_coco_license(id, name, url):
        license = {
            "id": id,
            "name": name,
            "url": url
        }

        return license

    def append_coco_license(self, id=0, name="", url=""):
        self.licenses.append(self.create_coco_license(id, name, url))

    def create_coco_dataset_dict(self, images, annotations, categories=None):
        if categories is None:
            dataset_dict = {"info": self.info,
                            "images": images,
                            "annotations": annotations,
                            "type": "instances",
                            "licenses": self.licenses,
                            "categories": self.categories
                            }
        else:
            dataset_dict = {"info": self.info,
                            "images": images,
                            "annotations": annotations,
                            "type": "instances",
                            "licenses": self.licenses,
                            "categories": categories
                            }

        return dataset_dict

    def create_json_annos(self, caltech_img_bool=False):
        """
        overriden in subclass
        subclass must implement this function
        this function should implement the conversion to ms-coco-style-annotations
        and output the according train.json, test.json and val.json file

        the file uses the data_dir specified in the constructor assuming the typical structure of the dataset
        in the original style

        the function should also specify the paths to json files in self.annotation_files
        """
        raise NotImplementedError("Please Implement this method")

    def check_json_annos(self, plot_bool, image_dir, json_file):
        print("\n")
        print("checking annotation ...")

        for file in self.annotation_files:
            print("... checking {}\n".format(file))
            if file is None:
                print("FILE {} not found, may not be implemented or intentionally left out. \n "
                      "Continuing ...\n")
                continue
            else:
                # initialize COCO api for instance annotations
                try:
                    coco = COCO(file)
                except:
                    print("ERROR occured: conversion failed !!!")
                    return

                try:
                    cats = coco.loadCats(coco.getCatIds())
                    nms = [cat['name'] for cat in cats]
                    nms = set([cat['supercategory'] for cat in cats])
                except:
                    print("ERROR occured: conversion failed !!!")
                    raise

                try:
                    imgs = coco.loadImgs(coco.getImgIds())
                    img_ids = [img['id'] for img in imgs]
                    annIds = coco.getAnnIds(imgIds=img_ids, iscrowd=None)
                    anns = coco.loadAnns(annIds)
                    print("{} contains {} images and {} annotations".format(file, len(img_ids), len(anns)))
                except:
                    print("ERROR occured: conversion failed !!!")
                    raise

                print("sub-check completed\n")

        print("created following json files")
        for file in self.annotation_files:
            print("....." + file)
        print("conversion completed")

        if plot_bool:
            print("\nploting samples of training set... ")
            coco = COCO(json_file)
            imgs = coco.loadImgs(coco.getImgIds())
            img_ids = [img['id'] for img in imgs]
            for i in range(5):
                fig = plt.figure()
                img = coco.loadImgs(img_ids[np.random.randint(0, len(img_ids))])[0]
                I = mpimg.imread(image_dir + '/' + img['file_name'])
                plt.axis('off')
                plt.imshow(I)
                annIds = coco.getAnnIds(imgIds=img['id'], iscrowd=None)
                anns = coco.loadAnns(annIds)
                coco.showAnns(anns)
                plt.show()



