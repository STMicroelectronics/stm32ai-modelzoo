# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import os
import sys
import cv2
import tqdm
import numpy as np
import pandas as pd
import random, math
from typing import List
import tensorflow as tf
from pathlib import Path
from imgaug import augmenters as iaa

from tiny_yolo_v2_utils import check_cfg_attributes, set_multi_scale_max_resolution
from tiny_yolo_v2_data_augment import tiny_yolo_v2_data_aug, convert_tiny_yolo_v2_to_iaa, convert_tiny_yolo_v2_from_iaa
from models_utils import get_model_name_and_its_input_shape

def parse_data(trainset: str) -> List[str]:
    """
    Parse the training data and return a list of paths to annotation files.
    
    Args:
    - trainset: A string representing the path to the training set directory.
    
    Returns:
    - A list of strings representing the paths to annotation files.
    """
    annotation_lines = []
    path = trainset+'/'
    for file in os.listdir(path):
        if file.endswith(".txt"):
            new_path = path+file
            annotation_lines.append(new_path)
    return annotation_lines

def parse_images(sett: str) -> List[str]:
    images_pathss = []
    path = sett+'/'
    for file in os.listdir(path):
        if file.endswith(".jpg"):
            new_path = path+file
            images_pathss.append(new_path)
    return images_pathss

def data_resize(images_list: list, gt_labels_list: list, img_height: int, img_width: int, resizing_type: int = 1) -> tuple:
    '''
    Resize the original images along with their ground truth bounding boxes

    Args:
    - images_list: list of original images
    - gt_labels_list: list of ground truth bounding boxes
    - img_height: target image height
    - img_width: target image width
    - resizing_type: an integer representing the interpolation type used for resizing (default is 1)

    Returns:
    - a tuple containing:
        - images_list_resize: list of resized images
        - gt_labels_list_resize: list of resized ground truth bounding boxes
    '''
    seq_resize = iaa.Sequential([iaa.Resize({"height": img_height,"width": img_width}, interpolation=resizing_type)])
    gt_labels_list_iaa = convert_tiny_yolo_v2_to_iaa(gt_labels_list)
    images_list_resize, gt_labels_list_iaa_resize = seq_resize(images=images_list, bounding_boxes=gt_labels_list_iaa)
    gt_labels_list_resize = convert_tiny_yolo_v2_from_iaa(gt_labels_list_iaa_resize)
    gt_labels_list_resize = np.asarray(gt_labels_list_resize)

    return images_list_resize, gt_labels_list_resize

def tiny_yolo_v2_boxes_to_corners(boxes, image):
    '''
    Convert YOLO bounding box format to absolute corner coordinates
    Arguments:
        boxes: a list of YOLO relative bounding boxes in the format of [[class_id, x_center, y_center, width, height], ...]
        image: a numpy array representing the image with shape (height, width, channels)
    Returns:
        abs_boxes: a list of absolute corner coordinates for each bounding box in the format of [xmin, ymin, xmax, ymax, class_id]
    '''
    height, width, _ = image.shape
    abs_boxes = []
    for box in boxes:
        x_min = box[1]*width-box[3]*width/2
        y_min = box[2]*height-box[4]*height/2
        x_max = x_min+box[3]*width
        y_max = y_min+box[4]*height
        abs_boxes.append(np.array([int(x_min), int(y_min), int(x_max), int(y_max), int(box[0])]))
    return abs_boxes


def get_ground_truth_data(annotation, max_boxes = 100):
    """
    Get the ground truth data for an image and return the image and box data.
    
    Args:
    - annotation: A string representing the path to the annotation file.
    - max_boxes: An integer representing the maximum number of boxes to include in the box data.
    
    Returns:
    - A tuple containing the image as a numpy array and the box data as a numpy array.
    """
    image_path = os.path.splitext(annotation)[0]+'.jpg'
    img = cv2.imread(image_path)
    if len(img.shape) != 3:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    txt_file_size = os.path.getsize(annotation)
    if txt_file_size != 0:
        ground_truths = pd.read_csv(annotation, sep=" ", header=None)
        ground_truths.columns = ["class_id", "x", "y", "w", "h"]
        labelz = ground_truths.values.tolist()
        labelz = tiny_yolo_v2_boxes_to_corners(labelz, img_rgb)
    else:
        labelz = []
    boxes = np.array(labelz)
    #(xmin, ymin, xmax, ymax, cls_id)
    if len(boxes)>max_boxes:
        boxes = boxes[:max_boxes]
    # fill in box data
    box_data = np.zeros((max_boxes,5))
    if len(boxes)>0:
        box_data[:len(boxes)] = boxes

    return img_rgb, box_data

def preprocess_true_boxes(true_boxes, anchors_a, input_shape, num_classes,network_stride):
    '''
    Preprocesses the ground truth bounding boxes to generate the target output for the YOLOv2 model

    Args:
    - true_boxes: a numpy array of ground truth bounding boxes in the format of [[xmin, ymin, xmax, ymax, class_id], ...]
    - anchors_a: a numpy array of anchor boxes
    - input_shape: a tuple representing the input shape of the model
    - num_classes: an integer representing the number of classes to be predicted by the model

    Returns:
    - a numpy array representing the processed output
    '''
    assert (true_boxes[..., 4] < num_classes).all(), 'class id must be less than num_classes'
    height, width = input_shape
    num_anchors = len(anchors_a)
    # Downsampling factor of 5x 2-stride max_pools == 32.
    assert height % network_stride == 0, 'Image sizes in YOLO_v2 must be multiples of {}.'.format(network_stride)
    assert width % network_stride == 0, 'Image sizes in YOLO_v2 must be multiples of {}.'.format(network_stride)
    conv_height = height // network_stride
    conv_width = width // network_stride
    #and image relative coordinate.
    true_boxes = np.array(true_boxes, dtype='float32')
    input_shape = np.array(input_shape, dtype='int32')
    boxes_xy = (true_boxes[..., 0:2] + true_boxes[..., 2:4]) // 2
    boxes_wh = true_boxes[..., 2:4] - true_boxes[..., 0:2]

    clipped_boxes_wh = np.clip((boxes_wh / input_shape[::-1]), a_min=0, a_max=0.99)
    clipped_boxes_xy = np.clip((boxes_xy / input_shape[::-1]), a_min=0, a_max=0.99)

    true_boxes[..., 0:2] = clipped_boxes_xy
    true_boxes[..., 2:4] = clipped_boxes_wh

    num_box_params = true_boxes.shape[1]
    y_true = np.zeros(
        (conv_height, conv_width, num_anchors, num_box_params+1),
        dtype=np.float32)
    #abs anchors wrt grid cell anch_lib = anch/model_input_shape*grid_size
    anchors = (anchors_a/height)*conv_height
    for box in true_boxes:
        # bypass invalid true_box, if w,h is 0
        if box[2] == 0 and box[3] == 0:
            continue
        box_class = box[4:5]
        box = box[0:4] * np.array([conv_width, conv_height, conv_width, conv_height],dtype=np.float32)
        i = np.floor(box[1]).astype('int')
        j = np.floor(box[0]).astype('int')
        best_iou = 0
        selected_anchors = []
        best_anchor = 0
        for k, anchor in enumerate(anchors):
            # Find IOU between box shifted to origin and anchor box.
            box_maxes = box[2:4] / 2.
            box_mins = -box_maxes
            anchor_maxes = (anchor / 2.)
            anchor_mins = -anchor_maxes

            intersect_mins = np.maximum(box_mins, anchor_mins)
            intersect_maxes = np.minimum(box_maxes, anchor_maxes)
            intersect_wh = np.maximum(intersect_maxes - intersect_mins, 0.)
            intersect_area = intersect_wh[0] * intersect_wh[1]
            box_area = (box[2]) * (box[3])
            anchor_area = anchor[0] * anchor[1]
            iou = intersect_area / (box_area + anchor_area - intersect_area)

            # select 1 best anchor
            if iou > best_iou:
                best_iou = iou
                best_anchor = k


        # Got selected anchor and assign to true box
        if best_iou > 0:
            adjusted_box = np.array(
                [
                    box[0] - j, box[1] - i,
                    np.log(box[2] / anchors[best_anchor][0]),
                    np.log(box[3] / anchors[best_anchor][1]),
                    1,
                    box_class[0]
                ],
                dtype=np.float32)
            y_true[i, j, best_anchor] = adjusted_box
    return y_true

def get_y_true_data(box_data, anchors, input_shape, num_classes,network_stride):
    '''
    Precompute y_true feature map data on a batch for training.

    Args:
        box_data: list of ground truth bounding boxes in the format of [[xmin, ymin, xmax, ymax, class_id], ...]
        anchors: array of anchor boxes in the format of [[width, height], ...]
        input_shape: input shape of the model in the format of (width, height)
        num_classes: number of classes in the dataset
    Returns:
        y_true_data: array of y_true feature map data
    '''
    y_true_data = [0 for i in range(len(box_data))]
    for i, boxes in enumerate(box_data):
        y_true_data[i] = preprocess_true_boxes(boxes, anchors, input_shape, num_classes,network_stride)

    return np.array(y_true_data)

class tiny_yolo_v2_data_geneator(tf.keras.utils.Sequence):

    def __init__(self, cfg, train_annotations, batch_size, input_shape, anchors, num_classes,aug=True, multi_scale = True):
        """
        Returns a yolo2 data generator.

        Args:
            cfg: object containing configuration parameters
            annotation_lines (list of str): List of strings containing the paths to image and annotation files.
            batch_size (int): Number of images to process at once.
            input_shape (tuple): Tuple specifying the size of the input images.
            anchors (list of tuples): List of tuples representing the anchor boxes used for object detection.
            num_classes (int): Number of classes to detect.
            aug (bool): Boolean indicating whether or not to apply data augmentation.
            multi_scale (bool): Apply or not multi scale data augmentation

        Returns:
            yolo2_data_generator: A yolo2 data generator.
        """        
        self.cfg = cfg
        self.annotations_files = train_annotations
        self.batch_size = batch_size
        self.input_size = input_shape[0]
        self.interpolation_id = 0
        self.rescale_step = 0
        self.rescale_interval = 10
        self.input_shape_list = self.cfg.data_augmentation.multi_scale_list
        self.size_id = 0
        self.len_dataset = len(self.annotations_files)
        self.aug = aug
        self.scale = cfg.preprocessing.rescaling.scale
        self.offset = cfg.preprocessing.rescaling.offset
        self.num_classes = num_classes
        self.multi_scale = multi_scale
        self.anchors_arr = anchors
        self.interpolation = cfg.preprocessing.resizing.interpolation
        self.network_stride = cfg.postprocessing.network_stride

        if self.interpolation == 'bilinear':
            self.interpolation_id = 1
        elif self.interpolation == 'nearest':
            self.interpolation_id = 0
        else:
            raise ValueError("Invalid interpolation method. Supported methods are 'bilinear' and 'nearest'.")

    def __len__(self):
        return math.ceil(len(self.annotations_files) / self.batch_size)

    def on_epoch_end(self):
        np.random.shuffle(self.annotations_files)
        np.random.shuffle(self.input_shape_list)

    def __getitem__(self, idx):

        low = idx * self.batch_size
        high = min(low + self.batch_size, len(self.annotations_files))

        annotations_files_batch = self.annotations_files[low:high]

        #count steps
        if self.multi_scale:
            self.rescale_step = (self.rescale_step + 1) % self.rescale_interval
            if self.rescale_step == 0:
                self.input_size = self.input_shape_list[self.size_id][0]
                self.size_id = self.size_id + 1
                if self.size_id == len(self.input_shape_list):
                    self.size_id = 0
                    np.random.shuffle(self.input_shape_list)

        images_batch = []
        labels_batch = []

        for annotation_file in annotations_files_batch:
            image_data , label_data = get_ground_truth_data(annotation_file, max_boxes = self.cfg.training.max_gt)
            images_batch.append(image_data)
            labels_batch.append(label_data)

        labels_batch_array = np.array(labels_batch)

        if self.aug:
            resized_img_batch, rescaled_gt_batch_array = data_resize(images_batch,
                                                                    labels_batch_array,
                                                                    self.input_size, self.input_size,
                                                                    resizing_type = self.interpolation_id)
            resized_images_batch, rescaled_labels_batch_array = tiny_yolo_v2_data_aug(self.cfg, resized_img_batch, rescaled_gt_batch_array, max_boxes = self.cfg.training.max_gt)
        else:
            resized_images_batch, rescaled_labels_batch_array = data_resize(images_batch,
                                                                    labels_batch_array,
                                                                    self.input_size, self.input_size,
                                                                    resizing_type = self.interpolation_id)
        
        images_batch_aug = [np.asarray(img).astype(float) * self.scale + self.offset for img in resized_images_batch]
        resized_images_batch_array = np.array(images_batch_aug)

        y_true_data = get_y_true_data(rescaled_labels_batch_array,
                                      self.anchors_arr,
                                      (self.input_size,self.input_size),
                                      self.num_classes,
                                      self.network_stride)
        return [resized_images_batch_array, y_true_data], np.zeros(self.batch_size)

def count_ground_truth_data(annotation):
    """
    Count number of ground truths within an annotation file.
    
    Args:
    - annotation: A string representing the path to the annotation file.
    
    Returns:
    - num : An int representing the number of get within a txt file.

    """
    txt_file_size = os.path.getsize(annotation)
    if txt_file_size != 0:
        ground_truths = pd.read_csv(annotation, sep=" ", header=None)
        labelz = ground_truths.values.tolist()
    else:
        labelz = []
    num = len(labelz)
    return num

def count_max_gt(cfg, train_annotations,val_annotations):
    """
    Get the maximum number of ground truths within the dataset txt files.
    
    Args:
        cfg: object containing configuration parameters
        train_annotations : List of strings containing the paths to image and annotation files.
        val_annotations : List of strings containing the paths to image and annotation files.
    
    Returns:
        - None

    """
    max_gt = 0

    tf.print("[INFO] : Analyzing the train set ...")
    for annotation_file in tqdm.tqdm(train_annotations):
        num = count_ground_truth_data(annotation_file)
        if num>max_gt:
            max_gt = num
    tf.print("[INFO] : Analyzing the validation set ...")
    for annotation_file in tqdm.tqdm(val_annotations):
        num = count_ground_truth_data(annotation_file)
        if num>max_gt:
            max_gt = num
    cfg.training.max_gt = max_gt

def generate_quant(cfg=None, images_filename_list=None, batch_size=None, img_width=None, img_height=None):
    """
    Create a generator for model.fit_generator
    Arguments:
        cfg: dictionary containing configuration parameters
        images_filename_list: list of filename of original images
        batch_size: size of generated minibatch
        img_width: image width
        img_height: image height
    Returns:
        [images_batch, truths_batch]: a minibatch of images and encoded bounding boxes for training
    """
    
    channels = 1 if cfg.preprocessing.color_mode == "grayscale" else 3
    interpolation = cfg.preprocessing.resizing.interpolation

    def parse_function(filename):

        image_string = tf.io.read_file(filename)
        image = tf.io.decode_image(image_string, channels=channels, expand_animations=False)
        image = tf.image.resize(image, [img_height, img_width], method=interpolation)
        image = tf.cast(image, tf.float32) * cfg.preprocessing.rescaling.scale + cfg.preprocessing.rescaling.offset

        return image

    # Get the number of samples
    num_samples = len(images_filename_list)
    # handle case when the batch size is greater or equal the dataset size
    if batch_size >= num_samples:
        exp = np.math.log(num_samples, 2)
        exp = np.math.floor(exp)
        batch_size = int(2 ** exp)

    quant_dataset = tf.data.Dataset.from_tensor_slices(images_filename_list)
    quant_dataset = quant_dataset.map(parse_function,num_parallel_calls=tf.data.AUTOTUNE)
    quant_dataset = quant_dataset.batch(batch_size,drop_remainder=True)

    return quant_dataset

def tiny_yolo_v2_preprocess(cfg):
    """
    Preprocesses the data based on the provided configuration.

    Args:
        cfg : Configuration object containing the settings.

    Returns:
        tuple: A tuple containing the following:
            - train_gen (object): Training data generator.
            - valid_gen (object): Validation data generator.
            - test_gen (object): Test data generator (default: None).
            - quantization_gen (object): Quantization data generator (default: None).
    """
    check_cfg_attributes(cfg)
    if cfg.operation_mode in ['training' ,'chain_tqeb','chain_tqe']:
        set_multi_scale_max_resolution(cfg)
    training_path = cfg.dataset.training_path
    validation_path = cfg.dataset.validation_path
    quantization_path = cfg.dataset.quantization_path
    test_path = cfg.dataset.test_path
    validation_split = cfg.dataset.validation_split

    input_shape = cfg.training.model.input_shape
    batch_size = cfg.training.batch_size
    classes = cfg.dataset.class_names
    if cfg.operation_mode not in ['quantization' ,'benchmarking', 'chain_qb']:
        num_classes = len(classes)
        anchors_list = cfg.postprocessing.yolo_anchors
        anchors = np.array(anchors_list).reshape(-1, 2)
        assert (input_shape[0]% cfg.postprocessing.network_stride == 0 and input_shape[1]% cfg.postprocessing.network_stride == 0), 'model_input_shape should be multiples of {}'.format(cfg.postprocessing.network_stride)

    if validation_path and training_path:
        # Load training and validation datasets
        tf.print("Loading Training dataset... ")
        train_annotations = parse_data(training_path)
        tf.print("Loading Validation dataset... ")
        val_annotations = parse_data(validation_path)
        num_train = len(train_annotations)
        num_val = len(val_annotations)

    elif training_path and not validation_path:
        # Split the training dataset into training and validation sets
        tf.print("Loading Training dataset... ")
        train_set = parse_data(training_path)
        num_val = int(len(train_set)*validation_split)
        num_train = len(train_set) - num_val

        train_annotations = train_set[:num_train]
        val_annotations = train_set[num_train:]

    else:
        train_annotations = None
        val_annotations = None
        num_val = 0
        num_train = 0

    num_samples = {"num_train_samples": num_train, "num_val_samples": num_val}

    if train_annotations and val_annotations:
        if cfg.operation_mode in ['training' ,'chain_tqeb','chain_tqe']:
            count_max_gt(cfg, train_annotations,val_annotations)
            train_dataset = tiny_yolo_v2_data_geneator(cfg, train_annotations, batch_size, input_shape[:-1], anchors, num_classes,aug=True, multi_scale = True)
            val_dataset = tiny_yolo_v2_data_geneator(cfg, val_annotations, batch_size, input_shape[:-1], anchors, num_classes,aug=False, multi_scale = False)
        else:
            train_dataset = None
            val_dataset = None
    else:
        train_dataset = None
        val_dataset = None


    # Load the quantization dataset if provided
    if quantization_path or training_path:

        if cfg.general.model_path:
            if Path(cfg.general.model_path).suffix =='.onnx':
                _, ish = get_model_name_and_its_input_shape(cfg.general.model_path)
                input_shape = [ish[1],ish[2],ish[0]]
            else:
                _, input_shape = get_model_name_and_its_input_shape(cfg.general.model_path)

        img_width, img_height, _ = input_shape
        if training_path:
            quant_annotations = parse_images(training_path)
        else:
            quant_annotations = parse_images(quantization_path)

        if not batch_size:
            batch_size=64

        quantization_dataset = generate_quant(cfg=cfg,
                                              images_filename_list=quant_annotations,
                                              batch_size = batch_size,
                                              img_width  = img_width,
                                              img_height = img_height)

        tf.print("Loading Quantization dataset...")
        quantization_annotations = parse_data(quantization_path)
    else:
        quantization_dataset = None
        quantization_annotations = None

    # Load the test dataset if provided
    if test_path:
        tf.print("Loading Test dataset...")
        test_dataset = parse_data(test_path)
    else:
        test_dataset = None


    # Create the training, validation, quantization, and test datasets
    return train_annotations, val_annotations, test_dataset, quantization_annotations, train_dataset, val_dataset, quantization_dataset
