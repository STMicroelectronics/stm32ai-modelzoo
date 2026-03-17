# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf

def check_fill_and_interpolation(fill_mode, interpolation, fill_value, function_name=None):
  """
  Function checking fill mode and value and interpolation method for a given augmentation function.
  Raise an error if parameter value is not allowed
  
    Args:
        fill_mode (str): fill mode method in tensorflow keras ("wrap", "nearest"...)
        interpolation (str): interpolation method. Support "nearest" and "bilinear"
        fill_value (float): pixel value in fill mode
        function_name (str): augmentation function name
    
    Returns:   
  """
  if fill_mode not in ("reflect", "wrap", "constant", "nearest"):
    raise ValueError(
        f"Argument `fill_mode` of function `{function_name}`: supported values are 'reflect', "
        f"'wrap', 'constant' and 'nearest'. Received {fill_mode}")
        
  if interpolation not in ("nearest", "bilinear"):
    raise ValueError(
         f"Argument `interpolation` of function `{function_name}`: supported values "
         f"are 'nearest' and 'bilinear'. Received {interpolation}")
       
  if type(fill_value) not in (int, float) or fill_value < -1.:
    raise ValueError(
         f"Argument `fill_value` of function `{function_name}`: expecting float values "
         f"greater than or equal to -1. Received {fill_value}")

def generate_coordinates(tensor_shape):
    """
    Create a list of indices for each dimension of the tensor
    
        Args:
            tensor_shape (tuple): tuple of 4 elements for all dimensions including batch
        Returns:
            a tf.Tensor with the generated coordinates
    """
    indices = [tf.range(tensor_shape[0]),tf.range(tensor_shape[1]),tf.range(tensor_shape[2]),tf.range(tensor_shape[3])]

    # Use tf.meshgrid to generate the grid of coordinates
    coordinates = tf.stack(tf.meshgrid(indices[0],indices[1],indices[2],indices[3],indexing='ij'), axis=-1) # INT32
    coordinates = tf.reshape(coordinates,[-1,tensor_shape[1]*tensor_shape[2]*tensor_shape[3],4]) # (batch, width*height*channel, 2) INT32
    coordinates = tf.cast(coordinates,tf.float32)

    return coordinates # shape: (batch, width*height*channel, 4) FLOAT32

def image_projective_transform(images, output_shape, fill_value, transforms, fill_mode, interpolation):
    """
    This function is here because tf.raw_ops.ImageProjectiveTransformV3() is not compatible with XLA_GPU compilation while this function works on GPU.
    Definition :
        If one row of transforms is [a0, a1, a2, b0, b1, b2, c0, c1], then it maps the output point (x, y) to a transformed input point
        (x', y') = ((a0 x + a1 y + a2) / k, (b0 x + b1 y + b2) / k), where k = c0 x + c1 y + 1.
        If the transformed point lays outside of the input image, the output pixel is set to fill_value.
     
    The function returns the transformed image.

        Args:
            images (tf.Tensor): batch of input images
            output_shape (tuple): shape of the output. Not used so far
            fill_value (float): filled pixel value
            transforms (np.array): transformation matrix to be applied on image
            fill_mode: method for filling when image is augmented ("wrap", "reflect"...)
            interpolation: interpolation method such as "nearest" or "bilinear"
        Returns: 
            images after transformation (tf.Tensor)
    """

    # Definition of a0, a1, a2, b0, b1, b2, c0 and c1 variables, shape: (batch, ) FLOAT32
    (a0, a1, a2, b0, b1, b2, c0, c1) = (transforms[:,0][...,None],
                                        transforms[:,1][...,None],
                                        transforms[:,2][...,None],
                                        transforms[:,3][...,None],
                                        transforms[:,4][...,None],
                                        transforms[:,5][...,None],
                                        transforms[:,6][...,None],
                                        transforms[:,7][...,None])

    # Get the shape of the input batch of images
    im_shape = tf.shape(images) # shape: (4,) INT32

    # Creation of the Tensor containing the coordinates of each pixel in the batch of images
    init_coordinates = generate_coordinates(im_shape) # shape: (batch, width*height*channel, 4) FLOAT32

    b = init_coordinates[:,:,0] # shape: (batch, width*height*channel) FLOAT32
    x = init_coordinates[:,:,1] # shape: (batch, width*height*channel) FLOAT32
    y = init_coordinates[:,:,2] # shape: (batch, width*height*channel) FLOAT32
    c = init_coordinates[:,:,3] # shape: (batch, width*height*channel) FLOAT32

    k = c1*x + c0*y + 1         # shape: (batch, width*height*channel) FLOAT32

    (x_prime, y_prime) = ((b1 * x + b0 * y + b2) / k, (a1 * x + a0 * y + a2) / k) # tuple of shape: (batch, width*height*channel) FLOAT32

    if fill_mode=='reflect'.upper() or fill_mode=='wrap'.upper():
        
        x_prime = tf.math.floormod(x_prime,tf.cast(im_shape[1]-1,tf.float32)) # shape: (batch, width*height*channel) FLOAT32
        y_prime = tf.math.floormod(y_prime,tf.cast(im_shape[2]-1,tf.float32)) # shape: (batch, width*height*channel) FLOAT32

    trans_coordinates = tf.stack([b,x_prime,y_prime,c],axis=-1) # shape: (batch, width*height*channel, 4) FLOAT32
    trans_coordinates = tf.cast(trans_coordinates,tf.int32)     # shape: (batch, width*height*channel, 4) INT32
    trans_coordinates = tf.reshape(trans_coordinates,[-1,4])    # shape: (batch*width*height*channel, 4) INT32

    ll_x = trans_coordinates[:,1]>=0               # shape: (batch*width*height*channel) BOOL
    ul_x = trans_coordinates[:,1]<=(im_shape[1]-1) # shape: (batch*width*height*channel) BOOL

    ll_y = trans_coordinates[:,2]>=0               # shape: (batch*width*height*channel) BOOL
    ul_y = trans_coordinates[:,2]<=(im_shape[2]-1) # shape: (batch*width*height*channel) BOOL

    xbmask = tf.logical_and(ll_x,ul_x)     # shape: (batch*width*height*channel) BOOL
    ybmask = tf.logical_and(ll_y,ul_y)     # shape: (batch*width*height*channel) BOOL
    bmask  = tf.logical_and(xbmask,ybmask) # shape: (batch*width*height*channel) BOOL

    # Create a mask for the out of bound coordinates fill the final images with fill_values
    mask = tf.cast(bmask,dtype=trans_coordinates.dtype) # shape: (batch*width*height*channel) INT32

    trans_coordinates *= mask[...,None]                 # shape: (batch*width*height*channel, 4) INT32

    mask = tf.cast(bmask,dtype=images.dtype)            # shape: (batch*width*height*channel) IMAGES_DTYPE

    mask = tf.reshape(mask,im_shape)                    # shape: (batch, width, height, channel) IMAGES_DTYPE

    fill_mask = (1-mask)*tf.cast(fill_value,dtype=images.dtype) # shape: (batch, width, height, channel) IMAGES_DTYPE
    
    # Gather pixels that are located in the original Tensor with the help of the transformed coordinates to form the new Tensor
    transformed_image = tf.gather_nd(images,trans_coordinates) # shape: (batch*width*height*channel) FLOAT32

    transformed_image = tf.reshape(transformed_image,im_shape) # shape: (batch, width, height, channel) FLOAT32

    transformed_image = transformed_image*mask + fill_mask     # shape: (batch, width, height, channel) FLOAT32
   
    return transformed_image
         

def transform_images(
            images,
            transforms,
            fill_mode='reflect',
            fill_value=0.0,
            interpolation='bilinear'):
    """
    The function returns the transformed images.

        Args:
            images (tf.Tensor): batch of input images
            transforms (np.array): transformation matrix to be applied on image
            fill_mode: method for filling when image is augmented ("wrap", "reflect"...)
            fill_value (float): filled pixel value
            interpolation: interpolation method such as "nearest" or "bilinear"
        Returns: 
            images after transformation (tf.Tensor)
    """

    output_shape = tf.shape(images)[1:3]

    return image_projective_transform(
            images=images,
            output_shape=output_shape,
            fill_value=fill_value,
            transforms=transforms,
            fill_mode=fill_mode.upper(),
            interpolation=interpolation.upper())

######### Legacy Code #########
# return tf.raw_ops.ImageProjectiveTransformV3(
#         images=images,
#         output_shape=output_shape,
#         fill_value=fill_value,
#         transforms=transforms,
#         fill_mode=fill_mode.upper(),
#         interpolation=interpolation.upper())


def get_flip_matrix(batch_size, width, height, mode):

    """
    This function creates a batch of flipping matrices
    
        Args:
            batch_size (int): size of input batch of images
            width (float): normalized image width
            height (float): normailzed image height
            mode (str): flipping direction, "horizontal", "vertical" or by default both
        Returns:
            batch of flipping matrices (tf.Tensor)
    """

    if mode == "horizontal":
        # Flip all the images horizontally
        matrix = tf.tile([-1, 0, (width-1), 0, 1, 0, 0, 0], [batch_size])
        matrix = tf.reshape(matrix, [batch_size, 8])
    elif mode == "vertical":
        # Flip all the images vertically
        matrix = tf.tile([1, 0, 0, 0, -1, (height-1), 0, 0], [batch_size])
        matrix = tf.reshape(matrix, [batch_size, 8])
    else:
        # Randomly flip images horizontally, vertically or both
        flips = [[-1, 0, (width-1),  0,  1,          0, 0, 0],
                 [ 1, 0,         0,  0, -1, (height-1), 0, 0],
                 [-1, 0, (width-1),  0, -1, (height-1), 0, 0]]
        select = tf.random.uniform([batch_size], minval=0, maxval=3, dtype=tf.int32)
        matrix = tf.gather(flips, select)

    return tf.cast(matrix, tf.float32)


def get_translation_matrix(translations):
    """
    This function creates a batch of translation matrices given 
    a batch of x and y translation fractions.
    Translation fractions are independent from each other 
    and may be different from one batch item to another.
    
    The translation matrix is:
    [[ 1,   0,  -x_translation],
     [ 0,   1,  -y_translation],
     [ 0,   1,   0            ]]
     
    The function returns the following representation of the matrix:
         [ 1, 0, -x_translation, 0, 1, -y_translation, 0, 1]
    with entry [2, 2] being implicit and equal to 1.

        Args: 
            translations (tuple): normalized translation values
        Returns:
            tf.Tensor with translation matrix    
    """
    
    num_translations = tf.shape(translations)[0]
    matrix = tf.concat([
                tf.ones((num_translations, 1), tf.float32),
                tf.zeros((num_translations, 1), tf.float32),
                -translations[:, 0, None],
                tf.zeros((num_translations, 1), tf.float32),
                tf.ones((num_translations, 1), tf.float32),
                -translations[:, 1, None],
                tf.zeros((num_translations, 2), tf.float32),
                ],
                axis=1)
    return matrix


def get_rotation_matrix(angles, width, height):
    """
    This function creates a batch of rotation matrices given a batch of angles.
    Angles are independent from each other and may be different from
    one batch item to another.
    
    The rotation matrix is:
        [ cos(angle)  -sin(angle), x_offset]
        [ sin(angle),  cos(angle), y_offset]
        [ 0,           0,          1       ]
    x_offset and y_offset are calculated from the angles and image dimensions.

    The function returns the following representation of the matrix:
         [ cos(angle), -sin(angle), x_offset, sin(angle), cos(angle), 0, 0 ]
    with entry [2, 2] being implicit and equal to 1.

        Args:
            angles (list(float)): batch of angles fow which we compute a rotation matrix
            width (float): normalized width of input images
            height (float): normalized height of input images
        Returns:
            (tf.Tensor), rotation matrices
    """

    width = tf.cast(width, tf.float32)
    height = tf.cast(height, tf.float32)
    
    num_angles = tf.shape(angles)[0]
    x_offset = ((width - 1) - (tf.cos(angles) * (width - 1) - tf.sin(angles) * (height - 1))) / 2.0
    y_offset = ((height - 1) - (tf.sin(angles) * (width - 1) + tf.cos(angles) * (height - 1))) / 2.0
    
    matrix = tf.concat([
                tf.cos(angles)[:, None],
                -tf.sin(angles)[:, None],
                x_offset[:, None],
                tf.sin(angles)[:, None],
                tf.cos(angles)[:, None],
                y_offset[:, None],
                tf.zeros((num_angles, 2), tf.float32)
                ],
                axis=1)

    return matrix


def get_shear_matrix(angles, axis):
    """
    This function creates a batch of shearing matrices given a batch 
    of angles. Angles are independent from each other and may be different
    from one batch item to another.
    
    The shear matrix along the x axis only is:
        [ 1  -sin(angle), 0 ]
        [ 0,  1,          0 ]
        [ 0,  0,          1 ]
    
    The shear matrix along the y axis only is:
        [ 1,           0, 0 ]
        [ cos(angle),  1, 0 ]
        [ 0,           0, 1 ]
    The shear matrix along both x and y axis is:
        [ 1  -sin(angle),  0 ]
        [ 0,  cos(angle),  0 ]
        [ 0,  0,           1 ]

    The function returns the following representation of the 
    shear matrix along both x and y axis:
         [ 1, -sin(angle), 0, 0, cos(angle), 0, 0, 0 ]
    with entry [2, 2] being implicit and equal to 1.
    Representations are similar for x axis only and y axis only.

        Args:
            angles (list(float)): batch of angles for which we compute a shear matrix 
            axis (str): axis on which we shear ("x" or "y", by default both)
        Returns:
            (tf.Tensor): shear matrices
    """
    
    num_angles = tf.shape(angles)[0]
    x_offset = tf.zeros(num_angles)
    y_offset = tf.zeros(num_angles)

    if axis == 'x':
        matrix = tf.concat([
                    tf.ones((num_angles, 1), tf.float32),
                    -tf.sin(angles)[:, None],
                    x_offset[:, None],
                    tf.zeros((num_angles, 1), tf.float32),
                    tf.ones((num_angles, 1), tf.float32),
                    y_offset[:, None],
                    tf.zeros((num_angles, 2), tf.float32)
                ],
                axis=1)    
    elif axis == 'y':
        matrix = tf.concat([
                    tf.ones((num_angles, 1), tf.float32),
                    tf.zeros((num_angles, 1), tf.float32),
                    x_offset[:, None],
                    tf.cos(angles)[:, None],
                    tf.ones((num_angles, 1), tf.float32),
                    y_offset[:, None],
                    tf.zeros((num_angles, 2), tf.float32)
                ],
                axis=1)    
    else:
        matrix = tf.concat([
                    tf.ones((num_angles, 1), tf.float32),
                    -tf.sin(angles)[:, None],
                    x_offset[:, None],
                    tf.zeros((num_angles, 1), tf.float32),
                    tf.cos(angles)[:, None],
                    y_offset[:, None],
                    tf.zeros((num_angles, 2), tf.float32)
                ],
                axis=1)    
                  
    return matrix


def get_zoom_matrix(zooms, width, height):
    """
    This function creates a batch of zooming matrices.
    Arguments width and height are the image dimensions.

    The zoom matrix is:
    [[ zoom   0,      x_offset],
     [ 0,     zoom,   y_offset],
     [ 0,     1,      0       ]]

        Args:
            zooms (list(float)): batch of zoom values
            width (float): normalized width of input images
            height (float): normalized height of input images
        Returns:
            (tf.Tensor): batch of zoom matrices
    """
    
    width = tf.cast(width, tf.float32)
    height = tf.cast(height, tf.float32)

    num_zooms = tf.shape(zooms)[0]
    x_offset = ((width - 1.) / 2.0) * (1.0 - zooms[:, 0, None])
    y_offset = ((height - 1.) / 2.0) * (1.0 - zooms[:, 1, None])
    
    matrix = tf.concat([
                zooms[:, 0, None],
                tf.zeros((num_zooms, 1), tf.float32),
                x_offset,
                tf.zeros((num_zooms, 1), tf.float32),
                zooms[:, 1, None],
                y_offset,
                tf.zeros((num_zooms, 2), tf.float32),
                ],
                axis=-1)
    
    return matrix
