# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import numpy as np
import tensorflow as tf
from random_utils import check_images_shape, check_dataaug_argument, remap_pixel_values_range, apply_change_rate


def check_rectangle_erasing_args(fill_method, nrec, area, wh_ratio):

    if fill_method not in {"uniform", "random", "mosaic"}:
        raise ValueError("\nArgument `fill_method` of function `random_rectangle_erasing`: expecting "
                         "'uniform', 'random' or 'mosaic'. Received {}".format(fill_method))

    check_dataaug_argument(nrec, "nrec", function_name="random_rectangle_erasing", data_type=int)
    if not isinstance(nrec, (tuple, list)):
        nrec = (nrec, nrec)
    if nrec[0] < 0 or nrec[1] < 1:
        raise ValueError("\nArgument `nrec` of function `random_rectangle_erasing`: expecting "
                         "an integer greater than 0 or a tuple of 2 integers (n1, n2) with n1 "
                         "greater than or equal to 0. Received {}".format(nrec))

    check_dataaug_argument(area, "area", function_name="random_rectangle_erasing", data_type=(int, float))
    if not isinstance(area, (tuple, list)):
        area = (area, area)
    if area[0] < 0 or area[0] > 1 or area[1] < 0 or area[1] > 1:
        raise ValueError("\nArgument `area` of function `random_rectangle_erasing`: expecting a float "
                         "or a tuple of 2 floats greater than 0.0 and less than 1.0. Received {}".format(area))

    check_dataaug_argument(wh_ratio, "wh_ratio", function_name="random_rectangle_erasing", data_type=(int, float))
    if not isinstance(wh_ratio, (tuple, list)):
        wh_ratio = (wh_ratio, wh_ratio)
    if wh_ratio[0] < 0 or wh_ratio[1] < 0:
        raise ValueError("\nArgument `wh_ratio` of function `random_rectangle_erasing`: expecting a float "
                         "or a tuple of 2 floats greater than or equal to 0.0. Received {}".format(wh_ratio))

    return nrec, area, wh_ratio
    

def parse_color_arg(color, fill_method=None, channels=None, function_name=None):
    """
    This function checks that argument `color` is set properly depending
    on the number of channels of the input images and on the fill method.
    It returns an RGB color specification as a tensor with shape (3, 2).
    Each element is an integer in the interval [0, 255].
    """
    if fill_method == "uniform":
        if channels == 3 and color:
            message = f"\nArgument `color` of function `{function_name}`: expecting a " + \
                      f"tuple of 3 integers in the interval [0, 255]. Received {color}"
            if not isinstance(color, (tuple, list)) or len(color) != 3:
                raise ValueError(message)
            if type(color[0]) != int or type(color[1]) != int or type(color[2]) != int:
                raise ValueError(message)
            if color[0] < 0 or color[0] > 255 or color[1] < 0 or color[1] > 255 or color[2] < 0 or color[2] > 255:
                raise ValueError(message)
            color_spec = ((color[0], color[0]), (color[1], color[1]), (color[2], color[2]))
        if channels == 1 and color:
            if type(color) != int or color < 0 or color > 255:
                raise ValueError("\nArgument `color` of function `{}`: expecting an integer "
                                "in the interval [0, 255]. Received {}".format(function_name, color))
            color_spec = ((color, color), (color, color), (color, color))
        if not color:
            # By default, rectangles are black.
            color_spec = ((0, 0), (0, 0), (0, 0))
    else:
        # Fill method is either 'random' or 'mosaic'.
        if color:
            raise ValueError("\nFunction `{}`: argument `color` is only applicable to fill "
                             "method 'uniform'. Received {}".format(function_name, color))
        # All colors are allowed.
        color_spec = ((0, 255), (0, 255), (0, 255))

    return tf.convert_to_tensor(color_spec, dtype=tf.int32)


def look_for_grayscale_rgb_images(images):
    """
    This function looks for grayscale images that may be present in input
    RGB images. Their R, G and B planes are identical. We have to insert
    grayscale rectangles in these images instead of color rectangles, 
    so we need to know where they are. 
    """
    batch_size = tf.shape(images)[0]
    width, height, channels = images.shape[1:]

    r = tf.reshape(images[..., 0], [batch_size, width * height])
    g = tf.reshape(images[..., 1], [batch_size, width * height])
    b = tf.reshape(images[..., 2], [batch_size, width * height])
        
    # Check if red, green and blue channels are the same
    rg = tf.cast(r != g, tf.int32)
    rb = tf.cast(r != b, tf.int32)
    s = tf.reduce_sum(rg, axis=-1) + tf.reduce_sum(rb, axis=-1)
    grayscale = tf.cast(s == 0, tf.int32)
    return grayscale


def generate_rectangle_mask(batch_size, image_size=None, num_planes=None,
                            nrec_range=None, area_range=None, wh_ratio_range=None):
    """
    This function first generates a rectangle in each plane. The coordinates
    (x, y) of the rectangle centers are chosen randomly. Their areas and 
    width/height aspect ratios are sampled from the specified ranges. All the
    rectangles are clipped to the image size.
    Then, a number of rectangles is sampled for each image in the specified
    range. Some of the rectangles are suppressed to meet the required number
    of rectangles for each image.
    The rectangles are represented by a mask generated by the function that
    has the following shape:
        [batch_size, num_planes, image_width, image_height]
    Each element of the mask is a pixel of a plane. If the mask is set to 1,
    a rectangle is present at this location. If it is set to 0, no rectangle
    is present.
    """
    width, height = image_size
 
    # Sample rectangle areas, aspect ratios and center coordinates of rectangles
    area = tf.random.uniform([batch_size, num_planes], minval=area_range[0], maxval=area_range[1], dtype=tf.float32)
    wh_ratio = tf.random.uniform([batch_size, num_planes], minval=wh_ratio_range[0], maxval=wh_ratio_range[1], dtype=tf.float32)
    x = tf.random.uniform([batch_size, num_planes], minval=0, maxval=width + 1, dtype=tf.int32)
    y = tf.random.uniform([batch_size, num_planes], minval=0, maxval=height + 1, dtype=tf.int32)

    # Calculate width and height of rectangles
    area = area * tf.cast(width, tf.float32) * tf.cast(height, tf.float32)
    w = tf.math.sqrt(wh_ratio * area)
    h = w / wh_ratio

    # Calculate corner coordinates of rectangles
    x = tf.cast(x, tf.float32)
    x1 = tf.cast(tf.round(x - w/2), tf.int32)
    x2 = tf.cast(tf.round(x + w/2), tf.int32)

    y = tf.cast(y, tf.float32)
    y1 = tf.cast(tf.round(y - h/2), tf.int32)
    y2 = tf.cast(tf.round(y + h/2), tf.int32)

    # Clip corner coordinates to the image size
    x1 = tf.math.maximum(x1, 0)
    y1 = tf.math.maximum(y1, 0)
    x2 = tf.math.minimum(x2, width)
    y2 = tf.math.minimum(y2, height)

    # Sample a number of rectangles for each image. Then, suppress
    # some of the rectangles so that the required number of rectangles
    # is met for each image. To eliminate a rectangle, we set its
    # 4 corner coordinates to 0.
    nrec = tf.random.uniform([batch_size, 1], minval=nrec_range[0], maxval=nrec_range[1] + 1, dtype=tf.int32)
    i = tf.range(batch_size * num_planes) % num_planes
    i = tf.reshape(i, [batch_size, num_planes])
    selected_recs = tf.where(i < nrec, 1, 0)

    x1 = tf.reshape(x1 * selected_recs, [batch_size, num_planes, 1, 1])
    y1 = tf.reshape(y1 * selected_recs, [batch_size, num_planes, 1, 1])
    x2 = tf.reshape(x2 * selected_recs, [batch_size, num_planes, 1, 1])
    y2 = tf.reshape(y2 * selected_recs, [batch_size, num_planes, 1, 1])

    # Generate a mask that has 0's inside (x1, x2)
    # intervals and 1's outside
    i = tf.range(batch_size * height * num_planes) % height
    i = tf.reshape(i, [batch_size, num_planes, height])
    i = tf.tile(i, [1, width, 1])
    grid_x = tf.reshape(i, [batch_size, num_planes, width, height])
    mask_x = tf.math.logical_and(grid_x >= x1, grid_x <= x2)

    # Generate a mask that has 0's inside (y1, y2)
    # intervals and 1's outside
    i = tf.range(batch_size * width * num_planes) % width
    i = tf.reshape(i, [batch_size, 1, num_planes, width])
    i = tf.repeat(i, height)
    grid_y = tf.reshape(i, [batch_size, num_planes, width, height])
    mask_y = tf.math.logical_and(grid_y >= y1, grid_y <= y2)

    mask = tf.math.logical_and(mask_x, mask_y)
    return tf.cast(mask, tf.int32)


def remove_rectangle_overlaps(rectangle_mask):
    """
    This function removes any overlap between the rectangles that will be
    inserted in an image. This is needed to avoid the superimposition of 
    colors in overlap areas.
    A number is assigned to each of the rectangles to be erased from an
    image. When several rectangles are present at the same pixel location,
    the rectangle with the largest number wins and remains intact. The 
    other rectangles get carved and become more complex shapes such as
    L-shapes, disconnected smaller rectangles, etc.
    """
    batch_size = tf.shape(rectangle_mask)[0]
    num_planes, width, height = rectangle_mask.shape[1:]

   # Assign a number from 1 to nrec to each rectangle
    n = tf.range(num_planes) + 1
    n = tf.repeat(n, width * height)
    n = tf.reshape(n, [num_planes, width, height])
    n = tf.tile(n, [batch_size, 1, 1])
    n = tf.reshape(n, [batch_size, num_planes, width, height])
    numbered_recs = n * tf.cast(rectangle_mask, dtype=tf.int32)
    
    winner_numbers = tf.math.reduce_max(numbered_recs, axis=1)
    winner_numbers = tf.expand_dims(winner_numbers, axis=1)
    
    mask = tf.where(numbered_recs == winner_numbers, winner_numbers, 0)
    # The mask has 1's inside rectangle areas.
    return tf.where(mask > 0, 1, 0)


def generate_color_planes(batch_size, image_size=None, num_planes=None, fill_method=None, color=None):
    """
    This function creates planes with uniform RGB colors. The rectangles
    to insert in the images will be cut from these planes to obtain 
    colored rectangles.
    The shape of the tensor generated by the function is:
        [batch_size, num_planes, width, height, 3]
    The color of each plane depends on the fill method and the color 
    specification. If the fill method is:
        - "random", the color of each plane is randomly chosen. All RGB 
          colors are usable. All the rectangles will have different colors.
        - "uniform", all the planes have the same RGB color that is 
          specified by the `color` argument (a tuple of 3 integers in 
          the [0, 255] interval).
        - "mosaic", the planes are filled with random RGB pixels.
    """
    width, height = image_size

    if fill_method == "uniform" or fill_method == "random":
        # If the fill method is "uniform", color[i, 0] and color[i, 1] have the
        # same value. If the fill method is "random", they have different values.
        r = tf.random.uniform([batch_size * num_planes], minval=color[0, 0], maxval=color[0, 1] + 1, dtype=tf.int32)
        r = tf.reshape(r, [batch_size, num_planes])
        r = tf.repeat(r, width * height)    
        
        g = tf.random.uniform([batch_size * num_planes], minval=color[1, 0], maxval=color[1, 1] + 1, dtype=tf.int32)
        g = tf.reshape(g, [batch_size, num_planes])
        g = tf.repeat(g, width * height)  
        
        b = tf.random.uniform([batch_size * num_planes], minval=color[2, 0], maxval=color[2, 1] + 1, dtype=tf.int32)
        b = tf.reshape(b, [batch_size, num_planes])
        b = tf.repeat(b, width * height)  
    else:
        # The fill method is "mosaic".
        pixels = batch_size *  num_planes * width * height
        r = tf.random.uniform([pixels], minval=color[0, 0], maxval=color[0, 1] + 1, dtype=tf.int32)
        g = tf.random.uniform([pixels], minval=color[1, 0], maxval=color[1, 1] + 1, dtype=tf.int32)
        b = tf.random.uniform([pixels], minval=color[2, 0], maxval=color[2, 1] + 1, dtype=tf.int32)

    r = tf.reshape(r, [batch_size, num_planes, width, height])
    g = tf.reshape(g, [batch_size, num_planes, width, height])
    b = tf.reshape(b, [batch_size, num_planes, width, height])

    x = tf.stack([r, g, b], axis=-1)
    color_planes = tf.reshape(x, [batch_size, num_planes, width, height, 3])
   
    return color_planes


def random_rectangle_erasing(
                images, 
                nrec=1,
                area=(0.05, 0.4),
                wh_ratio=(0.3, 2.0),
                fill_method="uniform",
                color=None,
                pixels_range=(0.0, 1.0),
                change_rate=1.0,
                mode="image"):

    """ 
    This function randomly erases a number of rectangular areas from input
    images and fills the voids with color.

    The function has two modes:
       - image mode: different sets of random rectangles are erased from 
         the different images of the batch.
       - batch mode: the same random set of images is erased from all the
         images of the batch.

    The image mode creates more image diversity, potentially leading to better
    training results, but run times are longer than in the batch mode.

    By default, if no arguments are specified, one random black rectangle 
    is erased from each image. All the rectangles are different (image mode).

    Arguments:
        images:
            Input RGB or grayscale images with shape
            [batch_size, width, height, channels].
        nrec:
            An integer or a tuple of 2 integers, specifies the range of values 
            the numbers of rectangles to erase are sampled from (one number
            of rectangles per image). If a scalar value v is used, the number
            of rectangles is equal to v for all the images.
        area:
            A float or a tuple of 2 floats, specifies the range of values
            the areas of rectangles are sampled from (one area per rectangle).
            If a scalar value v is used, the area of all the rectangles in all
            the images is equal to v.
            Area values are fractions of the image area. Therefore, they must
            be in the interval [0, 1].
        wh_ratio:
            A float or a tuple of 2 floats, specifies the range of values the
            width/height aspect ratio of rectangles are sampled from (one ratio
            per rectangle). If a scalar value v is used, the aspect ratio of 
            all the rectangles in all the images is equal to v.
        fill_method:
            A string, one of {"uniform", "random" or "mosaic"}, specifies the 
            method to use to fill with color the rectangles erased from the 
            images. If the fill method is:
                "uniform":
                    All the rectangles in all the images are filled with 
                    the same color specified using the `color` argument.
                    If no color is specified, all the rectangles are black.
                "random":
                    Each rectangle is filled with a randomly chosen RGB color
                    if the input images are RGB images or a randomly chosen
                    shade of gray if the input images are grayscale (all the
                    rectangles will have different colors).
                "mosaic":
                    Each rectangle is filled with random pixels.
        color:
            A tuple of 3 integers in the interval [0, 255] if the images
            are RGB images or an integer in the interval [0, 255] if the
            images are grayscale images, specifies the color to use to fill
            the rectangles erased from the images.
            This argument is only applicable to the 'uniform' fill method.
        change_rate:
            A float in the interval [0, 1], the number of changed images
            versus the total number of input images average ratio.
            For example, if `change_rate` is set to 0.25, 25% of the input
            images will get changed on average (75% won't get changed).
            If it is set to 0.0, no images are changed. If it is set
            to 1.0, all the images are changed.
        pixels_range:
            A tuple of 2 integers or floats, specifies the range 
            of pixel values in the input images and output images.
            Any range is supported. It generally is either
            [0, 255], [0, 1] or [-1, 1].
        mode:
            Either "image" or "batch". If set to "image", different sets
            of rectangles are erased from the different images of the batch.
            If set to "batch", the same set of rectangles is erased from
            all the images of the batch. The "image" mode creates more
            image diversity, potentially leading to better training results,
            but run times are longer than in the "batch" mode.

    Returns:
        The images with erased rectangles.
    """

    check_images_shape(images, function_name="random_rectangle_erasing")
    batch_size = tf.shape(images)[0]
    width, height, channels = images.shape[1:]

    pixels_dtype = images.dtype
    images = remap_pixel_values_range(images, pixels_range, (0, 255), dtype=tf.int32)
    
    nrec, area, wh_ratio = check_rectangle_erasing_args(fill_method, nrec, area, wh_ratio)
    color = parse_color_arg(color, fill_method=fill_method, channels=channels,
                            function_name="random_rectangle_erasing")

    if mode not in {"image", "batch"}:
        raise ValueError("\nArgument `mode` of function `random_rectangle_erasing`: "
                         "expecting 'image' or 'batch'. Received {}".format(mode))

    if channels == 3:
        grayscale = look_for_grayscale_rgb_images(images)
    else:
        # Convert single channel grayscale images to RGB
        x = tf.repeat(images[..., 0], 3)
        images = tf.reshape(x, [batch_size, width, height, 3])        
        grayscale = tf.ones([batch_size], tf.float32)

    # We call "planes" areas of the same size as the input images that
    # contain the rectangles to erase from the images. A set of planes
    # is associated to each image. Each plane either contains one
    # rectangle to erase from the image or no rectangle (empty plane).
    # The number of planes associated to an image is equal to the
    # maximum number of rectangles that may be erased from the image.
    num_planes = nrec[1]

    rectangle_mask = generate_rectangle_mask(
                            batch_size=batch_size if mode == "image" else 1,
                            image_size=[width, height],
                            num_planes=num_planes,
                            nrec_range=nrec,
                            area_range=area,
                            wh_ratio_range=wh_ratio)
    if nrec != (1, 1):
        rectangle_mask = remove_rectangle_overlaps(rectangle_mask)

    # Color the rectangles and compute the union of the
    # planes to obtain images of all the rectangles.
    color_planes = generate_color_planes(
                            batch_size=batch_size if mode == "image" else 1,
                            image_size=[width, height],
                            num_planes=num_planes, 
                            fill_method=fill_method,
                            color=color)
    colored_rectangles = tf.expand_dims(rectangle_mask, axis=-1) * color_planes
    rectangle_images = tf.math.reduce_sum(colored_rectangles, axis=1)

    if mode == "batch":
        # We have only one image of rectangles. Duplicate it to have a batch.
        rectangle_images = tf.tile(rectangle_images, [batch_size, 1, 1, 1])
        rectangle_images = tf.reshape(rectangle_images, [batch_size, width, height, 3])

    # If the image is grayscale, the rectangles must also be grayscale.
    gray_rectangle_images = tf.stack([rectangle_images[..., 0], rectangle_images[..., 0], rectangle_images[..., 0]], axis=-1)
    grayscale = tf.reshape(grayscale, [batch_size,1, 1, 1])
    rectangle_images = tf.where(grayscale == 1, gray_rectangle_images, rectangle_images)

    # Insert the rectangles in the input images
    rectangle_mask = tf.expand_dims(rectangle_mask, axis=-1)
    mask = tf.math.reduce_sum(rectangle_mask, axis=1)
    images_aug = tf.where(mask == 0, images, rectangle_images)

    if channels == 1:
        # Grayscale images, only keep the red channel.
        images = tf.expand_dims(images[..., 0], axis=-1)
        images_aug = tf.expand_dims(images_aug[..., 0], axis=-1)

    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0, 255), pixels_range, dtype=pixels_dtype)


#---------------------------------------------------------------------------------
# Grid cells erasing
#---------------------------------------------------------------------------------

def check_grid_cell_erasing_args(ncells_x, ncells_y, fill_method, erasing_prob):
    if type(ncells_x) != int or ncells_x <= 0:
        raise ValueError("\nArgument `ncells_x` of function `random_grid_cell_erasing`: "
                         "expecting a positive integer. Received {}".format(ncells_x))
    if type(ncells_y) != int or ncells_y <= 0:
        raise ValueError("\nArgument `ncells_y` of function `random_grid_cell_erasing`: "
                         "expecting a positive integer. Received {}".format(ncells_y))
    if fill_method not in {"uniform", "random", "mosaic"}:
        raise ValueError("\nArgument `fill_method` of function `random_rectangle_erasing`: expecting "
                         "'uniform', 'random' or 'mosaic'. Received {}".format(fill_method))
    if erasing_prob < 0 or erasing_prob > 1:
        raise ValueError("\nArgument `erasing_prob` of function `random_rectangle_erasing`: expecting "
                         "a float in the interval [0, 1]. Received {}".format(fill_method))


def expand_grid_to_pixels(grid, grid_specs):

    ncells_x, ncells_y, cell_w, cell_h = grid_specs[:4]
    batch_size = tf.shape(grid)[0]
    ncells_x, ncells_y = grid.shape[1:]
    
    w = ncells_x * cell_w
    h = ncells_y * cell_h
    
    x = tf.repeat(grid, cell_h)
    x = tf.reshape(x, [batch_size, ncells_x, h])
    x = tf.tile(x, [1, 1, cell_w])

    return tf.reshape(x, [batch_size, w, h])
    
    
def create_grid_cell_mask(batch_size, grid_specs, erasing_prob):
    """
    This function creates a mask to cut some of the cell 
    areas out of the input images.
    The mask has 3 identical channels as it will be applied
    to RGB images of the cell areas to fill with colors.
    """
    
    ncells_x, ncells_y, cell_w, cell_h, image_width, image_height = grid_specs

    # Choose randomly the cells that will be erased
    probs = tf.random.uniform(
                    [batch_size, ncells_x, ncells_y], minval=0, maxval=1, dtype=tf.float32)
    grid_mask = tf.cast(probs >= erasing_prob, tf.int32)
    
    # Clip the mask to the image size and replicate it
    # to have 3 identical channels 
    mask = expand_grid_to_pixels(grid_mask, grid_specs)
    mask = mask[:, :image_width, :image_height]
    mask = tf.repeat(mask, 3)
    return tf.reshape(mask, [batch_size, image_width, image_height, 3])    
        
    
def create_grid_cell_colors(batch_size, grid_specs, fill_method, color, grayscale):
    """
    This function creates images of grid cell areas filled with colors.
    If the fill method is "uniform", all the cell areas have the same
    color. If it is "random", they all have different colors chosen
    randomly. If it is "mosaic", they are all filled with random pixels.
    A mask will be used to only keep the cell areas that have
    to be erased from the input images.
    """
    ncells_x, ncells_y, cell_w, cell_h, image_width, image_height = grid_specs
    width = ncells_x * cell_w
    height = ncells_y * cell_h

    if fill_method == "uniform" or fill_method == "random":
        # Choose a color for each cell area
        # If the fill method is "uniform", color[i, 0] and color[i, 1] have the
        # same value. If the fill method is "random", they have different values.
        shape = [batch_size, ncells_x, ncells_y]
        r = tf.random.uniform(shape, minval=color[0, 0], maxval=color[0, 1] + 1, dtype=tf.int32)
        g = tf.random.uniform(shape, minval=color[1, 0], maxval=color[1, 1] + 1, dtype=tf.int32)
        b = tf.random.uniform(shape, minval=color[2, 0], maxval=color[2, 1] + 1, dtype=tf.int32)
        
        # Expand the grid to pixels
        r = expand_grid_to_pixels(r, grid_specs)
        g = expand_grid_to_pixels(g, grid_specs)
        b = expand_grid_to_pixels(b, grid_specs)        
    else:
        # mosaic
        shape = [batch_size, width, height]
        r = tf.random.uniform(shape, minval=color[0, 0], maxval=color[0, 1] + 1, dtype=tf.int32)
        g = tf.random.uniform(shape, minval=color[1, 0], maxval=color[1, 1] + 1, dtype=tf.int32)
        b = tf.random.uniform(shape, minval=color[2, 0], maxval=color[2, 1] + 1, dtype=tf.int32)

    # If the input image is grayscale, make the green 
    # and blue channels identical to the red channel.
    grayscale = tf.reshape(grayscale, [batch_size, 1, 1])
    g = tf.where(grayscale == 1, r, g)
    b = tf.where(grayscale == 1, r, b)

    color_map = tf.stack([r, g, b], axis=-1)
    color_map = tf.reshape(color_map, [batch_size, width, height, 3])
    # Clip to the image size
    return color_map[:, :image_width, :image_height]


def random_grid_cell_erasing(
            images,
            ncells_x=5,
            ncells_y=5,
            fill_method="uniform",
            color=None,
            pixels_range=(0.0, 1.0),
            erasing_prob=0.2,
            change_rate=1.0):
    """
    This function function places a grid of cells on top of input images and
    randomly erases some of the cells, filling the voids with color.
    
    Arguments:
        images:
            Input RGB or grayscale images with shape
            [batch_size, width, height, channels].
        ncells_x:
            A positive integer, specifies the number of cells to create
            along the x axis.
        ncells_y:
            A positive integer, specifies the number of cells to create
            along the y axis.
        fill_method:
            One of {"uniform", "random" or "mosaic"}, specifies the method
            to use to fill with color the cells erased from the images.
            If the fill method is:
                "uniform":
                    All the cells in all the images are filled with the
                    same color specified using the `color` argument.
                    If no color is specified, all the cells are black.
                "random":
                    Each cell is filled with a randomly chosen RGB color
                    if the input images are RGB images or a randomly chosen
                    shade of gray if the images are grayscale (all the 
                    cells will have different colors).
                "mosaic":
                    Each cell is filled with random pixels.
        color:
            A tuple of 3 integers in the interval [0, 255] if the images
            are RGB images or an integer in the interval [0, 255] if the
            images are grayscale images, specifies the color to use to fill
            the cells erased from the images. This argument is only 
            applicable to the 'uniform' fill method.
        erasing_prob:
            A float in the interval [0, 1], specifies the probability
            that a cell gets erased. The larger the value of this argument,
            the larger the number of cells that get erased on average.
        pixels_range:
            A tuple of 2 integers or floats, specifies the range 
            of pixel values in the input images and output images.
            Any range is supported. It generally is either
            [0, 255], [0, 1] or [-1, 1].
        change_rate:
            A float in the interval [0, 1], the number of changed images
            versus the total number of input images average ratio.
            For example, if `change_rate` is set to 0.25, 25% of the input
            images will get changed on average (75% won't get changed).
            If it is set to 0.0, no images are changed. If it is set
            to 1.0, all the images are changed.

    Returns:
        The images with erased grid cells.
    """

    check_images_shape(images, function_name="random_grid_cell_erasing", allow_grayscale=True)
    batch_size = tf.shape(images)[0]
    image_width, image_height, channels = images.shape[1:]

    pixels_dtype = images.dtype
    images = remap_pixel_values_range(images, pixels_range, (0, 255), dtype=tf.int32)

    check_grid_cell_erasing_args(ncells_x, ncells_y, fill_method, erasing_prob)
    color = parse_color_arg(color, fill_method=fill_method, channels=channels,
                            function_name="random_grid_cell_erasing")
        
    if channels == 3:
        grayscale = look_for_grayscale_rgb_images(images)
    else:
        # Convert single channel grayscale images to RGB
        x = tf.repeat(images[..., 0], 3)
        images = tf.reshape(x, [batch_size, image_width, image_height, 3])        
        grayscale = tf.ones([batch_size], tf.float32)

    # Calculate the width and height of the cells
    cell_w = tf.math.ceil(image_width / ncells_x)
    cell_w = tf.cast(cell_w, dtype=tf.int32)
    
    cell_h = tf.math.ceil(image_height / ncells_y)
    cell_h = tf.cast(cell_h, dtype=tf.int32)
    
    grid_specs = (ncells_x, ncells_y, cell_w, cell_h, image_width, image_height)
    
    mask = create_grid_cell_mask(batch_size, grid_specs, erasing_prob)
    color_map = create_grid_cell_colors(batch_size, grid_specs, fill_method, color, grayscale)
    images_aug = tf.where(mask == 1, images, color_map)

    if channels == 1:
        # Grayscale images, only keep the red channel.
        images = tf.expand_dims(images[..., 0], axis=-1)
        images_aug = tf.expand_dims(images_aug[..., 0], axis=-1)
    
    # Apply change rate and remap pixel values to input images range
    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0, 255), pixels_range, dtype=pixels_dtype)
