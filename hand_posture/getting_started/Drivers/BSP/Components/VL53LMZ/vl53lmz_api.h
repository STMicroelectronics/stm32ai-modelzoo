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

#ifndef VL53LMZ_API_H_
#define VL53LMZ_API_H_

#if defined (__ARMCC_VERSION) && (__ARMCC_VERSION < 6010050)
#pragma anon_unions
#endif



#include "platform.h"


/**
 * @brief Current driver version.
 */

#define VL53LMZ_API_REVISION			"VL53LMZ_2.0.7"

/**
 * @brief Default I2C address of VL53L5CX sensor. Can be changed using function
 * vl53lmz_set_i2c_address() function is called.
 */

#define VL53LMZ_DEFAULT_I2C_ADDRESS			((uint16_t)0x52)

/**
 * @brief Macro VL53LMZ_RESOLUTION_4X4 or VL53LMZ_RESOLUTION_8X8 allows
 * setting sensor in 4x4 mode or 8x8 mode, using function
 * vl53lmz_set_resolution().
 */

#define VL53LMZ_RESOLUTION_4X4			((uint8_t) 16U)
#define VL53LMZ_RESOLUTION_8X8			((uint8_t) 64U)


/**
 * @brief Macro VL53LMZ_TARGET_ORDER_STRONGEST or VL53LMZ_TARGET_ORDER_CLOSEST
 *	are used to select the target order for data output.
 */

#define VL53LMZ_TARGET_ORDER_CLOSEST		((uint8_t) 1U)
#define VL53LMZ_TARGET_ORDER_STRONGEST		((uint8_t) 2U)

/**
 * @brief Macro VL53LMZ_RANGING_MODE_CONTINUOUS and
 * VL53LMZ_RANGING_MODE_AUTONOMOUS are used to change the ranging mode.
 * Autonomous mode can be used to set a precise integration time, whereas
 * continuous is always maximum.
 */

#define VL53LMZ_RANGING_MODE_CONTINUOUS	((uint8_t) 1U)
#define VL53LMZ_RANGING_MODE_AUTONOMOUS	((uint8_t) 3U)

/**
 * @brief The default power mode is VL53LMZ_POWER_MODE_WAKEUP. User can choose
 * the mode VL53LMZ_POWER_MODE_SLEEP to save power consumption is the device
 * is not used. The low power mode retains the firmware and the configuration.
 * Both modes can be changed using function vl53lmz_set_power_mode().
 */

#define VL53LMZ_POWER_MODE_SLEEP		((uint8_t) 0U)
#define VL53LMZ_POWER_MODE_WAKEUP		((uint8_t) 1U)

/**
 * @brief Macro VL53LMZ_STATUS_OK indicates that VL53L5 sensor has no error.
 * Macro VL53LMZ_STATUS_ERROR indicates that something is wrong (value,
 * I2C access, ...). Macro VL53LMZ_MCU_ERROR is used to indicate a MCU issue.
 */

#define VL53LMZ_STATUS_OK					((uint8_t) 0U)
#define VL53LMZ_STATUS_TIMEOUT_ERROR		((uint8_t) 1U)
#define VL53LMZ_STATUS_CORRUPTED_FRAME		((uint8_t) 2U)
#define VL53LMZ_STATUS_LASER_SAFETY			((uint8_t) 3U)
#define VL53LMZ_STATUS_UNKNOWN_DEVICE		((uint8_t) 4U)
#define VL53LMZ_MCU_ERROR					((uint8_t) 66U)
#define VL53LMZ_STATUS_INVALID_PARAM		((uint8_t) 127U)
#define VL53LMZ_STATUS_FUNC_NOT_AVAILABLE   ((uint8_t) 254U)
#define VL53LMZ_STATUS_ERROR				((uint8_t) 255U)

/**
 * @brief Definitions for Range results block headers
 */

#define VL53L5_NULL_BH					((uint32_t)0x00000000U)

#if VL53LMZ_NB_TARGET_PER_ZONE == 1

#define VL53LMZ_NB_TARGET_DETECTED_BH	((uint32_t)0xDB840401U)
#define VL53LMZ_SIGNAL_RATE_BH			((uint32_t)0xDBC40404U)
#define VL53LMZ_RANGE_SIGMA_MM_BH		((uint32_t)0xDEC40402U)
#define VL53LMZ_DISTANCE_BH				((uint32_t)0xDF440402U)
#define VL53LMZ_REFLECTANCE_BH			((uint32_t)0xE0440401U)
#define VL53LMZ_TARGET_STATUS_BH		((uint32_t)0xE0840401U)

#define VL53LMZ_NB_TARGET_DETECTED_IDX	((uint16_t)0xDB84U)
#define VL53LMZ_SIGNAL_RATE_IDX			((uint16_t)0xDBC4U)
#define VL53LMZ_RANGE_SIGMA_MM_IDX		((uint16_t)0xDEC4U)
#define VL53LMZ_DISTANCE_IDX			((uint16_t)0xDF44U)
#define VL53LMZ_REFLECTANCE_EST_PC_IDX	((uint16_t)0xE044U)
#define VL53LMZ_TARGET_STATUS_IDX		((uint16_t)0xE084U)

#else
#define VL53LMZ_NB_TARGET_DETECTED_BH	((uint32_t)0x57D00401U)
#define VL53LMZ_SIGNAL_RATE_BH			((uint32_t)0x58900404U)
#define VL53LMZ_RANGE_SIGMA_MM_BH		((uint32_t)0x64900402U)
#define VL53LMZ_DISTANCE_BH				((uint32_t)0x66900402U)
#define VL53LMZ_REFLECTANCE_BH			((uint32_t)0x6A900401U)
#define VL53LMZ_TARGET_STATUS_BH		((uint32_t)0x6B900401U)

#define VL53LMZ_NB_TARGET_DETECTED_IDX	((uint16_t)0x57D0U)
#define VL53LMZ_SIGNAL_RATE_IDX			((uint16_t)0x5890U)
#define VL53LMZ_RANGE_SIGMA_MM_IDX		((uint16_t)0x6490U)
#define VL53LMZ_DISTANCE_IDX			((uint16_t)0x6690U)
#define VL53LMZ_REFLECTANCE_EST_PC_IDX	((uint16_t)0x6A90U)
#define VL53LMZ_TARGET_STATUS_IDX		((uint16_t)0x6B90U)
#endif

#define VL53LMZ_START_BH				((uint32_t)0x0000000DU)
#define VL53LMZ_METADATA_BH				((uint32_t)0x54B400C0U)
#define VL53LMZ_COMMONDATA_BH			((uint32_t)0x54C00040U)
#define VL53LMZ_AMBIENT_RATE_BH			((uint32_t)0x54D00404U)
#define VL53LMZ_SPAD_COUNT_BH			((uint32_t)0x55D00404U)
#define VL53LMZ_MOTION_DETECT_BH		((uint32_t)0xD85808C0U)


#define VL53LMZ_METADATA_IDX			((uint16_t)0x54B4U)
#define VL53LMZ_COMMONDATA_IDX			((uint16_t)0x54C0U)
#define VL53LMZ_AMBIENT_RATE_IDX		((uint16_t)0x54D0U)
#define VL53LMZ_SPAD_COUNT_IDX			((uint16_t)0x55D0U)
#define VL53LMZ_MOTION_DETEC_IDX		((uint16_t)0xD858U)
#define VL53LMZ_RAD2PERP_SCALE_GRID_IDX ((uint16_t)0xA2A8U)

#define VL53LMZ_MODULE_TYPE_IDX			((uint16_t)0xE0C5U)



/**
 * @brief Inner Macro for API. Not for user, only for development.
 */

#define VL53LMZ_NVM_DATA_SIZE			((uint16_t)492U)
#define VL53LMZ_CONFIGURATION_SIZE		((uint16_t)972U)
#define VL53LMZ_OFFSET_BUFFER_SIZE		((uint16_t)488U)
#define VL53LMZ_XTALK_BUFFER_SIZE		((uint16_t)776U)

#define VL53LMZ_DCI_ZONE_CONFIG			((uint16_t)0x5450U)
#define VL53LMZ_DCI_FREQ_HZ				((uint16_t)0x5458U)
#define VL53LMZ_DCI_INT_TIME			((uint16_t)0x545CU)
#define VL53LMZ_DCI_FW_NB_TARGET		((uint16_t)0x5478U)
#define VL53LMZ_DCI_RANGING_MODE		((uint16_t)0xAD30U)
#define VL53LMZ_DCI_DSS_CONFIG			((uint16_t)0xAD38U)
#define VL53LMZ_DCI_TARGET_ORDER		((uint16_t)0xAE64U)
#define VL53LMZ_DCI_SHARPENER			((uint16_t)0xAED8U)
#define VL53LMZ_DCI_INTERNAL_CP			((uint16_t)0xB39CU)
#define VL53LMZ_DCI_SYNC_PIN			((uint16_t)0xB5F0U)
#define VL53LMZ_DCI_MOTION_DETECTOR_CFG ((uint16_t)0xBFACU)
#define VL53LMZ_DCI_SINGLE_RANGE		((uint16_t)0xD964U)
#define VL53LMZ_DCI_OUTPUT_CONFIG		((uint16_t)0xD968U)
#define VL53LMZ_DCI_OUTPUT_ENABLES		((uint16_t)0xD970U)
#define VL53LMZ_DCI_OUTPUT_LIST			((uint16_t)0xD980U)
#define VL53LMZ_DCI_PIPE_CONTROL		((uint16_t)0xDB80U)
#define VL53LMZ_DCI_GLARE_FILTER_CFG	((uint16_t)0xE108U)

#define VL53LMZ_UI_CMD_STATUS			((uint16_t)0x2C00U)
#define VL53LMZ_UI_CMD_START			((uint16_t)0x2C04U)
#define VL53LMZ_UI_CMD_END				((uint16_t)0x2FFFU)

/**
 * @brief Inner values for API. Max buffer size depends of the selected output.
 */

#ifndef VL53LMZ_DISABLE_AMBIENT_PER_SPAD
#define L5CX_AMB_SIZE	260U
#else
#define L5CX_AMB_SIZE	0U
#endif

#ifndef VL53LMZ_DISABLE_NB_SPADS_ENABLED
#define L5CX_SPAD_SIZE	260U
#else
#define L5CX_SPAD_SIZE	0U
#endif

#ifndef VL53LMZ_DISABLE_NB_TARGET_DETECTED
#define L5CX_NTAR_SIZE	68U
#else
#define L5CX_NTAR_SIZE	0U
#endif

#ifndef VL53LMZ_DISABLE_SIGNAL_PER_SPAD
#define L5CX_SPS_SIZE ((256U * VL53LMZ_NB_TARGET_PER_ZONE) + 4U)
#else
#define L5CX_SPS_SIZE	0U
#endif

#ifndef VL53LMZ_DISABLE_RANGE_SIGMA_MM
#define L5CX_SIGR_SIZE ((128U * VL53LMZ_NB_TARGET_PER_ZONE) + 4U)
#else
#define L5CX_SIGR_SIZE	0U
#endif

#ifndef VL53LMZ_DISABLE_DISTANCE_MM
#define L5CX_DIST_SIZE ((128U * VL53LMZ_NB_TARGET_PER_ZONE) + 4U)
#else
#define L5CX_DIST_SIZE	0U
#endif

#ifndef VL53LMZ_DISABLE_REFLECTANCE_PERCENT
#define L5CX_RFLEST_SIZE ((64U * VL53LMZ_NB_TARGET_PER_ZONE) + 4U)
#else
#define L5CX_RFLEST_SIZE	0U
#endif

#ifndef VL53LMZ_DISABLE_TARGET_STATUS
#define L5CX_STA_SIZE ((64U	* VL53LMZ_NB_TARGET_PER_ZONE) + 4U)
#else
#define L5CX_STA_SIZE	0U
#endif

#ifndef VL53LMZ_DISABLE_MOTION_INDICATOR
#define L5CX_MOT_SIZE	144U
#else
#define L5CX_MOT_SIZE	0U
#endif

/* maximum size of (CNH_DATA + MI_OP_DEV) */
#define VL53LMZ_ADDITIONAL_RESULTS_DATA (6160U+268U)


/**
 * @brief Macro VL53LMZ_MAX_RESULTS_SIZE indicates the maximum size used by
 * output through I2C. Value 40 corresponds to headers + meta-data + common-data
 * and 20 corresponds to the footer.
 */

#define VL53LMZ_MAX_RESULTS_SIZE ( 40U \
	+ L5CX_AMB_SIZE + L5CX_SPAD_SIZE + L5CX_NTAR_SIZE + L5CX_SPS_SIZE \
	+ L5CX_SIGR_SIZE + L5CX_DIST_SIZE + L5CX_RFLEST_SIZE + L5CX_STA_SIZE \
	+ L5CX_MOT_SIZE + 20U + VL53LMZ_ADDITIONAL_RESULTS_DATA )


/**
 * @brief Macro VL53LMZ_TEMPORARY_BUFFER_SIZE can be used to know the size of
 * the temporary buffer. The minimum size is 1024, and the maximum depends of
 * the output configuration.
 */

#if VL53LMZ_MAX_RESULTS_SIZE < 1024U
#define VL53LMZ_TEMPORARY_BUFFER_SIZE ((uint32_t) 1024U)
#else
#define VL53LMZ_TEMPORARY_BUFFER_SIZE ((uint32_t) VL53LMZ_MAX_RESULTS_SIZE)
#endif


/**
 * @brief Structure VL53LMZ_Configuration contains the sensor configuration.
 * User MUST not manually change these field, except for the sensor address.
 */

typedef struct
{
	/* Platform, filled by customer into the 'platform.h' file */
	VL53LMZ_Platform	platform;
	/* Results streamcount, value auto-incremented at each range */
	uint8_t				streamcount;
	/* Size of data read though I2C */
	uint32_t			data_read_size;
	/* Address of default configuration buffer */
	uint8_t				*default_configuration;
	/* Address of default Xtalk buffer */
	uint8_t				*default_xtalk;
	/* Offset buffer */
	uint8_t				offset_data[VL53LMZ_OFFSET_BUFFER_SIZE];
	/* Xtalk buffer */
	uint8_t				xtalk_data[VL53LMZ_XTALK_BUFFER_SIZE];
	/* Temporary buffer used for internal driver processing */
	 uint8_t			temp_buffer[VL53LMZ_TEMPORARY_BUFFER_SIZE];
	/* Auto-stop flag for stopping the sensor */
	uint8_t				is_auto_stop_enabled;
    /* Device and revision information read back from sensor */
	uint8_t device_id, revision_id;
} VL53LMZ_Configuration;


/**
 * @brief Structure VL53LMZ_ResultsData contains the ranging results of
 * VL53L5CX. If user wants more than 1 target per zone, the results can be split
 * into 2 sub-groups :
 * - Per zone results. These results are common to all targets (ambient_per_spad
 * , nb_target_detected and nb_spads_enabled).
 * - Per target results : These results are different relative to the detected
 * target (signal_per_spad, range_sigma_mm, distance_mm, reflectance,
 * target_status).
 */

typedef struct
{
	/* Internal sensor silicon temperature */
	int8_t silicon_temp_degc;

	/* Ambient noise in kcps/spads */
#ifndef VL53LMZ_DISABLE_AMBIENT_PER_SPAD
	uint32_t ambient_per_spad[VL53LMZ_RESOLUTION_8X8];
#endif

	/* Number of valid target detected for 1 zone */
#ifndef VL53LMZ_DISABLE_NB_TARGET_DETECTED
	uint8_t nb_target_detected[VL53LMZ_RESOLUTION_8X8];
#endif

	/* Number of spads enabled for this ranging */
#ifndef VL53LMZ_DISABLE_NB_SPADS_ENABLED
	uint32_t nb_spads_enabled[VL53LMZ_RESOLUTION_8X8];
#endif

	/* Signal returned to the sensor in kcps/spads */
#ifndef VL53LMZ_DISABLE_SIGNAL_PER_SPAD
	uint32_t signal_per_spad[(VL53LMZ_RESOLUTION_8X8
					*VL53LMZ_NB_TARGET_PER_ZONE)];
#endif

	/* Sigma of the current distance in mm */
#ifndef VL53LMZ_DISABLE_RANGE_SIGMA_MM
	uint16_t range_sigma_mm[(VL53LMZ_RESOLUTION_8X8
					*VL53LMZ_NB_TARGET_PER_ZONE)];
#endif

	/* Measured distance in mm */
#ifndef VL53LMZ_DISABLE_DISTANCE_MM
	int16_t distance_mm[(VL53LMZ_RESOLUTION_8X8
					*VL53LMZ_NB_TARGET_PER_ZONE)];
#endif

	/* Estimated reflectance in percent */
#ifndef VL53LMZ_DISABLE_REFLECTANCE_PERCENT
	uint8_t reflectance[(VL53LMZ_RESOLUTION_8X8
					*VL53LMZ_NB_TARGET_PER_ZONE)];
#endif

	/* Status indicating the measurement validity (5 & 9 means ranging OK)*/
#ifndef VL53LMZ_DISABLE_TARGET_STATUS
	uint8_t target_status[(VL53LMZ_RESOLUTION_8X8
					*VL53LMZ_NB_TARGET_PER_ZONE)];
#endif

	/* Motion detector results */
#ifndef VL53LMZ_DISABLE_MOTION_INDICATOR
	struct
	{
		uint32_t global_indicator_1;
		uint32_t global_indicator_2;
		uint8_t	 status;
		uint8_t	 nb_of_detected_aggregates;
		uint8_t	 nb_of_aggregates;
		uint8_t	 spare;
		uint32_t motion[32];
	} motion_indicator;
#endif

} VL53LMZ_ResultsData;


union Block_header {
	uint32_t bytes;
	struct {
		uint32_t type : 4;
		uint32_t size : 12;
		uint32_t idx : 16;
	};
};



uint8_t vl53lmz_is_alive(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				*p_is_alive);

/**
 * @brief Mandatory function used to initialize the sensor. This function must
 * be called after a power on, to load the firmware into the VL53L5CX. It takes
 * a few hundred milliseconds.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @return (uint8_t) status : 0 if initialization is OK.
 */

uint8_t vl53lmz_init(
		VL53LMZ_Configuration	*p_dev);

/**
 * @brief This function is used to change the I2C address of the sensor. If
 * multiple VL53L5 sensors are connected to the same I2C line, all other LPn
 * pins needs to be set to Low. The default sensor address is 0x52.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint16_t) i2c_address : New I2C address.
 * @return (uint8_t) status : 0 if new address is OK
 */

uint8_t vl53lmz_set_i2c_address(
		VL53LMZ_Configuration	*p_dev,
		uint16_t			i2c_address);

/**
 * @brief This function is used to get the current sensor power mode.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t) *p_power_mode : Current power mode. The value of this
 * pointer is equal to 0 if the sensor is in low power,
 * (VL53LMZ_POWER_MODE_SLEEP), or 1 if sensor is in standard mode
 * (VL53LMZ_POWER_MODE_WAKEUP).
 * @return (uint8_t) status : 0 if power mode is OK
 */

uint8_t vl53lmz_get_power_mode(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				*p_power_mode);

/**
 * @brief This function is used to set the sensor in Low Power mode, for
 * example if the sensor is not used during a long time. The macro
 * VL53LMZ_POWER_MODE_SLEEP can be used to enable the low power mode. When user
 * want to restart the sensor, he can use macro VL53LMZ_POWER_MODE_WAKEUP.
 * Please ensure that the device is not streaming before calling the function.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t) power_mode : Selected power mode (VL53LMZ_POWER_MODE_SLEEP
 * or VL53LMZ_POWER_MODE_WAKEUP)
 * @return (uint8_t) status : 0 if power mode is OK, or 127 if power mode
 * requested by user is not valid.
 */

uint8_t vl53lmz_set_power_mode(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				power_mode);

/**
 * @brief This function starts a ranging session. When the sensor streams, host
 * cannot change settings 'on-the-fly'.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @return (uint8_t) status : 0 if start is OK.
 */

uint8_t vl53lmz_start_ranging(
		VL53LMZ_Configuration	*p_dev);

/**
 * @brief This function stops the ranging session. It must be used when the
 * sensor streams, after calling vl53lmz_start_ranging().
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @return (uint8_t) status : 0 if stop is OK
 */

uint8_t vl53lmz_stop_ranging(
		VL53LMZ_Configuration	*p_dev);

/**
 * @brief This function checks if a new data is ready by polling I2C. If a new
 * data is ready, a flag will be raised.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t) *p_isReady : Value of this pointer be updated to 0 if data
 * is not ready, or 1 if a new data is ready.
 * @return (uint8_t) status : 0 if I2C reading is OK
 */

uint8_t vl53lmz_check_data_ready(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				*p_isReady);

/**
 * @brief This function gets the ranging data, using the selected output and the
 * resolution.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (VL53LMZ_ResultsData) *p_results : VL53L5 results structure.
 * @return (uint8_t) status : 0 data are successfully get.
 */

uint8_t vl53lmz_get_ranging_data(
		VL53LMZ_Configuration	*p_dev,
		VL53LMZ_ResultsData		*p_results);

/**
 * @brief This function gets the current resolution (4x4 or 8x8).
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t) *p_resolution : Value of this pointer will be equal to 16
 * for 4x4 mode, and 64 for 8x8 mode.
 * @return (uint8_t) status : 0 if resolution is OK.
 */

uint8_t vl53lmz_get_resolution(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				*p_resolution);

/**
 * @brief This function sets a new resolution (4x4 or 8x8).
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t) resolution : Use macro VL53LMZ_RESOLUTION_4X4 or
 * VL53LMZ_RESOLUTION_8X8 to set the resolution.
 * @return (uint8_t) status : 0 if set resolution is OK.
 */

uint8_t vl53lmz_set_resolution(
		VL53LMZ_Configuration	*p_dev,
		uint8_t							resolution);

/**
 * @brief This function gets the current ranging frequency in Hz. Ranging
 * frequency corresponds to the time between each measurement.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t) *p_frequency_hz: Contains the ranging frequency in Hz.
 * @return (uint8_t) status : 0 if ranging frequency is OK.
 */

uint8_t vl53lmz_get_ranging_frequency_hz(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				*p_frequency_hz);

/**
 * @brief This function sets a new ranging frequency in Hz. Ranging frequency
 * corresponds to the measurements frequency. This setting depends of
 * the resolution, so please select your resolution before using this function.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t) frequency_hz : Contains the ranging frequency in Hz.
 * - For 4x4, min and max allowed values are : [1;60]
 * - For 8x8, min and max allowed values are : [1;15]
 * @return (uint8_t) status : 0 if ranging frequency is OK, or 127 if the value
 * is not correct.
 */

uint8_t vl53lmz_set_ranging_frequency_hz(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				frequency_hz);

/**
 * @brief This function gets the current integration time in ms.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint32_t) *p_time_ms: Contains integration time in ms.
 * @return (uint8_t) status : 0 if integration time is OK.
 */

uint8_t vl53lmz_get_integration_time_ms(
		VL53LMZ_Configuration	*p_dev,
		uint32_t			*p_time_ms);

/**
 * @brief This function sets a new integration time in ms. Integration time must
 * be computed to be lower than the ranging period, for a selected resolution.
 * Please note that this function has no impact on ranging mode continous.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint32_t) time_ms : Contains the integration time in ms. For all
 * resolutions and frequency, the minimum value is 2ms, and the maximum is
 * 1000ms.
 * @return (uint8_t) status : 0 if set integration time is OK.
 */

uint8_t vl53lmz_set_integration_time_ms(
		VL53LMZ_Configuration	*p_dev,
		uint32_t			integration_time_ms);

/**
 * @brief This function gets the current sharpener in percent. Sharpener can be
 * changed to blur more or less zones depending of the application.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint32_t) *p_sharpener_percent: Contains the sharpener in percent.
 * @return (uint8_t) status : 0 if get sharpener is OK.
 */

uint8_t vl53lmz_get_sharpener_percent(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				*p_sharpener_percent);

/**
 * @brief This function sets a new sharpener value in percent. Sharpener can be
 * changed to blur more or less zones depending of the application. Min value is
 * 0 (disabled), and max is 99.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint32_t) sharpener_percent : Value between 0 (disabled) and 99%.
 * @return (uint8_t) status : 0 if set sharpener is OK.
 */

uint8_t vl53lmz_set_sharpener_percent(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				sharpener_percent);

/**
 * @brief This function gets the current target order (closest or strongest).
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t) *p_target_order: Contains the target order.
 * @return (uint8_t) status : 0 if get target order is OK.
 */

uint8_t vl53lmz_get_target_order(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				*p_target_order);

/**
 * @brief This function sets a new target order. Please use macros
 * VL53LMZ_TARGET_ORDER_STRONGEST and VL53LMZ_TARGET_ORDER_CLOSEST to define
 * the new output order. By default, the sensor is configured with the strongest
 * output.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t) target_order : Required target order.
 * @return (uint8_t) status : 0 if set target order is OK, or 127 if target
 * order is unknown.
 */

uint8_t vl53lmz_set_target_order(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				target_order);

/**
 * @brief This function is used to get the ranging mode. Two modes are
 * available using ULD : Continuous and autonomous. The default
 * mode is Autonomous.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t) *p_ranging_mode : current ranging mode
 * @return (uint8_t) status : 0 if get ranging mode is OK.
 */

uint8_t vl53lmz_get_ranging_mode(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				*p_ranging_mode);

/**
 * @brief This function is used to set the ranging mode. Two modes are
 * available using ULD : Continuous and autonomous. The default
 * mode is Autonomous.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t) ranging_mode : Use macros VL53LMZ_RANGING_MODE_CONTINUOUS,
 * VL53LMZ_RANGING_MODE_CONTINUOUS.
 * @return (uint8_t) status : 0 if set ranging mode is OK.
 */

uint8_t vl53lmz_set_ranging_mode(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				ranging_mode);

/**
 * @brief This function is used to disable the VCSEL charge pump
 * This optimizes the power consumption of the device
 * To be used only if AVDD = 3.3V
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 */
uint8_t vl53lmz_enable_internal_cp(
		VL53LMZ_Configuration	*p_dev);

/**
 * @brief This function is used to disable the VCSEL charge pump
 * This optimizes the power consumption of the device
 * To be used only if AVDD = 3.3V
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 */
uint8_t vl53lmz_disable_internal_cp(
		  VL53LMZ_Configuration		 *p_dev);

/**
 * @brief This function is used to check if the synchronization pin is enabled
 * or disabled. When it is enabled, the sensor waits an interrupt on B1 pin
 * to start the next measurement. It is useful for multi-devices
 * synchronization. By default the sync pin is disabled.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t*) p_is_sync_pin_enabled : Pointer of sync pin status. Value
 * overridden to 0 if the pin is disabled, or 1 if the pin is enabled.
 * @return (uint8_t) status : 0 if get sync pin OK.
 */
uint8_t vl53lmz_get_external_sync_pin_enable(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				*p_is_sync_pin_enabled);


/**
 * @brief This function is used to enable or disable the synchronization pin. When
 * it is enabled, the sensor waits an interrupt on B1 pin to start the next
 * measurement. It is useful for multi-devices synchronization. By default the sync
 * pin is disabled.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t) enable_sync_pin : Ste the value to 1 to enable the sync
 * pin, or 0 to disable it.
 * @return (uint8_t) status : 0 if set sync pin OK.
 */
uint8_t vl53lmz_set_external_sync_pin_enable(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				enable_sync_pin);

/**
 * @brief This function gets the current Glare Filter config.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t) *p_threshold_x10: Pointer to variable to place threshold_x10 value.
 * @param (int16_t) *p_max_range: Pointer to variable to place max_range value.
 * @return (uint8_t) status : 0 if settings where applied successfully.
 */
uint8_t vl53lmz_get_glare_filter_cfg(
		VL53LMZ_Configuration	*p_dev,
		uint8_t					*p_threshold_pc_x10,
		int16_t					*p_max_range );

/**
 * @brief This function sets the current Glare Filter config.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t) threshold_x10: GlareFilter threshold value. Percentage scaled by a factor of 10, i.e. to set a threshold of 2.5% set a value of 25. Setting to zero completely disables the GlareFilter.
 * @param (int16_t) max_range: Maximum range for GlareFilter to operate. Valid range of values is 10mm to 1000mm.
 * @return (uint8_t) status : 0 if settings where applied successfully.
 */
uint8_t vl53lmz_set_glare_filter_cfg(
		VL53LMZ_Configuration	*p_dev,
		uint8_t					threshold_pc_x10,
		int16_t					max_range );


/**
 * @brief This function can be used to read 'extra data' from DCI. Using a known
 * index, the function fills the casted structure passed in argument.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t) *data : This field can be a casted structure, or a simple
 * array. Please note that the FW only accept data of 32 bits. So field data can
 * only have a size of 32, 64, 96, 128, bits ....
 * @param (uint32_t) index : Index of required value.
 * @param (uint16_t)*data_size : This field must be the structure or array size
 * (using sizeof() function).
 * @return (uint8_t) status : 0 if OK
 */

uint8_t vl53lmz_dci_read_data(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				*data,
		uint32_t			index,
		uint16_t			data_size);

/**
 * @brief This function can be used to write 'extra data' to DCI. The data can
 * be simple data, or casted structure.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t) *data : This field can be a casted structure, or a simple
 * array. Please note that the FW only accept data of 32 bits. So field data can
 * only have a size of 32, 64, 96, 128, bits ..
 * @param (uint32_t) index : Index of required value.
 * @param (uint16_t)*data_size : This field must be the structure or array size
 * (using sizeof() function).
 * @return (uint8_t) status : 0 if OK
 */

uint8_t vl53lmz_dci_write_data(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				*data,
		uint32_t			index,
		uint16_t			data_size);

/**
 * @brief This function can be used to replace 'extra data' in DCI. The data can
 * be simple data, or casted structure.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint8_t) *data : This field can be a casted structure, or a simple
 * array. Please note that the FW only accept data of 32 bits. So field data can
 * only have a size of 32, 64, 96, 128, bits ..
 * @param (uint32_t) index : Index of required value.
 * @param (uint16_t)*data_size : This field must be the structure or array size
 * (using sizeof() function).
 * @param (uint8_t) *new_data : Contains the new fields.
 * @param (uint16_t) new_data_size : New data size.
 * @param (uint16_t) new_data_pos : New data position into the buffer.
 * @return (uint8_t) status : 0 if OK
 */

uint8_t vl53lmz_dci_replace_data(
		VL53LMZ_Configuration	*p_dev,
		uint8_t				*data,
		uint32_t			index,
		uint16_t			data_size,
		uint8_t				*new_data,
		uint16_t			new_data_size,
		uint16_t			new_data_pos);



#define NUM_OUTPUT_ENABLE_WORDS	4
#define NUM_OUTPUT_CONFIG_WORDS	32		/* limited to 32 so that only the first word of of the output_enables needs to be updated */

/**
 * @brief This function creates the output configuration that will be sent to
 * the device by the vl53lmz_send_output_config_and_start() functions.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @return (uint8_t) status : 0 if OK
 */
uint8_t vl53lmz_create_output_config(
		VL53LMZ_Configuration	*p_dev );


/**
 * @brief This function sends the output configuration previously created by
 * vl53lmz_create_output_config() to the device. It then commands the device
 *	to start streaming data.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @return (uint8_t) status : 0 if OK
 */
uint8_t vl53lmz_send_output_config_and_start(
		VL53LMZ_Configuration	*p_dev );


/**
 * @brief This function adds the specified block header to the end of the
 * g_output_config list. It also enables this output in the g_output_bh_enable
 * structure.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint32_t) block_header : Block Header to add to output_config list.
 *	* @return (uint8_t) status : 0 if OK
 */
uint8_t vl53lmz_add_output_block(
		VL53LMZ_Configuration	*p_dev,
		uint32_t				block_header );


/**
 * @brief This function disables the specified block output in the
 * g_output_bh_enable structure. If the block is not in the g_output_config list
 * ,or, not enabled then it will do nothing (and return success).
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint32_t) block_header : Block Header to disable output_config list.
 *	* @return (uint8_t) status : 0 if OK
 */
uint8_t vl53lmz_disable_output_block(
		VL53LMZ_Configuration	*p_dev,
		uint32_t				block_header );


/**
 * @brief This function extracts the specified data block from a Results
 * packet of data.
 * @param (VL53LMZ_Configuration) *p_dev : VL53L5CX configuration structure.
 * @param (uint32_t) blk_index : Index of required block..
 * @param (uint8_t) *p_data : Pointer to the destination area to place the data.
 * @param (uint16_t)*data_size : This field must be the structure or array size
 * (using sizeof() function).
 * @return (uint8_t) status : 0 if OK
 */
uint8_t vl53lmz_results_extract_block(
		VL53LMZ_Configuration		*p_dev,
		uint32_t					blk_index,
		uint8_t						*p_data,
		uint16_t					data_size );


#endif //VL53LMZ_API_H_
