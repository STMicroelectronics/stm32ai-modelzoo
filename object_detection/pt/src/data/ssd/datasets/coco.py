# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import os
import torch
import numpy as np
from torch.utils.data import Dataset
import cv2
import logging
from pycocotools.coco import COCO


class CocoDataset(Dataset):
    def __init__(
        self,
        annotations_path="instances_train2017.json",     # full path to instances_*.json
        images_path="train2017",          # full path to image folder
        transform=None,
        target_transform=None,
        skip_annotations=False,
        filter_empty_gt=True,
    ):
        self.img_dir = images_path
        self.ann_file = annotations_path
        self.transform = transform
        self.target_transform = target_transform
        self.skip_annotations = skip_annotations

        if not os.path.exists(self.ann_file):
            raise FileNotFoundError(f"COCO ann file not found: {self.ann_file}")
        if not os.path.isdir(self.img_dir):
            raise NotADirectoryError(f"Image dir not found: {self.img_dir}")


        self.coco = COCO(self.ann_file)
        
        # Filter to only images with annotations if annotations are provided
        ids = list(self.coco.imgs.keys())

        if filter_empty_gt and (not skip_annotations):
            kept = []
            for img_id in ids:
                if len(self.coco.getAnnIds(imgIds=img_id)) > 0:
                    kept.append(img_id)
            self.ids = kept
        else:
            self.ids = ids
            
            logging.info(
                f"CocoDataset: Filtered {len(ids) - len(self.ids)} images without annotations. "
                f"Remaining: {len(self.ids)}"
            )
        
        # Categories
        self.cat_ids = sorted(self.coco.getCatIds())
        self.cats = self.coco.loadCats(self.cat_ids)
        
        # Creating a continuous map from 1..N for training (0 is background)
        # COCO IDs are sparse (1..90).
        self.class_names = ['BACKGROUND'] + [cat['name'] for cat in self.cats]
        # Map coco_category_id -> continuous_index (1-based)
        self.coco_id_to_continuous_id = {cat_id: i+1 for i, cat_id in enumerate(self.cat_ids)}
        self.continuous_id_to_coco_id = {v: k for k, v in self.coco_id_to_continuous_id.items()}

    def __getitem__(self, index):
        image_id = self.ids[index]
        image, boxes, labels = self._getitem(image_id)
        
        if self.transform:
             image, boxes, labels = self.transform(image, boxes, labels)
        if self.target_transform and not self.skip_annotations:
             boxes, labels = self.target_transform(boxes, labels)
             
        return image, boxes, labels

    def _getitem(self, image_id):
        img_info = self.coco.loadImgs(image_id)[0]
        file_name = img_info['file_name']
        image_path = os.path.join(self.img_dir, file_name)
        
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        boxes = []
        labels = []

        if not self.skip_annotations:
            # Load annotations
            ann_ids = self.coco.getAnnIds(imgIds=image_id)
            anns = self.coco.loadAnns(ann_ids)
            
            for ann in anns:
                if 'bbox' not in ann:
                    continue
                x, y, w, h = ann['bbox']
                if w <= 0 or h <= 0:
                    continue
                # Convert to [x1, y1, x2, y2]
                x1 = x
                y1 = y
                x2 = x + w
                y2 = y + h
                
                boxes.append([x1, y1, x2, y2])
                labels.append(self.coco_id_to_continuous_id[ann['category_id']])
            
        boxes = np.array(boxes, dtype=np.float32)
        labels = np.array(labels, dtype=np.int64)
        
        if len(boxes) == 0:
            boxes = np.zeros((0, 4), dtype=np.float32)
            
        return image, boxes, labels

    def __len__(self):
        return len(self.ids)
        
    def get_image(self, index):
        image_id = self.ids[index]
        img_info = self.coco.loadImgs(image_id)[0]
        file_name = img_info['file_name']
        image_path = os.path.join(self.img_dir, file_name)
        image = cv2.imread(image_path)
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
    def get_annotation(self, index):
        image_id = self.ids[index]
        return image_id, self._getitem(image_id)  