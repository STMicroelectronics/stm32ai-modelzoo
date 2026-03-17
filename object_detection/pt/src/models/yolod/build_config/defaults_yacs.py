# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
from ..build_config.yacs import CfgNode as CN

def get_cfg_defaults():
    _C = CN()
    _C.output_dir = "./runs"
    _C.operation_mode = ""
    # ---------------- General Configuration ---------------- #
    _C.general = CN()
    _C.general.project_name = "./runs"
    _C.general.saved_models_dir = "default_experiment"
    _C.general.dist_backend = "nccl"
    _C.general.dist_url = None
    _C.general.devices = 1
    _C.resume = False
    _C.general.num_machines = 1
    _C.general.machine_rank = 0
    _C.general.fp16 = True
    # _C.general.cache = None
    _C.general.occupy = False
    _C.general.logger = "tensorboard"
    _C.general.global_seed = 42

    # ---------------- Model Configuration ---------------- #
    _C.model = CN()
    _C.model.model_type = "yolod"
    _C.model.model_name = "yolod-tiny"
    _C.model.framework = "torch"
    _C.model.pretrained = True
    _C.model.pretrained_dataset = 'coco'
    _C.model.input_shape = [3, 640, 640]
    _C.model.model_path = ''
    _C.model.depthwise = True
    _C.model.standard = True
    _C.model.num_classes = 80
    _C.model.depth = 0.33
    _C.model.width = 0.25
    _C.model.act = "silu"
    _C.model.in_channels = (256, 512, 1024)
    _C.model.out_features = ("dark3", "dark4", "dark5")
  

    # ---------------- Dataset Configuration ---------------- #
    _C.dataset = CN()
    _C.dataset.format = "coco"
    _C.dataset.training_path = ""
    _C.dataset.dataset_name = "coco"
    _C.dataset.class_names = ""
    _C.dataset.seed = 0
    _C.dataset.multiscale_range = 5
    _C.dataset.random_size = (10, 20)
    _C.dataset.data_dir = "/neutrino/datasets/coco"
    _C.dataset.train_annotations_path = "instances_train2017.json"
    _C.dataset.val_annotations_path = "instances_val2017.json"
    _C.dataset.test_annotations_path = "instances_test2017.json"
    _C.dataset.train_images_path = "train2017"
    _C.dataset.val_images_path = "val2017"
    _C.dataset.test_images_path = "val2017"
    _C.dataset.quantization_split = 0.01 
    _C.dataset.quantization_path = ""
    _C.dataset.prediction_path = ""
    _C.dataset.mosaic_prob = 1.0
    _C.dataset.mixup_prob = 1.0
    _C.dataset.hsv_prob = 1.0
    _C.dataset.flip_prob = 0.5
    _C.dataset.degrees = 10.0
    _C.dataset.translate = 0.1
    _C.dataset.mosaic_scale = (0.5, 1.5)
    _C.dataset.enable_mixup = False
    _C.dataset.mixup_scale = (0.5, 1.5)
    _C.dataset.shear = 2.0

    # ---------------- Training Configuration ---------------- #
    _C.training = CN()
    _C.general.start_epoch = 0
    _C.general.resume_training_from = ''
    _C.dataset.num_workers = 4
    _C.training.batch_size = 16
    _C.training.warmup_epochs = 1
    _C.training.epochs = 100
    _C.training.warmup_lr = 0.0
    _C.training.min_lr_ratio = 0.05
    _C.training.basic_lr_per_img = 0.00015625
    _C.training.scheduler = "yoloxwarmcos"
    _C.training.no_aug_epochs = 15
    _C.training.ema = True
    _C.training.weight_decay = 5e-4
    _C.training.momentum = 0.9
    _C.training.print_interval = 1
    _C.training.eval_interval = 1
    _C.training.save_history_ckpt = True
    _C.training.optimizer = CN()
    _C.training.optimizer.Adam = CN() 
    _C.training.optimizer.Adam.learning_rate = 0.1 
      
    # ---------------- Pre processing Configuration ---------------- #
    
    _C.preprocessing = CN()
    _C.preprocessing.rescaling = CN()

    _C.preprocessing.rescaling.scale = 1
    _C.preprocessing.rescaling.offset = 1

    
    _C.preprocessing.resizing = CN()
    _C.preprocessing.resizing.aspect_ratio = "fit"
    _C.preprocessing.resizing.interpolation = "nearest"
    _C.preprocessing.color_mode = "rgb"


    
    # ---------------- Post processing Configuration ---------------- #
    
    _C.postprocessing = CN()
    _C.postprocessing.confidence_thresh = 0.01 
    _C.postprocessing.NMS_thresh = 0.65
    _C.postprocessing.IoU_eval_th = 0.65

    # ---------------- Testing Configuration ---------------- #
    _C.test = CN()
    _C.test.test_size = (640, 640)
    _C.test.test_conf = 0.01
    _C.test.nmsthre = 0.65


    # ---------------- MLFlow Configuration ---------------- #
    _C.mlflow = CN()
    _C.mlflow.uri = "mlruns"

    # ---------------- Hydra Configuration ---------------- #

    _C.hydra = CN()
    _C.hydra.run = CN()
    _C.hydra.run.dir = ""
        
    return _C