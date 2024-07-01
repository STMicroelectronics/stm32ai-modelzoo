# <a id="">Using data augmentation</a>

## <a id="">Table of contents</a>

<details open><summary><a href="#1"><b>1. Introduction</b></a></summary><a id="1"></a>

Data augmentation has proved an effective technique to reduce the overfit of a network and make it generalize better. It is generally useful when you have a small dataset or a dataset that is too easy for the network to learn.

A rich set of functions are available in the Model Zoo to enable you to develop effective data augmentation solutions for your applications. All functions were written to run efficiently with Tensorflow using GPU resources.

The data augmentation transforms you want to apply to the images are specified in the YAML configuration file. The transforms are only applied to the images during training. They are not applied when the model is evaluated or quantized.

The Model Zoo code can be customized to implement your own data augmentation. In particular, *dynamic data augmentation*, i.e. data augmentation that changes as the training progresses instead of staying the same from beginning to end, can be easily implemented.

</details>
<details open><summary><a href="#2"><b>2. Specifying your data augmentation</b></a></summary><a id="2"></a>

The data augmentation transforms to apply to the input images are specified in the configuration file using a `data_augmentation` section, as illustrated in the YAML code below:

```yaml
data_augmentation:
   random_flip:
      mode: horizontal_and_vertical
   random_translation:
      width_factor: 0.2
      height_factor: 0.1
   random_contrast:
      factor: 0.4
   random_brightness:
      factor: 0.3
```

In this example, the following transforms are successively applied to the input images in their order of appearance in the configuration file:
1. Random flip
2. Random translation
3. Random contrast adjustment
4. Random brightness adjustment

These transforms are performed by functions from the Model Zoo that are called successively as follows:
```python
images = random_flip(input_images, mode="horizontal_and_vertical")
images = random_translation(images, width_factor=0.2, height_factor=0.1)
images = random_contrast(images, factor=0.4)
images = random_brightness(images, factor=0.3)
return images
```

As it can be seen, the names of the data augmentation transforms and their attributes that are used in the configuration file are names of functions and arguments. From now on, we will use the term "function" instead of "transform".

If an argument of a function is not specified in the configuration file, its default value is used. For example, the `random_translation()` function is defined as follows:
```python
def random_translation(
        images,
        width_factor=None,
        height_factor=None,
        fill_mode='reflect',
        interpolation='bilinear',
        fill_value=0.0,
        change_rate=1.0):
```

In the YAML code above, only the `width_factor` and `height_factor` arguments of the `random_translation()` function are mentioned. Therefore, the `fill_mode`, `interpolation`, `fill_value` and `change_rate` arguments will take their default values, which respectively are 'reflect', 'bilinear', 0.0 and 1.0.

There are no constraints on the number of functions, types of functions and order of functions that you can use in your configuration file. However, as the YAML language does not support multiple occurrences of the same attribute in the same section, each function can only be used once.

</details>
<details open><summary><a href="#3"><b>3. Available data augmentation functions</b></a></summary><a id="3"></a>

Four packages of data augmentation functions are provided with the Model Zoo:
- `random_color.py`, contains functions that alter color features, such as contrast and brightness.
- `random_affine.py`, contains functions that apply affine transformations to images, such as flip and rotation.
- `random_erasing.py`, contains functions that erase rectangles from images.
- `random_misc.py`, contains a number of miscellaneous functions.

The available data augmentation functions are listed in the table below.

| Package | Function | Changes made to input images |
|:---------|:------|:----------------------|
| random_color.py | random_contrast | Adjust contrast |
| random_color.py | random_brightness | Adjust brightness |
| random_color.py | random_gamma_adjust | Adjust gamma |
| random_color.py | random_hue | Adjust hue |
| random_color.py | random_saturation | Adjust saturation |
| random_color.py | random_value | Adjust value |
| random_color.py | random_hsv | Adjust hue, saturation and value simultaneously |
| random_color.py | random_rgb_to_hsv | Convert from RGB representation to HSV (Hue, Saturation, Value) representation |
| random_color.py | random_rgb_to_grayscale | Convert from RGB to grayscale |
| random_color.py | random_sharpness | Adjust sharpness |
| random_color.py | random_posterize | Change the number of bits used to encode colors |
| random_color.py | random_invert | Invert pixels |
| random_color.py | random_solarize | Invert pixels with a value above a given threshold |
| random_color.py | random_equalize | Equalize images |
| random_color.py | random_autocontrast | Maximize the contrast of images |
| random_misc.py | random_blur | Blur images |
| random_misc.py | random_gaussian_noise | Add gaussian noise to images |
| random_misc.py | random_jpeg_quality | Adjust JPEG quality |
| random_affine.py | random_flip | Flip images in horizontal and/or vertical directions |
| random_affine.py | random_translation | Translate images in horizontal and/or vertical directions |
| random_affine.py | random_rotation | Rotate images |
| random_affine.py | random_zoom | zoom in/out |
| random_affine.py | random_shear | Shear images |
| random_affine.py | random_shear_x | Shear images along the x axis only |
| random_affine.py | random_shear_y | Shear images along the y axis only |
| random_erasing.py | random_rectangle_erasing | Erase rectangles from images |
| random_erasing.py | random_grid_cell_erasing | Partition images in a grid of cells and erase some of them |
| random_misc.py | random_periodic_resizing | Periodically resize images to a set of random sizes|

These functions and their arguments are documented in the exhibits of this document.

You can also refer to the source code of the data augmentation packages. They are all in the *\<MODEL-ZOO-ROOT\>/image_classification/src/data_augmentation* directory. Comments are included at the top of each function that explain what the function does and how its arguments should be used.

</details>
<details open><summary><a href="#4"><b>4. Getting familiar with the available data augmentation functions</b></a></summary><a id="4"></a>

A script called `demo_data_augment.py` is available in the *\<MODEL-ZOO-ROOT\>/image_classification/src/data_augmentation* directory that you can use to get familiar with the available data augmentation functions.

This script samples a number of images from a dataset of your choice and applies each data augmentation function to them. For each function, it displays before/after images side-by-side that show the effect of the function on the input images.

To run the script, change the current directory to *\<MODEL-ZOO-ROOT\>/image_classification/src/data_augmentation* and execute `demo_data_augmentation.py`. The arguments the script takes are listed in the table below.

| Argument | Type | Default | Usage |
|:---------|:------|:------|:----------------------|
| dataset | String | None | Path to the root directory of a dataset in the ImageNet format (such as Flowers or PlantLeafDiseases) or a path to a directory containing images |
| num_images | Integer | 8 | Number of images to sample, augment and display |
| image_size | Tuple of 2 integers | (224, 224) | Image resizing size |
| interpolation | String | "bilinear" | Image resizing method, one of {"bilinear", "nearest", "bicubic", "area", "lanczos3", "lanczos5", "gaussian", "mitchellcubic"} |
| rescaling | Tuple of 2 floats | (1/127.5, -1.0) | Image rescaling scale and offset |
| seed | integer | None | Seed to use to sample the images from the dataset |
| grayscale | N/A | N/A | Argument with no value. If present, images from the dataset are converted to grayscale before being augmented and display. |

Note that some functions are not applicable to grayscale images. For example, the `random_hue` function that changes the hue of images does not make sense for grayscale images.

A random generator is used to sample the images from the dataset. By default, different images will be selected every time you run the script. If you want to run the script multiple times with the same set of images, then set the seed argument to an integer value. If you use different seed values, different sets of images will be sampled.

We encourage you to run this script as it is an efficient way to learn about the data augmentation functions that are provided with the Model Zoo.

</details>
<details open><summary><a href="#5"><b>5. Setting the rate of change</b></a></summary><a id="5"></a>

Each data augmentation function has an argument called `change_rate` that enables you to control the average percentage of images that get changed by the function.

For example, if you set the `change_rate` argument of a given function to 0.25, the function will change 25% of the input images on average, leaving 75% unchanged. If you set it to 1.0, all the images will be changed by the function. If you set it to 0.0, no images will be changed (the function has no effect).

The default value of `change_rate` is set to 1.0 for all the data augmentation functions to the exception of the functions listed in the table below.

| Function | Default `change_rate` value |
|:---------|:------|
| random_flip | 0.5 |
| random_rgb_to_hsv | 0.25 |
| random_rgb_to_grayscale | 0.25 |
| random_invert | 0.25 |
| random_solarize | 0.25 |
| random_equalize | 0.25 |
| random_autocontrast | 0.25 |

</details>
<details open><summary><a href="#6"><b>6. Testing your data augmentation</b></a></summary><a id="6"></a>

As you work on your data augmentation, we strongly recommend that you carefully examine the effects it has on the images of your dataset.

Some transformations may be too aggressive, some others not enough. If you use too much data augmentation, you may create images that are not representative of your dataset, or simply don't make sense. If you don't use enough data augmentation, you may not create enough image diversity to have a significant impact on the overfit and accuracy. Experimenting is key.

A script called `test_data_augment.py` is available in the *\<MODEL-ZOO-ROOT\>/image_classification/src/data_augmentation* directory that you can use to visualize the effects on images of the data augmentation you specified in your configuration file. This scripts samples a number of images from the dataset, applies the data augmentation functions to them, and displays before/after images side-by-side.

The script reads the `dataset`, `preprocessing` and `data_augmentation` sections of the configuration file. If a `training` section is present, it uses it to obtain the model input shape and derives the image size from it. If there is no `training` section, the '--image_size' argument is available to specify the image size.

The `test_data_augment.py` script takes the following arguments:

| Argument | Type | Default | Usage |
|:---------|:------|:------|:----------------------|
| config_file | String | ../user_config.yaml | Path to the YAML configuration file |
| num_images | Integer | 8 | Number of images to sample from the dataset and augment |
| image_size | Tuple of 2 integers | None | Image size, used to specify the image size when the model input shape is not available in the configuration file |
| seed | integer | None | Seed to use to sample the images from the dataset |

A random generator is used to sample the images from the dataset. By default, different images will be selected every time you run the script. If you want to always use the same set of images, then set the seed argument to an integer value. If you use different seed values, different sets of images will be sampled.

We encourage you to run the `test_data_augment.py` script. No extra work is required to use it as it only needs your configuration file. It could prove instrumental in helping you develop effective data augmentation solutions.

</details>
<details open><summary><a href="#7"><b>7. Customizing the data augmentation</b></a></summary><a id="7"></a>

<ul><details open><summary><a href="#7-1">7.1 The Master Data Augmentation (MDA) function</a></summary><a id="7-1"></a>

Every time a new batch of images is received and needs to be augmented before it is presented to the model to train, a function gets called with the `data_augmentation` section of the configuration file passed in argument as a dictionary. The function uses this dictionary to call the specified data augmentation functions, in their order of appearance in the file. Then, it returns the augmented images.

All the data augmentation functions, such as `random_rotation()` or `random_contrast()`, are called by this function. Therefore, we refer to it as the *Master Data Augmentation (MDA)* function.

As an example, assume that your configuration file includes the following `data_augmentation` section:

```yaml
data_augmentation:
   random_flip:
      mode: horizontal_and_vertical
   random_translation:
      width_factor: 0.2
      height_factor: 0.1
   random_contrast:
      factor: 0.5
   random_brightness:
      factor: 0.4
```

When it gets called, the MDA function receives in argument the following Python dictionary:

```python
 config = {
    'random_flip': {'mode': 'horizontal_and_vertical'}},
    'random_translation': {'width_factor': 0.2, 'height_factor': 0.1},
    'random_contrast': {'factor': 0.5}},
    'random_brightness': {'factor': 0.4}}
}
```
The MDA function uses this dictionary to successively call the `random_flip()`, `random_translation()`, `random_contrast()` and `random_brightness()` functions, in this order and with the specified arguments. Then, it returns the augmented images.

</details></ul>
<ul><details open><summary><a href="#7-2">7.2 The MDA function arguments</a></summary><a id="7-2"></a>

Every time a new batch of images is received, the MDA function is called with the following arguments:
- `images`, the images to augment. A tensor with shape [batch_size, image_width, image_height, image_channels].
- `config`, the dictionary created from the `data_augmentation` section of the YAML configuration file.
- `pixels_range`, the range of pixel values of the images. A tuple of 2 floats, such as (0.0, 1.0).
- `batch_info`, information about the current batch of images (explained below). A Tensorflow 4D variable.

The `batch_info` argument has the following elements which are all integers:
- `batch_info[0]` : current batch number since the beginning of the training.
- `batch_info[1]` : current epoch.
- `batch_info[2]` : width of the images of the previous batch.
- `batch_info[3]` : height of the images of the previous batch.

The current epoch can be used to implement *dynamic data augmentation*, i.e. data augmentation that changes during training instead of staying the same from beginning to end. An example will be presented later.

The current batch number, width and height of the images of the previous batch are useful to implement dynamic resizing of images. You can refer to the `random_periodic_resizing` function in the `random_misc.py` package for an example of how they can be used.

</details></ul>
<ul><details open><summary><a href="#7-3">7.3 Using a custom MDA function</a></summary><a id="7-3"></a>

The YAML code below shows how you can use your own MDA function instead of the MDA function that is provided with the Model Zoo.

```yaml
custom_data_augmentation:
    function_name: my_data_augmentation
    config:
        a1:
            a11: v1
            a12: v2
        a2: v2
```

A section called `custom_data_augmentation` is used instead of a `data_augmentation` section. It has 2 attributes:
- `function_name` : the name of the custom MDA function to use.
- `config` : an optional section to pass as a dictionary to the MDA function. If you use it, you can write anything you want in this section as long as you follow the YAML syntax.

In the example above, the `a1`, `a11`, `a12` and `a2` attributes are user-defined attributes that are unknown to the Model Zoo. The following Python dictionary gets passed in argument to `my_data_augmentation()`:

```python
config = {
  'a1': {'a11': v1, 'a12': v2},
  'a2': 'v2'
}
```

</details></ul>
<ul><details open><summary><a href="#7-4">7.4 Writing your own MDA function</a></summary><a id="7-4"></a>

The MDA function that is provided with the Model Zoo is called `data_augmentation()`. The source code is in file *\<MODEL-ZOO-ROOT\>/image_classification/src/data_augmentation/data_augmentation.py*.

In order to create your own MDA function, you need to follow the following rules:
1. The source code of the function is in file *\<MODEL-ZOO-ROOT\>/image_classification/src/data_augmentation/data_augmentation.py*.
2. The arguments of the function are `images`, `config`, `pixels_range` and `batch_info`.
3. The function returns the augmented images.

The MDA function is part of the Tensorflow graph to enable fast execution on GPUs. Therefore, you need to follow the Tensorflow 2.x rules and guidelines to write code that can execute in graph mode. Refer to the Tensorflow documentation for more detail.

You can write and use any number of custom MDA functions. As long as they are placed in the *\<MODEL-ZOO-ROOT\>/image_classification/src/data_augmentation/data_augmentation.py* package, they are all visible to the training script.

</details></ul>
<ul><details open><summary><a href="#7-5">7.5 Progressive learning, an example of custom data augmentation</a></summary><a id="7-5"></a>

In a *Progressive learning* approach, light transformations are applied at the beginning of the training. Then, transformations are made more and more aggressive as the training progresses.

The same transformations may be used from beginning to end but with increasing effects over epochs. For example, a random rotation function may be used with an increasing range of angles. New transformations may be added along the way.

The Python code below is an example of MDA function that implements a progressive learning approach. Note that the `random_flip` function is used for the entire training. The value of its `change_rate` argument is increased over epochs, so more and more images get flipped.

```python
def progressive_dataaug(images, config=None, pixels_range=None, batch_info=None):

    epoch = batch_info[1]
    if epoch < 40:
        images = random_affine.random_flip(
                    images,
                    mode="horizontal_and_vertical",
                    change_rate=0.1)
    elif epoch < 80:
        images = random_affine.random_flip(
                    images,
                    mode="horizontal_and_vertical",
                    change_rate=0.3)
    elif epoch < 120:
        images = random_affine.random_flip(
                    images,
                    mode="horizontal_and_vertical",
                    change_rate=0.5)
    elif epoch < 160:
        images = random_affine.random_flip(
                    images,
                    mode="horizontal_and_vertical",
                    change_rate=0.5)
        images = random_affine.random_translation(
                    images,
                    width_factor=0.1,
                    height_factor=0.1)
        images = random_affine.random_zoom(
                    images,
                    width_factor=0.2)
    else:
        images = random_affine.random_flip(
                    images,
                    mode="horizontal_and_vertical",
                    change_rate=0.5)
        images = random_affine.random_translation(
                    images,
                    width_factor=0.2,
                    height_factor=0.2)
        images = random_affine.random_zoom(
                    images,
                    width_factor=0.4)
        images = random_color.random_contrast(
                    images,
                    factor=0.7,
                    pixels_range=pixels_range)
        images = random_color.random_brightness(
                    images,
                    factor=0.5,
                    pixels_range=pixels_range)
    return images
```

</details></ul>
</details>
<details open><summary><a href="#A"><b>Exhibit A: Data augmentation functions of the random_color.py package</b></a></summary><a id="A"></a>
<ul><details open><summary><a href="#A-1">A.1 random_contrast</a></summary><a id="A-1"></a>

The `random_contrast` function randomly changes the contrast of input images.

| Argument| Default value| Usage |
|:---------|:------|:------|
| `factor` | None |  A float or a tuple of 2 floats, specifies the range of values contrast factors are sampled from (one per image). If a scalar value v is used, it is equivalent to the tuple (-v, v). The contrast of an input image is decreased if the contrast factor is less than 0, increased if the contrast factor is greater than 0, unchanged if the contrast factor is equal to 0.
| `change_rate` | 1.0 |  A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#A-2">A.2 random_brightness</a></summary><a id="A-2"></a>

The `random_brightness` function randomly changes the brightness of input images.

| Argument| Default value| Usage |
|:---------|:------|:------|
| `factor` | None |  A float or a tuple of 2 floats, specifies the range of values brightness factors are sampled from (one per image). If a scalar value v is used, it is equivalent to the tuple (-v, v). The brightness of an input image is decreased if the brightness factor is less than 0, increased if the brightness factor is greater than 0, unchanged if the brightness factor is equal to 0. |
| `change_rate` | 1.0 |  A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#A-3">A.3 random_gamma</a></summary><a id="A-3"></a>

The `random_gamma` function randomly changes the pixels of input images according to the equation "Out = In**gamma".

| Argument| Default value| Usage |
|:---------|:------|:------|
| `gamma` | None | A tuple of 2 floats greater than 0.0, specifies the range of values gamma factors are sampled from (one per image). The output image is darker if the gamma factor is less than 1.0, brighter if the gamma factor is greater than 1.0, unchanged if the gamma factor is equal to 1.0 |
| `change_rate` | 1.0 |  A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#A-4">A.4 random_hue</a></summary><a id="A-4"></a>

The `random_hue` function randomly changes the hue of input RGB images.

Images are first converted to HSV (Hue, Saturation, Value) representation, then a randomly chosen offset is added to the hue channel, and the images are converted back to RGB representation.

This function is not applicable to grayscale images (RGB only).

| Argument| Default value| Usage |
|:---------|:------|:------|
| `delta` | None | A float or a tuple of 2 floats, specifies the range of values the offsets added to the hue channel are sampled from (one per image). If a scalar value v is used, it is equivalent to the tuple (-v, v). |
| `change_rate` | 1.0 |  A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#A-5">A.5 random_saturation</a></summary><a id="A-5"></a>

The `random_saturation` function randomly changes the saturation of input RGB images.

Images are first converted to HSV (Hue, Saturation, Value) representation, then a randomly chosen offset is added to the saturation channel, and the images are converted back to RGB representation.

This function is not applicable to grayscale images (RGB only).

| Argument| Default value| Usage |
|:---------|:------|:------|
| `delta` | None | A float or a tuple of 2 floats, specifies the range of values the offsets added to the saturation channel are sampled from (one per image). If a scalar value v is used, it is equivalent to the tuple (-v, v). |
| `change_rate` | 1.0 |  A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#A-6">A.6 random_value</a></summary><a id="A-6"></a>

The `random_value` function randomly changes the value of input RGB images.

Images are first converted to HSV (Hue, Saturation, Value) representation, then a randomly chosen offset is added to the value channel, and the images are converted back to RGB representation.

This function is not applicable to grayscale images (RGB only).

| Argument| Default value| Usage |
|:---------|:------|:------|
| `delta` | None | A float or a tuple of 2 floats, specifies the range of values the offsets added to the value channels are sampled from (one per image). If a scalar value v is used, it is equivalent to the tuple (-v, v). |
| `change_rate` | 1.0 |  A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#A-7">A.7 random_hsv</a></summary><a id="A-7"></a>

The `random_hsv` function randomly changes the hue, saturation and value of input RGB images. Images are first converted to HSV (Hue, Saturation, Value) representation, then randomly chosen offsets are added to the hue, saturation and value channels. Finally the images are converted back to RGB representation.

This function is not applicable to grayscale images (RGB only).

| Argument| Default value| Usage |
|:---------|:------|:------|
| `delta_hue` | None | A float or a tuple of 2 floats, specifies the range of values the offsets added to the hue channels are sampled from (one per image). If a scalar value v is used, it is equivalent to the tuple (-v, v). |
| `delta_saturation` | None | A float or a tuple of 2 floats, specifies the range of values the offsets added to the saturation channels are sampled from (one per image). If a scalar value v is used, it is equivalent to the tuple (-v, v). |
| `delta_value` | None | A float or a tuple of 2 floats, specifies the range of values the offsets added to the value channels are sampled from (one per image). If a scalar value v is used, it is equivalent to the tuple (-v, v). |
| `change_rate` | None |  A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#A-8">A.8 random_rgb_to_hsv</a></summary><a id="A-8"></a>

The `random_rgb_to_hsv` function randomly converts input RGB images to HSV (Hue, Saturation, Value) representation.

This function is not applicable to grayscale images (RGB only).

| Argument| Default value| Usage |
|:---------|:------|:------|
| `change_rate` | 0.25 |  A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#A-9">A.9 random_rgb_to_grayscale</a></summary><a id="A-9"></a>

The `random_rgb_to_grayscale` function randomly converts input RGB images to grayscale.

| Argument| Default value| Usage |
|:---------|:------|:------|
| `change_rate` | 0.25 |  A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#A-10">A10. random_sharpness</a></summary><a id="A-10"></a>

The `random_sharpness` function randomly increases the sharpness of input images. Use the random_blur() function if you want to decrease the sharpness.

| Argument| Default value| Usage |
|:---------|:------|:------|
| `factor` | None | A float or a tuple of 2 floats greater than or equal to 0, specifies the range of values the sharpness factors are sampled
from (one per image). If a scalar value v is used, it is equivalent to the tuple (0, v). The larger the value of the sharpness factor, the more pronounced the sharpening effect is. If the sharpness factor is equal to 0, the images are unchanged. |
| `change_rate` | 1.0 |  A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#A-11">A11. random_posterize</a></summary><a id="A-11"></a>

The `random_posterize` function randomly reduces the number of bits used for each color channel of input images. Color contraction occurs when the number of bits is reduced.

| Argument| Default value| Usage |
|:---------|:------|:------|
| `bits` | None | A tuple of 2 integers in the interval [1, 8], specifies the range of values the numbers of bits used to encode pixels are sampled from (one per image). The lower the number of bits, the more degraded the image is. |
| `change_rate` | 1.0 | A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#A-12">A.12 random_invert</a></summary><a id="A-12"></a>

The `random_invert` function inverts (negates) all the pixel values of input images.

| Argument| Default value| Usage |
|:---------|:------|:------|
| `change_rate` | 0.25 | A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#A-13">A.13 random_solarize</a></summary><a id="A-13"></a>

The `random_solarize` function randomly solarizes input images. For each image, a threshold value is sampled in the interval [0, 255]. Then, all the pixels that are above the threshold are inverted (negated).

| Argument| Default value| Usage |
|:---------|:------|:------|
| `change_rate` | 0.25 | A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#A-14">A.14 random_equalize</a></summary><a id="A-14"></a>

The `random_equalize` function equalizes the histogram of images by spreading out the highly populated intensity values. It usually increases the global contrast of images, especially when the image is represented by a narrow range of intensity values. It is useful in images with backgrounds and foregrounds that are both bright or both dark. 

| Argument| Default value| Usage |
|:---------|:------|:------|
| `change_rate` | 0.25 | A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#A-15">A.15 random_autocontrast</a></summary><a id="A-15"></a>

The `random_equalize` function maximizes the contrast of input images.

Cutoff percent of the lightest and darkest pixels are first removed from the image, then the image is remapped so that the darkest pixel becomes black (0), and the lightest becomes white (255).
 
| Argument| Default value| Usage |
|:---------|:------|:------|
| `cutoff` | 10 | A positive integer greater than 0, specifies the percentage of pixels to remove on the low and high ends of the pixels histogram. If `cutoff` is equal to 0, the images are unchanged. |
| `change_rate` | 0.25 | A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
</details>
<details open><summary><a href="#B"><b>Exhibit B: Data augmentation functions of the random_misc.py package</b></a></summary><a id="B"></a>
<ul><details open><summary><a href="#B-1">B.1 random_blur</a></summary><a id="B-1"></a>

The `random_blur` function randomly blurs input images using a mean filter. The filter is square with a size that is sampled from a specified range. The larger the filter size, the more pronounced the blur effect is.

| Argument| Default value| Usage |
|:---------|:------|:------|
| `filter_size` | None | A tuple of 2 integers greater than or equal to 1, specifies the range of values the filter sizes are sampled from (one per image). The width and height of the filter are both equal to  `filter_size`. The larger the filter size, the more pronounced the blur effect is. If the filter size is equal to 1, the image is unchanged.   |
| `padding` | 'reflect' | A string, one of 'REFLECT', 'CONSTANT', or 'SYMMETRIC'. The type of padding algorithm to use. |
| `constant_values` | 0.0 | A float or integer, the pad value to use in "CONSTANT" padding mode. |
| `change_rate` | 1.0 | A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#B-2">B.2 random_gaussian_noise</a></summary><a id="B-2"></a>

The `random_gaussian_noise` function adds gaussian noise to input images. The standard deviations of the gaussian distribution are sampled from a specified range. The mean of the distribution is equal to 0.

The function has two modes:
- image mode: a different standard deviation is used for each image of the batch.
- batch mode: the same standard deviation is used for all the images of the batch.

The image mode creates more image diversity, potentially leading to better training results, but run times are longer than in the batch mode.

| Argument| Default value| Usage |
|:---------|:------|:------|
| `stddev` | None | A tuple of 2 floats greater than or equal to 0.0, specifies the range of values the standard deviations of the gaussian distribution are sampled from (one per image). The larger the standard deviation, the larger the amount of noise added to the input image is. If the standard deviation is equal to 0.0, the image is unchanged.|
| `change_rate` | 1.0 | A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |
|  `mode` | "image" | Either "image" or "batch". If set to "image", noise will be sampled using a different standard deviation for each image of the batch. If set to "batch", noise will be sampled using the same standard deviation for all the images of the batch. |

</details></ul>
<ul><details open><summary><a href="#B-3">B.3 random_jpeg_quality</a></summary><a id="B-3"></a>

The `random_jpeg_quality` function randomly changes the JPEG quality of input images.

If the `jpeg_quality` argument is equal to 100, images are unchanged. If it is less than 100, JPEG quality is decreased.

| Argument| Default value| Usage |
|:---------|:------|:------|
| `jpeg_quality` | None | An integer or a tuple of 2 integers in the interval [0, 100], specifies the range of values the JPEG quality factor may take. A lower value means lower quality. If a tuple is used, the values of jpeg_quality will be randomly chosen within the specified range and different images will get different values. If a scalar value v is used, jpeg_quality is equal to v for all the images. |
| `change_rate` | 1.0 | A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
</details>
<details open><summary><a href="#C"><b>Exhibit C: Data augmentation functions of the random_affine.py package</b></a></summary><a id="C"></a>
<ul><details open><summary><a href="#C-1">C.1 random_flip</a></summary><a id="C-1"></a>

The `random_flip` function randomly flips input images horizontally and/or vertically.

| Argument| Default value| Usage |
|:---------|:------|:------|
| `mode` | None | A string, specifies the flip mode. Either 'horizontal', 'vertical' or 'horizontal_and_vertical'. |
| `change_rate` | 0.5 | A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

The default value of `change_rate` is 0.5, meaning that 50% of images are flipped on average. This value generally gives good results although you try to tune it.

</details></ul>
<ul><details open><summary><a href="#C-2">C.2 random_translation</a></summary><a id="C-2"></a>

The `random_translation` function randomly translates input images horizontally and/or vertically.

| Argument| Default value| Usage |
|:---------|:------|:------|
| `width_factor` | None | A float or a tuple of 2 floats, specifies the range of values the horizontal shift factors are sampled from (one per image). If a scalar value v is used, it is equivalent to the tuple (-v, v). A negative factor means shifting the image left, while a positive factor means shifting the image right. For example, width_factor=(-0.2, 0.3) results in an output shifted left by up to 20% or shifted right by up to 30%. |
| `height_factor` | None | A float or a tuple of 2 floats, specifies the range of values the vertical shift factors are sampled from (one per image). If a scalar value v is used, it is equivalent to the tuple (-v, v). A negative factor means shifting the image up, while a positive factor means shifting the image down. For example, height_factor=(-0.2, 0.3) results in an output shifted up by up to 20% or shifted down by up to 30%. |
| `fill_mode` | 'reflect' | Points outside the boundaries of the input are filled according to the given mode. One of {'constant', 'reflect', 'wrap', 'nearest'}. See Tensorflow documentation at https://tensorflow.org for more details. |
| `interpolation` | 'bilinear' | A string, the interpolation method. Supported values: 'nearest', 'bilinear'. |
| `change_rate` | 1.0 | A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#C-3">C.3 random_rotation</a></summary><a id="C-3"></a>

The `random_rotation` function randomly rotates input images clock-wise and counter clock-wise.

| Argument| Default value| Usage |
|:---------|:------|:------|
| `factor` | None | A float or a tuple of 2 floats, specifies the range of values the rotation angles are sampled from (one per image). If a scalar value v is used, it is equivalent to the tuple (-v, v). Rotation angles are in gradients (fractions of 2*pi). A positive angle means rotating counter clock-wise, while a negative angle means rotating clock-wise. For example, `factor`=(-0.2, 0.3) results in an output rotated by a random amount in the range [-20% * 2pi, 30% * 2pi]. |
| `fill_mode` | 'reflect' | Points outside the boundaries of the input are filled according to the given mode. One of {'constant', 'reflect', 'wrap', 'nearest'}. See Tensorflow documentation at https://tensorflow.org for more details. |
| `interpolation` | 'bilinear' | A string, the interpolation method. Supported values: 'nearest', 'bilinear'. |
| `change_rate` | 1.0 | A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#C-4">C.4 random_shear</a></summary><a id="C-4"></a>

The `random_shear` function randomly shears input images.

| Argument| Default value| Usage |
|:---------|:------|:------|
| `factor` | None | A float or a tuple of 2 floats, specifies the range of values the shear angles are sampled from (one per image). If a scalar value v is used, it is equivalent to the tuple (-v, v). Angles are in radians (fractions of 2*pi). For example, factor=(-0.349, 0.785) results in an output sheared by a random angle in the range [-20 degrees, +45 degrees]. |
| `fill_mode` | 'reflect' | Points outside the boundaries of the input are filled according to the given mode. One of {'constant', 'reflect', 'wrap', 'nearest'}. See Tensorflow documentation at https://tensorflow.org for more details. |
| `change_rate` | 1.0 | A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#C-5">C.5 random_shear_x</a></summary><a id="C-5"></a>

The `random_shear_x` function randomly shears input images along the x axis.

| Argument| Default value| Usage |
|:---------|:------|:------|
| `factor` | None | A float or a tuple of 2 floats, specifies the range of values the shear angles are sampled from (one per image). If a scalar value v is used, it is equivalent to the tuple (-v, v). Angles are in radians (fractions of 2*pi). For example, factor=(-0.349, 0.785) results in an output sheared along the x axis by a random angle in the range [-20 degrees, +45 degrees]. |
| `fill_mode` | 'reflect' | Points outside the boundaries of the input are filled according to the given mode. One of {'constant', 'reflect', 'wrap', 'nearest'}. See Tensorflow documentation at https://tensorflow.org for more details. |
| `interpolation` | 'bilinear' | A string, the interpolation method. Supported values: 'nearest', 'bilinear'. |
| `change_rate` | 1.0 | A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#C-6">C.6 random_shear_y</a></summary><a id="C-6"></a>

The `random_shear_y` function randomly shears input images along the y axis.

| Argument| Default value| Usage |
|:---------|:------|:------|
| `factor` | None | A float or a tuple of 2 floats, specifies the range of values the shear angles are sampled from (one per image). If a scalar value v is used, it is equivalent to the tuple (-v, v). Angles are in radians (fractions of 2*pi). For example, factor=(-0.349, 0.785) results in an output sheared along the y axis by a random angle in the range [-20 degrees, +45 degrees]. |
| `fill_mode` | 'reflect' | Points outside the boundaries of the input are filled according to the given mode. One of {'constant', 'reflect', 'wrap', 'nearest'}. See Tensorflow documentation at https://tensorflow.org for more details. |
| `interpolation` | 'bilinear' | A string, the interpolation method. Supported values: 'nearest', 'bilinear'. |
| `change_rate` | 1.0 | A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
<ul><details open><summary><a href="#C-7">C.7 random_zoom</a></summary><a id="C-7"></a>

The `random_zoom` function randomly zooms in/out on each axis of input images.

If `width_factor` and `height_factor` are both set, the images are zoomed in or out on each axis independently, which may result in noticeable distortion. If you want to avoid distortion, only set `width_factor` and the mages will be zoomed by the same amount in both directions.

| Argument| Default value| Usage |
|:---------|:------|:------|
| `width_factor` | None | A float or a tuple of 2 floats, specifies the range of values horizontal zoom factors are sampled from (one per image). If a scalar value v is used, it is equivalent to the tuple (-v, v). Factors are fractions of the width of the image. A positive factor means zooming out, while a negative factor means zooming in. For example, width_factor=(0.2, 0.3) results in an output zoomed out by a random amount in the range [+20%, +30%]. width_factor=(-0.3, -0.2) results in an output zoomed in by a random amount in the range [+20%, +30%]. |
| `height_factor` | None | A float or a tuple of 2 floats, specifies the range of values vertical zoom factors are sampled from (one per image). If a scalar value v is used, it is equivalent to the tuple (-v, v). Factors are fractions of the height of the image. A positive value means zooming out, while a negative value means zooming in. For example, height_factor=(0.2, 0.3) results in an output zoomed out between 20% to 30%. height_factor=(-0.3, -0.2) results in an output zoomed in between 20% to 30%. If `height_factor` is not set, it defaults to None. In this case, images images will be zoomed by the same amounts in both directions and no image distortion will occur. |
| `fill_mode` | 'reflect' | Points outside the boundaries of the input are filled according to the given mode. One of {'constant', 'reflect', 'wrap', 'nearest'}. See Tensorflow documentation at https://tensorflow.org for more details. |
| `interpolation` | 'bilinear' | A string, the interpolation method. Supported values: 'nearest', 'bilinear'. |
| `change_rate` | 1.0 | A float in the interval [0, 1], the number of changed images versus the total number of input images average ratio. For example, if `change_rate` is set to 0.25, 25% of the input images will get changed on average (75% won't get changed). If it is set to 0.0, no images are changed. If it is set to 1.0, all the images are changed. |

</details></ul>
</details>
<details open><summary><a href="#D"><b>Exhibit D: Data augmentation functions of the random_erasing.py package</b></a></summary><a id="D"></a>
<ul><details open><summary><a href="#D-1">D.1 random_rectangle_erasing</a></summary><a id="D-1"></a>

The `random_rectangle_erasing` function randomly erases a number of rectangular areas out of input images and fills the voids with color.

The function has two modes:
- image mode: different sets of random rectangles are erased from the different images of the batch.
- batch mode: the same random set of images is erased from all the images of the batch.

The image mode creates more image diversity, potentially leading to better training results, but run times are longer than in the batch mode.

By default, if no arguments are specified, one random black rectangle is erased from each image. All the rectangles are different (image mode).

| Argument| Default value| Usage |
|:---------|:------|:------|
| `nrec` | 1 | An integer or a tuple of 2 integers, specifies the range of values the numbers of rectangles to erase are sampled from (one number of rectangles per image). If a scalar value v is used, the number of rectangles is equal to v for all the images. |
| `area` | (0.05, 0.4) | A float or a tuple of 2 floats, specifies the range of values the areas of rectangles are sampled from (one area per rectangle). If a scalar value v is used, the area of rectangles is equal to v for all the images. Area values are fractions of the image area. Therefore, they must be in the interval [0, 1]. |
| `wh_ratio` | (0.3, 2.0) | A float or a tuple of 2 floats, specifies the range of values the width/height ratio of rectangles are sampled from (one ratio per rectangle). If a scalar value v is used, the ratio is equal to v for all the images. |
| `fill_method` | 'random' | A string, one of {'uniform', 'random', 'mosaic'}. If the method is 'uniform', all the rectangles in all the images are filled with the same color specified using the `color` argument. If the fill method is 'random', each rectangle is filled with a randomly chosen RGB color if the input images are RGB images or a randomly chosen shade of gray if the input images are grayscale (all the rectangles will have different colors). If the fill method is 'mosaic', rectangles are filled with random pixels. |
| `color` | None | A tuple of 3 integers in the interval [0, 255] if the images are RGB images or an integer in the interval [0, 255] if the images are grayscale images, specifies the color to use to fill the rectangles erased from the images. This argument is only  applicable to the 'uniform' fill method. |
| `change_rate` | 1.0 | A float in the interval [0, 1], controls the number of changed images/total number of images average ratio. The higher the value, the larger the average number of images that will get changed. If set to 0.0, no images will get changed. If set to 1.0, all images will get changed. |
| `mode` | 'image' | Either "image" or "batch". If set to "image", different sets of rectangles are erased from the different images of the batch. If set to "batch", the same set of rectangles is erased from all the images of the batch. |

</details></ul>
<ul><details open><summary><a href="#D-2">D.2 random_grid_cell_erasing</a></summary><a id="D-2"></a>

The `random_grid_cell_erasing` function places a grid of cells on top of input images and randomly erases some of the cells, filling the voids with color. By default, all the erased cells are black.

| Argument| Default value| Usage |
|:---------|:------|:------|
| `ncells_x` | 5 | A positive integer, specifies the number of cells to create along the x axis. |
| `ncells_y` | 5 | A positive integer, specifies the number of cells to create along the y axis. |
| `fill_method` | 'uniform' | A string, one of {'uniform', 'random', 'mosaic'}. If the method is 'uniform', all the cells in all the images are filled with the same color specified using the `color` argument. If the fill method is 'random', each cell is filled with a randomly chosen RGB color if the input images are RGB images or a randomly chosen shade of gray if the input images are grayscale (all the cells will have different colors). If the fill method is 'mosaic', cells are filled with random pixels. |
| `erasing_prob` | 0.2 | A float in the interval [0, 1], specifies the probability that a cell gets erased. The larger the value of this argument, the larger the number of cells that get erased on average. |
| `change_rate` | 1.0 |  A float in the interval [0, 1], controls the number of changed images/total number of images average ratio. The higher the value, the larger the average number of images that will get changed. If set to 0.0, no images will get changed. If set to 1.0, all images will get changed. |

</details></ul>
</details>
