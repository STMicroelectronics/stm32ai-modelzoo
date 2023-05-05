/**
  ******************************************************************************
  * @file    filter_gravity.c
  * @author  STMicroelectronics - AIS - MCD Team
  * @version $Version$
  * @date    $Date$
  * @brief   Remove gravity and consider device orientation from raw data
  *
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2021 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */


/* Includes ------------------------------------------------------------------*/
#include "../Inc/filter_gravity.h"
#include "arm_math.h"

#define GRAVITY_HIGHPASS_N 5
#define FILT_ORDER GRAVITY_HIGHPASS_N-1

const float kGravityHighPassA[GRAVITY_HIGHPASS_N] = {
  1.0, -3.868656635, 5.614526749, -3.622760773, 0.8768966198
};
const float kGravityHighPassB[GRAVITY_HIGHPASS_N] = {
  0.9364275932, -3.745710373, 5.618565559, -3.745710373, 0.9364275932
};
const float kGravityHighPassInit[FILT_ORDER] = {
  -0.936528250873, 2.809571532101, -2.809559172096, 0.936515859573
};


typedef struct IIRFilterDirect2_
{
  float z[FILT_ORDER];
  const float * a;
  const float * b;
} IIRFilterDirect2;


void iir_direct2_init(IIRFilterDirect2 * filter,
                      const float * a, const float * b, const float * z,
                      float first)
{
  filter->a = a;
  filter->b = b;

  if (z)
  {
    float scale = (first == 0.0f) ? 1.0f : first;
    for (int i = 0; i < FILT_ORDER; ++i) filter->z[i] = scale * z[i];
  }
}


float iir_direct2_filter(IIRFilterDirect2 * filter, float x)
{
  float filtered = filter->b[0] * x + filter->z[0];

  for (int i = 1; i < FILT_ORDER; ++i) {
    filter->z[i-1] = filter->z[i] + filter->b[i] * x - filter->a[i]*filtered;
  }
  filter->z[FILT_ORDER-1] = filter->b[FILT_ORDER] * x -
                            filter->a[FILT_ORDER] * filtered;

  return filtered;
}


void dynamic_acceleration(float acc_x, float acc_y, float acc_z,
                          float * dyn_x, float * dyn_y, float * dyn_z)
{
  static IIRFilterDirect2 grav_x_filter, grav_y_filter, grav_z_filter;
  static int first_sample = 1;

  if (first_sample) {
    iir_direct2_init(&grav_x_filter, kGravityHighPassA, kGravityHighPassB,
                     kGravityHighPassInit, acc_x);
    iir_direct2_init(&grav_y_filter, kGravityHighPassA, kGravityHighPassB,
                     kGravityHighPassInit, acc_y);
    iir_direct2_init(&grav_z_filter, kGravityHighPassA, kGravityHighPassB,
                     kGravityHighPassInit, acc_z);
    first_sample = 0;
  }

  *dyn_x = iir_direct2_filter(&grav_x_filter, acc_x);
  *dyn_y = iir_direct2_filter(&grav_y_filter, acc_y);
  *dyn_z = iir_direct2_filter(&grav_z_filter, acc_z);
}

/* Exported Functions --------------------------------------------------------*/
/**
* @brief  Remove gravity from acceleration raw data
* @param  HAR_input_t Acceleration value (x/y/z)
* @retval HAR_input_t Acceleration value filtered (x/y/z)
*/
GRAV_input_t gravity_suppress_rotate(GRAV_input_t * data)
{
  float dyn_x, dyn_y, dyn_z;
  dynamic_acceleration(data->AccX, data->AccY, data->AccZ, &dyn_x, &dyn_y, &dyn_z);

  /* gravity versor */
  float grav_x = data->AccX - dyn_x;
  float grav_y = data->AccY - dyn_y;
  float grav_z = data->AccZ - dyn_z;

  float grav_m = grav_x * grav_x + grav_y * grav_y + grav_z * grav_z;
  float sqrt_grav_m = sqrtf(grav_m);
  grav_m = 1.0f / sqrt_grav_m;
  grav_x *= grav_m, grav_y *= grav_m, grav_z *= grav_m;

  float sqrt_for_sin = sqrtf(1.0f - grav_z*grav_z);
  float sin_theta = sqrt_for_sin, cos_theta = -grav_z;

  /* rotation axis: v = [-grav_y, grav_x, 0] / sin */
  float v_x = -grav_y / sin_theta, v_y = grav_x / sin_theta;
  float v_factor = (v_x * dyn_x + v_y * dyn_y) * (1 - cos_theta);

  /*
   * Rodrigues' formula for rotations (a is the dynamic acceleration dyn)
   * a' = a * cos + (v x a) * sin + v * (v . a) * (1 - cos)
   */
  GRAV_input_t out;
  out.AccX = dyn_x * cos_theta + v_y * dyn_z * sin_theta + v_x * v_factor;
  out.AccY = dyn_y * cos_theta - v_x * dyn_z * sin_theta + v_y * v_factor;
  out.AccZ = dyn_z * cos_theta + (v_x * dyn_y - v_y * dyn_x) * sin_theta;
  return out;
}

GRAV_input_t gravity_rotate(GRAV_input_t * data)
{
  float dyn_x, dyn_y, dyn_z;
  dynamic_acceleration(data->AccX, data->AccY, data->AccZ, &dyn_x, &dyn_y, &dyn_z);

  /* gravity versor */
  float grav_x = data->AccX - dyn_x;
  float grav_y = data->AccY - dyn_y;
  float grav_z = data->AccZ - dyn_z;

  float grav_m = grav_x * grav_x + grav_y * grav_y + grav_z * grav_z;
  float sqrt_grav_m = sqrtf(grav_m);
  grav_m = 1.0f / sqrt_grav_m;
  grav_x *= grav_m, grav_y *= grav_m, grav_z *= grav_m;

  float sqrt_for_sin = sqrtf(1.0f - grav_z*grav_z);
  float sin_theta = sqrt_for_sin, cos_theta = -grav_z;

  /* rotation axis: v = [-grav_y, grav_x, 0] / sin */
  float v_x = -grav_y / sin_theta, v_y = grav_x / sin_theta;
  float v_factor = (v_x * dyn_x + v_y * dyn_y) * (1 - cos_theta);

  /*
   * Rodrigues' formula for rotations (a is the dynamic acceleration dyn)
   * a' = a * cos + (v x a) * sin + v * (v . a) * (1 - cos)
   */
  GRAV_input_t out;
  /* rodriguez only */
  out.AccX = data->AccX * cos_theta + v_y * data->AccZ * sin_theta + v_x * v_factor;
  out.AccY = data->AccY * cos_theta - v_x * data->AccZ * sin_theta + v_y * v_factor;
  out.AccZ = data->AccZ * cos_theta + (v_x * data->AccY - v_y * data->AccX) * sin_theta;
  return out;
}
