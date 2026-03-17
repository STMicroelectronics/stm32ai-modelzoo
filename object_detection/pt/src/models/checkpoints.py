# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import os
CHECKPOINT_STORAGE_URL = "https://raw.githubusercontent.com/STMicroelectronics/stm32ai-modelzoo/main/object_detection/torch_checkpoints/"
CURRENT_REPO_PATH = os.path.dirname(os.path.abspath(__file__))
SERVICES_ROOT = os.path.abspath(os.path.join(CURRENT_REPO_PATH, '../../../..'))
#CHECKPOINT_STORAGE_URL = os.path.join(os.path.dirname(SERVICES_ROOT), "stm32ai-modelzoo/object_detection/torch_checkpoints/")

model_checkpoints = {
    "st_resnettiny_actrelu_pt_datasetimagenet_res224" : "st_resnettiny_actrelu_pt_224.pth.tar", 
    "st_resnetmilli_actrelu_pt_datasetimagenet_res224" : "st_resnetmilli_actrelu_pt_224.pth.tar", 
    
    ## YOLOD v2 640px COCO # 
    "st_yolodv2tiny_actrelu_pt_datasetcoco_res640" : "st_yolodv2tiny_actrelu_pt_coco_640.pth", 
    "st_yolodv2milli_actrelu_pt_datasetcoco_res640" : "st_yolodv2milli_actrelu_pt_coco_640.pth",
    
    ## YOLOD v2 Tiny 320px 288px # 
    "st_yolodv2tiny_actrelu_pt_datasetcoco_res288" : "st_yolodv2tiny_actrelu_pt_coco_288.pth",
    ## YOLOD v2 320px COCO # 
    "st_yolodv2milli_actrelu_pt_datasetcoco_res320" : "st_yolodv2milli_actrelu_pt_coco_320.pth",
    
    ## YOLOD v2 192px COCO # 
    "st_yolodv2milli_actrelu_pt_datasetcoco_res192" : "st_yolodv2milli_actrelu_pt_coco_192.pth",
    "st_yolodv2tiny_actrelu_pt_datasetcoco_res192" : "st_yolodv2tiny_actrelu_pt_coco_192.pth",
        

    # YOLODv2Tiny coco_person 
    
    "st_yolodv2tiny_actrelu_pt_datasetcoco_person_res192" : "st_yolodv2tiny_actrelu_pt_coco_person_192.pth", 
    "st_yolodv2tiny_actrelu_pt_datasetcoco_person_res256" : "st_yolodv2tiny_actrelu_pt_coco_person_256.pth",
    "st_yolodv2tiny_actrelu_pt_datasetcoco_person_res288" : "st_yolodv2tiny_actrelu_pt_coco_person_288.pth",
    
    # YOLODv2Milli coco_person
    "st_yolodv2milli_actrelu_pt_datasetcoco_person_res192" : "st_yolodv2milli_actrelu_pt_coco_person_192.pth", 
    "st_yolodv2milli_actrelu_pt_datasetcoco_person_res256" : "st_yolodv2milli_actrelu_pt_coco_person_256.pth",
     "st_yolodv2milli_actrelu_pt_datasetcoco_person_res320" : "st_yolodv2milli_actrelu_pt_coco_person_320.pth", 
    
    
    # SSD 300px Pascal VOC 
    "ssd_mobilenetv1_pt_datasetvoc_res300" : "ssd_mobilenetv1_pt_voc_300.pth",
    "ssdlite_mobilenetv1_pt_datasetvoc_res300" : "ssdlite_mobilenetv1_pt_voc_300.pth", 
    "ssd_mobilenetv2_pt_datasetvoc_res300" : "ssd_mobilenetv2_pt_voc_300.pth",
    "ssdlite_mobilenetv2_pt_datasetvoc_res300" : "ssdlite_mobilenetv2_pt_voc_300.pth",
    "ssdlite_mobilenetv3small_pt_datasetvoc_res300" : "ssdlite_mobilenetv3small_pt_voc_300.pth",
    "ssdlite_mobilenetv3large_pt_datasetvoc_res300" : "ssdlite_mobilenetv3large_pt_voc_300.pth", 
    
    # SSD backbone pretrained Imagenet 224px  
    "mobilenetv1_base" :  "mobilenetv1_basenet.pth",
    "mobilenetv2_base" :  "mobilenetv2_basenet.pth",
    
    
    # SSD 300px coco person 
    "ssd_mobilenetv1_pt_datasetcoco_person_res300" : "ssd_mobilenetv1_pt_coco_person_300.pth",
    "ssd_mobilenetv2_pt_datasetcoco_person_res300" : "ssd_mobilenetv2_pt_coco_person_300.pth", 
    "ssdlite_mobilenetv1_pt_datasetcoco_person_res300" : "ssdlite_mobilenetv1_pt_coco_person_300.pth", 
    "ssdlite_mobilenetv2_pt_datasetcoco_person_res300" : "ssdlite_mobilenetv2_pt_coco_person_300.pth",
    "ssdlite_mobilenetv3small_pt_datasetcoco_person_res300" : "ssdlite_mobilenetv3small_pt_coco_person_300.pth",
    "ssdlite_mobilenetv3large_pt_datasetcoco_person_res300" : "ssdlite_mobilenetv3large_pt_coco_person_300.pth",

    # SSD 300px coco (80-classes) 
    "ssd_mobilenetv1_pt_datasetcoco_res300" : "ssd_mobilenetv1_pt_coco_300.pth",
    "ssd_mobilenetv2_pt_datasetcoco_res300" : "ssd_mobilenetv2_pt_coco_300.pth", 
    "ssdlite_mobilenetv1_pt_datasetcoco_res300" : "ssdlite_mobilenetv1_pt_coco_300.pth", 
    "ssdlite_mobilenetv2_pt_datasetcoco_res300" : "ssdlite_mobilenetv2_pt_coco_300.pth",
    "ssdlite_mobilenetv3small_pt_datasetcoco_res300" : "ssdlite_mobilenetv3small_pt_coco_300.pth",
    "ssdlite_mobilenetv3large_pt_datasetcoco_res300" : "ssdlite_mobilenetv3large_pt_coco_300.pth",
    
    
}