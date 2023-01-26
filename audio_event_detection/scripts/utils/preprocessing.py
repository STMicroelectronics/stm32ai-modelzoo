# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

def preprocessing(cfg):
    # Placeholder, as Audio preprocessing doesn't have convenient TF layers.
    # For now, return dicts containing params for temporal & freq domain preprocessing

    temp_preprocessing_params = cfg.pre_processing
    feature_extraction_params = cfg.feature_extraction
    print('[INFO] Audio preprocessing has not been converted to TF layers yet. Using Librosa on CPU instead')
    return temp_preprocessing_params, feature_extraction_params