# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import torch
import torchvision
from object_detection.pt.src.utils.ssd import box_utils
from object_detection.pt.src.data.ssd.data_preprocessing import PredictionTransform
from object_detection.pt.src.utils.ssd.misc import Timer


class Predictor:
    def __init__(self, net, size, mean=0.0, std=1.0, nms_method=None,
                 iou_threshold=0.45, filter_threshold=0.01, candidate_size=200, sigma=0.5, device=None):
        self.net = net
        self.transform = PredictionTransform(size, mean, std)
        self.iou_threshold = iou_threshold
        self.filter_threshold = filter_threshold
        self.candidate_size = candidate_size
        self.nms_method = nms_method

        self.sigma = sigma
        if device:
            self.device = device
        else:
            self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        self.net.to(self.device)
        self.net.eval()

        self.timer = Timer()

    def predict(self, image, top_k=-1, prob_threshold=None):
        # cpu_device = torch.device("cpu")
        height, width, _ = image.shape
        image = self.transform(image)
        images = image.unsqueeze(0)
        images = images.to(self.device)
        with torch.no_grad():
            self.timer.start()
            scores, boxes = self.net.forward(images)
            # print("Inference time: ", self.timer.end())
        boxes = boxes[0]
        scores = scores[0]
        if not prob_threshold:
            prob_threshold = self.filter_threshold
        # changed to GPU nms.
        # boxes = boxes.to(cpu_device)
        # scores = scores.to(cpu_device)
        picked_box_probs = []
        picked_labels = []
        for class_index in range(1, scores.size(1)):
            probs = scores[:, class_index]
            mask = probs > prob_threshold
            probs = probs[mask]
            if probs.size(0) == 0:
                continue
            subset_boxes = boxes[mask, :]
            box_probs = torch.cat([subset_boxes, probs.reshape(-1, 1)], dim=1)
            box_probs = box_utils.nms(box_probs, self.nms_method,
                                      score_threshold=prob_threshold,
                                      iou_threshold=self.iou_threshold,
                                      sigma=self.sigma,
                                      top_k=top_k,
                                      candidate_size=self.candidate_size)
            picked_box_probs.append(box_probs)
            picked_labels.extend([class_index] * box_probs.size(0))
        if not picked_box_probs:
            return torch.tensor([]), torch.tensor([]), torch.tensor([])
        picked_box_probs = torch.cat(picked_box_probs)
        picked_box_probs[:, 0] *= width
        picked_box_probs[:, 1] *= height
        picked_box_probs[:, 2] *= width
        picked_box_probs[:, 3] *= height
        return picked_box_probs[:, :4], torch.tensor(picked_labels), picked_box_probs[:, 4]
    
    def batch_predict(self, images, top_k=-1, prob_threshold=None):
        if not prob_threshold:
            prob_threshold = self.filter_threshold

        # Process batch
        processed_images = []
        original_dims = []
        for image in images:
            height, width, _ = image.shape
            original_dims.append((height, width))
            processed_images.append(self.transform(image))
        
        images = torch.stack(processed_images)
        images = images.to(self.device)
        
        with torch.no_grad():
            self.timer.start()
            scores, boxes = self.net.forward(images)
            
        batch_results = []
        
        for i in range(len(images)):
            img_scores = scores[i]
            img_boxes = boxes[i]
            height, width = original_dims[i]
            
            # Filter candidates > prob_threshold
            scores_nobg = img_scores[:, 1:]
            
            if scores_nobg.is_cuda:
                candidate_mask = scores_nobg > prob_threshold
                candidates = candidate_mask.nonzero()
            else:
                # CPU fallback
                candidate_mask = scores_nobg > prob_threshold
                candidates = candidate_mask.nonzero()

            if candidates.size(0) == 0:
                 batch_results.append((torch.tensor([], device=self.device), torch.tensor([], device=self.device), torch.tensor([], device=self.device)))
                 continue

            anchor_idxs = candidates[:, 0]
            class_idxs = candidates[:, 1] + 1 # Convert back to 1-based indexing
            
            candidate_scores = scores_nobg[candidates[:, 0], candidates[:, 1]]
            candidate_boxes = img_boxes[anchor_idxs]
            
            # Batched NMS
            # torchvision.ops.batched_nms handles multiclass NMS efficiently
            keep = torchvision.ops.batched_nms(candidate_boxes, candidate_scores, class_idxs, self.iou_threshold)
            
            if top_k > 0:
                keep = keep[:top_k]
            
            final_boxes = candidate_boxes[keep]
            final_scores = candidate_scores[keep]
            final_labels = class_idxs[keep]
            
            # Scale boxes
            final_boxes[:, 0] *= width
            final_boxes[:, 1] *= height
            final_boxes[:, 2] *= width
            final_boxes[:, 3] *= height
            
            batch_results.append((final_boxes, final_labels, final_scores))
            
        return batch_results