# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import pathlib

import numpy as np
import torch

from object_detection.pt.src.utils.ssd import box_utils, measurements
from object_detection.pt.src.utils.ssd.misc import Timer
from torch.utils.data import DataLoader
from tqdm import tqdm

def group_annotation_by_class(dataset):
    true_case_stat = {}
    all_gt_boxes = {}
    all_difficult_cases = {}

    for i in range(len(dataset)):
        image_id, annotation = dataset.get_annotation(i)
        gt_boxes, classes, is_difficult = annotation
        gt_boxes = torch.from_numpy(gt_boxes)

        for j, difficult in enumerate(is_difficult):
            class_index = int(classes[j])
            gt_box = gt_boxes[j]

            if not difficult:
                true_case_stat[class_index] = true_case_stat.get(class_index, 0) + 1

            if class_index not in all_gt_boxes:
                all_gt_boxes[class_index] = {}
            if image_id not in all_gt_boxes[class_index]:
                all_gt_boxes[class_index][image_id] = []
            all_gt_boxes[class_index][image_id].append(gt_box)

            if class_index not in all_difficult_cases:
                all_difficult_cases[class_index] = {}
            if image_id not in all_difficult_cases[class_index]:
                all_difficult_cases[class_index][image_id] = []
            all_difficult_cases[class_index][image_id].append(difficult)

    for class_index in all_gt_boxes:
        for image_id in all_gt_boxes[class_index]:
            all_gt_boxes[class_index][image_id] = torch.stack(all_gt_boxes[class_index][image_id])

    for class_index in all_difficult_cases:
        for image_id in all_difficult_cases[class_index]:
            all_difficult_cases[class_index][image_id] = torch.tensor(
                all_difficult_cases[class_index][image_id]
            )

    return true_case_stat, all_gt_boxes, all_difficult_cases


def compute_average_precision_per_class(
    num_true_cases,
    gt_boxes,
    difficult_cases,
    prediction_file,
    iou_threshold,
    use_2007_metric,
):
    with open(prediction_file) as f:
        image_ids = []
        boxes = []
        scores = []

        for line in f:
            t = line.rstrip().split(" ")
            image_ids.append(t[0])
            scores.append(float(t[1]))
            box = torch.tensor([float(v) for v in t[2:]]).unsqueeze(0)
            box -= 1.0  # convert to python format where indexes start from 0
            boxes.append(box)

        scores = np.array(scores)
        sorted_indexes = np.argsort(-scores)
        boxes = [boxes[i] for i in sorted_indexes]
        image_ids = [image_ids[i] for i in sorted_indexes]

        true_positive = np.zeros(len(image_ids))
        false_positive = np.zeros(len(image_ids))
        matched = set()

        for i, image_id in enumerate(image_ids):
            box = boxes[i]
            if image_id not in gt_boxes:
                false_positive[i] = 1
                continue

            gt_box = gt_boxes[image_id]
            ious = box_utils.iou_of(box, gt_box)
            max_iou = torch.max(ious).item()
            max_arg = torch.argmax(ious).item()

            if max_iou > iou_threshold:
                if difficult_cases[image_id][max_arg] == 0:
                    if (image_id, max_arg) not in matched:
                        true_positive[i] = 1
                        matched.add((image_id, max_arg))
                    else:
                        false_positive[i] = 1
            else:
                false_positive[i] = 1

    true_positive = true_positive.cumsum()
    false_positive = false_positive.cumsum()

    precision = true_positive / (true_positive + false_positive)
    recall = true_positive / num_true_cases

    if use_2007_metric:
        return measurements.compute_voc2007_average_precision(precision, recall)
    else:
        return measurements.compute_average_precision(precision, recall)

def collate_fn(batch):
    # batch is list of (image, boxes, labels)
    images = [x[0] for x in batch]
    return images

def compute_average_precision_per_class(dataset, num_true_cases, gt_boxes, difficult_cases,
                                        prediction_tensor, iou_threshold, use_2007_metric):
    if prediction_tensor.size(0) == 0:
        return 0.0

    image_indices = prediction_tensor[:, 0]
    scores = prediction_tensor[:, 2]
    boxes = prediction_tensor[:, 3:]

    # Sort by score descending
    sorted_indexes = torch.argsort(scores, descending=True)
    boxes = boxes[sorted_indexes]
    image_indices = image_indices[sorted_indexes]
    
    true_positive = np.zeros(len(image_indices))
    false_positive = np.zeros(len(image_indices))
    matched = set()
    
    for i, image_index in enumerate(image_indices):
        image_id = dataset.ids[int(image_index)]
        box = boxes[i]
        
        if image_id not in gt_boxes:
            false_positive[i] = 1
            continue

        gt_box = gt_boxes[image_id]
        ious = box_utils.iou_of(box, gt_box)
        max_iou = torch.max(ious).item()
        max_arg = torch.argmax(ious).item()
        
        if max_iou > iou_threshold:
            if difficult_cases[image_id][max_arg] == 0:
                if (image_id, max_arg) not in matched:
                    true_positive[i] = 1
                    matched.add((image_id, max_arg))
                else:
                    false_positive[i] = 1
        else:
            false_positive[i] = 1

    true_positive = true_positive.cumsum()
    false_positive = false_positive.cumsum()
    precision = true_positive / (true_positive + false_positive)
    recall = true_positive / num_true_cases
    if use_2007_metric:
        return measurements.compute_voc2007_average_precision(precision, recall)
    else:
        return measurements.compute_average_precision(precision, recall)

def ssd_voc_evaluate(
    predictor,
    dataset,
    class_names,
    iou_threshold=0.5,
    use_2007_metric=True,
):
    """
    Core SSD VOC evaluation loop.

    - predictor: SSD predictor object with .predict(image) -> (boxes, labels, probs)
    - dataset: VOCDataset (or compatible)
    - class_names: list of class names, index-aligned
    """

    true_case_stat, all_gb_boxes, all_difficult_cases = group_annotation_by_class(dataset)

    data_loader = DataLoader(dataset, batch_size=32, num_workers=4, shuffle=False, collate_fn=collate_fn)
    results = []
    for i, batch_images in enumerate(tqdm(data_loader, desc="Evaluating")):
        start = i * data_loader.batch_size
        
        batch_results = predictor.batch_predict(batch_images)
        
        for j, (boxes, labels, probs) in enumerate(batch_results):
            image_index = start + j
            boxes = boxes.cpu()
            labels = labels.cpu()
            probs = probs.cpu()
            
            indexes = torch.ones(labels.size(0), 1, dtype=torch.float32) * image_index
            results.append(torch.cat([
                indexes.reshape(-1, 1),
                labels.reshape(-1, 1).float(),
                probs.reshape(-1, 1),
                boxes + 1.0  # matlab's indexes start from 1
            ], dim=1))
    results = torch.cat(results)
    
    aps = []
    print("\n\nAverage Precision Per-class:")
    for class_index, class_name in enumerate(class_names):
        if class_index == 0:
            continue
            
        # Select predictions for this class
        sub = results[results[:, 1] == class_index, :]
        
        ap = compute_average_precision_per_class(
            dataset,
            true_case_stat.get(class_index, 0),
            all_gb_boxes.get(class_index, {}),
            all_difficult_cases.get(class_index, {}),
            sub,
            iou_threshold,
            use_2007_metric
        )
        aps.append(ap)
        print(f"{class_name}: {ap}")

    mAP = float(sum(aps) / len(aps)) if aps else 0.0
    print(f"\nAverage Precision Across All Classes: {mAP}")

    return {
        "per_class_ap": aps,
        "mAP": mAP,
    }