# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import numpy as np

from object_detection.pt.src.utils.ssd.box_utils import SSDSpec, SSDBoxSizes, generate_ssd_priors

class SQUEEZENET_CONFIG():
    def __init__(self):
        self.image_size = 300
        self.image_mean = np.array([127, 127, 127])  # RGB layout
        self.image_std = 128.0
        self.iou_threshold = 0.45
        self.center_variance = 0.1
        self.size_variance = 0.2

        specs = [
            SSDSpec(17, 16, SSDBoxSizes(60, 105), [2, 3]),
            SSDSpec(10, 32, SSDBoxSizes(105, 150), [2, 3]),
            SSDSpec(5, 64, SSDBoxSizes(150, 195), [2, 3]),
            SSDSpec(3, 100, SSDBoxSizes(195, 240), [2, 3]),
            SSDSpec(2, 150, SSDBoxSizes(240, 285), [2, 3]),
            SSDSpec(1, 300, SSDBoxSizes(285, 330), [2, 3])
        ]


        self.priors = generate_ssd_priors(specs, self.image_size)