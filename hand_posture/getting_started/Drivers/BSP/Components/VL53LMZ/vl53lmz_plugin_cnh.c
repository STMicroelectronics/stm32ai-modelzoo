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

#include <string.h>

#include "vl53lmz_plugin_cnh.h"
#include "vl53lmz_plugin_motion_indicator.h"

/**
 * @brief Size buffer header areas within persistent data area.
 */
#define CNH_PER_HEADER_BYTES			(5*4)
#define CNH_PER_BUFFER_HEADER_BYTES	(2*4)


/**
 * @brief Indexes for information stored in the persistent data header area.
 */
#define CNH_PER_HEADER_STATE_IDX			   0   /* State							   */
#define CNH_PER_HEADER_BUFFER_INFO_IDX	   1   /* FLAGS<<24 | NUM_BUFFERS<<16 | BUFFER_WORDS */
#define CNH_PER_HEADER_NOISE_SEED_IDX	   2   /* Noise seed					   */
#define CNH_PER_HEADER_FLAGS_IDX			   3   /* Flags used to communicate between SFE and SCI modules	   */
#define CNH_PER_HEADER_AGG_INFO_IDX		   4   /* NumberFeatures[31:16], NumberAggregates[15:0]			   */

/**
 * @brief Possible values of the STATE field.
 */
#define MI_STATE__PING		((uint8_t) 0U)	/** Current feature extract is into ping. */
#define MI_STATE__PONG		((uint8_t) 1U)	/** Current feature extract is into pong. */


/**
 * @brief Fields within the CNH_PER_HEADER_BUFFER_INFO_IDX dword.
 */
#define CNH_PER_HEADER_BUFFER_INFO_WORDS_MASK		   0xFFFFU
#define CNH_PER_HEADER_BUFFER_INFO_NUM_BUFFERS_MASK	   0x00FF0000U
#define CNH_PER_HEADER_BUFFER_INFO_NUM_BUFFERS_SHIFT	   16

#define CNH_PER_HEADER_BUFFER_INFO_FLAGS_MASK		   0xFF000000U
#define CNH_PER_HEADER_BUFFER_INFO_FLAGS_SHIFT		   24

/**
 * @brief Flags bit within the INFO_FLAGS field.
 */
#define CNH_PER_HEADER_BUFFER_INFO_NO_VARIANCE_DATA_FLAG 0x01


/**
 * @brief Indexes for information stored in the Ping-Pong buffer header areas.
 */
#define CNH_PER_BUFFER_STATE_IDX				   0   /* State								*/
#define CNH_PER_BUFFER_NUM_ACCUMULATED_IDX	   1   /* Number of accumulations performed	 */



/**
 * @brief  Returns the size in 32-bits words of a ping or pong block.
 *
 * @param[in]	   option_flags:   option flags to modify memory map
 * @param[in]	   nb_of_agg:	   the number of aggregates.
 * @param[in]	   feat_length:	   the feature length.
 *
 */
int32_t cnh_get_pingpong_size_in_word(
	uint8_t						 option_flags,
	int32_t						 nb_of_agg,
	int32_t						 feat_length
);

/**
 * @brief This function is used to compute the required memory
 *
 * @param[in]	   option_flags:   option flags to modify memory map
 * @param[in]	   nb_of_agg:	   the number of aggregates.
 * @param[in]	   feat_length:	   the feature length.
 * @return			size :		   memory required in bytes.
 */
uint32_t cnh_calculate_required_memory(
		uint8_t						 option_flags,
		int32_t						 nb_of_agg,
		int32_t						 feat_length);


/**
 * @brief Possible values for the pingpong parameter of cnh_get_mem_block_addresses()
 */
#define MI_REQUIRED__PREVIOUS	((uint8_t) 0U)
#define MI_REQUIRED__CURRENT	((uint8_t) 1U)

/**
 * @brief Function to calculate memory block addresses.
 * @return (uint8_t) status : 0 if programming is OK
 */
void cnh_get_mem_block_addresses(
	int32_t						 nb_of_agg,
	int32_t						 feat_length ,
	int32_t						 pingpong,
	int32_t						 agg_id,
	cnh_data_buffer_t			 p_mi_persistent_array,
	int32_t						 **p_status,
	int32_t						 **p_nb_of_acc,
	int32_t						 **p_feat,
	int8_t						 **p_feat_scaler,
	int32_t						 **p_var,
	int8_t						 **p_var_scaler,
	int32_t						 **p_amb_est_var,
	int8_t						 **p_amb_est_var_scaler
);



uint8_t vl53lmz_cnh_init_config( VL53LMZ_Motion_Configuration *p_mi_config,
									int16_t start_bin,
									int16_t num_bins,
									int16_t sub_sample) {
	uint8_t status = VL53LMZ_STATUS_OK;

	p_mi_config->ref_bin_offset = (int32_t)(((uint32_t)start_bin)<<11U);
	p_mi_config->detection_threshold = 0;
	p_mi_config->extra_noise_sigma = 0;
	p_mi_config->null_den_clip_value = 0;
	p_mi_config->mem_update_mode = 0;
	p_mi_config->mem_update_choice = 0;
	p_mi_config->feature_length = (uint8_t)num_bins;
	p_mi_config->sum_span = (uint8_t)sub_sample;
	p_mi_config->nb_of_temporal_accumulations = 1;
	p_mi_config->min_nb_for_global_detection = 0;
	p_mi_config->global_indicator_format_1 = 0;
	p_mi_config->global_indicator_format_2 = 0;
	p_mi_config->cnh_cfg = MI_SFE_DISABLE_PING_PONG |
							MI_SFE_DISABLE_VARIANCE |
							MI_SFE_ENABLE_AMBIENT_LEVEL |
							MI_SFE_ENABLE_XTALK_REMOVAL |
							MI_SFE_ZERO_NON_VALID_BINS |
							MI_SFE_STORE_REF_RESIDUAL;
	p_mi_config->cnh_flex_shift = 1;
	p_mi_config->spare_3 = 0;

	return(status);
}


uint8_t vl53lmz_cnh_create_agg_map( VL53LMZ_Motion_Configuration *p_mi_config,
									int16_t resolution,
									int16_t start_x,
									int16_t start_y,
									int16_t merge_x,
									int16_t merge_y,
									int16_t cols,
									int16_t rows ) {
	uint8_t status = VL53LMZ_STATUS_OK;
	uint16_t zone_res, row, col, i, agg_id;

	// first clear down entirely the map
	memset(p_mi_config->map_id,-1,sizeof(p_mi_config->map_id));

	if (resolution == 16)
		zone_res = 4;
	else
		zone_res = 8;

	if ( ((start_x + (cols*merge_x)) > zone_res)
			|| ((start_y + (rows*merge_y)) > zone_res) ) {
		status = VL53LMZ_STATUS_INVALID_PARAM;
		goto exit;
	}

	if ( status == VL53LMZ_STATUS_OK )
	p_mi_config->nb_of_aggregates = (uint8_t)cols*rows;

	// loop using row and col will step through all the locations in the aggregate map
	// we want to fill.
	for( row = start_y; row < (start_y + (rows*merge_y)); row++ ) {
		for( col = start_x; col < (start_x + (cols*merge_x)); col++ ) {
			i = row * zone_res + col;
			// calc of what aggregrate ID to place in array takes into account the
			// start location and step sizes(which can cause IDs to be used in more than one zone).
			agg_id = ((row - start_y)/merge_y)*cols + ((col - start_x)/merge_x);
			if ( (agg_id >= 0) && (agg_id < VL53LMZ_MI_MAP_ID_LENGTH) ) {
				p_mi_config->map_id[i] = agg_id;
			}
			else {
				status = VL53LMZ_STATUS_INVALID_PARAM;
				goto exit;
			}
		}
	}

exit:
	return( status );
}


uint32_t vl53lmz_cnh_calc_required_memory( VL53LMZ_Motion_Configuration *p_mi_config, int32_t *p_mem_size )
{
	uint32_t size;

	/* check that the MI Config structure is not blank */
	if ( p_mi_config->nb_of_aggregates == 0 )
		return VL53LMZ_STATUS_INVALID_PARAM;

	size = cnh_calculate_required_memory(p_mi_config->cnh_cfg,
									(int32_t)p_mi_config->nb_of_aggregates,
									(int32_t)p_mi_config->feature_length);

	if ( size <= VL53LMZ_CNH_MAX_DATA_BYTES ) {
		*p_mem_size = ((int32_t)size);
	}
	else {
		*p_mem_size = -((int32_t)size);
		return VL53LMZ_STATUS_INVALID_PARAM;
	}

	return VL53LMZ_STATUS_OK;
}


uint8_t vl53lmz_cnh_calc_min_max_distance( VL53LMZ_Motion_Configuration *p_mi_config,
											int16_t *p_min_distance,
											int16_t *p_max_distance ) {
	uint8_t status = VL53LMZ_STATUS_OK;
	int bin_center_mm;

	/* find the centre distance of the first subsampled CNH histogram bin */
	bin_center_mm = (int)(((p_mi_config->ref_bin_offset>>11) + p_mi_config->sum_span/2.0)*VL53LMZ_CNH_BIN_WIDTH_MM);

	/* find minimum distance target can be so that the pulse is entirely within CNH histogram */
	*p_min_distance = (int16_t)(bin_center_mm + (int)((VL53LMZ_CNH_PULSE_WIDTH_BIN/2.0)*VL53LMZ_CNH_BIN_WIDTH_MM));

	/* do the same for the last bin */
	bin_center_mm = (int)(((p_mi_config->ref_bin_offset>>11) + (p_mi_config->feature_length-1)*p_mi_config->sum_span + p_mi_config->sum_span/2.0)*VL53LMZ_CNH_BIN_WIDTH_MM);

	*p_max_distance = (int16_t)(bin_center_mm - (int)((VL53LMZ_CNH_PULSE_WIDTH_BIN/2.0)*VL53LMZ_CNH_BIN_WIDTH_MM));

	return(status);
}


uint8_t vl53lmz_cnh_send_config( VL53LMZ_Configuration		*p_dev,
								 VL53LMZ_Motion_Configuration *p_mi_config ) {
	uint8_t status = VL53LMZ_STATUS_OK;
	status = vl53lmz_dci_write_data(p_dev,(uint8_t *)p_mi_config, VL53LMZ_MI_CFG_DEV_IDX, sizeof(VL53LMZ_Motion_Configuration));
	return status;
}


uint8_t vl53lmz_cnh_get_block_addresses( VL53LMZ_Motion_Configuration *p_mi_config,
											int32_t						 agg_id,
											cnh_data_buffer_t			 mi_persistent_array,
											int32_t						 **p_hist,
											int8_t						 **p_hist_scaler,
											int32_t						 **p_ambient,
											int8_t						 **p_ambient_scaler ) {
	/* dummy variables to hold data we do not want to pass back to caller */
	int32_t						 *p_tmp_32 = NULL;
	int8_t						 *p_tmp_8 = NULL;

	cnh_get_mem_block_addresses(	(int32_t)p_mi_config->nb_of_aggregates,
									(int32_t)p_mi_config->feature_length,
									MI_REQUIRED__CURRENT,
									agg_id,
									mi_persistent_array,
									&p_tmp_32,
									&p_tmp_32,
									p_hist,
									p_hist_scaler,
									&p_tmp_32,
									&p_tmp_8,
									p_ambient,
									p_ambient_scaler );

	return VL53LMZ_STATUS_OK;
}


uint32_t vl53lmz_cnh_get_ref_residual( cnh_data_buffer_t mi_persistent_array ) {
	return( mi_persistent_array[2] );
}


int32_t cnh_get_pingpong_size_in_word(
	uint8_t						 option_flags,
	int32_t						 nb_of_agg,
	int32_t						 feat_length )
{
	int32_t agg_x_feat;
	int32_t size;

	agg_x_feat = nb_of_agg * feat_length;

	size = CNH_PER_BUFFER_HEADER_BYTES;

	size += agg_x_feat * 4;				/* FEAT_INT - 32b per value */
	size += ((3+agg_x_feat)/4)*4;		/* FEAT_FRAC - 8b per value, rounding size up to nearest 32b word */

	size += nb_of_agg*4;				/* AMBIENT_INT - 32b per value */
	size += ((3+nb_of_agg)/4)*4;		/* AMBIENT_FRAC - 8b per value, rounding size up to nearest 32b word */

	if ( !(option_flags & MI_SFE_DISABLE_VARIANCE) ) {
		size += agg_x_feat * 4;			/* VARIANCE_INT - 32b per value */
		size += ((3+agg_x_feat)/4)*4;	/* VARIANCE_FRAC - 8b per value, rounding size up to nearest 32b word */
	}

	return size;
}

uint32_t cnh_calculate_required_memory(
		uint8_t						 option_flags,
		int32_t						 nb_of_agg,
		int32_t						 feat_length )
{
	uint32_t size;

	size = cnh_get_pingpong_size_in_word(option_flags, nb_of_agg, feat_length);
	if ( !(option_flags & MI_SFE_DISABLE_PING_PONG) ) {
		size *= 2;
	}
	size += CNH_PER_HEADER_BYTES;
	return size;
}

void cnh_get_mem_block_addresses(
        int32_t						 nb_of_agg,
        int32_t						 feat_length,
        int32_t						 pingpong,
        int32_t						 agg_id,
        cnh_data_buffer_t			 mi_persistent_array,
        int32_t						 **p_status,
        int32_t						 **p_nb_of_acc,
        int32_t						 **p_feat,
        int8_t						 **p_feat_scaler,
        int32_t						 **p_var,
        int8_t						 **p_var_scaler,
        int32_t						 **p_amb_est_var,
        int8_t						 **p_amb_est_var_scaler
)
{
	/* Local variable declaration. */
	int32_t	 agg_x_feat = nb_of_agg * feat_length;
	int32_t	 agg_off   = agg_id * feat_length;
	uint32_t  *p		= &mi_persistent_array[0];
	int8_t	 *blk_start;
	int32_t	 size;
	int16_t	 buffer_info_flags;

	/* Force to current if we are in the "no previous mode". */
	if ((p[3] & 0x10) == 0x10)
	{
		pingpong = 1;
	}

	/* If current is ping:
	 *	   - if required is current (i.e. pingpong arg = 1) then we must set
	 *		 pingpong to ping (i.e 0) so to 1 - pingpong arg.
	 *	   - if required is previous (i.e. pingpong arg = 0) then we must set
	 *		 pingpong to pong (i.e. 1) so to 1 - pingpong arg.
	 * If current is pong:
	 *		- if required is current (i.e. pingpong arg = 1) then we must set
	 *		 pingpong to pong (i.e 1) so to pingpong arg: nothing to do.
	 *	   - if required is previous (i.e. pingpong arg = 0) then we must set
	 *		 pingpong to ping (i.e. 0) so to pingpong arg: nothing to do.
	 */
	if (p[0] == MI_STATE__PING)
	{
		pingpong = 1 - pingpong;
	}

	/* Get the size of the ping or pong area. */
	size = p[CNH_PER_HEADER_BUFFER_INFO_IDX] & CNH_PER_HEADER_BUFFER_INFO_WORDS_MASK;

	/* Get additional information about the buffer */
	buffer_info_flags = (p[CNH_PER_HEADER_BUFFER_INFO_IDX] & CNH_PER_HEADER_BUFFER_INFO_FLAGS_MASK)>>CNH_PER_HEADER_BUFFER_INFO_FLAGS_SHIFT;

	/* Get status.
	 * - jump the first 3 words
	 * - if pong is required jump also the ping area size.
	 */
	p = p + 5;			/* Points to ping. */
	if (pingpong == 1)
	{
		p = p + size;	/* Points to pong. */
	}

	*p_status			  = (int32_t *)&(p[0]);
	*p_nb_of_acc		  = (int32_t *)&(p[1]);

	blk_start			  = (int8_t *)&p[2];

	/* Store feature location */
	*p_feat				  = &(((int32_t *)blk_start)[agg_off]);
	blk_start			  = blk_start + agg_x_feat*4;			/* skip over this block, one 32b word per agg_x_feat */

	/* Store fractional part of feature. */
	*p_feat_scaler		  = &(blk_start[agg_off]);
	blk_start			  = blk_start + ((3+agg_x_feat)/4)*4;	/* skip over this block, one byte per agg_x_feat, rounded up to next 32b word */

	/* Store variance of estimated ambient. */
	*p_amb_est_var		  = &(((int32_t *)blk_start)[agg_id]);
	blk_start			  = blk_start + nb_of_agg*4;			/* skip over this block, one 32b word per nb_of_agg */

	/* Store fractional part of variance of estimated ambient. */
	*p_amb_est_var_scaler	  = &(blk_start[agg_id]);
	blk_start			  = blk_start + ((3+nb_of_agg)/4)*4;   /* skip over this block, one byte per nb_of_agg, rounded up to next 32b word */

	if (buffer_info_flags & CNH_PER_HEADER_BUFFER_INFO_NO_VARIANCE_DATA_FLAG) {
		/* no Variance data in buffer, set pointers to NULL */
		*p_var			  = (int32_t *)NULL;
		*p_var_scaler		  = (int8_t *)NULL;
	}
	else {
		/* Store variances.*/
		*p_var			  = &(((int32_t *)blk_start)[agg_off]);
		blk_start		  = blk_start + agg_x_feat*4;			/* skip over this block, one 32b word per agg_x_feat */

		/* Store fractional part of variance. */
		*p_var_scaler		  = &(blk_start[agg_off]);
	}

	return;
}

