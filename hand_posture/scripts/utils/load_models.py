# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


import CNN2D_ST_HandPosture


def get_model(cfg):
    if cfg.model.model_type.version == "v1" and cfg.model.model_type.name == "CNN2D_ST_HandPosture":
        return CNN2D_ST_HandPosture.get_ST_CNN2D_model(cfg)
    # elif cfg.model.model_type.name == "custom":
    #     return custom_model.get_scratch_model(cfg)
    else:
        raise TypeError("Model not defined, please select the listed options in `./doc/model.json`.")
