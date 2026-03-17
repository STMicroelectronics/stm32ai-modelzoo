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

from common.data_augmentation import random_color, random_erasing, random_misc
from object_detection.tf.src.data_augmentation import objdet_random_affine, objdet_random_misc



def data_augmentation(images, gt_labels, config=None, pixels_range=None, batch_info=None):
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
    """

    def _get_arg_values(used_args, default_args, function_name):
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
    for fn, args in config.items():
        if fn == 'random_contrast':
            default = {'factor': None, 'change_rate': 1.0}         
            args = _get_arg_values(args, default, fn)
            images = random_color.random_contrast(
                            images,
                            factor=args.factor,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate)

        elif fn == 'random_brightness':            
            default = {'factor': None, 'change_rate': 1.0}
            args = _get_arg_values(args, default, fn)
            images = random_color.random_brightness(
                            images,
                            factor=args.factor,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate)

        elif fn == 'random_gamma':
            default = {'gamma': None, 'change_rate': 1.0}
            args = _get_arg_values(args, default, fn)
            images = random_color.random_gamma(
                            images, 
                            gamma=args.gamma,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate)

        elif fn == 'random_hue':
            default = {'delta': None, 'change_rate': 1.0}
            args = _get_arg_values(args, default, fn)
            images = random_color.random_hue(
                            images,
                            delta=args.delta,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate)

        elif fn == 'random_saturation':
            default = {'delta': None, 'change_rate': 1.0}
            args = _get_arg_values(args, default, fn)
            images = random_color.random_saturation(
                            images,
                            delta=args.delta,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate)

        elif fn == 'random_value':
            default = {'delta': None, 'change_rate': 1.0}
            args = _get_arg_values(args, default, fn)
            images = random_color.random_value(
                            images,
                            delta=args.delta,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate)

        elif fn == 'random_hsv':
            default = {'hue_delta': None, 'saturation_delta': None, 'value_delta': None, 'change_rate': 1.0}
            args = _get_arg_values(args, default, fn)
            images = random_color.random_hsv(
                            images,
                            hue_delta=args.hue_delta,
                            saturation_delta=args.saturation_delta,
                            value_delta=args.value_delta,
                            pixels_range=pixels_range,
                            change_rate=args.change_rate)

        elif fn == 'random_rgb_to_hsv':
            default = {'change_rate': 0.25}
            args = _get_arg_values(args, default, fn)
            images = random_color.random_rgb_to_hsv(
                            images,
                            pixels_range=pixels_range,
                            change_rate=args.change_rate)

        elif fn == 'random_rgb_to_grayscale':
            default = {'change_rate': 0.25}
            args = _get_arg_values(args, default, fn)
            images = random_color.random_rgb_to_grayscale(
                            images,
                            pixels_range=pixels_range,
                            change_rate=args.change_rate)
                            
        elif fn == 'random_sharpness':
            default = {'factor': None, 'change_rate': 1.0}
            args = _get_arg_values(args, default, fn)
            images = random_color.random_sharpness(
                            images,
                            factor=args.factor,
                            pixels_range=pixels_range,
                            change_rate=args.change_rate)

        elif fn == 'random_posterize':
            default = {'bits': None, 'change_rate': 1.0}
            args = _get_arg_values(args, default, fn)
            images = random_color.random_posterize(
                            images,
                            bits=args.bits,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate)

        elif fn == 'random_invert':
            default = {'change_rate': 0.25}
            args = _get_arg_values(args, default, fn)
            images = random_color.random_invert(
                            images,
                            pixels_range=pixels_range,
                            change_rate=args.change_rate)

        elif fn == 'random_solarize':
            default = {'change_rate': 0.25}
            args = _get_arg_values(args, default, fn)
            images = random_color.random_solarize(
                            images,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate)

        elif fn == 'random_autocontrast':
            default = {'cutoff': 10, 'change_rate': 0.25}
            args = _get_arg_values(args, default, fn)
            images = random_color.random_autocontrast(
                            images,
                            cutoff=args.cutoff, 
                            pixels_range=pixels_range,
                            change_rate=args.change_rate)

        elif fn == 'random_blur':            
            default = {'filter_size': None, 'padding': 'constant', 'constant_values': 0,
                       'change_rate': 1.0}
            args = _get_arg_values(args, default, fn)
            images = random_misc.random_blur(
                            images, 
                            filter_size=args.filter_size,
                            padding=args.padding,
                            constant_values=args.constant_values,
                            pixels_range=pixels_range,
                            change_rate=args.change_rate)

        elif fn == 'random_gaussian_noise':
            default = {'stddev': None,
                       'change_rate': 1.0}
            args = _get_arg_values(args, default, fn)
            images = random_misc.random_gaussian_noise(
                            images,
                            stddev=args.stddev,
                            pixels_range=pixels_range, 
                            change_rate=args.change_rate)

        # elif fn == 'random_crop':
        #     default = {'crop_center_x': (0.25, 0.75),
        #                'crop_center_y': (0.25, 0.75),
        #                'crop_width': (0.6, 0.9),
        #                'crop_height': (0.6, 0.9),
        #                'interpolation': 'bilinear',
        #                'change_rate': 0.9}
        #     args = _get_arg_values(args, default, fn)
        #     images, gt_labels = objdet_random_misc.objdet_random_crop(
        #                     images,
        #                     gt_labels,
        #                     crop_center_x=args.crop_center_x,
        #                     crop_center_y=args.crop_center_y, 
        #                     crop_width=args.crop_width, 
        #                     crop_height=args.crop_height, 
        #                     interpolation=args.interpolation, 
        #                     change_rate=args.change_rate)

        elif fn == 'random_flip':
            default = {'mode': None, 'change_rate': 0.5}
            args = _get_arg_values(args, default, fn)
            images, gt_labels = objdet_random_affine.objdet_random_flip(
                            images,
                            gt_labels,
                            mode=args.mode,
                            change_rate=args.change_rate)

        elif fn == 'random_translation':
            default = {'width_factor': None, 'height_factor': None,
                       'fill_mode': 'constant', 'interpolation': 'bilinear', 'fill_value': 0.0,
                       'change_rate': 1.0} 
            args = _get_arg_values(args, default, fn)
            images, gt_labels = objdet_random_affine.objdet_random_translation(
                            images,
                            gt_labels,
                            width_factor=args.width_factor,
                            height_factor=args.height_factor,
                            fill_mode=args.fill_mode,
                            interpolation=args.interpolation,
                            fill_value=args.fill_value,
                            change_rate=args.change_rate)

        elif fn == 'random_rotation':
            default = {'factor': None,
                       'fill_mode': 'constant', 'interpolation': 'bilinear', 'fill_value': 0.0,
                       'change_rate': 1.0} 
            args = _get_arg_values(args, default, fn)
            images, gt_labels = objdet_random_affine.objdet_random_rotation(
                            images,
                            gt_labels,
                            factor=args.factor,
                            fill_mode=args.fill_mode,
                            interpolation=args.interpolation,
                            fill_value=args.fill_value,
                            change_rate=args.change_rate)

        elif fn in ('random_shear', 'random_shear_x', 'random_shear_y'):
            default = {'factor': None,
                       'fill_mode': 'constant', 'interpolation': 'bilinear', 'fill_value': 0.0,
                       'change_rate': 1.0}
            args = _get_arg_values(args, default, fn)            
            axis = fn[-1] if fn[-2:] in ('_x', '_y') else 'xy'
            images, gt_labels = objdet_random_affine.objdet_random_shear(
                            images,
                            gt_labels,
                            factor=args.factor,
                            axis=axis,
                            fill_mode=args.fill_mode,
                            interpolation=args.interpolation,
                            fill_value=args.fill_value,
                            change_rate=args.change_rate)

        elif fn == 'random_zoom':
            default = {'width_factor': None, 'height_factor': None,
                       'fill_mode': 'constant', 'interpolation': 'bilinear', 'fill_value': 0.0,
                       'change_rate': 1.0} 
            args = _get_arg_values(args, default, fn)
            images, gt_labels = objdet_random_affine.objdet_random_zoom(
                            images,
                            gt_labels,
                            width_factor=args.width_factor,
                            height_factor=args.height_factor,
                            fill_mode=args.fill_mode,
                            interpolation=args.interpolation,
                            fill_value=args.fill_value,
                            change_rate=args.change_rate)

        elif fn == 'random_crop':
            default = {'crop_width': (0.6, 0.9),
                       'crop_height': (0.6, 0.9),
                       'crop_center_x': (0.25, 0.75),
                       'crop_center_y': (0.25, 0.75),
                       'fill_mode': 'constant',
                       'interpolation': 'bilinear',
                       'fill_value': 0.0,
                       'change_rate': 0.9}
            args = _get_arg_values(args, default, fn)
            images, gt_labels = objdet_random_affine.objdet_random_bounded_crop(
                            images,
                            gt_labels,
                            width_factor=args.crop_width,
                            height_factor=args.crop_height,
                            crop_center_x=args.crop_center_x,
                            crop_center_y=args.crop_center_y,
                            fill_mode=args.fill_mode,
                            interpolation=args.interpolation,
                            fill_value=args.fill_value,
                            change_rate=args.change_rate)
                            
        elif fn == 'random_rectangle_erasing':
            default = {'nrec': (0, 3),
                       'area': (0.05, 0.2), 
                       'wh_ratio': (0.2, 1.5),
                       'fill_method': 'random',
                       'color': None,
                       'change_rate': 1.0,
                       'mode': 'image'}
            args = _get_arg_values(args, default, fn)
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

        elif fn == 'random_periodic_resizing':
            default = {'period': None, 'image_sizes': None, 'interpolation': 'bilinear'}
            args = _get_arg_values(args, default, fn)
            images, gt_labels = objdet_random_misc.objdet_random_periodic_resizing(
                            images,
                            gt_labels,
                            interpolation=args.interpolation,
                            new_image_size=(batch_info[1], batch_info[2]))

        else:
            raise ValueError(f"\nUnknown or unsupported data augmentation function: `{fn}`\n"
                             "Please check the 'data_augmentation' section of your "
                             "configuration file.")

    return images, gt_labels
