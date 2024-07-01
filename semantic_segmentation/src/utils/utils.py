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
from PIL import Image
from matplotlib import gridspec, pyplot as plt
import os
import sys
from omegaconf import DictConfig
from preprocess import preprocess_image


COLOR_MAP = {
    (0, 0, 0): 0,          # background
    (128, 0, 0): 1,        # aeroplane
    (0, 128, 0): 2,        # bicycle
    (128, 128, 0): 3,      # bird
    (0, 0, 128): 4,        # boat
    (128, 0, 128): 5,      # bottle
    (0, 128, 128): 6,      # bus
    (128, 128, 128): 7,    # car
    (64, 0, 0): 8,         # cat
    (192, 0, 0): 9,        # chair
    (64, 128, 0): 10,      # cow
    (192, 128, 0): 11,     # dining table
    (64, 0, 128): 12,      # dog
    (192, 0, 128): 13,     # horse
    (64, 128, 128): 14,    # motorbike
    (192, 128, 128): 15,   # person
    (0, 64, 0): 16,        # potted plant
    (128, 64, 0): 17,      # sheep
    (0, 192, 0): 18,       # sofa
    (128, 192, 0): 19,     # train
    (0, 64, 128): 20       # tv/monitor
}


def create_pascal_label_colormap():
    """Creates a label colormap used in PASCAL VOC segmentation benchmark."""
    colormap = np.zeros((256, 3), dtype=int)
    ind = np.arange(256, dtype=int)
    for shift in reversed(range(8)):
        for channel in range(3):
            colormap[:, channel] |= ((ind >> channel) & 1) << shift
        ind >>= 3
    return colormap


def label_to_color_image(label: np.ndarray = None) -> np.ndarray:

    """
    Adds color defined by the dataset colormap to the label.
    Args:
        label (np.ndarray): vector of labels we want to map into colors
    Returns:
        np.ndarray: colors associated to labels
    """
    if label.ndim != 2:
        raise ValueError('Expect 2-D input label')
    colormap = create_pascal_label_colormap()
    if np.max(label) >= len(colormap):
        raise ValueError('label value too large.')
    return colormap[label]


def vis_segmentation(image_path: str = None, seg_map: np.ndarray = None, cfg: DictConfig = None,
                     input_size: list = None):

    """
        Predicts a class for all the images that are inside a given directory.
        The model used for the predictions can be either a .h5 or .tflite file.

        Args:
            image_path (str): complete path to input image
            seg_map (np.ndarray): segmentation class output: each pixel is associated to a class
            cfg (dict): A dictionary containing the configuration file parameters.
            input_size (list): [height, width] in pixels

        Returns:

    """

    # Some instrumental parameters
    class_names = cfg.dataset.class_names
    cpp = cfg.preprocessing
    nb_channels = 1 if cpp.color_mode == "grayscale" else 3
    interpolation = cpp.resizing.interpolation
    aspect_ratio = cpp.resizing.aspect_ratio

    height = input_size[0]
    width = input_size[1]

    # directory for saving prediction outputs
    prediction_result_dir = f'{cfg.output_dir}/predictions/'
    os.makedirs(prediction_result_dir, exist_ok=True)

    # Load the original image
    original_image = tf.io.read_file(image_path)
    original_image = tf.image.decode_image(original_image, channels=nb_channels)

    original_image = preprocess_image(original_image, height=height, width=width, aspect_ratio=aspect_ratio, 
                                      interpolation=interpolation, scale=None, offset=None, perform_scaling=False)

    # Visualize the segmentation
    full_label_map = np.arange(len(class_names)).reshape(len(class_names), 1)
    full_color_map = label_to_color_image(full_label_map)

    if not cfg.general.display_figures:
        plt.ioff()

    plt.figure(figsize=(15, 5))
    grid_spec = gridspec.GridSpec(1, 4, width_ratios=[6, 6, 6, 1])

    # back to integer numbers for plotting
    original_image = original_image.numpy()
    original_image = original_image.astype(np.uint8)
    # Plot input image
    plt.subplot(grid_spec[0])
    plt.imshow(original_image)
    plt.axis('off')
    plt.title('Input image')

    # plot Segmentation map
    plt.subplot(grid_spec[1])
    seg_image = label_to_color_image(seg_map).astype(np.uint8)
    plt.imshow(seg_image)
    plt.axis('off')
    plt.title('Segmentation map')

    # plot input and segmentation overlay
    plt.subplot(grid_spec[2])
    extent = [0, input_size[0], input_size[1], 0]
    plt.imshow(original_image, extent=extent)
    plt.imshow(seg_image, alpha=0.7, extent=extent)
    plt.axis('off')
    plt.title('Segmentation overlay')

    unique_labels = np.unique(seg_map)
    ax = plt.subplot(grid_spec[3])
    plt.imshow(full_color_map[unique_labels].astype(np.uint8), interpolation='nearest')
    ax.yaxis.tick_right()
    plt.yticks(range(len(unique_labels)), [class_names[i] for i in unique_labels])
    plt.xticks([], [])
    ax.tick_params(width=0.0)
    plt.grid('off')

    # Save figure in the predictions directory
    fig_image_name = os.path.split(image_path)[1]
    pred_res_filename = f'{prediction_result_dir}/{os.path.basename(fig_image_name.split(".")[0])}.png'
    plt.savefig(pred_res_filename, bbox_inches='tight')

    if cfg.general.display_figures:
        plt.waitforbuttonpress()

    plt.close()


def tf_segmentation_dataset_to_np_array(input_ds: tf.data.Dataset = None, nchw: bool = True) -> tuple:
    """
    Converts a TensorFlow dataset into two NumPy arrays containing the data and Pascal VOC masks.

    This function iterates over the provided TensorFlow dataset, casts the image data to
    float32, and then converts the images and masks into NumPy arrays. The images and
    masks from all batches are concatenated along the first axis (batch dimension) to
    form two unified arrays.

    Parameters:
    - input_ds (tf.data.Dataset): A TensorFlow dataset object that yields tuples of
      (images, masks) when iterated over.

    - nchw (boolean): nchw = True if we want to convert to channel first

    Returns:
    - tuple: A tuple containing two NumPy arrays:
        - The first array contains the image data from the dataset.
        - The second array contains the corresponding masks.

    Example:
    ```python
    import tensorflow as tf
    import numpy as np

    # Assuming `dataset` is a pre-defined TensorFlow dataset with image-masks pairs
    data, masks = tf_dataset_to_np_array(dataset)

    print(data.shape)   # Prints the shape of the image data array
    print(masks.shape) # Prints the shape of the masks array

    ```

    Note:
    - The input TensorFlow dataset is expected to yield batches of data.
    - The function assumes that the dataset yields data in the form of (images, masks),
      where `images` are the features and `masks` are the corresponding targets
      or the data is of the form (images).
    - The function will fail if the input dataset does not yield data in the expected format.
    """
    batch_data = []
    batch_masks = []
    if input_ds is None:
        return None, None

    for images, masks in input_ds:
        images = tf.cast(images, dtype=tf.float32).numpy()
        batch_data.append(images)
        batch_masks.append(masks)

    batch_masks = np.concatenate(batch_masks, axis=0)
    batch_data = np.concatenate(batch_data, axis=0)

    # Convert image to input data
    if nchw and batch_data is not None:
        if batch_data.ndim == 4:
            # For a 4D array with shape [n, h, w, c], the new order will be [n, c, h, w]
            axes_order = (0, 3, 1, 2)
        elif batch_data.ndim == 3:
            # For a 3D array with shape [n, h, c], the new order will be [n, c, h]
            axes_order = (0, 2, 1)
        else:
            raise ValueError("The input array must have either 3 or 4 dimensions.")
        batch_data = np.transpose(batch_data, axes_order)

    # same for masks
    if nchw and batch_masks is not None:
        if batch_masks.ndim == 4:
            # For a 4D array with shape [n, h, w, c], the new order will be [n, c, h, w]
            axes_order = (0, 3, 1, 2)
        elif batch_masks.ndim == 3:
            # For a 3D array with shape [n, h, c], the new order will be [n, c, h]
            axes_order = (0, 2, 1)
        else:
            raise ValueError("The input array must have either 3 or 4 dimensions.")
        batch_masks = np.transpose(batch_masks, axes_order)

    return batch_data, batch_masks
