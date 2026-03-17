# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
#!/usr/bin/env python3
# Copyright (c) Megvii Inc. All rights reserved.

from .yacs import CfgNode

cfg = CfgNode(new_allowed=True)
cfg.model = CfgNode(new_allowed=True)
cfg.dataset = CfgNode(new_allowed=True)
cfg.training = CfgNode(new_allowed=True)
cfg.test = CfgNode(new_allowed=True)
cfg.optimizer = CfgNode(new_allowed=True)
cfg.scheduler = CfgNode(new_allowed=True)
cfg.eval = CfgNode(new_allowed=True)

# ---------------- Utility Functions ---------------- #
def load_config(cfg, config_file):
    """
    Load configuration from a YAML file and merge it into the default cfg.
    """
    cfg.defrost()
    cfg.merge_from_file(config_file)
    cfg.freeze()


def check_cfg_value(cfg: CfgNode):
    h, w = cfg.input_size
    assert h % 32 == 0 and w % 32 == 0, "input size must be multiples of 32"
