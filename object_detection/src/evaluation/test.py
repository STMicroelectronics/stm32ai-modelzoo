# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import logging
import os
import sys
import warnings

import cv2
import hydra
import numpy as np
import tensorflow as tf
from omegaconf import OmegaConf, DictConfig
from munch import DefaultMunch
from matplotlib import pyplot as plt

from metrics_utils import *


logger = tf.get_logger()
logger.setLevel(logging.ERROR)
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def get_config(cfg):
    config_dict = OmegaConf.to_container(cfg)
    configs = DefaultMunch.fromDict(config_dict)
    return configs


def run_quantized_model_inference(cfg):
    interpreter_quant = tf.lite.Interpreter(model_path = cfg.model.model_path)
    interpreter_quant.allocate_tensors()
    input_details = interpreter_quant.get_input_details()[0]
    input_index_quant = interpreter_quant.get_input_details()[0]["index"]
    output_index_quant = interpreter_quant.get_output_details()
    class_names = ["background"] + cfg.dataset.class_names

    if cfg.dataset.test_path is not None:
        test_set_path = cfg.dataset.test_path
    else:
        test_set_path = cfg.dataset.validation_path

    for image_file in tqdm.tqdm(os.listdir(test_set_path)):
        if image_file.endswith(".jpg"):
            image = cv2.imread(os.path.join(test_set_path, image_file))
            if len(image.shape) != 3:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, _ = image.shape
            resized_image = cv2.resize(image, (int(cfg.model.input_shape[0]), int(cfg.model.input_shape[0])), interpolation=cv2.INTER_LINEAR)
            image_data = resized_image/cfg.pre_processing.rescaling.scale + cfg.pre_processing.rescaling.offset
            img = image_data.astype(np.float32)
            image_processed = (img / input_details['quantization'][0]) + input_details['quantization'][1]
            image_processed = np.clip(np.round(image_processed), np.iinfo(input_details['dtype']).min, np.iinfo(input_details['dtype']).max)
            image_processed = image_processed.astype(input_details['dtype'])
            image_processed = tf.expand_dims(image_processed, 0)
            interpreter_quant.set_tensor(input_index_quant, image_processed)
            interpreter_quant.invoke()

            predicted_scores_output = interpreter_quant.get_tensor(output_index_quant[0]["index"])
            predicted_boxes_output = interpreter_quant.get_tensor(output_index_quant[1]["index"])
            predicted_anchors_output = interpreter_quant.get_tensor(output_index_quant[2]["index"])

            predictions = np.concatenate([predicted_scores_output, predicted_boxes_output, predicted_anchors_output], axis=2)
            preds_decoded = decode_predictions(predictions, normalize=True, org_img_height=height, org_img_width=width)
            final_preds = do_nms(preds_decoded, nms_thresh=float(cfg.postprocessing.NMS_thresh), confidence_thresh=float(cfg.postprocessing.confidence_thresh))
            bbox_thick = int(0.6 * (height + width) / 600)
            for _category, predictions in final_preds.items():
                predicted_class = _category
                for prediction in predictions:
                    score, xmi, ymi, xma, yma = prediction
                    idClass, conf, x_min, y_min, x_max, y_max = int(predicted_class), float(check(score)), int(check(xmi)), int(check(ymi)), int(check(xma)), int(check(yma))
                    bbox_mess = '{}-{:.2}'.format(class_names[int(idClass)],conf)
                    cv2.rectangle(image,(x_min, y_min), (x_max, y_max),(0,255,0),2)
                    cv2.putText(image, bbox_mess, (x_min,y_min-5), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 255, 0), bbox_thick//2, lineType=cv2.LINE_AA)
            plt.imshow(image)
            plt.axis("off")
            plt.show()


@hydra.main(version_base=None, config_path="", config_name="user_config")
def main(cfg: DictConfig) -> None:
    configs = get_config(cfg)
    run_quantized_model_inference(configs)

if __name__ == "__main__":
    main()