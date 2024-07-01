# <a xid="">Learning rate schedulers</a>

A number of callbacks are available that implement different learning rate decay functions. The *ReduceLROnPlateau* and *LearningRateScheduler* schedulers are Keras callbacks, the others are provided with the Model Zoo. They all update the learning rate at the beginning of each epoch.
To use one of these learning rate schedulers, simply add it to the list of callbacks in the `training:` section of your configuration file. 

### <summary><a><b>Plotting the learning rate before training</b></a></summary>

A script that plots the learning rate schedule without running a training is available. To run it,  execute **plot_lr_schedule.py** script from the current directory. The script reads the `training:` section of your configuration file to get the number of training epochs, and the name and arguments of the learning rate scheduler in the `callbacks:` subsection. 

We encourage you to run this script. It does not require any extra work as it only needs your configuration file. It may save you a lot of time to choose a learning rate scheduler and tune its parameters.

You can use the script to vizualize the output of the learning rate schedulers that are presented in the [the learning rate schedulers README](../../../../common/training/lr_schedulers_README.md) for a description of the available callbacks and learning rate plotting utility.

Just copy the examples and paste them to a configuration file. Then you can launch the script as example below:

```bash
python plot_lr_schedule.py --config-path ../../ --config-name user_config.yaml --fname plot.png
```

This will plot the learning rate schedule used in /src/user_config.yaml and save the plotted curve in /src/training/lr_schedule/plot.png file

Note that the script cannot be used with the Tensorflow *ReduceLROnPlateau* scheduler as the learning rate schedule is only available after training.
