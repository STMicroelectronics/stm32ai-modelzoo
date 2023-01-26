# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import ssl
from datetime import datetime

from hydra.core.hydra_config import HydraConfig

ssl._create_default_https_context = ssl._create_unverified_context


def class_names_list(class_names):
    clist_str = '{'
    for class_name in class_names:
        clist_str += f'"{class_name}",'
    clist_str = clist_str[:-1] + '}'
    return clist_str


def gen_h_user_file(config):
    class Flags:
        def __init__(self, **entries):
            self.__dict__.update(entries)
    params = Flags(**config)
    class_names = params.dataset.class_names
    # input_shape = params.model.input_shape

    classes = ''
    for i, x in enumerate(params.dataset.class_names):
        if i == (len(class_names) - 1):
            classes = classes + '"' + str(x) + '"'
        else:
            classes = classes + '"' + str(x) + '"' + ','

    path = os.path.join(HydraConfig.get().runtime.output_dir, "C_header/")
    try:
        os.mkdir(path)
    except OSError as error:
        print(error)

    with open(os.path.join(path, "ai_model_config.h"), "wt") as f:
        f.write('/**')
        f.write('******************************************************************************\n')
        f.write('* @file    ai_model_config.h\n')
        f.write('* @author  STMicroelectronics - AIS - MCD Team\n')
        f.write('* @version 1.0.0\n')
        f.write(f'* @date    {datetime.now().strftime("%Y-%b-%d")}\n')
        f.write('* @brief   Configure the getting started functionality\n')
        f.write('*\n')
        f.write('*  Each logic module of the application should define a DEBUG control byte\n')
        f.write('* used to turn on/off the log for the module.\n')
        f.write('*\n')
        f.write('*********************************************************************************\n')
        f.write('* @attention\n')
        f.write('*\n')
        f.write('* Copyright (c) 2022 STMicroelectronics\n')
        f.write('* All rights reserved.\n')
        f.write('*\n')
        f.write('* This software is licensed under terms that can be found in the LICENSE file in\n')
        f.write('* the root directory of this software component.\n')
        f.write('* If no LICENSE file comes with this software, it is provided AS-IS.\n')
        f.write('*********************************************************************************\n')
        f.write('*/\n')

        f.write("/* ---------------    Generated code    ----------------- */\n")
        f.write('#ifndef AI_MODEL_CONFIG_H\n')
        f.write('#define AI_MODEL_CONFIG_H\n')
        f.write('\n')
        f.write('#ifdef __cplusplus\n')
        f.write('extern "C" {\n')
        f.write('#endif\n')
        f.write('\n')
        f.write('\n')
        # f.write('#define CTRL_SEQUENCE                          {CTRL_CMD_PARAM_AI,0}\n')

        if params.model.model_type.name == 'svc':
            f.write('#define CTRL_X_CUBE_AI_MODE_NB_OUTPUT          (2U)\n')
            f.write('#define CTRL_X_CUBE_AI_MODE_OUTPUT_1           (CTRL_AI_CLASS_IDX)\n')
            f.write('#define CTRL_X_CUBE_AI_MODE_OUTPUT_2           (CTRL_AI_CLASS_DISTRIBUTION)\n')
            f.write('#define CTRL_X_CUBE_AI_VECTORIZE\n')
        else:
            f.write('#define CTRL_X_CUBE_AI_MODE_NB_OUTPUT          (1U)\n')
            f.write('#define CTRL_X_CUBE_AI_MODE_OUTPUT_1           (CTRL_AI_CLASS_DISTRIBUTION)\n\n')

        f.write(f'#define CTRL_X_CUBE_AI_MODE_CLASS_NUMBER       ({len(class_names)}U)\n')
        f.write('#define CTRL_X_CUBE_AI_MODE_CLASS_LIST         ' + class_names_list(class_names)+'\n')
        f.write('#define CTRL_X_CUBE_AI_SENSOR_TYPE             (COM_TYPE_ACC)\n')
        f.write('#define CTRL_X_CUBE_AI_SENSOR_ODR              (26.0F)\n')
        f.write('#define CTRL_X_CUBE_AI_SENSOR_FS               (4.0F)\n')
        f.write('#define CTRL_X_CUBE_AI_NB_SAMPLES              (0U) // for how many samples you want to run inference on\n')
        if params.pre_processing.preprocessing:
            f.write('#define CTRL_X_CUBE_AI_PREPROC                 (CTRL_AI_GRAV_ROT_SUPPR)\n')
        f.write('\n')
        f.write('#ifdef __cplusplus\n')
        f.write('}\n')
        f.write('#endif\n')
        f.write('\n')
        f.write('#endif /* AI_MODEL_CONFIG_H */\n')
