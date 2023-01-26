# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import custom_model as custom_model
import gmp as gmp
import ign as ign


def get_model(cfg):
    if cfg.model.model_type.name == "gmp":
        return gmp.build_gmp(cfg)
    if cfg.model.model_type.name == "ign":
        return ign.build_ign(cfg)
    if cfg.model.model_type.name == "svc":
        print('svc chosen')
        return None
    if cfg.model.model_type.name == "custom":
        return custom_model.get_model(cfg)
