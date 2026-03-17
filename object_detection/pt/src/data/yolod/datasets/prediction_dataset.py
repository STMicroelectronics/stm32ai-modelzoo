# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Copyright (c) Megvii, Inc. and its affiliates.


import os
import glob
from torch.utils.data import Dataset
from PIL import Image
import cv2 

class PredictionDataset(Dataset):
    """
    Simple dataset for prediction/inference:
    - Loads images from a directory
    - Applies YOLOD ValTransform (no labels)
    - Returns: processed_img, image_path
    """

    IMG_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp")

    def __init__(self, image_dir, input_size=640, transform=None):
        """
        Args:
            image_dir (str): Directory containing images for prediction.
            transform: ValTransform or any preprocessing transform.
        """
        self.image_dir = image_dir
        self.transform = transform
        self.input_size = input_size
        # Collect all images
        self.image_paths = []
        for ext in self.IMG_EXTENSIONS:
            self.image_paths.extend(glob.glob(os.path.join(image_dir, f"*{ext}")))

        self.image_paths.sort()

        if len(self.image_paths) == 0:
            raise RuntimeError(f"No images found in {image_dir}")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, index):
        """
        Returns:
            img: transformed tensor
            path: original file path
        """
        path = self.image_paths[index]
        img = cv2.imread(path)
        
        if self.transform is not None:
            img, _ = self.transform(img, None, self.input_size) # res and input_size needed
            
            # YOLOD ValTransform expects numpy arrays (H, W, C)
            # img = self.transform(img)[0]  # transform returns (img, target)

        return img, path