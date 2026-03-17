# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import os
import sys
import itertools
import logging
import numpy as np
import torch
from torch.utils.data import DataLoader, ConcatDataset
from torch.optim.lr_scheduler import MultiStepLR, CosineAnnealingLR
from object_detection.pt.src.utils.ssd.misc import Timer
from object_detection.pt.src.models.ssd.detectors.ssd import MatchPrior
from object_detection.pt.src.models.ssd.losses.multibox_loss import MultiboxLoss
from object_detection.pt.src.models.ssd.detectors.config.mobilenetv1_ssd_config import MOBILENET_CONFIG
from common.onnx_utils.onnx_model_convertor import torch_model_export_static
from object_detection.pt.wrappers.evaluation.ssd import SSDEvaluatorWrapper
from common.onnx_utils.ssd_onnx_export import SSDExportWrapper
from torch.cuda.amp import GradScaler, autocast
from object_detection.pt.src.data.ssd.data_preprocessing import TrainAugmentation, TestTransform
from torch.utils.tensorboard import SummaryWriter
from pathlib import Path
import copy 
current_file = Path(__file__).resolve()
zoo_path = current_file.parents[5]
sys.path.append(str(zoo_path))
from pathlib import Path

class SSDTrainer:
    # Default values for config parameters
    DEFAULTS = {
        # Optimizer
        'optimizer': 'SGD',
        'SGD.learning_rate': 0.01,
        'SGD.momentum': 0.9,
        'SGD.weight_decay': 0.0005,
        'Adam.learning_rate': 0.001,
        'Adam.weight_decay': 0.0005,
        'Adam.betas': [0.9, 0.999],
        # Training
        'training.base_net_lr': None,
        'training.extra_layers_lr': None,
        'training.scheduler': 'cosine',
        'training.t_max': 200,
        'training.milestones': '80,100',
        'training.gamma': 0.1,
        'training.validation_epochs': 5,
        'training.print_interval': 50,
        # Model
        'model.input_shape': [3, 300, 300],
        'model.num_classes': 20,
        'model.width_mult': 1.0,
        'model.pretrained': False,
        # Dataset
        'dataset.num_workers': 4,
        'dataset.class_names': ['aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car', 'cat', 'chair',
                                'cow', 'diningtable', 'dog', 'horse', 'motorbike', 'person', 'pottedplant',
                                'sheep', 'sofa', 'train', 'tvmonitor'],
    }

    def _get_default(self, value, key):
        """Return value if not None, else return default from DEFAULTS and log it."""
        if value is None:
            default = self.DEFAULTS.get(key)
            if default is not None:
                logging.info(f"'{key}' not set in config, using default: {default}")
            return default
        return value

    def __init__(self, dataloaders, model, cfg):
        self.cfg = cfg
        self.model = model
        self.dataloader = dataloaders
        self.batch_size = cfg.training.batch_size
        self.timer = Timer()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if torch.cuda.is_available():
            torch.backends.cudnn.benchmark = True
            logging.info("Use CUDA.")

        model_name = getattr(cfg.model, "model_name", None)
        if model_name is None:
            raise ValueError("Model name must be provided cfg.model.model_name")
        self.model_name = model_name
        self.config=MOBILENET_CONFIG()
        
        self.scaler = GradScaler() if torch.cuda.is_available() else None
        self.evaluator = None
        
        # TensorBoard setup
        tensorboard_dir = os.path.join(cfg.output_dir, 'tensorboard')
        self.writer = SummaryWriter(log_dir=tensorboard_dir)
        logging.info(f"TensorBoard logs will be saved to: {tensorboard_dir}")
        self.global_step = 0  # Track global training steps

    # ------------------------------- data ------------------------------------
    def setup_data(self):
        logging.info("Prepare training datasets.")

        self.train_loader, self.val_loader = self.dataloader['train'], self.dataloader['valid']
    # ------------------------------ model ------------------------------------
    def build_model_and_optim(self):
        cfg = self.cfg
        maybe_cfg = getattr(self.model, "config", None)
        if maybe_cfg is not None:
            self.config = maybe_cfg

        # Get optimizer config - detect which optimizer is defined
        optimizer_cfg = getattr(cfg.training, 'optimizer', None)
        sgd_cfg = getattr(optimizer_cfg, 'SGD', None) if optimizer_cfg else None
        adam_cfg = getattr(optimizer_cfg, 'Adam', None) if optimizer_cfg else None

        if sgd_cfg is not None:
            optimizer_name = 'SGD'
            lr = self._get_default(getattr(sgd_cfg, 'learning_rate', None), 'SGD.learning_rate')
            momentum = self._get_default(getattr(sgd_cfg, 'momentum', None), 'SGD.momentum')
            weight_decay = self._get_default(getattr(sgd_cfg, 'weight_decay', None), 'SGD.weight_decay')
        elif adam_cfg is not None:
            optimizer_name = 'Adam'
            lr = self._get_default(getattr(adam_cfg, 'learning_rate', None), 'Adam.learning_rate')
            weight_decay = self._get_default(getattr(adam_cfg, 'weight_decay', None), 'Adam.weight_decay')
            betas = tuple(self._get_default(getattr(adam_cfg, 'betas', None), 'Adam.betas'))
        else:
            # Default to SGD with default values
            optimizer_name = self.DEFAULTS['optimizer']
            logging.info(f"'optimizer' not set in config, using default: {optimizer_name}")
            lr = self.DEFAULTS['SGD.learning_rate']
            momentum = self.DEFAULTS['SGD.momentum']
            weight_decay = self.DEFAULTS['SGD.weight_decay']
            logging.info(f"Using default SGD params: lr={lr}, momentum={momentum}, weight_decay={weight_decay}")

        base_net_lr = self._get_default(getattr(cfg.training, 'base_net_lr', None), 'training.base_net_lr')
        if base_net_lr is None:
            base_net_lr = lr
        extra_layers_lr = self._get_default(getattr(cfg.training, 'extra_layers_lr', None), 'training.extra_layers_lr')
        if extra_layers_lr is None:
            extra_layers_lr = lr

        params = [
            {'params': self.model.base_net.parameters(), 'lr': base_net_lr},
            {'params': itertools.chain(
                self.model.source_layer_add_ons.parameters(),
                self.model.extras.parameters()
            ), 'lr': extra_layers_lr},
            {'params': itertools.chain(
                self.model.regression_headers.parameters(),
                self.model.classification_headers.parameters()
            )}
        ]

        self.criterion = MultiboxLoss(
            self.config.priors,
            iou_threshold=getattr(cfg, "iou_threshold", 0.5) or 0.5,
            neg_pos_ratio=3,
            center_variance=0.1,
            size_variance=0.2,
            device=self.device
        )

        # Create optimizer based on config
        if optimizer_name == 'SGD':
            self.optimizer = torch.optim.SGD(
                params, lr=lr, momentum=momentum, weight_decay=weight_decay
            )
            logging.info(f"Using SGD optimizer: lr={lr}, momentum={momentum}, weight_decay={weight_decay}")
        elif optimizer_name == 'Adam':
            self.optimizer = torch.optim.Adam(
                params, lr=lr, betas=betas, weight_decay=weight_decay
            )
            logging.info(f"Using Adam optimizer: lr={lr}, betas={betas}, weight_decay={weight_decay}")

        logging.info(
            f"Base net learning rate: {base_net_lr}, Extra Layers learning rate: {extra_layers_lr}."
        )
        self.last_epoch = -1

        # Scheduler
        if cfg.training.scheduler == 'multi-step':
            logging.info("Uses MultiStepLR scheduler.")
            milestones = [int(v.strip()) for v in cfg.training.milestones.split(",")]
            self.scheduler = MultiStepLR(self.optimizer, milestones=milestones, gamma=0.1, last_epoch=self.last_epoch)
        elif cfg.training.scheduler == 'cosine':
            logging.info("Uses CosineAnnealingLR scheduler.")
            self.scheduler = CosineAnnealingLR(self.optimizer, cfg.training.t_max, last_epoch=self.last_epoch)
        else:
            raise ValueError(f"Unsupported Scheduler: {cfg.training.scheduler}.")

    # --------------------------- one epoch train ------------------------------
    def train_one_epoch(self, epoch, debug_steps=50):
        self.model.train(True)
        running_loss = 0.0
        running_regression_loss = 0.0
        running_classification_loss = 0.0
       
        total_steps = len(self.train_loader)
        for i, data in enumerate(self.train_loader):
            images, boxes, labels = data
            images = images.to(self.device)
            boxes = boxes.to(self.device)
            labels = labels.to(self.device)

            self.optimizer.zero_grad()
            
            if self.scaler is not None:
                with autocast():
                    confidence, locations = self.model(images)
                    regression_loss, classification_loss = self.criterion(confidence, locations, labels, boxes)
                    loss = regression_loss + classification_loss
                
                self.scaler.scale(loss).backward()
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                confidence, locations = self.model(images)
                regression_loss, classification_loss = self.criterion(confidence, locations, labels, boxes)
                loss = regression_loss + classification_loss
                loss.backward()
                self.optimizer.step()

            running_loss += loss.item()
            running_regression_loss += regression_loss.item()
            running_classification_loss += classification_loss.item()
            
            # Log to TensorBoard every step
            self.writer.add_scalar('Train/Loss', loss.item(), self.global_step)
            self.writer.add_scalar('Train/Regression_Loss', regression_loss.item(), self.global_step)
            self.writer.add_scalar('Train/Classification_Loss', classification_loss.item(), self.global_step)
            self.global_step += 1

            if i and i % debug_steps == 0:
                avg_loss = running_loss / debug_steps
                avg_reg_loss = running_regression_loss / debug_steps
                avg_clf_loss = running_classification_loss / debug_steps
                logging.info(
                    f"Epoch: {epoch}, Step: {i}/{total_steps}, "
                    f"Average Loss: {avg_loss:.4f}, "
                    f"Average Regression Loss {avg_reg_loss:.4f}, "
                    f"Average Classification Loss: {avg_clf_loss:.4f}"
                )
                running_loss = 0.0
                running_regression_loss = 0.0
                running_classification_loss = 0.0

    # ----------------------------- evaluation --------------------------------

    @torch.no_grad()
    def evaluate(self, epoch=None):
        """
        Combined evaluation:
        - Always compute validation loss.
        - Additionally run SSD VOC mAP via SSDEvaluatorWrapper based on cfg.
        """
        # ---------------- val loss ----------------
        self.model.eval()
        self.epoch = epoch
        running_loss = 0.0
        running_regression_loss = 0.0
        running_classification_loss = 0.0
        num = 0

        for _, data in enumerate(self.val_loader):
            images, boxes, labels = data
            images = images.to(self.device)
            boxes = boxes.to(self.device)
            labels = labels.to(self.device)
            num += 1

            confidence, locations = self.model(images)
            regression_loss, classification_loss = self.criterion(
                confidence, locations, labels, boxes
            )
            loss = regression_loss + classification_loss

            running_loss += loss.item()
            running_regression_loss += regression_loss.item()
            running_classification_loss += classification_loss.item()

        avg_loss = running_loss / max(num, 1)
        avg_reg = running_regression_loss / max(num, 1)
        avg_cls = running_classification_loss / max(num, 1)

        loss_dict = {
            "loss": avg_loss,
            "reg_loss": avg_reg,
            "cls_loss": avg_cls,
        }
        
        # Log validation metrics to TensorBoard
        if self.epoch is not None:
            self.writer.add_scalar('Val/Loss', avg_loss, self.epoch)
            self.writer.add_scalar('Val/Regression_Loss', avg_reg, self.epoch)
            self.writer.add_scalar('Val/Classification_Loss', avg_cls, self.epoch)

        map_dict = None

        #if map_interval is different than validation_epochs
        # if (self.epoch + 1) % map_interval == 0:
        if self.evaluator is None:
            self.evaluator = SSDEvaluatorWrapper(
                dataloaders=self.dataloader,
                model=self.model,
                cfg=self.cfg,
            )
        metrics = self.evaluator.evaluate() 

        map_dict = metrics
        
        # Log mAP to TensorBoard
        if map_dict is not None and self.epoch is not None:
            if 'mAP' in map_dict:
                self.writer.add_scalar('Val/mAP', map_dict['mAP'], self.epoch)
            # Log per-class AP if available
            for key, value in map_dict.items():
                if key != 'mAP' and isinstance(value, (int, float)):
                    self.writer.add_scalar(f'Val/AP_{key}', value, self.epoch)

        return loss_dict, map_dict

    # ------------------------------ training loop ----------------------------
    def train(self):
        cfg = self.cfg
        self.setup_data()
        self.build_model_and_optim()

        min_loss = float("inf")
        self.last_epoch = -1

        logging.info(f"Start training from epoch {self.last_epoch + 1}.")
        for epoch in range(self.last_epoch + 1, cfg.training.epochs):
            self.scheduler.step()
            self.train_one_epoch(epoch, debug_steps=self.cfg.training.print_interval)

            if epoch % cfg.training.validation_epochs == 0 or epoch == cfg.training.epochs - 1:
                loss_dict, map_dict = self.evaluate(epoch=epoch)

                val_loss = loss_dict["loss"]
                val_reg = loss_dict["reg_loss"]
                val_cls = loss_dict["cls_loss"]

                logging.info(
                    f"Epoch: {epoch}, "
                    f"Validation Loss: {val_loss:.4f}, "
                    f"Validation Regression Loss {val_reg:.4f}, "
                    f"Validation Classification Loss: {val_cls:.4f}"
                )

                if map_dict is not None and map_dict.get("mAP") is not None:
                    logging.info(f"Epoch: {epoch}, SSD mAP: {map_dict['mAP']:.4f}")

                self.save_checkpoint(epoch, val_loss)
                min_loss = min(min_loss, val_loss)
        
        # Close TensorBoard writer
        self.writer.close()
        logging.info("TensorBoard writer closed.")
        
        onnx_model = torch_model_export_static(cfg=self.cfg,
            model_dir=self.cfg.output_dir,
            model=self.model)
        
        return onnx_model 

    def save_checkpoint(self, epoch, val_loss):
        model_path = os.path.join(self.cfg.output_dir, self.cfg.general.saved_models_dir, f"{self.model_name}-Epoch-{epoch}-Loss-{val_loss}.pth")
        self.model.save(model_path)
        logging.info(f"Saved model {model_path}")