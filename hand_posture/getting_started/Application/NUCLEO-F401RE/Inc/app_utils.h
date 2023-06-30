/**
 ******************************************************************************
 * @file    app_utils.h
 * @author  MCD Application Team
 * @brief   Library to manage application related operation
 ******************************************************************************
 * @attention
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

#ifndef INC_APP_UTILS_H_
#define INC_APP_UTILS_H_

/* Includes ------------------------------------------------------------------*/
#include "stm32f4xx_hal.h"
#include "vl53lmz_api.h"
#include "network.h"

#include <stdbool.h>

/* Exported macro ------------------------------------------------------------*/

/* Network-related macro ---------*/
/* Maximum number of zones */
#define SENSOR__MAX_NB_OF_ZONES                   (64)
/* Max distance software limit */
#define HANDPOSTURE_APP_MAX_DISTANCE_MM           (400)
/* Used if the zone is not valid */
#define DEFAULT_RANGING_VALUE                     (4000)
/* Used if the zone is not valid */
#define DEFAULT_SIGNAL_VALUE                      (0)
/* Median */
#define NORMALIZATION_RANGING_CENTER              (295)
/* Interquartile range */
#define NORMALIZATION_RANGING_IQR                 (196)
/* Median */
#define NORMALIZATION_SIGNAL_CENTER               (281)
/* Interquartile range */
#define NORMALIZATION_SIGNAL_IQR                  (452)
/* Number of output class filtering */
#define LABEL_FILTER_N                            (3)
/* Keep last class valid until a new one is detected */
#define KEEP_LAST_VALID                           (1)
/* Conversion from 14.2 fixed point values to floating point */
#define FIXED_POINT_14_2_TO_FLOAT                 (4.0)
/* Conversion from 21.11 fixed point values to floating point */
#define FIXED_POINT_21_11_TO_FLOAT                (2048.0)

/* Communication-related macro ---*/
/* UART buffer size */
#define UART_BUFFER_SIZE                          (2048)

/* Sensor-related macro ----------*/
#define XTALK_MARGIN                              (50)
#define MILLIHERTZ_TO_HERTZ                       (1000)
#define RESOLUTION_16                             (16)
/* To select strongest (default) or closest target first */
#define DEV_PSORT_CFG_IDX                         ((uint16_t) 0xae64)
/* Definition of default Gesture algo settings */
#define DEFAULT_GESTURE_APP_RANGING_PERIOD        (100)
#define DEFAULT_GESTURE_APP_INTEGRATION_TIME      (10)
#define MAX_COMMAND_BUFFER_SIZE 776

/* Exported types ------------------------------------------------------------*/
struct pipe_grp__sort__cfg_t
{
  uint8_t sort__target_order;
  uint8_t sort__cfg__pad_0;
  uint8_t sort__cfg__pad_1;
  uint8_t sort__cfg__pad_2;
};

/** @struct dci_grp__dss_cfg_t
*   @brief DSS Configuration Parameters
*   @{
*/
struct dci_grp__dss_cfg_t {
  /**
   * - max_value = 4095
   * - min_value = 0
   * - format = unsigned 12.4
   * - units = Mcps
   * - resolution = 0.0625
  */
  uint16_t dss__lower_target_rate_mcps;
  /**
   * - max_value = 4095
   * - min_value = 0
   * - format = unsigned 12.4
   * - units = Mcps
   * - resolution = 0.0625
  */
  uint16_t dss__upper_target_rate_mcps;
  /**
   * - max_value = 4095
   * - min_value = 0
   * - format = unsigned 12.4
   * - units = effective SPAD's
   * - resolution = 0.0625
  */
  uint16_t dss__initial_effective_spads;
  /**
   * - max_value = 4095
   * - min_value = 0
   * - format = unsigned 12.4
   * - units = effective SPAD's
   * - resolution = 0.0625
  */
  uint16_t dss__min_effective_spads;
  /**
   * - max_value = 4095
   * - min_value = 0
   * - format = unsigned 12.4
   * - units = effective SPAD's
   * - resolution = 0.0625
  */
  uint16_t dss__max_effective_spads;
  /**
   * - max_value = 2
   * - min_value = 0
   * - format = unsigned 2.0
  */
  uint8_t dss__additional_steps;
  uint8_t dss__mode;
  /**
   * - max_value = 1
   * - min_value = 0
   * - format = unsigned 1.7
   * - resolution = 0.0078
  */
  uint8_t dss__spatial_mode;
  uint8_t dss_cfg__spare_0;
  uint8_t dss_cfg__spare_1;
  uint8_t dss_cfg__spare_2;
};


union dci_union__block_header_u {
  uint32_t bytes;
  struct {

    uint32_t p_type : 4;

    uint32_t b_size__p_rep : 12;

    uint32_t b_idx__p_idx : 16;
  };
};

struct dci_grp__rng_repeat_cfg_t {
  uint16_t rng_repeat__ranging_rate_hz;
  uint16_t rng_repeat__fw_per_range_overhead_us;
};

struct fw_grp__analogue_dynamic_t {
  uint16_t pll_fm_depth;
  uint16_t pll_fm_freq;
  uint8_t vcsel_sel_ctrl_0;
  uint8_t vcsel_sel_ctrl_1;
  uint8_t vcsel_mon_ctrl;
  uint8_t vcselcp_sel_ovrcur_ctrl;
  uint8_t vcselcp_clk_range_sel;
  uint8_t sequencer_output_delay;
  uint8_t vcselcp_bootup_fsm_ext_en;
  uint8_t vcsel_atest1_sel;
  uint8_t vcselcp_mini_sel;
  uint8_t vcselcp_reg_sel;
  uint8_t analogue_dynamic_pad_0;
  uint8_t analogue_dynamic_pad_1;
};

struct Params_t {
  /* Enable a specific data logging on the Uart for the GUI */
  int gesture_gui;
  /* Sensor resolution, only 64 is available */
  uint32_t Resolution;
  /* Ranging period in ms */
  int RangingPeriod;
  /* Integration time in ms */
  int IntegrationTime;
};

typedef struct {
  int start;
  int stop;
  int get_caldata;
  uint8_t buffer[MAX_COMMAND_BUFFER_SIZE];
  int calibrate;
} CommandData_t;

typedef struct {
  long timestamp_ms;
  uint8_t target_status[SENSOR__MAX_NB_OF_ZONES];
  uint8_t nb_targets[SENSOR__MAX_NB_OF_ZONES];
  float ranging[SENSOR__MAX_NB_OF_ZONES];
  float peak[SENSOR__MAX_NB_OF_ZONES]; /* Distance [mm] */
} HANDPOSTURE_Input_Data_t;

typedef struct {
  /* Internals */
  uint8_t is_valid_frame;
  uint8_t previous_label;
  uint8_t label_count;
  /* Outputs */
  uint8_t model_output;
  uint8_t handposture_label;
} HANDPOSTURE_Data_t;

typedef struct
{
  /* App context */
  bool app_run;
  struct Params_t Params;

  /* Sensor context */
  VL53LMZ_Configuration ToFDev;
  VL53LMZ_Platform p_platform;
  VL53LMZ_ResultsData RangingData;
  volatile int IntrCount;
  bool new_data_received;
  bool params_modif;

  /* NN context */
  HANDPOSTURE_Input_Data_t HANDPOSTURE_Input_Data;
  HANDPOSTURE_Data_t AI_Data;
  float aiInData[AI_NETWORK_IN_1_SIZE];
  float aiOutData[AI_NETWORK_OUT_1_SIZE];

  /* Comm context */
  volatile char Uart_RXBuffer[UART_BUFFER_SIZE];
  char Comm_RXBuffer[UART_BUFFER_SIZE];
  volatile size_t Uart_RxRcvIndex;
  volatile uint32_t Uart_nOverrun;
  volatile uint8_t UartComm_CmdReady;
  uint32_t frame_count;
} AppConfig_TypeDef;

#endif /* INC_APP_UTILS_H_ */
