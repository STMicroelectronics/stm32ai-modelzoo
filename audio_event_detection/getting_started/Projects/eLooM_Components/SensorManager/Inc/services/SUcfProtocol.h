/**
  ******************************************************************************
  * @file    SUcfProtocol.h
  * @author  SRA - MCD
  * @brief
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file in
  * the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
#ifndef SENSORMANAGER_INC_SERVICES_SUCFPROTOCOL_H_
#define SENSORMANAGER_INC_SERVICES_SUCFPROTOCOL_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "ISensorLL.h"
#include "ISensorLL_vtbl.h"


/*
 * This comes from sensors PID (to avoid including one specific PID file)
 **/
#ifndef MEMS_UCF_SHARED_TYPES
#define MEMS_UCF_SHARED_TYPES

typedef struct
{
  uint8_t address;
  uint8_t data;
} ucf_line_t;

#endif /* MEMS_UCF_SHARED_TYPES */

/*
 * This is for compatibility with ispu
 **/
#ifndef MEMS_UCF_ISPU_SHARED_TYPES
#define MEMS_UCF_ISPU_SHARED_TYPES

#define MEMS_UCF_OP_WRITE 0
#define MEMS_UCF_OP_DELAY 1

typedef struct {
  uint8_t op;
  uint8_t address;
  uint8_t data;
} ucf_line_ispu_t;

#endif /* MEMS_UCF_ISPU_SHARED_TYPES */


/**
  * Create a type name for ::_SUcfProtocol_t
  */
typedef struct _SUcfProtocol_t SUcfProtocol_t;

/**
  * Sensor Query internal state.
  */
struct _SUcfProtocol_t
{
  /**
    * Specifies the sensor Low-Level interface.
    */
  ISensorLL_t *sensor_ll; 
};

/**
 *  Initialize the UCF protocol with a specific Sensor Low-level interface.
 *
 * @param _this [IN] specifies an ::SUcfProtocol_t object.
 * @param p_sensor_ll [IN] specifies a ::ISensorLL_t instance.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
sys_error_code_t UCFP_Init(SUcfProtocol_t *_this, ISensorLL_t *p_sensor_ll);

/**
 * Load the UCF into the using the SensorLL interface configured in the object.
 * This function expects a compressed UCF format:
 *
 * \code
 * +--------------+----------------+
 * | Standard UCF | Compressed UCF |
 * +--------------+----------------+
 * | Ac 01 00     | 0100           |
 * | WAIT 5       | W005           |
 * | Ac 10 76     | 1076           |
 * +--------------+----------------+
 * \endcode
 *
 *
 * @param _this [IN] specifies an ::SUcfProtocol_t object.
 * @param p_ucf [IN] specifies the compressed UCF buffer
 * @param size [IN] specifies the size [Bytes] of the compressed UCF buffer
 *
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
sys_error_code_t UCFP_LoadCompressedUcf(SUcfProtocol_t *_this, const char *p_ucf, uint32_t size);

/**
 * Load the UCF into the using the SensorLL interface configured in the object.
 * This function expects the Standard UCF format:
 *
 * \code
 * +--------------+----------------+
 * | Standard UCF | Compressed UCF |
 * +--------------+----------------+
 * | Ac 01 00     | 0100           |
 * | WAIT 5       | W005           |
 * | Ac 10 76     | 1076           |
 * +--------------+----------------+
 * \endcode
 *
 * @param _this [IN] specifies an ::SUcfProtocol_t object.
 * @param p_ucf [IN] specifies the UCF buffer
 * @param size [IN] specifies the size [Bytes] of the UCF buffer
 *
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 *
 */
sys_error_code_t UCFP_LoadUcf(SUcfProtocol_t *_this, const char *p_ucf, uint32_t size);

/**
 * Load the UCF using the SensorLL interface configured in the object.
 * This function expects an ucf_line_ispu_t array
 *
 * \code
 * const ucf_line_t ispu_conf[] = {
 *    { .op = MEMS_UCF_OP_WRITE, .address = 0x01, .data = 0x00 },
 *    { .op = MEMS_UCF_OP_DELAY, .address = 0, .data = 5 },
 *    { .op = MEMS_UCF_OP_WRITE, .address = 0x10, .data = 0x76 },
 *   };
 * \endcode
 *
 * @param _this [IN] specifies an ::SUcfProtocol_t object.
 * @param p_ucf [IN] specifies the UCF buffer int ::ucf_line_ext_t format
 * @param size [IN] specifies the size [Bytes] of the UCF buffer
 *
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 *
 */
sys_error_code_t UCFP_LoadUcfHeader(SUcfProtocol_t *_this, const ucf_line_ispu_t *p_ucf, uint32_t size);

/**
 * Get a string with the compressed UCF converted from a full one
 *
 * @param p_ucf [IN] specifies the UCF buffer
 * @param ucf_size [IN] specifies the size [Bytes] of the UCF buffer
 * @param p_compressed_ucf [OUT] pointer to a valid buffer where to put the compressed ucf
 * @param compressed_ucf_size [IN] specifies the size [Bytes] of the compressed UCF buffer
 * @param compressed_ucf_size_actual [OUT] specifies the actual size [Bytes] of the compressed UCF string
 *
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 *
 */
sys_error_code_t UCFP_GetCompressedUcf(const char *p_ucf, uint32_t ucf_size, char *p_compressed_ucf, uint32_t compressed_ucf_size, uint32_t *compressed_ucf_size_actual);

/**
 * Get a string with the compressed UCF converted from a full one
 *
 * @param p_compressed_ucf [IN] specifies the compressed UCF buffer
 * @param compressed_ucf_size [IN] specifies the size [Bytes] of the compressed UCF buffer
 * @param p_ucf [OUT] pointer to a valid buffer where to put the converted ucf
 * @param ucf_size [IN] specifies the size [Bytes] of the UCF buffer
 * @param ucf_size_actual [OUT] specifies the actual size [Bytes] of the compressed UCF string
 *
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 *
 */
sys_error_code_t UCFP_GetUcf(const char *p_compressed_ucf, uint32_t compressed_ucf_size, char *p_ucf, uint32_t ucf_size, uint32_t *ucf_size_actual);

/**
 * Get the estimated size of the ucf, given the compressed ucf size
 *
 * @param compressed_ucf_size [IN] specifies the size [Bytes] of the compressed UCF
 *
 * @return maximum size of the compressed UCF
 *
 */
uint32_t UCFP_UcfSize(uint32_t compressed_ucf_size);

/**
 * Get the estimated size of the compressed ucf, given the ucf file size
 *
 * @param ucf_size [IN] specifies the size [Bytes] of the UCF file to be converted.
 *
 * @return maximum size of the compressed UCF
 *
 */
uint32_t UCFP_CompressedUcfSize(uint32_t ucf_size);


#ifdef __cplusplus
}
#endif

#endif /* SENSORMANAGER_INC_SERVICES_SUCFPROTOCOL_H_ */
