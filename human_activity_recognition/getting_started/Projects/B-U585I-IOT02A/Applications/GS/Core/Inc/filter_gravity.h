/**
  ******************************************************************************
  * @file    filter_gravity.h
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


 /* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __FILTER_GRAVITY_H__
#define __FILTER_GRAVITY_H__

 typedef struct
{
  float AccX;           /*  acc x axes [g]  */
  float AccY;           /*  acc y axes [g]  */
  float AccZ;           /*  acc z axes [g]  */
} GRAV_input_t;

/* Exported Functions --------------------------------------------------------*/
GRAV_input_t gravity_rotate(GRAV_input_t * data);
GRAV_input_t gravity_suppress_rotate(GRAV_input_t * data);

#endif /* __FILTER_GRAVITY_H__ */
