# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from SSD_MV1 import ssd_model

def get_model(cfg):

    if cfg.model.model_type.version =="v1" and cfg.model.model_type.name.lower() == "mobilenet".lower():
        if cfg.model.model_type.alpha in [0.25,0.50,0.75,1.0]:
            return ssd_model(cfg)
        else:
            raise TypeError("alpha should be in [0.25,0.50]")
    else:
        raise TypeError("Model not define, please select version = v1 and name = mobilenet")