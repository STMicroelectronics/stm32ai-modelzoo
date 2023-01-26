# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import numpy as np
import scipy.signal as signal

np.random.seed(611)


# Hi-pass IIR filter to separate the low-varying signal
# 26 Hz
A_COEFF = [1.0, -3.868656635, 5.614526749, -3.622760773, 0.8768966198]
B_COEFF = [0.9364275932, -3.745710373, 5.618565559, -3.745710373, 0.9364275932]
#
# 20 Hz
# A_COEFF = [1.0, -3.83582554, 5.52081914, -3.53353522, 0.848556]
# B_COEFF = [0.92117099, -3.68468397, 5.52702596, -3.68468397, 0.92117099]
#


def hipass_filter(data, A_COEFF=A_COEFF, B_COEFF=B_COEFF):
    """Filter signal on all axis with an high-pass filter."""
    A_COEFF = [1.0, -3.868656635, 5.614526749, -3.622760773, 0.8768966198]
    B_COEFF = [0.9364275932, -3.745710373,
               5.618565559, -3.745710373, 0.9364275932]
    if data.ndim == 2:
        # print('internal if')
        return np.vstack([hipass_filter(d, A_COEFF, B_COEFF) for d in data.T]).T

    # initial_state = signal.lfilter_zi(B_COEFF, A_COEFF) * data[0]  # padding
    if data[0] == 0:
        initial_state = [-0.936528250873,
                         2.809571532101, -2.809559172096, 0.936515859573]
    else:
        initial_state = [-0.936528250873 * data[0], 2.809571532101 *
                         data[0], -2.809559172096 * data[0], 0.936515859573 * data[0]]
    # print('initial state', initial_state)
    data_dyn, _ = signal.lfilter(B_COEFF, A_COEFF, data, zi=initial_state)
    return data_dyn


def decompose_dyn(data, A_COEFF=A_COEFF, B_COEFF=B_COEFF):
    """ separate acceleration in low-varying and dynamic component """
    data_dyn = hipass_filter(data, A_COEFF, B_COEFF)
    return data - data_dyn, data_dyn


def colwise_dot(lhs, rhs):
    """ compute the dot product column by column"""
    return np.sum(lhs * rhs, axis=1)


def gravity_rotation(data, A_COEFF=A_COEFF, B_COEFF=B_COEFF):

    # Rotate the coordinate system in order to have z pointing in the gravity direction
    #
    data_g, data_dyn = decompose_dyn(data, A_COEFF, B_COEFF)

    # Normalize gravity
    data_g = data_g / np.sqrt(colwise_dot(data_g, data_g))[:, np.newaxis]

    # Cross product between z and g versors
    axis = np.concatenate(
        (-data_g[:, 1:2], data_g[:, 0:1], np.zeros((data.shape[0], 1))), axis=1)
    sin, cos = np.sqrt(colwise_dot(axis, axis))[:, np.newaxis], -data_g[:, 2:3]

    # Normalize rotation axis and handle degenerate configurations
    with np.errstate(divide='ignore', invalid='ignore'):
        axis = np.true_divide(axis, sin)
        # Set rotation to 0 if gravity aligned to z
        axis[axis == np.inf] = 0.0
        axis = np.nan_to_num(axis)

    data_dyn = data_dyn * cos + np.cross(axis, data_dyn) * sin + \
        axis * colwise_dot(axis, data_dyn)[:, np.newaxis] * (1.0 - cos)
    # print( data_dyn[0,:])
    return data_dyn


if __name__ == '__main__':
    #
    dataExample = [[1, 0, 0], [1, 0, 0], [0, 0, 1]]
    dataExample = np.array(dataExample)
    print(dataExample)
    A_COEFF = [1.0, -3.868656635, 5.614526749, -3.622760773, 0.8768966198]
    B_COEFF = [0.9364275932, -3.745710373,
               5.618565559, -3.745710373, 0.9364275932]
    print(gravity_rotation(dataExample, A_COEFF, B_COEFF))
