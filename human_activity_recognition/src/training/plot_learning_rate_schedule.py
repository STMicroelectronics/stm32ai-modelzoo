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
from omegaconf import DictConfig
from munch import DefaultMunch
import tensorflow as tf
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath('../utils'))
sys.path.append(os.path.abspath('../preprocessing'))

from parse_config import postprocess_config_dict
import lr_schedulers


def collect_callback_args(name, args=None, message=None):
    if args:
        if type(args) != DefaultMunch:
            raise ValueError(f"\nInvalid syntax for `{name}` callback arguments{message}")
        text = "("
        for k, v in args.items():
            if type(v) == str and v[:7] != "lambda ":
                text += f'{k}=r"{v}", '
            else:
                text += f'{k}={v}, '
        text = text[:-2] + ")"
    else:
        text = "()"
    return text


def get_learning_rate_scheduler(cfg: DictConfig) -> tf.keras.callbacks.Callback:
        
    # Get the list of all learning rate scheduler callback names.
    # This includes the Keras LearningRateScheduler callback.
    lr_scheduler_names = lr_schedulers.get_scheduler_names() + ["LearningRateScheduler"]

    message = "\nPlease check the 'training.callbacks' section of your configuration file."

    scheduler_name = None
    scheduler = None
    num_lr_schedulers = 0
    for name, args in cfg.items():
        if name == "ReduceLROnPlateau":
           raise ValueError("\nUnable to plot the learning rate before training when using "
                            "the `ReduceLROnPlateau` scheduler\n"
                            f"The learning rate schedule is only available after training.{message}")
        if name in lr_scheduler_names:
            scheduler_name = name
            num_lr_schedulers += 1
            if name == "LearningRateScheduler":
                text = "tf.keras.callbacks.LearningRateScheduler"
            else:
                text = "lr_schedulers.{}".format(name)

            # Collect the callback arguments
            text += collect_callback_args(name, args=cfg[name], message=message)

            # Evaluate the callback string
            try:
                scheduler = eval(text)
            except:
                raise ValueError(f"\nThe arguments of the `{name}` callback are incomplete or invalid.\n"
                                 f"Received: {text}{message}")

    if scheduler is None:
        raise ValueError(f"\nCould not find a learning rate scheduler{message}")
    if num_lr_schedulers > 1:
        raise ValueError(f"\nFound more than one learning rate scheduler{message}")

    return scheduler_name, scheduler


def get_initial_learning_rate(cfg: DictConfig) -> float:
    """
    The learning rate scheduler may need the initial learning rate provided
    in the optimizer. If the learning_rate attribute is present in the optimizersection, we get its value.

    Args:
        cdf (DictConfig): Dictionary containing the 'optimizer' section 
                          of the configuration file.
    Returns:
        lr (float): The value of the 'learning_rate' argument of the optimizer.
    """

    # Look for the 'lr' or 'learning_rate' argument
    optimizer_name = list(cfg.keys())[0]
    optimizer_args = cfg[optimizer_name]
    optimizer_lr = None
    if optimizer_args:
        for k, v in optimizer_args.items():
            if k == "learning_rate" or k == "lr":
                optimizer_lr = v
                
    if not optimizer_lr:
        optimizer_lr = 0.01 if optimizer_name == "SGD" else 0.001
    return optimizer_lr


def plot_lr_schedule(scheduler_name: str,
                     scheduler: tf.keras.callbacks.Callback,
                     epochs: int = None,
                     initial_lr: float = None,
                     fname: str = None) -> None:
    """
    This function plots the learning rate schedule for a given number of epochs.

    Args:
        scheduler (tf.keras.callbacks.Callback): learning rate scheduler callback.
        epochs (int): number of epochs to plot.
        initial_lr (float): initial learning given in argument to the optimizer.
        fname (str): filename to use the save the plot.

    Returns:
        None
    """

    learning_rate = []
    lr = initial_lr
    for e in range(epochs):
        lr = scheduler.schedule(e, lr)
        learning_rate.append(lr)

    plt.plot(learning_rate)
    plt.title(f"{scheduler_name} Learning Rate Schedule")
    plt.xlabel("epochs")
    plt.ylabel("learning rate")
    plt.show()
    if fname:
        plt.savefig(fname)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--config_file", type=str, default="user_config.yaml",
                        help="Path to the YAML config file from the directory above")
    parser.add_argument("--fname", type=str, default="",
                        help="Path to output plot file (.png or any other format supported by matplotlib savefig())")
    args = parser.parse_args()

    config_file_path = os.path.join(os.pardir, args.config_file)
    if not os.path.isfile(config_file_path):
        raise ValueError(f"\nUnable to find the YAML configuration file\nReceived path: {args.config_file}")
    
    # Load and postprocess the config file
    with open(config_file_path) as f:
        config = yaml.load(f, Loader=SafeLoader)
    postprocess_config_dict(config)
    cfg = DefaultMunch.fromDict(config)

    # Check that the required sections of the config file are present
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

    scheduler_name, scheduler = get_learning_rate_scheduler(cfg.training.callbacks)
    
    initial_lr = get_initial_learning_rate(cfg.training.optimizer)
    fname = args.fname if args.fname else None
    plot_lr_schedule(scheduler_name, scheduler, epochs=cfg.training.epochs, initial_lr=initial_lr, fname=fname)


if __name__ == '__main__':
    main()
