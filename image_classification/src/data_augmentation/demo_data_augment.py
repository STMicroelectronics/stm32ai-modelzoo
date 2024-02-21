# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import argparse
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import random_color, random_affine, random_erasing, random_misc
from random_utils import remap_pixel_values_range


def sample_images(dataset_path, image_size=None, interpolation=None, num_images=None, seed=None):

    subdir_names = [x for x in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, x))]
    if subdir_names:
        # The dataset contains subdirectories, so it is in the ImageNet format.
        # Create a data loader using a tf.data.Dataset and load a batch
        data_loader = tf.keras.preprocessing.image_dataset_from_directory(
                dataset_path,
                image_size=(image_size[0], image_size[1]),
                label_mode="categorical",
                interpolation=interpolation,
                color_mode="rgb",
                batch_size=num_images,
                shuffle=True,
                seed=seed)
        images, _ = iter(data_loader).next()
    else:
        # The dataset is a directory containing images.
        # Get the list of files (subdirectories are ignored).
        image_paths = []
        for x in os.listdir(dataset_path):
            path = os.path.join(dataset_path, x)
            if os.path.isfile(path):
                image_paths.append(path)
        if not image_paths:
            raise ValueError(f"\nCould not find any image file in directory {dataset_path}")
        
        # Sample image path indices
        indices = tf.random.uniform([num_images], minval=0, maxval=len(image_paths), dtype=tf.int32, seed=seed)

        # Read and concatenate images to create a batch
        images = tf.zeros([1, image_size[1], image_size[0], 3], dtype=tf.float32)
        for i in indices:
            data = tf.io.read_file(image_paths[i])
            try:
                img = tf.image.decode_image(data, channels=3)
                img = tf.image.resize(img, size=[image_size[1], image_size[0]], method=interpolation)
            except:
                raise ValueError(f"\nUnable to read image file {image_paths[i]}\n"
                                 "Supported image file formats are JPEG, PNG, GIF and BMP.")
            img = tf.expand_dims(img, axis=0)
            images = tf.concat([images, img], axis=0)
        images = images[1:]

    return images

    
def view_images(images, images_aug, pixels_range, function=None):

    images = remap_pixel_values_range(images, pixels_range, (0.0, 1.0), dtype=tf.float32)
    images_aug = remap_pixel_values_range(images_aug, pixels_range, (0.0, 1.0), dtype=tf.float32)

    for i in range(len(images)):        
        f = plt.figure()
        f.add_subplot(1, 2, 1)
        plt.imshow(images[i], cmap="gray")
        plt.title("original")
        f.add_subplot(1, 2, 2)
        plt.imshow(images_aug[i], cmap="gray")
        plt.title(function)
        plt.show(block=True)
        plt.close()


def augment_and_display(images, pixels_range=None, grayscale=None):

    print("Showing random_contrast")
    images_aug = random_color.random_contrast(images, factor=0.7, pixels_range=pixels_range)
    view_images(images, images_aug, pixels_range, function="random_contrast")

    print("Showing random_brightness")
    images_aug = random_color.random_brightness(images, factor=0.4, pixels_range=pixels_range)
    view_images(images, images_aug, pixels_range, function="random_brightness")

    print("Showing random_gamma")
    images_aug = random_color.random_gamma(images, gamma=(0.2, 2.0), pixels_range=pixels_range)
    view_images(images, images_aug, pixels_range, function="random_gamma")

    if not grayscale:
        print("Showing random_hue")               
        images_aug = random_color.random_hue(images, delta=0.1, pixels_range=pixels_range)
        view_images(images, images_aug, pixels_range, function="random_hue")
    else:
        print("random_hue: not applicable to grayscale images")               
    
    if not grayscale:
        print("Showing random_saturation")               
        images_aug = random_color.random_saturation(images, delta=0.4, pixels_range=pixels_range)
        view_images(images, images_aug, pixels_range, function="random_saturation")
    else:
        print("random_saturation: not applicable to grayscale images")               
        
    if not grayscale:
        print("Showing random_value")               
        images_aug = random_color.random_value(images, delta=0.4, pixels_range=pixels_range)        
        view_images(images, images_aug, pixels_range, function="random_value")
    else:
        print("random_value: not applicable to grayscale images")               
        
    if not grayscale:
        print("Showing random_hsv")               
        images_aug = random_color.random_hsv(
                        images, hue_delta=0.1, saturation_delta=0.1, value_delta=0.2, pixels_range=pixels_range)
        view_images(images, images_aug, pixels_range, function="random_hsv")
    else:
        print("random_hsv: not applicable to grayscale images")               
        
    if not grayscale:
        print("Showing random_rgb_to_hsv")
        images_aug = random_color.random_rgb_to_hsv(images, pixels_range=pixels_range, change_rate=1.0)
        view_images(images, images_aug, pixels_range, function="random_rgb_to_hsv")
    else:
        print("random_rgb_to_hsv: not applicable to grayscale images")               

    if not grayscale:
        print("Showing random_rgb_to_grayscale")
        images_aug = random_color.random_rgb_to_grayscale(images, pixels_range=pixels_range, change_rate=1.0)
        view_images(images, images_aug, pixels_range, function="random_rgb_to_grayscale")
    else:
        print("random_rgb_to_grayscale: not applicable to grayscale images")               
    
    print("Showing random_sharpness")
    images_aug = random_color.random_sharpness(images, factor=(1.0, 4.0), pixels_range=pixels_range)
    view_images(images, images_aug, pixels_range, function="random_sharpness")    

    print("Showing random_posterize")
    images_aug = random_color.random_posterize(images, bits=(1, 8), pixels_range=pixels_range)
    view_images(images, images_aug, pixels_range, function="random_posterize")    

    print("Showing random_invert")
    images_aug = random_color.random_invert(images, pixels_range=pixels_range, change_rate=1.0)
    view_images(images, images_aug, pixels_range, function="random_invert")
    
    print("Showing random_solarize")
    images_aug = random_color.random_solarize(images, pixels_range=pixels_range, change_rate=1.0)
    view_images(images, images_aug, pixels_range, function="random_solarize")

    print("Showing random_equalize")
    images_aug = random_color.random_equalize(images, pixels_range=pixels_range, change_rate=1.0)
    view_images(images, images_aug, pixels_range, function="random_equalize")

    print("Showing random_autocontrast")
    images_aug = random_color.random_autocontrast(images, cutoff=10, pixels_range=pixels_range, change_rate=1.0)
    view_images(images, images_aug, pixels_range, function="random_autocontrast")

    print("Showing random_blur")
    images_aug = random_misc.random_blur(images, filter_size=(1, 4))
    view_images(images, images_aug, pixels_range, function="random_blur")

    print("Showing random_gaussian_noise")
    images_aug = random_misc.random_gaussian_noise(images, stddev=(0.02, 0.1), pixels_range=pixels_range)
    view_images(images, images_aug, pixels_range, function="random_gaussian_noise")
 
    print("Showing random_jpeg_quality")
    images_aug = random_misc.random_jpeg_quality(images, jpeg_quality=(3, 100), pixels_range=pixels_range)
    view_images(images, images_aug, pixels_range, function="random_jpeg_quality")

    print("Showing horizontal flip")
    images_aug = random_affine.random_flip(images, mode="horizontal")
    view_images(images, images_aug, pixels_range, function="flip 'horizontal'")

    print("Showing vertical flip")
    images_aug = random_affine.random_flip(images, mode="vertical")
    view_images(images, images_aug, pixels_range, function="flip 'vertical'")

    print("Showing horizontal_and_vertical flip")
    images_aug = random_affine.random_flip(images, mode="horizontal_and_vertical")
    view_images(images, images_aug, pixels_range, function="flip 'horizontal_and_vertical'")

    print("Showing random_translation")
    images_aug = random_affine.random_translation(images, width_factor=0.2, height_factor=0.2)
    view_images(images, images_aug, pixels_range, function="random_translation")

    print("Showing random_rotation")
    images_aug = random_affine.random_rotation(images, factor=0.2)
    view_images(images, images_aug, pixels_range, function="random_rotation")

    print("Showing random_shear_x")
    images_aug = random_affine.random_shear_x(images, factor=0.1)
    view_images(images, images_aug, pixels_range, function="random_shear_x")

    print("Showing random_shear_y")
    images_aug = random_affine.random_shear_y(images, factor=0.3)
    view_images(images, images_aug, pixels_range, function="random_shear_y")

    print("Showing random_shear")
    images_aug = random_affine.random_shear(images, factor=0.1)
    view_images(images, images_aug, pixels_range, function="random_shear")

    print("Showing random_zoom")
    images_aug = random_affine.random_zoom(images, width_factor=0.3)
    view_images(images, images_aug, pixels_range, function="random_zoom")

    print("Showing random_rectangle_erasing")
    images_aug = random_erasing.random_rectangle_erasing(
                images,
                nrec=(0, 3),
                area=(0.05, 0.2),
                wh_ratio=(0.2, 1.5),
                fill_method="random",
                pixels_range=pixels_range)
    view_images(images, images_aug, pixels_range, function="random_rectangle_erasing")
    
    print("Showing random_grid_cell_erasing")
    images_aug = random_erasing.random_grid_cell_erasing(
                images,
                ncells_x=6,
                ncells_y=3,
                fill_method="random",
                erasing_prob=0.2,
                change_rate=1.0,
                pixels_range=pixels_range)
    view_images(images, images_aug, pixels_range, function="random_grid_cell_erasing")


def demo_data_augmentation(dataset_path,
                           num_images=8,
                           image_size=(224, 224),
                           rescaling=(1/127.5, -1),
                           interpolation="bilinear",
                           grayscale=False,
                           seed=None):
                             
    images = sample_images(dataset_path,
                           image_size=image_size,
                           interpolation=interpolation,
                           num_images=num_images,
                           seed=seed)
                                                             
    if grayscale:
        # Convert the images from RGB to grayscale
        img = tf.cast(images, tf.float32) / 255
        img = 0.299*img[..., 0] + 0.587*img[..., 1] + 0.114*img[..., 2]
        img = tf.clip_by_value(img, 0.0, 1.0)
        images = tf.expand_dims(img, axis=-1)
        pixels_range = (0.0, 1.0)
    else:
        # Rescale the images
        scale = float(rescaling[0])
        offset = float(rescaling[1])
        images = tf.cast(images, tf.float32) * scale + offset
        pixels_range = (offset, 255 * scale + offset)

    augment_and_display(images, pixels_range=pixels_range, grayscale=grayscale)
 

def main():
    """
    Script entry point
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default='', required=False,
                        help="Path to the image data to sample from, either the root directory of a "
                             "dataset in the ImageNet format (like for example the Flowers dataset) "
                             "or a directory containing images")
    parser.add_argument("--num_images", type=int, default=8,
                        help="Number of images to augment and display. Default: 8")
    parser.add_argument("--image_size", type=str, default="(224, 224)",
                        help="Image size, a tuple of 2 integers. Default: (224, 224)")
    parser.add_argument("--interpolation", type=str, default="bilinear",
                        help="Interpolation method used to resize the images. Default: 'bilinear'")
    parser.add_argument("--rescaling", type=str, default="(1/127.5, -1)",
                        help="Scale and offset to use for rescaling images, a tuple of 2 floats. Default: (1/127.5, -1)")
    parser.add_argument("--grayscale", action="store_true",
                        help="Convert input images to grayscale before augmentation")
    parser.add_argument("--seed", type=str, default="None",
                        help="Seed to use to sample the images from the dataset. Default: None")
    args = parser.parse_args()

    if not args.dataset:
        raise FileNotFoundError("Please specify a dataset path using the --dataset option.")
    if not os.path.isdir(args.dataset):
        raise FileNotFoundError("Could not find dataset directory `{}`.".format(args.dataset))
    
    message = "Invalid `image_size` argument, expecting a tuple of 2 integers"
    try:
        args.image_size = eval(args.image_size)
    except:
        raise ValueError(message)
    if type(args.image_size) != tuple or len(args.image_size) != 2:
        raise ValueError(message)

    message = "Invalid `rescaling` argument, expecting a tuple of 2 floats"
    try:
        args.rescaling = eval(args.rescaling)
    except:
        raise ValueError(message)
    if type(args.rescaling) != tuple or len(args.rescaling) != 2:
        raise ValueError(message)

    args.seed = None if args.seed == "None" else int(args.seed)
        
    demo_data_augmentation(
                    args.dataset,
                    num_images=args.num_images,
                    image_size=args.image_size,
                    interpolation=args.interpolation,
                    rescaling=args.rescaling,
                    grayscale = args.grayscale,
                    seed=args.seed)


if __name__ == '__main__':
    main()
    