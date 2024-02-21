/**
  *
  * Copyright (c) 2023 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */

#ifndef VL53LMZ_PLUGIN_CNH_H_
#define VL53LMZ_PLUGIN_CNH_H_

#include "vl53lmz_api.h"
#include "vl53lmz_plugin_motion_indicator.h"


/**
 * @brief Fundamental characteristics of histogram.
 */
#define VL53LMZ_CNH_PULSE_WIDTH_BIN				10
#define VL53LMZ_CNH_BIN_WIDTH_MM				37.5348

/**
 * @brief Max length of the aggregate id map and MI per aggregate indicator map.
 */
#define VL53LMZ_CNH_AGG_MAX					VL53LMZ_MI_MAP_ID_LENGTH


/** Maximum size for CNH buffer in 32b words. */
#define VL53LMZ_CNH_MAX_DATA_WORDS			((uint32_t)(1540U))

/**
 * @brief Maximum size for CNH buffer in bytes
 */
#define VL53LMZ_CNH_MAX_DATA_BYTES			(VL53LMZ_CNH_MAX_DATA_WORDS*4)

/**
 * @typedef cnh_data_buffer_t
 * @brief Array to hold the raw CNH data from the device.
 */
typedef uint32_t cnh_data_buffer_t[VL53LMZ_CNH_MAX_DATA_BYTES];

#define VL53LMZ_CNH_DATA_IDX 			((uint32_t)0xC048U)
#define VL53LMZ_CNH_DATA_BH 			((uint32_t)((VL53LMZ_CNH_DATA_IDX<<16)+((sizeof(cnh_data_buffer_t)<<4)))


/**
 * @brief Function to initialise the CNH configuration structure.
 * @param (VL53LMZ_Motion_Configuration) *p_mi_config : Motion Indicator configuration structure used by CNH.
 * @param (int16_t) start_bin : Start bin within device histogram to for CNH data.
 * @param (int16_t) num_bins : Number of bin from device histogram for CNH data.
 * @param (int16_t) sub_sample : Sub-sample factor to reduce histogram bins by for CNH data.
 * @return (uint8_t) status :  0 if configuration is OK
 */
uint8_t vl53lmz_cnh_init_config( VL53LMZ_Motion_Configuration *p_mi_config,
									int16_t start_bin,
									int16_t num_bins,
									int16_t sub_sample);


/**
 * @brief Function to create aggregate map CNH.
 * @param (VL53LMZ_Motion_Configuration) *p_mi_config : Motion Indicator configuration structure used by CNH.
 * @param (int16_t) resolution : Mode sensor is operating in, 16 for 4x4 mode, 64 for 8x8 mode.
 * @param (int16_t) start_x : Start zone X location.
 * @param (int16_t) start_y : Start zone Y location.
 * @param (int16_t) merge_x : Merge factor for zones in X direction.
 * @param (int16_t) merge_y : Merge factor for zones in Y direction.
 * @param (int16_t) cols : Number of columns for the aggregate map.
 * @param (int16_t) rows : Number of rows for the aggregate map.
 * @return (uint8_t) status :  0 if configuration is OK
 */
uint8_t vl53lmz_cnh_create_agg_map( VL53LMZ_Motion_Configuration *p_mi_config,
									int16_t resolution,
									int16_t start_x,
									int16_t start_y,
									int16_t merge_x,
									int16_t merge_y,
									int16_t cols,
									int16_t rows );


/**
 * @brief Calculate the size of persistent memory required on the sensor for the MI or CNH configuration.
 * @param (VL53LMZ_Motion_Configuration) *p_mi_config : Motion Indicator configuration structure used by CNH.
 * @param (int32_t) *p_mem_size : Positive value if CNH configuration is good. Returns negative value if bad CNH configuration.
 * @return (uint8_t) status : 0 if configuration is OK
 */
uint32_t vl53lmz_cnh_calc_required_memory( VL53LMZ_Motion_Configuration *p_mi_config,
												int32_t *p_mem_size);

/**
 * @brief Function to calculate minimum and maximum distances for the CNH configuration.
 * @param (VL53LMZ_Motion_Configuration) *p_mi_config : Motion Indicator configuration structure used by CNH.
 * @param (int16_t) *p_min_distance : Minimum distance, in mm.
 * @param (int16_t) *p_max_distance_x : Maximum distance, in mm.
 * @return (uint8_t) status :  0 if configuration is OK
 */
uint8_t vl53lmz_cnh_calc_min_max_distance( VL53LMZ_Motion_Configuration *p_mi_config,
											int16_t *p_min_distance,
											int16_t *p_max_distance );


/**
 * @brief Function to send the CNH configuration to the sensor.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (VL53LMZ_Motion_Configuration) *p_mi_config : Motion Indicator configuration structure used by CNH.
 * @return (uint8_t) status : 0 if programming is OK
 */
uint8_t vl53lmz_cnh_send_config( VL53LMZ_Configuration		*p_dev,
								 VL53LMZ_Motion_Configuration *p_mi_config );


/**
 * @brief Function to calculate location within the CNH buffer of various blocks.
 * @param (VL53LMZ_Motion_Configuration) *p_mi_config : Motion Indicator configuration structure used by CNH.
 * @param (int32_t) agg_id : aggregate ID to get the dat locations for
 * @param (cnh_data_buffer_t) mi_persistent_array : raw CNH data buffer
 * @Param (int32_t) **p_hist : Pointer to histogram array
 * @Param (int8_t) **p_hist_scaler : Pointer to histogram data scaler array
 * @Param (int32_t) **p_ambient : Pointer to pointer to ambient value
 * @Param (int8_t) **p_ambient_scaler : Pointer to pointer to ambient data scaler value
 * @return (uint8_t) status : 0 if no error
 */

uint8_t vl53lmz_cnh_get_block_addresses( VL53LMZ_Motion_Configuration *p_mi_config,
											int32_t						 agg_id,
											cnh_data_buffer_t			 mi_persistent_array,
											int32_t						 **p_hist,
											int8_t						 **p_hist_scaler,
											int32_t						 **p_ambient,
											int8_t						 **p_ambient_scaler );


/**
 * @brief Function to retrieve the Reference Residual value from the raw CNH buffer
 * @param (cnh_data_buffer_t) mi_persistent_array : raw CNH data buffer
 * @return (uint32_t) ref_residual : Reference Residual value (11 fractional bits)
 */
uint32_t vl53lmz_cnh_get_ref_residual( cnh_data_buffer_t	 mi_persistent_array );


#endif /* VL53LMZ_PLUGIN_CNH_H_ */

