# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
from PIL import Image
from torch.utils.data import Dataset
import os
import numpy as np

class SSDPredictionDataset(Dataset):
    def __init__(self, path, transform):
        self.transform = transform
        self.path = path

        if os.path.isdir(path):
            exts = (".jpg", ".jpeg", ".png", ".bmp")
            self.path = [
                os.path.join(path, f) for f in sorted(os.listdir(path))
                if f.lower().endswith(exts)
            ]
        elif os.path.isfile(path):
            with open(path, "r") as f:
                self.path = [ln.strip() for ln in f if ln.strip()]
        else:
            raise ValueError(f"prediction_path not found: {path}")

    def __len__(self):
        return len(self.path)

    def __getitem__(self, idx):
        p = self.path[idx]
        img = Image.open(p).convert("RGB")
        img = np.array(img)
        empty_boxes  = np.zeros((0, 4), dtype=np.float32)
        empty_labels = np.zeros((0,),   dtype=np.int64)
        img, _, _ = self.transform(img, boxes=empty_boxes, labels=empty_labels)        
        return img, p