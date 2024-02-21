# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from munch import DefaultMunch
import tensorflow as tf
import random_color
import random_affine
import random_erasing
import random_misc


def data_augmentation(images, config=None, pixels_range=None, batch_info=None):
    """
    This function is called every time a new batch of input images needs 
    to be augmented before it gets presented to the model to train. 
    It applies to the images all the data augmentation functions that are
    specified in the `config` argument, which is a dictionary created from
    the 'data_augmentation' section of the YAML configuration file.

    Inputs:
        images:
            Images to augment,a tensor with shape
            [batch_size, width, height, channels].
        config:
            Config dictionary created from the YAML file.
            Contains the names and the arguments of the data augmentation
            functions to apply to the input images.
        batch_info:
            Information passed by the data augmentation layer.
            A Tensorflow 4D variable with the following elements:
            - batch number since the beginning of the training
            - training epoch number
            - width of the images of the previous batch
            - height of the images of the previous batch
    """  

    def get_arg_values(used_args, default_args, function_name):
        """
        This function generates the arguments to use with a data augmentation
        function to be applied to the images, given the arguments used in 
        the `config` dictionary and the default arguments of the function.
        """
        if used_args is None:
            # No attributes were given to the function.
            used_args =  DefaultMunch.fromDict({})
        if 'pixels_range' in used_args:
            raise ValueError("\nThe `pixels_range` argument is managed by the Model Zoo and "
                             "should not be used.\nPlease update the 'data_augmentation' "
                             "section of your configuration file.")
        args = DefaultMunch.fromDict(default_args)        
        if used_args is not None:
            for k, v in used_args.items():
                if k in default_args:
                    args[k] = used_args[k]
                else:
                    raise ValueError("\nFunction `{}`: unknown or unsupported argument `{}`\n"
                                     "Please check the 'data_augmentation' section of your "
                                     "configuration file.".format(function_name, k))
        return args


    # Apply all the data augmentation functions to the input images
    config = DefaultMunch.fromDict(config)
    for fn, args in config.items():             
        if fn == 'random_contrast':
            default = {'factor': None, 'change_rate': 1.0}
            args = get_arg_values(args, default, fn)            
            images = random_color.random_contrast(
                            images,
                            factor=args.factor,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate)

        elif fn == 'random_brightness':            
            default = {'factor': None, 'change_rate': 1.0}
            args = get_arg_values(args, default, fn)
            images = random_color.random_brightness(
                            images,
                            factor=args.factor,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate)

        elif fn == 'random_gamma':
            default = {'gamma': None, 'change_rate': 1.0}
            args = get_arg_values(args, default, fn)
            images = random_color.random_gamma(
                            images, 
                            gamma=args.gamma,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate)

        elif fn == 'random_hue':
            default = {'delta': None, 'change_rate': 1.0}
            args = get_arg_values(args, default, fn)
            images = random_color.random_hue(
                            images,
                            delta=args.delta,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate)

        elif fn == 'random_saturation':
            default = {'delta': None, 'change_rate': 1.0}
            args = get_arg_values(args, default, fn)
            images = random_color.random_saturation(
                            images,
                            delta=args.delta,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate)

        elif fn == 'random_value':
            default = {'delta': None, 'change_rate': 1.0}
            args = get_arg_values(args, default, fn)
            images = random_color.random_value(
                            images,
                            delta=args.delta,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate)

        elif fn == 'random_hsv':
            default = {'hue_delta': None, 'saturation_delta': None, 'value_delta': None, 'change_rate': 1.0}
            args = get_arg_values(args, default, fn)
            images = random_color.random_hsv(
                            images,
                            hue_delta=args.hue_delta,
                            saturation_delta=args.saturation_delta,
                            value_delta=args.value_delta,
                            pixels_range=pixels_range,
                            change_rate=args.change_rate)

        elif fn == 'random_rgb_to_hsv':
            default = {'change_rate': 0.25}
            args = get_arg_values(args, default, fn)
            images = random_color.random_rgb_to_hsv(
                            images,
                            pixels_range=pixels_range,
                            change_rate=args.change_rate)

        elif fn == 'random_rgb_to_grayscale':
            default = {'change_rate': 0.25}
            args = get_arg_values(args, default, fn)
            images = random_color.random_rgb_to_grayscale(
                            images,
                            pixels_range=pixels_range,
                            change_rate=args.change_rate)
                            
        elif fn == 'random_sharpness':
            default = {'factor': None, 'change_rate': 1.0}
            args = get_arg_values(args, default, fn)
            images = random_color.random_sharpness(
                            images,
                            factor=args.factor,
                            pixels_range=pixels_range,
                            change_rate=args.change_rate)

        elif fn == 'random_posterize':
            default = {'bits': None, 'change_rate': 1.0}
            args = get_arg_values(args, default, fn)
            images = random_color.random_posterize(
                            images,
                            bits=args.bits,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate)

        elif fn == 'random_invert':
            default = {'change_rate': 0.25}
            args = get_arg_values(args, default, fn)
            images = random_color.random_invert(
                            images,
                            pixels_range=pixels_range,
                            change_rate=args.change_rate)

        elif fn == 'random_solarize':
            default = {'change_rate': 0.25}
            args = get_arg_values(args, default, fn)
            images = random_color.random_solarize(
                            images,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate)
                            
        elif fn == 'random_equalize':
            default = {'change_rate': 0.25}
            args = get_arg_values(args, default, fn)
            images = random_color.random_equalize(
                            images,
                            pixels_range=pixels_range,
                            change_rate=args.change_rate)
            
        elif fn == 'random_autocontrast':
            default = {'cutoff': 10, 'change_rate': 0.25}
            args = get_arg_values(args, default, fn)
            images = random_color.random_autocontrast(
                            images,
                            cutoff=args.cutoff, 
                            pixels_range=pixels_range,
                            change_rate=args.change_rate)

        elif fn == 'random_blur':
            default = {'filter_size': None, 'padding': 'reflect', 'constant_values': 0,
                       'change_rate': 1.0}
            args = get_arg_values(args, default, fn)
            images = random_misc.random_blur(
                            images, 
                            filter_size=args.filter_size,
                            padding=args.padding,
                            constant_values=args.constant_values,
                            change_rate=args.change_rate)

        elif fn == 'random_gaussian_noise':
            default = {'stddev': None, 'change_rate': 1.0, 'mode': 'image'}
            args = get_arg_values(args, default, fn)
            images = random_misc.random_gaussian_noise(
                            images,
                            stddev=args.stddev,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate,
                            mode=args.mode)

        elif fn == 'random_jpeg_quality':
            default = {'jpeg_quality': None, 'change_rate': 1.0}
            args = get_arg_values(args, default, fn)
            images = random_misc.random_jpeg_quality(
                            images,
                            jpeg_quality=args.jpeg_quality,
                            pixels_range=pixels_range,
                            change_rate=args.change_rate)

        elif fn == 'random_flip':
            default = {'mode': None, 'change_rate': 0.5}
            args = get_arg_values(args, default, fn)
            images = random_affine.random_flip(
                            images,
                            mode=args.mode, 
                            change_rate=args.change_rate)
                            
        elif fn == 'random_translation':
            default = {'width_factor': None, 'height_factor': None,
                       'fill_mode': 'reflect', 'interpolation': 'bilinear', 'fill_value': 0.0, 
                       'change_rate': 1.0}
            args = get_arg_values(args, default, fn)
            images = random_affine.random_translation(images,
                            width_factor=args.width_factor,
                            height_factor=args.height_factor,
                            fill_mode=args.fill_mode,
                            interpolation=args.interpolation,
                            fill_value=args.fill_value,
                            change_rate=args.change_rate)

        elif fn == 'random_rotation':
            default = {'factor': None,
                       'fill_mode': 'reflect', 'interpolation': 'bilinear', 'fill_value': 0.0, 
                       'change_rate': 1.0}
            args = get_arg_values(args, default, fn)
            images = random_affine.random_rotation(
                            images,
                            factor=args.factor,
                            fill_mode=args.fill_mode,
                            interpolation=args.interpolation,
                            fill_value=args.fill_value,
                            change_rate=args.change_rate)

        elif fn == 'random_shear_x':
            default = {'factor': None,
                       'fill_mode': 'reflect', 'interpolation': 'bilinear', 'fill_value': 0.0,
                       'change_rate': 1.0}
            args = get_arg_values(args, default, fn)
            images = random_affine.random_shear_x(
                            images,
                            factor=args.factor,
                            fill_mode=args.fill_mode,
                            interpolation=args.interpolation,
                            fill_value=args.fill_value,
                            change_rate=args.change_rate)
                            
        elif fn == 'random_shear_y':
            default = {'factor': None,
                       'fill_mode': 'reflect', 'interpolation': 'bilinear', 'fill_value': 0.0,
                       'change_rate': 1.0}
            args = get_arg_values(args, default, fn)
            images = random_affine.random_shear_y(
                            images,
                            factor=args.factor,
                            fill_mode=args.fill_mode,
                            interpolation=args.interpolation,
                            fill_value=args.fill_value,
                            change_rate=args.change_rate)

        elif fn == 'random_shear':
            default = {'factor': None,
                       'fill_mode': 'reflect', 'interpolation': 'bilinear', 'fill_value': 0.0,
                       'change_rate': 1.0}
            args = get_arg_values(args, default, fn)            
            images = random_affine.random_shear(
                            images,
                            factor=args.factor,
                            fill_mode=args.fill_mode,
                            interpolation=args.interpolation,
                            fill_value=args.fill_value,
                            change_rate=args.change_rate)

        elif fn == 'random_zoom':
            default = {
                       'width_factor': None, 'height_factor': None,
                       'fill_mode': 'reflect', 'interpolation': 'bilinear', 'fill_value': 0.0,
                       'change_rate': 1.0}
            args = get_arg_values(args, default, fn)
            images = random_affine.random_zoom(
                            images,
                            width_factor=args.width_factor,
                            height_factor=args.height_factor,
                            fill_mode=args.fill_mode,
                            interpolation=args.interpolation,
                            fill_value=args.fill_value,
                            change_rate=args.change_rate)
                
        elif fn == 'random_rectangle_erasing':
            default = {'nrec': 1,
                       'area': (0.05, 0.4), 
                       'wh_ratio': (0.3, 2.0),
                       'fill_method': 'uniform', 
                       'color': None,
                       'change_rate': 1.0,
                       'mode': 'image'}
            args = get_arg_values(args, default, fn)
            images = random_erasing.random_rectangle_erasing(
                            images,
                            nrec=args.nrec,
                            area=args.area,
                            wh_ratio=args.wh_ratio,
                            fill_method=args.fill_method,
                            color=args.color,
                            pixels_range=pixels_range,
                            change_rate=args.change_rate,
                            mode=args.mode)

        elif fn == 'random_grid_cell_erasing':
            default = {'ncells_x': 5,
                       'ncells_y': 5,
                       'fill_method': 'uniform',
                       'color': None,
                       'erasing_prob': 0.2,
                       'change_rate': 1.0}
            args = get_arg_values(args, default, fn)
            images = random_erasing.random_grid_cell_erasing(
                            images,
                            ncells_x=args.ncells_x,
                            ncells_y=args.ncells_y,
                            fill_method=args.fill_method,
                            color=args.color,
                            pixels_range=pixels_range,
                            erasing_prob=args.erasing_prob,
                            change_rate=args.change_rate)

        elif fn == 'random_periodic_resizing':            
            default = {'resizing_period': None, 'initial_image_size': None,
                       'random_image_sizes': None, 'interpolation': 'bilinear'}
            args = get_arg_values(args, default, fn)
            images = random_misc.random_periodic_resizing(
                            images,
                            resizing_period=args.resizing_period,
                            initial_image_size=args.initial_image_size,
                            random_image_sizes=args.random_image_sizes,
                            interpolation=args.interpolation,
                            batch=batch_info[0],
                            previous_image_width=batch_info[1],
                            previous_image_height=batch_info[2])
                            
        else:
            raise ValueError("\nUnknown data augmentation function `{}`\nPlease check the "
                             "'data_augmentation' section of your configuration file.".format(fn))

    return images


def progressive_dataaug(images, config=None, pixels_range=None, batch_info=None):

    epoch = batch_info[1]
    if epoch < 40:
        images = random_affine.random_flip(images, mode="horizontal_and_vertical", change_rate=0.1)
    elif epoch < 80:
        images = random_affine.random_flip(images, mode="horizontal_and_vertical", change_rate=0.3)
    elif epoch < 120:
        images = random_affine.random_flip(images, mode="horizontal_and_vertical", change_rate=0.5)
    elif epoch < 160:
        images = random_affine.random_flip(images, mode="horizontal_and_vertical", change_rate=0.5)
        images = random_affine.random_translation(images, width_factor=0.2, height_factor=0.2)
        images = random_affine.random_zoom(images, width_factor=0.4)
    else:
        images = random_affine.random_flip(images, mode="horizontal_and_vertical", change_rate=0.5)
        images = random_affine.random_translation(images, width_factor=0.2, height_factor=0.2)
        images = random_affine.random_zoom(images, width_factor=0.4)
        images = random_color.random_contrast(images, factor=0.7, pixels_range=pixels_range)
        images = random_color.random_brightness(images, factor=0.5, pixels_range=pixels_range)
        images = random_color.random_invert(images, change_rate=0.1)
    return images

 