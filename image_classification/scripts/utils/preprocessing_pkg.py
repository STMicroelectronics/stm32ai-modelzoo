# /*---------------------------------------------------------------------------------------------
#  * Copyright 2019 The TensorFlow Authors. 
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
"""Keras image preprocessing layers."""

# pylint: disable=g-classes-have-attributes
# pylint: disable=g-direct-tensorflow-import

from tensorflow import keras
from keras import backend
from keras.engine import base_layer
from keras.engine import base_preprocessing_layer
from keras.utils import control_flow_util
import numpy as np
import tensorflow.compat.v2 as tf
from tensorflow.python.util.tf_export import keras_export

ResizeMethod = tf.image.ResizeMethod

_RESIZE_METHODS = {
    'bilinear': ResizeMethod.BILINEAR,
    'nearest': ResizeMethod.NEAREST_NEIGHBOR,
    'bicubic': ResizeMethod.BICUBIC,
    'area': ResizeMethod.AREA,
    'lanczos3': ResizeMethod.LANCZOS3,
    'lanczos5': ResizeMethod.LANCZOS5,
    'gaussian': ResizeMethod.GAUSSIAN,
    'mitchellcubic': ResizeMethod.MITCHELLCUBIC
}

H_AXIS = -3
W_AXIS = -2


def check_fill_mode_and_interpolation(fill_mode, interpolation):
    if fill_mode not in {'reflect', 'wrap', 'constant', 'nearest'}:
        raise NotImplementedError(
            'Unknown `fill_mode` {}. Only `reflect`, `wrap`, '
            '`constant` and `nearest` are supported.'.format(fill_mode))
    if interpolation not in {'nearest', 'bilinear'}:
        raise NotImplementedError('Unknown `interpolation` {}. Only `nearest` and '
                                  '`bilinear` are supported.'.format(interpolation))


HORIZONTAL = 'horizontal'
VERTICAL = 'vertical'
HORIZONTAL_AND_VERTICAL = 'horizontal_and_vertical'


def transform(images,
              transforms,
              fill_mode='reflect',
              fill_value=0.0,
              interpolation='bilinear',
              output_shape=None,
              name=None):
    """
  Applies the given transform(s) to the image(s).
  Args:
    images: A tensor of shape
      `(num_images, num_rows, num_columns, num_channels)` (NHWC). The rank must
      be statically known (the shape is not `TensorShape(None)`).
    transforms: Projective transform matrix/matrices. A vector of length 8 or
      tensor of size N x 8. If one row of transforms is [a0, a1, a2, b0, b1, b2,
      c0, c1], then it maps the *output* point `(x, y)` to a transformed *input*
      point `(x', y') = ((a0 x + a1 y + a2) / k, (b0 x + b1 y + b2) / k)`, where
      `k = c0 x + c1 y + 1`. The transforms are *inverted* compared to the
      transform mapping input points to output points. Note that gradients are
      not backpropagated into transformation parameters.
    fill_mode: Points outside the boundaries of the input are filled according
      to the given mode (one of `{"constant", "reflect", "wrap", "nearest"}`).
    fill_value: a float represents the value to be filled outside the boundaries
      when `fill_mode="constant"`.
    interpolation: Interpolation mode. Supported values: `"nearest"`,
      `"bilinear"`.
    output_shape: Output dimension after the transform, `[height, width]`.
      If `None`, output is the same size as input image.
    name: The name of the op.
  Fill mode behavior for each valid value is as follows:
  - reflect (d c b a | a b c d | d c b a)
  The input is extended by reflecting about the edge of the last pixel.
  - constant (k k k k | a b c d | k k k k)
  The input is extended by filling all
  values beyond the edge with the same constant value k = 0.
  - wrap (a b c d | a b c d | a b c d)
  The input is extended by wrapping around to the opposite edge.
  - nearest (a a a a | a b c d | d d d d)
  The input is extended by the nearest pixel.
  Input shape:
    4D tensor with shape: `(samples, height, width, channels)`,
      in `"channels_last"` format.
  Output shape:
    4D tensor with shape: `(samples, height, width, channels)`,
      in `"channels_last"` format.
  Returns:
    Image(s) with the same type and shape as `images`, with the given
    transform(s) applied. Transformed coordinates outside of the input image
    will be filled with zeros.
  Raises:
    TypeError: If `image` is an invalid type.
    ValueError: If output shape is not 1-D int32 Tensor.
    """

    with backend.name_scope(name or 'transform'):
        if output_shape is None:
            output_shape = tf.shape(images)[1:3]
            if not tf.executing_eagerly():
                output_shape_value = tf.get_static_value(output_shape)
                if output_shape_value is not None:
                    output_shape = output_shape_value

    output_shape = tf.convert_to_tensor(
        output_shape, tf.int32, name='output_shape')

    if not output_shape.get_shape().is_compatible_with([2]):
        raise ValueError('output_shape must be a 1-D Tensor of 2 elements: '
                         'new_height, new_width, instead got '
                         '{}'.format(output_shape))

    fill_value = tf.convert_to_tensor(
        fill_value, tf.float32, name='fill_value')

    return tf.raw_ops.ImageProjectiveTransformV3(
        images=images,
        output_shape=output_shape,
        fill_value=fill_value,
        transforms=transforms,
        fill_mode=fill_mode.upper(),
        interpolation=interpolation.upper())


def get_shear_matrix(angles, image_height, image_width, name=None):
    """
  Returns projective transform(s) for the given angle(s).
  Args:
    angles: A scalar angle to shear all images by, or (for batches of images) a
      vector with an angle to shear each image in the batch. The rank must be
      statically known (the shape is not `TensorShape(None)`).
    image_height: Height of the image(s) to be transformed.
    image_width: Width of the image(s) to be transformed.
    name: The name of the op.
  Returns:
    A tensor of shape (num_images, 8). Projective transforms which can be given
      to operation `image_projective_transform_v2`. If one row of transforms is
       [a0, a1, a2, b0, b1, b2, c0, c1], then it maps the *output* point
       `(x, y)` to a transformed *input* point
       `(x', y') = ((a0 x + a1 y + a2) / k, (b0 x + b1 y + b2) / k)`,
       where `k = c0 x + c1 y + 1`.
    """

    with backend.name_scope(name or 'shear_matrix'):
        num_angles = tf.shape(angles)[0]
        x_offset = tf.zeros(num_angles, dtype=tf.float32)
        y_offset = tf.zeros(num_angles, dtype=tf.float32)

        matrix = tf.concat(
            values=[
                tf.ones((num_angles, 1), tf.float32),
                -tf.sin(angles)[:, None],
                x_offset[:, None],
                tf.zeros((num_angles, 1), tf.float32),
                tf.cos(angles)[:, None],
                y_offset[:, None],
                tf.zeros((num_angles, 2), tf.float32),
            ],
            axis=1)

        return matrix


@keras_export('keras.layers.RandomShear',
              'keras.layers.experimental.preprocessing.RandomShear')
class RandomShear(base_layer.Layer):
    """
  A preprocessing layer which randomly shears images during training.
  This layer will apply random shears to each image, filling empty space
  according to `fill_mode`.
  By default, random shears are only applied during training.
  At inference time, the layer does nothing. If you need to apply random
  shears at inference time, set `training` to True when calling the layer.
  For an overview and full list of preprocessing layers, see the preprocessing
  [guide](https://www.tensorflow.org/guide/keras/preprocessing_layers).
  Input shape:
    3D (unbatched) or 4D (batched) tensor with shape:
    `(..., height, width, channels)`, in `"channels_last"` format
  Output shape:
    3D (unbatched) or 4D (batched) tensor with shape:
    `(..., height, width, channels)`, in `"channels_last"` format
  Attributes:
    factor: a float represented as fraction of 2 Pi, or a tuple of size 2
      representing lower and upper bound for rotating clockwise and
      counter-clockwise. A positive values means rotating counter clock-wise,
      while a negative value means clock-wise. When represented as a single
      float, this value is used for both the upper and lower bound. For
      instance, `factor=(-0.2, 0.3)` results in an output rotation by a random
      amount in the range `[-20% * 2pi, 30% * 2pi]`. `factor=0.2` results in an
      output rotating by a random amount in the range `[-20% * 2pi, 20% * 2pi]`.
    fill_mode: Points outside the boundaries of the input are filled according
      to the given mode (one of `{"constant", "reflect", "wrap", "nearest"}`).
      - *reflect*: `(d c b a | a b c d | d c b a)` The input is extended by
        reflecting about the edge of the last pixel.
      - *constant*: `(k k k k | a b c d | k k k k)` The input is extended by
        filling all values beyond the edge with the same constant value k = 0.
      - *wrap*: `(a b c d | a b c d | a b c d)` The input is extended by
        wrapping around to the opposite edge.
      - *nearest*: `(a a a a | a b c d | d d d d)` The input is extended by the
        nearest pixel.
    interpolation: Interpolation mode. Supported values: `"nearest"`,
      `"bilinear"`.
    seed: Integer. Used to create a random seed.
    fill_value: a float represents the value to be filled outside the boundaries
      when `fill_mode="constant"`.
    """

    def __init__(self,
                 factor,
                 fill_mode='reflect',
                 interpolation='bilinear',
                 seed=None,
                 fill_value=0.0,
                 **kwargs):
        base_preprocessing_layer.keras_kpl_gauge.get_cell(
            'RandomShear').set(True)
        super(RandomShear, self).__init__(**kwargs)
        self.factor = factor
        if isinstance(factor, (tuple, list)):
            self.lower = factor[0]
            self.upper = factor[1]
        else:
            self.lower = -factor
            self.upper = factor
        if self.upper < self.lower:
            raise ValueError(
                'Factor cannot have negative values, got {}'.format(factor))
        check_fill_mode_and_interpolation(fill_mode, interpolation)
        self.fill_mode = fill_mode
        self.fill_value = fill_value
        self.interpolation = interpolation
        self.seed = seed
        self._random_generator = backend.RandomGenerator(
            seed, force_generator=True)

    def call(self, inputs, training=True):
        if training is None:
            training = backend.learning_phase()

        inputs = tf.convert_to_tensor(inputs)
        original_shape = inputs.shape
        unbatched = inputs.shape.rank == 3
        # The transform op only accepts rank 4 inputs, so if we have an unbatched
        # image, we need to temporarily expand dims to a batch.
        if unbatched:
            inputs = tf.expand_dims(inputs, 0)

        def random_sheared_inputs():
            """Rotated inputs with random ops."""
            inputs_shape = tf.shape(inputs)
            batch_size = inputs_shape[0]
            img_hd = tf.cast(inputs_shape[H_AXIS], tf.float32)
            img_wd = tf.cast(inputs_shape[W_AXIS], tf.float32)

            min_angle = self.lower * 2. * np.pi
            max_angle = self.upper * 2. * np.pi

            angles = self._random_generator.random_uniform(
                shape=[batch_size], minval=min_angle, maxval=max_angle)

            return transform(
                inputs,
                get_shear_matrix(angles, img_hd, img_wd),
                fill_mode=self.fill_mode,
                fill_value=self.fill_value,
                interpolation=self.interpolation)

        output = control_flow_util.smart_cond(
            training, random_sheared_inputs, lambda: inputs)

        if unbatched:
            output = tf.squeeze(output, 0)
        output.set_shape(original_shape)
        return output

    def compute_output_shape(self, input_shape):
        return input_shape

    def get_config(self):
        config = {
            'factor': self.factor,
            'fill_mode': self.fill_mode,
            'fill_value': self.fill_value,
            'interpolation': self.interpolation,
            'seed': self.seed,
        }
        base_config = super(RandomShear, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))


@keras_export('keras.layers.RandomBrightness',
              'keras.layers.experimental.preprocessing.RandomBrightness')
class RandomBrightness(base_layer.Layer):
    """
  A preprocessing layer which randomly adjusts brightness during training.
  This layer will randomly adjust the brightness of an image or images by a random
  factor. brightness is adjusted independently for each channel of each image
  during training.
  For each channel, this layer computes the mean of the image pixels in the
  channel and then adjusts each component `x` of each pixel to
  `(x - mean) * brightness + mean`.
  For an overview and full list of preprocessing layers, see the preprocessing
  [guide](https://www.tensorflow.org/guide/keras/preprocessing_layers).
  Input shape:
    3D (unbatched) or 4D (batched) tensor with shape:
    `(..., height, width, channels)`, in `"channels_last"` format.
  Output shape:
    3D (unbatched) or 4D (batched) tensor with shape:
    `(..., height, width, channels)`, in `"channels_last"` format.
  Attributes:
    factor: a positive float represented as fraction of value, or a tuple of
      size 2 representing lower and upper bound. When represented as a single
      float, lower = upper. The brightness factor will be randomly picked between
      `[1.0 - lower, 1.0 + upper]`.
    seed: Integer. Used to create a random seed.
    """

    def __init__(self, max_delta, seed=None, **kwargs):
        base_preprocessing_layer.keras_kpl_gauge.get_cell(
            'RandomBrightness').set(True)
        super(RandomBrightness, self).__init__(**kwargs)

        if isinstance(max_delta, (tuple, list)):
            raise ValueError(
                'Expecting single value for argument max_delta, got {}'.format(max_delta))
        if max_delta < 0.:
            raise ValueError(
                'Argument max_delta cannot have negative values, got {}'.format(max_delta))

        self.max_delta = max_delta
        self.seed = seed
        self._random_generator = backend.RandomGenerator(
            seed, force_generator=True)

    def call(self, inputs, training=True):

        if training is None:
            training = backend.learning_phase()

        def random_brightened_inputs():
            seed = self._random_generator.make_seed_for_stateless_op()
            if seed is not None:
                return tf.image.stateless_random_brightness(
                    inputs, self.max_delta, seed=seed)
            else:
                return tf.image.random_brightness(
                    inputs, self.max_delta,
                    seed=self._random_generator.make_legacy_seed())

        output = control_flow_util.smart_cond(training, random_brightened_inputs,
                                              lambda: inputs)
        output.set_shape(inputs.shape)
        return output

    def compute_output_shape(self, input_shape):
        return input_shape

    def get_config(self):
        config = {
            'max_delta': self.max_delta,
            'seed': self.seed,
        }
        base_config = super(RandomBrightness, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))


@keras_export('keras.layers.RandomHue',
              'keras.layers.experimental.preprocessing.RandomHue')
class RandomHue(base_layer.Layer):
    """
  A preprocessing layer which randomly adjusts hue during training.
  This layer will randomly adjust the hue of an image or images by a random
  factor. hue is adjusted independently for each channel of each image
  during training.
  For each channel, this layer computes the mean of the image pixels in the
  channel and then adjusts each component `x` of each pixel to
  `(x - mean) * hue + mean`.
  For an overview and full list of preprocessing layers, see the preprocessing
  [guide](https://www.tensorflow.org/guide/keras/preprocessing_layers).
  Input shape:
    3D (unbatched) or 4D (batched) tensor with shape:
    `(..., height, width, channels)`, in `"channels_last"` format.
  Output shape:
    3D (unbatched) or 4D (batched) tensor with shape:
    `(..., height, width, channels)`, in `"channels_last"` format.
  Attributes:
    factor: a positive float represented as fraction of value, or a tuple of
      size 2 representing lower and upper bound. When represented as a single
      float, lower = upper. The hue factor will be randomly picked between
      `[1.0 - lower, 1.0 + upper]`.
    seed: Integer. Used to create a random seed.
    """

    def __init__(self, max_delta, seed=None, **kwargs):
        base_preprocessing_layer.keras_kpl_gauge.get_cell(
            'RandomHue').set(True)
        super(RandomHue, self).__init__(**kwargs)
        self.max_delta = max_delta

        if isinstance(self.max_delta, (tuple, list)):
            raise ValueError(
                'Expecting single value for argument max_delta, got {}'.format(max_delta))

        if self.max_delta < 0. or max_delta > 0.5:
            raise ValueError(
                'Argument max_delta must in the interval [0, 0.5], got {}'.format(max_delta))
        self.seed = seed
        self._random_generator = backend.RandomGenerator(
            seed, force_generator=True)

    def call(self, inputs, training=True):

        if training is None:
            training = backend.learning_phase()

        def random_hued_inputs():
            seed = self._random_generator.make_seed_for_stateless_op()
            if seed is not None:
                return tf.image.stateless_random_hue(
                    inputs, self.max_delta, seed=seed)
            else:
                return tf.image.random_hue(
                    inputs, self.max_delta,
                    seed=self._random_generator.make_legacy_seed())

        output = control_flow_util.smart_cond(training, random_hued_inputs,
                                              lambda: inputs)
        output.set_shape(inputs.shape)
        return output

    def compute_output_shape(self, input_shape):
        return input_shape

    def get_config(self):
        config = {
            'max_delta': self.max_delta,
            'seed': self.seed,
        }
        base_config = super(RandomHue, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))


@keras_export('keras.layers.RandomSaturation',
              'keras.layers.experimental.preprocessing.RandomSaturation')
class RandomSaturation(base_layer.Layer):
    """
  A preprocessing layer which randomly adjusts hue during training.
  This layer will randomly adjust the hue of an image or images by a random
  factor. hue is adjusted independently for each channel of each image
  during training.
  For each channel, this layer computes the mean of the image pixels in the
  channel and then adjusts each component `x` of each pixel to
  `(x - mean) * hue + mean`.
  For an overview and full list of preprocessing layers, see the preprocessing
  [guide](https://www.tensorflow.org/guide/keras/preprocessing_layers).
  Input shape:
    3D (unbatched) or 4D (batched) tensor with shape:
    `(..., height, width, channels)`, in `"channels_last"` format.
  Output shape:
    3D (unbatched) or 4D (batched) tensor with shape:
    `(..., height, width, channels)`, in `"channels_last"` format.
  Attributes:
    factor: a positive float represented as fraction of value, or a tuple of
      size 2 representing lower and upper bound. When represented as a single
      float, lower = upper. The hue factor will be randomly picked between
      `[1.0 - lower, 1.0 + upper]`.
    seed: Integer. Used to create a random seed.
    """

    def __init__(self, lower, upper, seed=None, **kwargs):
        base_preprocessing_layer.keras_kpl_gauge.get_cell(
            'RandomSaturation').set(True)
        super(RandomSaturation, self).__init__(**kwargs)

        if lower < 0:
            raise ValueError(
                'Argument lower must be greater or equal to 0, got {}'.format(lower))
        if upper <= lower:
            raise ValueError(
                'Argument upper must be greater than lower, got upper={} and lower={}'.format(upper, lower))

        self.lower = lower
        self.upper = upper
        self.seed = seed
        self._random_generator = backend.RandomGenerator(
            seed, force_generator=True)

    def call(self, inputs, training=True):

        if training is None:
            training = backend.learning_phase()

        def random_saturated_inputs():
            seed = self._random_generator.make_seed_for_stateless_op()
            if seed is not None:
                return tf.image.stateless_random_saturation(
                    inputs, self.lower, self.upper, seed=seed)
            else:
                return tf.image.random_saturation(
                    inputs, self.lower, self.upper,
                    seed=self._random_generator.make_legacy_seed())

        output = control_flow_util.smart_cond(training, random_saturated_inputs,
                                              lambda: inputs)
        output.set_shape(inputs.shape)
        return output

    def compute_output_shape(self, input_shape):
        return input_shape

    def get_config(self):
        config = {
            'lower': self.lower,
            'upper': self.upper,
            'seed': self.seed,
        }
        base_config = super(RandomSaturation, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))
