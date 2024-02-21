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

#ifndef VL53LMZ_PLUGIN_MOTION_INDICATOR_H_
#define VL53LMZ_PLUGIN_MOTION_INDICATOR_H_

#include "vl53lmz_api.h"


#define VL53LMZ_MI_MAP_ID_LENGTH		VL53LMZ_RESOLUTION_8X8
#define VL53LMZ_MI_INDICATOR_LENGTH		32


/**
 * @brief Motion indicator internal configuration structure.
 */

typedef struct {
	int32_t	 ref_bin_offset;
	uint32_t detection_threshold;
	uint32_t extra_noise_sigma;
	uint32_t null_den_clip_value;
	uint8_t	 mem_update_mode;
	uint8_t	 mem_update_choice;
	uint8_t	 sum_span;
	uint8_t	 feature_length;
	uint8_t	 nb_of_aggregates;
	uint8_t	 nb_of_temporal_accumulations;
	uint8_t	 min_nb_for_global_detection;
	uint8_t	 global_indicator_format_1;
	uint8_t	 global_indicator_format_2;
	uint8_t	 cnh_cfg;
	uint8_t	 cnh_flex_shift;
	uint8_t	 spare_3;
	int8_t	 map_id[VL53LMZ_MI_MAP_ID_LENGTH];
	uint8_t	 indicator_format_1[VL53LMZ_MI_INDICATOR_LENGTH];
	uint8_t	 indicator_format_2[VL53LMZ_MI_INDICATOR_LENGTH];
}VL53LMZ_Motion_Configuration;




/**
 * @brief Flags to modify the operation of the mi__scene_feature_extract module
 * They should be placed in cnh_cfg field before calling start()
 */
#define MI_SFE_DISABLE_PING_PONG	0x01U
#define MI_SFE_DISABLE_VARIANCE		0x02U
#define MI_SFE_ENABLE_AMBIENT_LEVEL 0x04U
#define MI_SFE_ENABLE_XTALK_REMOVAL 0x08U
#define MI_SFE_ZERO_NON_VALID_BINS	0x10U
#define MI_SFE_STORE_REF_RESIDUAL	0x20U



/**
 * @brief Structure of Motion Indicator output block.
 */
typedef struct {
	/* The MI output structure for the not-arrayed output */
	struct {
		uint32_t global_indicator_1;
		uint32_t global_indicator_2;
		uint8_t status;
		uint8_t nb_of_detected_aggregates;
		uint8_t nb_of_aggregates;
		uint8_t spare;
	} op;

	/* The MI output structure for the arrayed output. */
	struct {
		uint32_t per_aggregate_indicator_1[VL53LMZ_MI_INDICATOR_LENGTH];
		uint32_t per_aggregate_indicator_2[VL53LMZ_MI_INDICATOR_LENGTH];
	} arrayed_op;

} VL53LMZ_MI_Output;


#define VL53LMZ_MI_CFG_DEV_IDX			((uint32_t)0xBFACU)
#define VL53LMZ_MI_CFG_DEV_BH			((uint32_t)((VL53LMZ_MI_CFG_DEV_IDX<<16)+(sizeof(VL53LMZ_Motion_Configuration)<<4) )))

#define VL53LMZ_MI_OP_DEV_IDX			((uint32_t)0xD858U)
#define VL53LMZ_MI_OP_DEV_BH			((uint32_t)((VL53LMZ_MI_OP_DEV_IDX<<16)+(sizeof(VL53LMZ_MI_Output)<<4)))


/**
 * @brief This function is used to initialized the motion indicator. By default,
 * indicator is programmed to monitor movements between 400mm and 1500mm.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (VL53LMZ_Motion_Configuration) *p_motion_config : Structure
 * containing the initialized motion configuration.
 * @param (uint8_t) resolution : Wanted resolution, defined by macros
 * VL53LMZ_RESOLUTION_4X4 or VL53LMZ_RESOLUTION_8X8.
 * @return (uint8_t) status : 0 if OK, or 127 is the resolution is unknown.
 */

uint8_t vl53lmz_motion_indicator_init(
		VL53LMZ_Configuration		*p_dev,
		VL53LMZ_Motion_Configuration	*p_motion_config,
		uint8_t				resolution);

/**
 * @brief This function can be used to change the working distance of motion
 * indicator. By default, indicator is programmed to monitor movements between
 * 400mm and 1500mm.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (VL53LMZ_Motion_Configuration) *p_motion_config : Structure
 * containing the initialized motion configuration.
 * @param (uint16_t) distance_min_mm : Minimum distance for indicator (min value 
 * 400mm, max 4000mm).
 * @param (uint16_t) distance_max_mm : Maximum distance for indicator (min value 
 * 400mm, max 4000mm).
 * VL53LMZ_RESOLUTION_4X4 or VL53LMZ_RESOLUTION_8X8.
 * @return (uint8_t) status : 0 if OK, or 127 if an argument is invalid.
 */

uint8_t vl53lmz_motion_indicator_set_distance_motion(
		VL53LMZ_Configuration		*p_dev,
		VL53LMZ_Motion_Configuration	*p_motion_config,
		uint16_t			distance_min_mm,
		uint16_t			distance_max_mm);

/**
 * @brief This function is used to update the internal motion indicator map.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (VL53LMZ_Motion_Configuration) *p_motion_config : Structure
 * containing the initialized motion configuration.
 * @param (uint8_t) resolution : Wanted MI resolution, defined by macros
 * VL53LMZ_RESOLUTION_4X4 or VL53LMZ_RESOLUTION_8X8.
 * @return (uint8_t) status : 0 if OK, or 127 is the resolution is unknown.
 */

uint8_t vl53lmz_motion_indicator_set_resolution(
		VL53LMZ_Configuration		*p_dev,
		VL53LMZ_Motion_Configuration	*p_motion_config,
		uint8_t				resolution);

#endif /* VL53LMZ_PLUGIN_MOTION_INDICATOR_H_ */
