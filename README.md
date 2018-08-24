## Custom datasets

The detection pipeline requires the COCO-like annotations in a json-file, i.e. annotations should have the following form:
```
{
    "info": info # optional
    "images": [image]
    "annotations": [annotation]
    "licenses": license # optional
    "categories": categories
}
```
with the corresponding sub-directories

```
    info = {
        "year": int
        "version": str
        "description": str
        "contributor": str
        "url": str
        "date_created": datetime
    }
``` 
```    
licence = {
          "id": id
          "name": str
          "url": str
          }
```
```
    image = {
        "file_name": str
        "height": int
        "width": int
        "id": int # use number from file-name
        "licencce": int # optional
        "flickr_url": str # optinal
        "coco_url": str # optional
        "date_captured": datetime # optional
    }
```
```
    annotation = {
        "id": int,
        "image_id" : int,
        "category_id" : int,
        "segmentation": RLE # or [polygon],
        "area" : float,
        "bbox" : [x,y,width,height],
        "iscrowd" : 0 # or 1,
        # if iscrowd == 0: polyongs used (single object, several polyongs may be needed due to occlusions)
        # if iscrowd == 1: RLE coding of binary mask (for larger objects, like groups of people)
        }
```
```
    categories = [{
        "id" : int,
        "name" : str,
        "supercategory" : str,
        }]
 ```
 For each of the training-sets, test-sets and val-sets, a json-file is required. If this is the case, custom datasets can be easily trained with Detectron. To do so, they also have to be written in "dataset_catalog.py". E.g. :
 
 ## 0. Download
 The shell directory contains some shell scripts that perform a batch-download of all required parts of the supported datasets. 
 E.g., the command ```./shell/tt100k_download.sh /path/to/datasets``` downloads all parts needed for the TT100k datasets into /path/to/datasets, unpacks archives and deletes them. 
 For some datasets, it is recommended to re-structure the dataset by ordering images into an "Images" or into a "Train" directory, etc. .
 For the Virtual Kitti setup, a specific shell-script exists for that purpose. 
  
  ## 1. Dataset conversion
  For some datasets, dataset_conversion_main.py includes functionalies to convert the annotation in the correct files. 
  Currently supported (yet not all tested). 
  - Tencent-Tsinghua 100K
  - Caltech-Pedestrian
  - Kitti
  - Virtual Kitti
  
  All these conversion require the dataset to be in a specific structure, that can be derived from the conversion codes for each of dataset. 
  
TT100k can simply be downloaded. It then contains a data directory, where the original annotations.json file is stored and the images are orded according to train, test and other in corresponding folders. 
The conversion than can be achieved by simply calling. 
    ```
    python2 dataset_conversion_main.py --data_dir /path/to/tt100k/data --type tt100k
    ```
It supports the options  
- ``` --check [True | False ]```, which when True (default is False) is trying to load a subset of the newly created annotations with the COCO API and checks the very basics of the structure. 
- ``` --plot [True | False ]```, which when True (default is False) is ploting 5 random images with the corresponding ground-truth boxes. 
- ``` --caltech_img_bool [True | False]``` which when False (default is True) is not performing the conversion of the caltech .seq video files. This might be useful if the images already have been converted and only the annotations need to be created.

## 2. Modifying Annotations
For some datasets, some categories are ignored (e.g. because they only cover 10 to 100 instances). To do so and still keep the original unmodified json-files, json_dataset_modify_categories.py includes functionality to do that. 
It requires a keep.txt or a remove.txt that contain the categories in a comma-seperated list that should be kept or removed. For each annotation-file that should be modified, one simply calls
``` python2 json_dataset_modify_categories.py --json /path/to/json-annotation.json --remove /path/to/remove.txt ```
or 
``` python2 json_dataset_modify_categories.py --json /path/to/json-annotation.json --keep /path/to/keep.txt ```

## 3. Append dataset_catalog
Each json-annotation file represents a dataset (e.g. for training / testing, ...) and should have been named accordingly. To be able to train on these sets, each set has to be written in the dataset_catalog: dataset_catalog.py
E.g. for the tt100k_trainval dataset:
  ```
     'tt100k_trainval':  {
        _IM_DIR:
            _DATA_DIR + '/tt100k/train',
        _ANN_FN:
            _DATA_DIR + '/tt100k/annotations/tt100k_train.json'
    },
  ```
  
  ## 4. Link dataset
  For training / testing with Detectron, the datasets should actually be located in $Detectron/detectron/datasets/data. As this is rather unconfortable, it is recommended to create symbolic links. For a faster setup, the shell direcotry, includes some shell scripts that link the datasets automatically. 
  
  E.g. for the TT100K dataset: 
  ```./shell/link_dataset_tt100k_detectron.sh -detectron_path /path/to/Detectron -dataset_path /path/to/where/datasets/stored ```
  The last past is therefore the path to the parent folder of the tt100k folder, where the actual dataset is located. 
  This is then similiar for other supported datasets. 
