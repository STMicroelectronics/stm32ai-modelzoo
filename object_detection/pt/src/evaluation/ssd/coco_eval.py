import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
from pycocotools.cocoeval import COCOeval

def collate_fn(batch):
    # batch is list of (image, boxes, labels)
    images = [x[0] for x in batch]
    return images

def ssd_coco_evaluate(
    predictor,
    dataset,
    class_names,
    iou_threshold=0.5,
):
    """
    Core SSD COCO evaluation loop.

    - predictor: SSD predictor object with .batch_predict(images) -> list of (boxes, labels, probs)
    - dataset: CocoDataset (or compatible)
    - class_names: list of class names (not directly used by COCOeval but kept for consistency)
    - iou_threshold: used potentially for custom logic, but standard COCOeval calculates over range 0.5:0.95
    """
    
    # DataLoader
    data_loader = DataLoader(
        dataset, 
        batch_size=32, 
        num_workers=4, 
        shuffle=False, 
        collate_fn=collate_fn
    )
    
    results = []
    print("Starting batched evaluation...")
    
    global_idx = 0
    
    for batch_images in tqdm(data_loader, desc="Evaluating"):
        batch_size = len(batch_images)
        # Predictor must support batch_predict
        batch_results = predictor.batch_predict(batch_images)
        
        for j, (boxes, labels, probs) in enumerate(batch_results):
            dataset_index = global_idx + j
            image_id = dataset.ids[dataset_index]
            
            boxes = boxes.cpu().numpy()
            labels = labels.cpu().numpy()
            probs = probs.cpu().numpy()
            
            for k in range(len(boxes)):
                label = labels[k]
                score = float(probs[k])
                box = boxes[k]
                
                # Filter low score detections for speed
                if score < 0.05:
                    continue
                
                # Label 0 is background in SSD, but COCO categories might differ.
                # Assuming dataset.continuous_id_to_coco_id map exists.
                if label == 0: 
                    continue
                    
                category_id = dataset.continuous_id_to_coco_id[label]
                
                x1, y1, x2, y2 = box
                w = x2 - x1
                h = y2 - y1
                
                results.append({
                    "image_id": image_id,
                    "category_id": category_id,
                    "bbox": [float(x1), float(y1), float(w), float(h)],
                    "score": score
                })
        
        global_idx += batch_size

    if len(results) == 0:
        print("No detections found!")
        # Return empty metrics
        return {"mAP": 0.0}

    # COCO Evaluation
    print("Accumulating results for COCO...")
    coco_dt = dataset.coco.loadRes(results)
    
    # Standard COCO evaluation on bbox
    coco_eval = COCOeval(dataset.coco, coco_dt, 'bbox')
    
    # iouThrs default is 0.5:0.05:0.95
    # coco_eval.params.iouThrs = [iou_threshold] 

    coco_eval.evaluate()
    coco_eval.accumulate()
    coco_eval.summarize()
    
    # Extract mAP (IoU=0.50:0.95) which is stats[0]
    mAP = coco_eval.stats[0]
    
    return {
        "mAP": mAP,
        "coco_eval_object": coco_eval  # Return full object if needed
    }
