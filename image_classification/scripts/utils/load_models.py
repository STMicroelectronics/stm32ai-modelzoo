# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


import custom_model
import fdmobilenet
import MobileNetV1
import MobileNetV2
import resnetv1
import squeezenetv10
import squeezenetv11
import stmnist
import sys


def ask_yes_no(question):
    """
    Helper to get yes / no answer from user.
    """
    confirm = {'yes', 'y'}
    discard = {'no', 'n'}

    done = False
    answer = 0
    print(question)
    while not done:
        choice = input().lower()
        if choice in confirm:
            answer = 1
            done = True
        elif choice in discard:
            answer = 0
            done = True
        else:
            print("Please respond by yes or no.")
    return answer


def get_model(cfg):
    if cfg.model.model_type.version == "v1" and cfg.model.model_type.name.lower() == "mobilenet".lower():
        if cfg.model.transfer_learning and (cfg.model.model_type.alpha in [0.25, 0.50, 0.75, 1.0]):
            return MobileNetV1.get_transfer_learning_model(cfg)
        elif cfg.model.transfer_learning:
            confirmation = ask_yes_no(
                "No pretrained weights are found for this model, do you want to continue the training with random weights (Y/N)?")
            if confirmation == 1:
                return MobileNetV1.get_scratch_model(cfg)
            else:
                sys.exit("Training aborted!")
        else:
            return MobileNetV1.get_scratch_model(cfg)

    elif cfg.model.model_type.version == "v2" and cfg.model.model_type.name.lower() == "mobilenet".lower():
        if cfg.model.transfer_learning and (cfg.model.model_type.alpha in [0.35, 0.50, 0.75, 1.0, 1.3, 1.4]):
            return MobileNetV2.get_transfer_learning_model(cfg)
        elif cfg.model.transfer_learning:
            confirmation = ask_yes_no(
                "No pretrained weights are found for this model, do you want to continue the training with random weights(Y/N)?")
            if confirmation == 1:
                return MobileNetV2.get_scratch_model(cfg)
            else:
                sys.exit("Training aborted!")
        else:
            return MobileNetV2.get_scratch_model(cfg)

    elif cfg.model.model_type.name.lower() == "fdmobilenet".lower():
        if cfg.model.transfer_learning:
            raise TypeError("Can't load pretrained weights, only training from scratch exists")
        elif not cfg.model.transfer_learning and cfg.model.model_type.alpha in [0.25, 0.50, 0.75, 1.0]:
            return fdmobilenet.get_scratch_model(cfg)
        else:
            raise ValueError("alpha value should be in [0.25, 0.50, 0.75, 1.0] ")

    elif cfg.model.model_type.version == "v1" and cfg.model.model_type.name.lower() == "resnet".lower():
        if cfg.model.transfer_learning:
            raise TypeError("Can't load pretrained weights, only training from scratch exists")
        elif not cfg.model.transfer_learning and cfg.model.model_type.depth in [8, 20, 32]:
            return resnetv1.get_scratch_model(cfg)
        else:
            raise ValueError("depth value should be in [8, 20, 32] ")

    elif cfg.model.model_type.version == "v10" and cfg.model.model_type.name.lower() == "squeezenet":
        if cfg.model.transfer_learning:
            raise TypeError("Can't load pretrained weights, only training from scratch exists")
        else:
            return squeezenetv10.get_scratch_model(cfg)

    elif cfg.model.model_type.version == "v11" and cfg.model.model_type.name.lower() == "squeezenet":
        if cfg.model.transfer_learning:
            raise TypeError("Can't load pretrained weights, only training from scratch exists")
        else:
            return squeezenetv11.get_scratch_model(cfg)

    elif cfg.model.model_type.name.lower() == "stmnist":
        return stmnist.get_scratch_model(cfg)
    
    elif cfg.model.model_type.name == "custom":
        return custom_model.get_scratch_model(cfg)
    else:
        raise TypeError("Model not defined, please select the listed options in `./doc/model.json`.")
