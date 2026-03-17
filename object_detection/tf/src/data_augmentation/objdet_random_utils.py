# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf


def objdet_apply_change_rate(images, boxes, images_augmented, boxes_augmented, change_rate=1.0): 
    """
    This function outputs a mix of augmented images and original
    images. The argument `change_rate` is a float in the interval 
    [0.0, 1.0] representing the number of changed images versus 
    the total number of input images average ratio. For example,
    if `change_rate` is set to 0.25, 25% of the input images will
    get changed on average (75% won't get changed). If it is set
    to 0.0, no images are changed. If it is set to 1.0, all the
    images are changed.
    """
    
    if change_rate == 1.0:
        return images_augmented, boxes_augmented
        
    if change_rate < 0. or change_rate > 1.:
        raise ValueError("The value of `change_rate` must be in the interval [0, 1]. ",
                         "Received {}".format(change_rate))

    dims = tf.shape(images)
    batch_size = dims[0]
    width = dims[1]
    height = dims[2]
    channels = dims[3]
    
    probs = tf.random.uniform([batch_size], minval=0, maxval=1, dtype=tf.float32)
    change_mask = tf.where(probs < change_rate, True, False)

    # Create a mask to apply to the images
    mask = tf.repeat(change_mask, width * height * channels)
    mask = tf.reshape(mask, [batch_size, width, height, channels])
    mask_not = tf.math.logical_not(mask)
    images_mix = tf.cast(mask_not, images.dtype) * images + tf.cast(mask, images.dtype) * images_augmented

    # Create a mask to apply to the labels
    num_boxes = tf.shape(boxes)[1]
    mask = tf.repeat(change_mask, num_boxes * 4)
    mask = tf.reshape(mask, [batch_size, num_boxes, 4])
    mask_not = tf.math.logical_not(mask)
    boxes_mix = tf.cast(mask_not, tf.float32) * boxes + tf.cast(mask, tf.float32) * boxes_augmented

    return images_mix, boxes_mix
