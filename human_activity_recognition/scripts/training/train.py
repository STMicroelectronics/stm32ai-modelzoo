# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import logging
import os
import sys
import warnings

import hydra
import mlflow
from omegaconf import DictConfig

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

logger = tf.get_logger()
logger.setLevel(logging.ERROR)
warnings.filterwarnings("ignore")
sys.path.append(os.path.abspath('../utils'))
sys.path.append(os.path.abspath('../utils/models'))
sys.path.append(os.path.abspath('../../../common'))
from utils import get_config, mlflow_ini, setup_seed, train, train_svc


@hydra.main(version_base=None, config_path="", config_name="user_config")
def main(cfg: DictConfig) -> None:
    # initilize configuration & mlflow
    configs = get_config(cfg)
    mlflow_ini(configs)
    setup_seed()

    # train the model
    model_name = configs.model.model_type.name
    if model_name in ['ign', 'gmp', 'custom', 'svc']:
        mlflow.log_param('model_type', cfg.model.model_type.name)
        if model_name == 'svc':
            train_svc(configs)
        else:
            train(configs)
    else:
        print('''[ERROR:] MODEL_TYPE_NOT_SUPPORTED : Only supported model types are 'ign', 'gmp', 'custom', or 'svc' ''')


if __name__ == "__main__":
    main()
