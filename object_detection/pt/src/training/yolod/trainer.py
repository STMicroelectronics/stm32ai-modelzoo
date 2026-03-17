# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import datetime
import os
import random
import sys
import time
from pathlib import Path
from copy import deepcopy
import torch
import torch.distributed as dist
import torch.nn as nn
from loguru import logger
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.tensorboard import SummaryWriter

from tqdm import tqdm

from common.model_utils.torch_utils import load_pretrained_weights
from common.registries.evaluator_registry import EVALUATOR_WRAPPER_REGISTRY
from object_detection.pt.src.data.yolod import (DataLoader, DataPrefetcher,
                                                InfiniteSampler,
                                                MosaicDetection,
                                                TrainTransform,
                                                YoloBatchSampler,
                                                worker_init_reset_seed)
from object_detection.pt.src.data.yolod.augmentations.data_augment import (
    TrainTransform, ValTransform)
from object_detection.pt.src.data.yolod.datasets import (COCODataset,
                                                         VOCDetection)
from object_detection.pt.src.evaluation.yolod.evaluators import (COCOEvaluator,
                                                                 VOCEvaluator)
from object_detection.pt.src.models.yolod.build_config import CfgNode
from object_detection.pt.src.utils.yolod import (LRScheduler, MeterBuffer,
                                                 ModelEMA, adjust_status,
                                                 all_reduce_norm,
                                                 get_local_rank,
                                                 get_model_info, get_rank,
                                                 get_world_size, gpu_mem_usage,
                                                 is_parallel, load_ckpt,
                                                 mem_usage, occupy_mem,
                                                 save_checkpoint, setup_logger,
                                                 synchronize,
                                                 wait_for_the_master)
from common.onnx_utils.onnx_model_convertor import torch_model_export_static
from object_detection.pt.src.utils.config.resolve import normalize_cfg, log_used_defaults, dict_to_ns

current_file = Path(__file__).resolve()
zoo_path = current_file.parents[5]
sys.path.append(str(zoo_path))


class YOLODTrainer:
    def __init__(self, dataloaders, model, cfg: CfgNode):
        # init function only defines some basic attr, other attrs like model, optimizer are built in
        # before_train methods.
        self.cfg_hydra = cfg
        cfg_local = deepcopy(cfg)
        cfg_local, used_defaults = normalize_cfg(cfg_local)
        log_used_defaults(used_defaults)
        cfg_local = dict_to_ns(cfg_local)

        self.cfg = cfg_local

        self.model = model
        self.dataloader = dataloaders
        # training related attr
        self.scaler = torch.cuda.amp.GradScaler(enabled=self.cfg.training.fp16)
        self.is_distributed = get_world_size() > 1
        self.rank = get_rank()
        self.local_rank = get_local_rank()
        self.device = "cuda:{}".format(self.local_rank)
        self.use_model_ema = self.cfg.training.ema
        self.progress_bar = None
        # data/dataloader related attr
        self.dataset = None # declaration
        self.data_type = torch.float16 if self.cfg.training.fp16 else torch.float32
        self.input_shape = self.cfg.model.input_shape[-2:]
        self.best_ap = 0
        self.ap50_95 = 0.0 
        self.ap50 = 0.0 
        self.pbar = None 

        # metric record
        self.meter = MeterBuffer(window_size=self.cfg.training.print_interval)
        # self.file_name = os.path.join(self.cfg.general.project_name, self.cfg.general.saved_models_dir)
        self.file_name = os.path.join(self.cfg.output_dir, self.cfg.general.saved_models_dir)
        if self.rank == 0:
            os.makedirs(self.file_name, exist_ok=True)

        setup_logger(
            self.file_name,
            distributed_rank=self.rank,
            filename="train_log.txt",
            mode="a",
        )

    def train(self):
        self.before_train()
        
        self.train_in_epoch()
        return self.after_train()
    
        # try:
        #     self.train_in_epoch()
        # except Exception as e:
        #     logger.error("Exception in training: ", e)
        #     raise
        # finally:
        #      return self.after_train()
        return self.after_train()
            

    def train_in_epoch(self):
        for self.epoch in range(self.start_epoch, self.cfg.training.epochs):
            # with tqdm(self.train_loader, desc=f"Epoch {self.epoch+1}/{self.cfg.train.epochs}", position=0, leave=True) as self.progress_bar: 
            self.before_epoch()
            self.train_in_iter()
            self.after_epoch()

    def train_in_iter(self):
        for self.iter in range(self.max_iter):   
        #for self.iter in range(4): 
            self.before_iter()
            self.train_one_iter()
            self.after_iter()

    def train_one_iter(self):
        
        iter_start_time = time.time()
        
        inps, targets = self.prefetcher.next()
        inps = inps.to(self.data_type)
        targets = targets.to(self.data_type)
        targets.requires_grad = False
        inps, targets = self.preprocess(inps, targets, self.input_shape)
        data_end_time = time.time()

        with torch.cuda.amp.autocast(enabled=self.cfg.training.fp16):
            outputs = self.model(inps, targets)

        loss = outputs["total_loss"]

        self.optimizer.zero_grad()
        self.scaler.scale(loss).backward()
        self.scaler.step(self.optimizer)
        self.scaler.update()

        if self.use_model_ema:
            self.ema_model.update(self.model)

        lr = self.lr_scheduler.update_lr(self.progress_in_iter + 1)
        for param_group in self.optimizer.param_groups:
            param_group["lr"] = lr
        
        iter_end_time = time.time()
        self.meter.update(
            iter_time=iter_end_time - iter_start_time,
            data_time=data_end_time - iter_start_time,
            lr=lr,
            **outputs,
        )

    def before_train(self):
        
        logger.info("Model :\n{}".format(self.cfg.model))
        logger.info("Data :\n{}".format(self.cfg.dataset))
        
        

        # model related init
        torch.cuda.set_device(self.local_rank)
        logger.info(
            "Model Summary: {}".format(get_model_info(self.cfg.model.input_shape[-1], self.model, self.input_shape))
        )
        self.model.to(self.device)      
        self.model.train()
        self.optimizer = self.get_optimizer(self.cfg.training.batch_size)

        # value of epoch will be set in `resume_train`
        self.model = self.resume_train(self.model)

        # data related init
        self.no_aug = self.start_epoch >= self.cfg.training.epochs - self.cfg.training.no_aug_epochs
        
        self.train_loader = self.dataloader["train"]
        
        logger.info("init prefetcher, this might take one minute or less...")
        self.prefetcher = DataPrefetcher(self.train_loader)
        # max_iter means iters per epoch
        self.max_iter = len(self.train_loader)

        self.lr_scheduler = self.get_lr_scheduler(
            self.optimizer_params['learning_rate'], self.max_iter
        )
        if self.is_distributed:
            self.model = DDP(self.model, device_ids=[self.local_rank], broadcast_buffers=False)

        if self.use_model_ema:
            self.ema_model = ModelEMA(self.model, 0.9998)
            self.ema_model.updates = self.max_iter * self.start_epoch

        self.evaluator = self.get_evaluator(
            batch_size=self.cfg.training.batch_size, is_distributed=self.is_distributed
        )
        # Tensorboard and Wandb loggers
        if self.rank == 0:
            if self.cfg.general.logger == "tensorboard":
                self.tblogger = SummaryWriter(os.path.join(self.file_name, "tensorboard"))
            else:
                raise ValueError("logger must be either 'tensorboard'")

        logger.info("Training start...")
        # logger.info("\n{}".format(self.model))

    def after_train(self):
        
        if self.use_model_ema:
            model = self.ema_model.ema
        else:
            model = self.model
        onnx_path = os.path.join(self.cfg_hydra.output_dir, self.cfg_hydra.general.saved_models_dir)
        onnx_model = torch_model_export_static(cfg=self.cfg_hydra,
                    model_dir=onnx_path,
                    model=model.to("cpu"))
        logger.info(
            "Training of experiment is done and the best AP is {:.2f}".format(self.best_ap * 100)
        )
        
        return onnx_model
        


    def before_epoch(self):
        logger.info("---> start train epoch{}".format(self.epoch + 1))

        if self.epoch + 1 == self.cfg.training.epochs - self.cfg.training.no_aug_epochs or self.no_aug:
            logger.info("--->No mosaic aug now!")
            self.train_loader.close_mosaic()
            logger.info("--->Add additional L1 loss now!")
            if self.is_distributed:
                self.model.module.head.use_l1 = True
            else:
                self.model.head.use_l1 = True
            if not self.no_aug:
                self.save_ckpt(ckpt_name="last_mosaic_epoch")

    def after_epoch(self):
        self.save_ckpt(ckpt_name="latest")

        if (self.epoch + 1) % self.cfg.training.eval_interval == 0:
            all_reduce_norm(self.model)
            self.evaluate_and_save_model()
        logger.info (f'validation : mAP(50:95) : {self.ap50_95}, AP50 : {self.ap50}, Best mAP : {self.best_ap}')
    
    def before_iter(self):
        pass

    def after_iter(self):
        """
        `after_iter` contains two parts of logic:
            * log information
            * reset setting of resize
        """
        
        # log needed information
        if (self.iter + 1) % self.cfg.training.print_interval == 0:
            # TODO check ETA logic
            left_iters = self.max_iter * self.cfg.training.epochs - (self.progress_in_iter + 1)
            eta_seconds = self.meter["iter_time"].global_avg * left_iters
            eta_str = "ETA: {}".format(datetime.timedelta(seconds=int(eta_seconds)))

            progress_str = "epoch: {}/{}, iter: {}/{}".format(
                self.epoch + 1, self.cfg.training.epochs, self.iter + 1, self.max_iter
            )
            loss_meter = self.meter.get_filtered_meter("loss")
            
            loss_str = ", ".join(
                ["{}: {:.1f}".format(k, v.latest) for k, v in loss_meter.items()]
            )

            time_meter = self.meter.get_filtered_meter("time")
            time_str = ", ".join(
                ["{}: {:.3f}s".format(k, v.avg) for k, v in time_meter.items()]
            )

            mem_str = "gpu mem: {:.0f}Mb, mem: {:.1f}Gb".format(gpu_mem_usage(), mem_usage())

            # self.progress_bar.set_postfix(loss=f'{loss_meter["total_loss"].latest:.4f}', lr=f'{self.meter["lr"].latest:.2f}')
            # self.progress_bar.update(1)
            
            logger.info(

                "{}, {}, lr: {:.3e}".format(
                    progress_str,
                    loss_str,
                    self.meter["lr"].latest,
                )
                # + (", size: {:d}, {}".format(self.input_shape[0], eta_str))
            )

            if self.rank == 0:
                if self.cfg.general.logger == "tensorboard":
                    self.tblogger.add_scalar(
                        "train/lr", self.meter["lr"].latest, self.progress_in_iter)
                    for k, v in loss_meter.items():
                        self.tblogger.add_scalar(
                            f"train/{k}", v.latest, self.progress_in_iter)

            self.meter.clear_meters()

        # random resizing
        if (self.progress_in_iter + 1) % 10 == 0:
            self.input_shape = self.random_resize(
                self.train_loader, self.epoch, self.rank, self.is_distributed
            )

    @property
    def progress_in_iter(self):
        return self.epoch * self.max_iter + self.iter

    def resume_train(self, model):
        if self.cfg.training.resume_training_from is not '':
            logger.info("resume training")
            # if self.cfg.ckpt is None:
            #     ckpt_file = os.path.join(self.file_name, "latest" + "_ckpt.pth")
            # else:
            ckpt_file = self.cfg.training.resume_training_from

            ckpt = torch.load(ckpt_file, map_location=self.device, weights_only=False)
            # resume the model/optimizer state dict
            ckpt = torch.load(ckpt_file, weights_only=False)  # or your device
            state = ckpt.get("state_dict", ckpt.get("model", ckpt))      # pick the right dict
            # strip DDP prefix
            state = {k.replace("module.", "", 1): v for k, v in state.items()}
            model.load_state_dict(state, strict=True)  # set strict=False if heads differ
            # model = load_pretrained_weights(model, ckpt_file)
            # model.load_state_dict(ckpt["model"])
            self.optimizer.load_state_dict(ckpt["optimizer"])
            self.best_ap = ckpt.pop("best_ap", 0)
            # resume the training states variables
            start_epoch = (
                self.cfg.training.start_epoch - 1
                if self.cfg.training.start_epoch is not None
                else ckpt["start_epoch"]
            )
            self.start_epoch = start_epoch
            logger.info(
                "loaded checkpoint '{}' (epoch {})".format(
                    self.cfg.training.resume_training_from, self.start_epoch
                )
            )  # noqa
        else:
            self.start_epoch = 0

        return model

    def evaluate_and_save_model(self):
        if self.use_model_ema:
            evalmodel = self.ema_model.ema
        else:
            evalmodel = self.model
            if is_parallel(evalmodel):
                evalmodel = evalmodel.module

        with adjust_status(evalmodel, training=False):
            (ap50_95, ap50, summary), predictions = self.eval_step(
                evalmodel, self.evaluator, self.is_distributed, return_outputs=True
            )

        self.ap50_95 = ap50_95
        self.ap50 = ap50 
        update_best_ckpt = ap50_95 > self.best_ap
        self.best_ap = max(self.best_ap, ap50_95)

        if self.rank == 0:
            if self.cfg.general.logger == "tensorboard":
                self.tblogger.add_scalar("val/AP50", ap50, self.epoch + 1)
                self.tblogger.add_scalar("val/AP50_95", ap50_95, self.epoch + 1)
            logger.info("\n" + summary)
        synchronize()

        self.save_ckpt("last_epoch", update_best_ckpt, ap=ap50_95)
        if self.cfg.training.save_history_ckpt:
            self.save_ckpt(f"epoch_{self.epoch + 1}", ap=ap50_95)

    def save_ckpt(self, ckpt_name, update_best_ckpt=False, ap=None):
        if self.rank == 0:
            save_model = self.ema_model.ema if self.use_model_ema else self.model
            # logger.info("Save weights to {}".format(self.file_name))
            ckpt_state = {
                "start_epoch": self.epoch + 1,
                "model": save_model.state_dict(),
                "optimizer": self.optimizer.state_dict(),
                "best_ap": self.best_ap,
                "curr_ap": ap,
            }
            save_checkpoint(
                ckpt_state,
                update_best_ckpt,
                self.file_name,
                ckpt_name,
            )

    def random_resize(self, data_loader, epoch, rank, is_distributed):
        tensor = torch.LongTensor(2).cuda()

        if rank == 0:
            size_factor = self.input_shape[1] * 1.0 / self.input_shape[0]
            if not hasattr(self.cfg.dataset, 'random_size'):
                min_size = int(self.input_shape[0] / 32) - self.cfg.dataset.multiscale_range
                max_size = int(self.input_shape[0] / 32) + self.cfg.dataset.multiscale_range
                self.cfg.defrost()
                self.cfg.dataset.random_size = (min_size, max_size)
                self.cfg.freeze()
            size = random.randint(*self.cfg.dataset.random_size)
            size = (int(32 * size), 32 * int(size * size_factor))
            tensor[0] = size[0]
            tensor[1] = size[1]

        if is_distributed:
            dist.barrier()
            dist.broadcast(tensor, 0)

        input_shape = (tensor[0].item(), tensor[1].item())
        return input_shape

    def preprocess(self, inputs, targets, tsize):
        scale_y = tsize[0] / self.input_shape[0]
        scale_x = tsize[1] / self.input_shape[1]
        if scale_x != 1 or scale_y != 1:
            inputs = nn.functional.interpolate(
                inputs, size=tsize, mode="bilinear", align_corners=False
            )
            targets[..., 1::2] = targets[..., 1::2] * scale_x
            targets[..., 2::2] = targets[..., 2::2] * scale_y
        return inputs, targets


    def get_optimizer(self, batch_size):
        if "optimizer" not in self.__dict__:
            optimizer_cfg = self.cfg.training.optimizer

            if hasattr(optimizer_cfg, 'Adam') and optimizer_cfg.Adam is not None:
                optimizer_type = "adam"
                opt_params = optimizer_cfg.Adam
            elif hasattr(optimizer_cfg, 'AdamW') and optimizer_cfg.AdamW is not None:
                optimizer_type = "adamw"
                opt_params = optimizer_cfg.AdamW
            elif hasattr(optimizer_cfg, 'SGD') and optimizer_cfg.SGD is not None:
                optimizer_type = "sgd"
                opt_params = optimizer_cfg.SGD
            else:
                optimizer_type = "sgd"
                opt_params = None

            if opt_params is not None:
                base_lr = getattr(opt_params, 'learning_rate', 0.01)
                warmup_lr = getattr(opt_params, 'warmup_lr', 0.0)
                weight_decay = getattr(opt_params, 'weight_decay', 5e-4)
            else:
                base_lr = getattr(self.cfg.training, 'lr', 0.01)
                warmup_lr = getattr(self.cfg.training, 'warmup_lr', 0.0)
                weight_decay = getattr(self.cfg.training, 'weight_decay', 5e-4)

            self.optimizer_params = {
                'learning_rate': base_lr,
                'warmup_lr': warmup_lr,
                'weight_decay': weight_decay,
                'min_lr_ratio': getattr(opt_params, 'min_lr_ratio', 0.05) if opt_params else getattr(self.cfg.training, 'min_lr_ratio', 0.05)
            }

            if self.cfg.training.warmup_epochs > 0:
                lr = warmup_lr
            else:
                lr = base_lr

            logger.info(f"Using optimizer: {optimizer_type.upper()}, lr: {lr}")

            if "yolod" in self.cfg.model.model_name:

                pg0, pg1, pg2 = [], [], []  # optimizer parameter groups

                for k, v in self.model.named_modules():
                    if hasattr(v, "bias") and isinstance(v.bias, nn.Parameter):
                        pg2.append(v.bias)  # biases
                    if isinstance(v, nn.BatchNorm2d) or "bn" in k:
                        pg0.append(v.weight)  # no decay
                    elif hasattr(v, "weight") and isinstance(v.weight, nn.Parameter):
                        pg1.append(v.weight)  # apply decay

                if optimizer_type == "adam":
                    optimizer = torch.optim.Adam(pg0, lr=lr)
                elif optimizer_type == "adamw":
                    optimizer = torch.optim.AdamW(pg0, lr=lr)
                else:  # default to sgd
                    optimizer = torch.optim.SGD(
                        pg0, lr=lr, momentum=self.cfg.training.momentum, nesterov=True
                    )
                optimizer.add_param_group(
                    {"params": pg1, "weight_decay": weight_decay}
                )  # add pg1 with weight_decay
                optimizer.add_param_group({"params": pg2})
                self.optimizer = optimizer

            else:
                if optimizer_type == "adam":
                    self.optimizer = torch.optim.Adam([
                        # Backbone
                        {"params": [p for n, p in self.model.backbone.named_parameters() if p.requires_grad and "bias" not in n and "bn" not in n], "lr": lr*0.2, "weight_decay": weight_decay},
                        {"params": [p for n, p in self.model.backbone.named_parameters() if p.requires_grad and ("bn" in n or "bias" in n)], "lr": lr*0.2, "weight_decay": 0.0},
                        # Neck
                        {"params": [p for n, p in self.model.neck.named_parameters() if p.requires_grad and "bias" not in n and "bn" not in n], "lr": lr*0.8, "weight_decay": weight_decay},
                        {"params": [p for n, p in self.model.neck.named_parameters() if p.requires_grad and ("bn" in n or "bias" in n)], "lr": lr*0.8, "weight_decay": 0.0},
                        # Head
                        {"params": [p for n, p in self.model.head.named_parameters() if p.requires_grad and "bias" not in n and "bn" not in n], "lr": lr, "weight_decay": weight_decay},
                        {"params": [p for n, p in self.model.head.named_parameters() if p.requires_grad and ("bn" in n or "bias" in n)], "lr": lr, "weight_decay": 0.0},
                    ])
                elif optimizer_type == "adamw":
                    self.optimizer = torch.optim.AdamW([
                        # Backbone
                        {"params": [p for n, p in self.model.backbone.named_parameters() if p.requires_grad and "bias" not in n and "bn" not in n], "lr": lr*0.2, "weight_decay": weight_decay},
                        {"params": [p for n, p in self.model.backbone.named_parameters() if p.requires_grad and ("bn" in n or "bias" in n)], "lr": lr*0.2, "weight_decay": 0.0},
                        # Neck
                        {"params": [p for n, p in self.model.neck.named_parameters() if p.requires_grad and "bias" not in n and "bn" not in n], "lr": lr*0.8, "weight_decay": weight_decay},
                        {"params": [p for n, p in self.model.neck.named_parameters() if p.requires_grad and ("bn" in n or "bias" in n)], "lr": lr*0.8, "weight_decay": 0.0},
                        # Head
                        {"params": [p for n, p in self.model.head.named_parameters() if p.requires_grad and "bias" not in n and "bn" not in n], "lr": lr, "weight_decay": weight_decay},
                        {"params": [p for n, p in self.model.head.named_parameters() if p.requires_grad and ("bn" in n or "bias" in n)], "lr": lr, "weight_decay": 0.0},
                    ])
                else:  # default to sgd
                    self.optimizer = torch.optim.SGD([
                        # Backbone
                        {"params": [p for n, p in self.model.backbone.named_parameters() if p.requires_grad and "bias" not in n and "bn" not in n], "lr": lr*0.2, "weight_decay": weight_decay, "momentum": 0.9, "nesterov": True, "dampening": 0},
                        {"params": [p for n, p in self.model.backbone.named_parameters() if p.requires_grad and ("bn" in n or "bias" in n)], "lr": lr*0.2, "weight_decay": 0.0, "momentum": 0.9, "nesterov": True, "dampening": 0},
                        # Neck
                        {"params": [p for n, p in self.model.neck.named_parameters() if p.requires_grad and "bias" not in n and "bn" not in n], "lr": lr*0.8, "weight_decay": weight_decay, "momentum": 0.9, "nesterov": True, "dampening": 0},
                        {"params": [p for n, p in self.model.neck.named_parameters() if p.requires_grad and ("bn" in n or "bias" in n)], "lr": lr*0.8, "weight_decay": 0.0, "momentum": 0.9, "nesterov": True, "dampening": 0},
                        # Head
                        {"params": [p for n, p in self.model.head.named_parameters() if p.requires_grad and "bias" not in n and "bn" not in n], "lr": lr, "weight_decay": weight_decay, "momentum": 0.9, "nesterov": True, "dampening": 0},
                        {"params": [p for n, p in self.model.head.named_parameters() if p.requires_grad and ("bn" in n or "bias" in n)], "lr": lr, "weight_decay": 0.0, "momentum": 0.9, "nesterov": True, "dampening": 0},
                    ])

        return self.optimizer
        

    def get_lr_scheduler(self, lr, iters_per_epoch):

        scheduler = LRScheduler(
            self.cfg.training.scheduler,
            lr,
            iters_per_epoch,
            self.cfg.training.epochs,
            warmup_epochs=self.cfg.training.warmup_epochs,
            warmup_lr_start=self.optimizer_params['warmup_lr'],
            no_aug_epochs=self.cfg.training.no_aug_epochs,
            min_lr_ratio=self.optimizer_params['min_lr_ratio'],
        )
        return scheduler

    def get_evaluator(self, batch_size, is_distributed, testdev=False, legacy=False):
        
        if self.cfg.dataset.dataset_name== "coco": 
            num_classes = getattr(self.cfg.model, "num_classes", 80)
            return COCOEvaluator(
                dataloader = self.dataloader["valid"], 
                img_size=self.input_shape,
                confthre=self.cfg.postprocessing.confidence_thresh,
                nmsthre=self.cfg.postprocessing.NMS_thresh,
                num_classes=num_classes,
                testdev=testdev,
            )

        elif self.cfg.dataset.dataset_name == "voc": 
            num_classes = getattr(self.cfg.model, "num_classes", 20)   
            return VOCEvaluator(
                # dataloader=self.get_eval_loader(batch_size, is_distributed),
                dataloader=self.dataloader["valid"],
                img_size=self.cfg.test.test_size,
                confthre=self.cfg.test.test_conf,
                nmsthre=self.cfg.test.nmsthre,
                num_classes=num_classes,
            )
        else : 
            print ("only voc and coco datasets are supported")

    def eval_step(self, model, evaluator, is_distributed, half=False, return_outputs=False):
        return evaluator.evaluate(model, is_distributed, half, return_outputs=return_outputs)

    def _parse_per_class_ap_from_summary(self, summary: str):
        """
        Parse the 'per class AP' Markdown table from the evaluator's summary string.
        Returns Ordered dict {class_name: ap_float} in the order they appear.
        """
        if not isinstance(summary, str):
            return {}

        start = summary.find("per class AP")
        if start == -1:
            return {}
        end = summary.find("per class AR", start)
        block = summary[start:end] if end != -1 else summary[start:]

        per_class = {}
        for line in block.splitlines():
            line = line.strip()
            # skip header/separator rows
            if not line.startswith("|") or line.startswith("|:"):
                continue
            # split markdown row: | class | AP | class | AP | ...
            cells = [c.strip() for c in line.split("|") if c.strip()]
            # consume pairs
            for i in range(0, len(cells) - 1, 2):
                cls_name = cells[i]
                try:
                    ap_val = float(cells[i + 1])
                except ValueError:
                    continue
                # summary prints per-class AP as percent (e.g., 47.947); convert to 0-1
                ap_val = ap_val / 100.0 if ap_val > 1.0 else ap_val
                per_class[cls_name] = ap_val
        return per_class

    def _extract_overall_map(self, eval_result):
        """
        Many YOLO/SSD evaluators return ((ap50_95, ap50, summary), preds)
        or (ap50_95, ap50, summary). Grab overall mAP@0.50:0.95 and summary.
        """
        ap5095, summary = None, None
        if isinstance(eval_result, tuple):
            head = eval_result[0]
            if isinstance(head, tuple):
                # ((ap50_95, ap50, summary), preds)
                if len(head) >= 3 and isinstance(head[0], (float, int)) and isinstance(head[2], str):
                    ap5095 = float(head[0])
                    summary = head[2]
            else:
                # (ap50_95, ap50, summary)
                if len(eval_result) >= 3 and isinstance(eval_result[0], (float, int)) and isinstance(eval_result[2], str):
                    ap5095 = float(eval_result[0])
                    summary = eval_result[2]
        return ap5095, summary

    def eval(self, **kwargs):
        evaluator_cls = EVALUATOR_WRAPPER_REGISTRY.get(
            evaluator_name="yolod",
            framework=self.cfg.model.framework,
            use_case=self.cfg.use_case,
        )

        evaluator = evaluator_cls(
            dataloaders=self.dataloaders,
            model=self.model,
            cfg=self.cfg,
            trainer_ref=self,
        )

        return evaluator.evaluate(**kwargs)