# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import sys
import argparse
import yaml
from yaml.loader import SafeLoader
from munch import DefaultMunch
import tensorflow as tf
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath('../utils'))
sys.path.append(os.path.abspath('../models'))

from parse_config import postprocess_config_dict
import lr_schedulers


def get_learning_rate_scheduler(cfg):
        
    # Get the list of all learning rate scheduler callback names.
    # This includes the Tensorflow LearningRateScheduler callback.
    lr_scheduler_names = lr_schedulers.get_scheduler_names() + ["LearningRateScheduler"]

    message = "\nPlease check the 'training.callbacks' section of your configuration file."

    scheduler = None
    num_lr_schedulers = 0
    for name, args in cfg.items():
   
        if name == "ReduceLROnPlateau":
           raise ValueError("\nThe ReduceLROnPlateau learning rate schedule is only "
                            "available after training.{}".format(message))

        if name in lr_scheduler_names:
            num_lr_schedulers += 1
            if name == "LearningRateScheduler":
                text = "tf.keras.callbacks.LearningRateScheduler("
            else:
                text = "lr_schedulers.{}(".format(name)

            # Collect the callback arguments
            for k, v in args.items():
                text += f'{k}={v}, '
            text = text[:-2] + ")"

            try:
                scheduler = eval(text)
            except:
                raise ValueError(
                    "\nThe arguments of the `{}` callback are incomplete "
                    "or invalid, got:\n{}{}".format(name, text, message))
            
            if name == "LearningRateScheduler":
                scheduler.name = "LearningRateScheduler"

    if scheduler is None:
        raise ValueError("\nCould not find a learning rate scheduler.{}".format(message))
   
    if num_lr_schedulers > 1:
        raise ValueError("\nFound more than one learning rate scheduler.{}".format(message))

    return scheduler


def get_initial_learning_rate(cfg):
    """
    The learning rate scheduler may make use of the learning rate
    provided in the optimizer. If the learning_rate attribute is 
    present in the optimizer section, return its value.
    """
    optimizer_name = list(cfg.keys())[0]
    optimizer_args = cfg[optimizer_name]
    if optimizer_args is not None and optimizer_args.learning_rate:
        lr = optimizer_args.learning_rate
    else:
        lr = None
    return lr


def plot_lr_schedule(scheduler, epochs, initial_lr=None, fname=None):
    
    learning_rate = []
    lr = initial_lr if initial_lr is not None else 0.0
 
    for e in range(epochs):
        lr = scheduler.schedule(e, lr)
        learning_rate.append(lr)

    plt.plot(learning_rate)
    plt.title("{} Learning Rate Schedule".format(scheduler.name))
    plt.xlabel("epochs")
    plt.ylabel("learning rate")
    plt.show()

    if fname is not None:
        plt.savefig(fname)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--config_file", type=str, default="../user_config.yaml",
                        help="Path to the YAML config file")
    parser.add_argument("--fname", type=str, default="",
                        help="Path to output plot file (.png or any other format supported by matplotlib savefig())")
    args = parser.parse_args()
    
    if not os.path.isfile(args.config_file):
        raise ValueError("\nUnable to find configuration file, got {}".format(args.config_file))
    
    # Load and postprocess the config file
    with open(args.config_file) as f:
        config = yaml.load(f, Loader=SafeLoader)
    postprocess_config_dict(config)
    cfg = DefaultMunch.fromDict(config)

    # Chcek that the required sections of the config file are present
    if not cfg.training:
        raise ValueError("\nThe configuration file should include a 'training' section.")
    if not cfg.training.optimizer:
        raise ValueError("\nThe configuration file should include a 'training.optimizer' section.")
    
    # If it has no argument, the optimizer may written as below:
    #       optimizer: Adam
    if type(cfg.training.optimizer) == str:
        cfg.training.optimizer = DefaultMunch.fromDict({cfg.training.optimizer: None})

    if "callbacks" not in cfg.training:
        raise ValueError("\nThe configuration file should include a 'training.callbacks' section.")
    if cfg.training.callbacks is None:
        cfg.training.callbacks = {}

    scheduler = get_learning_rate_scheduler(cfg.training.callbacks)
    
    initial_lr = get_initial_learning_rate(cfg.training.optimizer)
    fname = args.fname if args.fname else None
    plot_lr_schedule(scheduler, cfg.training.epochs, initial_lr=initial_lr, fname=fname)

    
if __name__ == '__main__':
    main()
