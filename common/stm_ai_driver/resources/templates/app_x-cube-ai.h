
/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __APP_AI_H
#define __APP_AI_H
#ifdef __cplusplus
extern "C" {
#endif
/**
  ******************************************************************************
  * @file    app_x-cube-ai.h
  * @author  X-CUBE-AI C code generator
  * @brief   AI entry function definitions
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* Includes ------------------------------------------------------------------*/
#include "ai_platform.h"
#include "network.h"
#include "network_data.h"

#define MIN_HEAP_SIZE 0x800
#define MIN_STACK_SIZE 0x800

% if name!="network":
#error Invalid c-name
% endif

#define AI_MNETWORK_IN_NUM (${len(inputs)})

% for idx, input in enumerate(inputs):
	% if allocate_inputs:
#define AI_MNETWORK_IN_${loop.index+1}_SIZE_BYTES (1)
	% else:
#define AI_MNETWORK_IN_${loop.index+1}_SIZE_BYTES AI_NETWORK_IN_${loop.index+1}_SIZE_BYTES
	% endif
% endfor


#define AI_MNETWORK_OUT_NUM (${len(outputs)})

% for idx, output in enumerate(outputs):
	% if allocate_outputs:
#define AI_MNETWORK_OUT_${loop.index+1}_SIZE_BYTES (1)
	% else:
#define AI_MNETWORK_OUT_${loop.index+1}_SIZE_BYTES AI_NETWORK_OUT_${loop.index+1}_SIZE_BYTES
	% endif
% endfor


#define AI_NETWORK_DATA_ACTIVATIONS_START_ADDR 0xFFFFFFFF

#define AI_MNETWORK_DATA_ACTIVATIONS_INT_SIZE AI_NETWORK_DATA_ACTIVATIONS_SIZE


/* IO buffers ----------------------------------------------------------------*/

extern ai_i8* data_ins[];
extern ai_i8* data_outs[];

extern ai_handle data_activations0[];

void MX_X_CUBE_AI_Init(void);
void MX_X_CUBE_AI_Process(void);
/* USER CODE BEGIN includes */
/* USER CODE END includes */

/* Multiple network support --------------------------------------------------*/

typedef struct {
    const char *name;
    ai_buffer *config;
    ai_bool (*ai_data_params_get)(ai_network_params* params);
    ai_bool (*ai_get_report)(ai_handle network, ai_network_report* report);
    ai_error (*ai_create)(ai_handle* network, const ai_buffer* network_config);
    ai_error (*ai_get_error)(ai_handle network);
    ai_handle (*ai_destroy)(ai_handle network);
    ai_bool (*ai_init)(ai_handle network, const ai_network_params* params);
    ai_i32 (*ai_run)(ai_handle network, const ai_buffer* input, ai_buffer* output);
    ai_i32 (*ai_forward)(ai_handle network, const ai_buffer* input);
    ai_handle * activations;
} ai_network_entry_t;

#define AI_MNETWORK_NUMBER  (1)

AI_API_DECLARE_BEGIN

AI_API_ENTRY
const char* ai_mnetwork_find(const char *name, ai_int idx);

/*!
 * @brief Get network library report as a datastruct.
 * @ingroup network
 * @param[in] network: the handler to the network context
 * @param[out] report a pointer to the report struct where to
 * store network info. See @ref ai_network_report struct for details
 * @return a boolean reporting the exit status of the API
 */
AI_API_ENTRY
ai_bool ai_mnetwork_get_report(
ai_handle network, ai_network_report* report);

/*!
* @brief Get first network error code.
* @ingroup network
* @details Get an error code related to the 1st error generated during
* network processing. The error code is structure containing an
* error type indicating the type of error with an associated error code
* Note: after this call the error code is internally reset to AI_ERROR_NONE
* @param network an opaque handle to the network context
* @return an error type/code pair indicating both the error type and code
* see @ref ai_error for struct definition
*/
AI_API_ENTRY
ai_error ai_mnetwork_get_error(ai_handle network);

/*!
* @brief Create a neural network.
* @ingroup network
* @details Instantiate a network and returns an object to handle it;
* @param network an opaque handle to the network context
* @param network_config a pointer to the network configuration info coded as a
* buffer
* @return an error code reporting the status of the API on exit
*/
AI_API_ENTRY
ai_error ai_mnetwork_create(const char *name,
ai_handle* network, const ai_buffer* network_config);

/*!
* @brief Destroy a neural network and frees the allocated memory.
* @ingroup network
* @details Destroys the network and frees its memory. The network handle is returned;
* if the handle is not NULL, the unloading has not been successful.
* @param network an opaque handle to the network context
* @return an object handle : AI_HANDLE_NULL if network was destroyed
* correctly. The same input network handle if destroy failed.
*/
AI_API_ENTRY
ai_handle ai_mnetwork_destroy(ai_handle network);

/*!
* @brief Initialize the data structures of the network.
* @ingroup network
* @details This API initialized the network after a successfull
* @ref ai_network_create. Both the activations memory buffer
* and params (i.e. weights) need to be provided by caller application
*
* @param network an opaque handle to the network context
* @param params the parameters of the network (required).
* see @ref ai_network_params struct for details
* @return true if the network was correctly initialized, false otherwise
* in case of error the error type could be queried by
* using @ref ai_network_get_error
*/
AI_API_ENTRY
ai_bool ai_mnetwork_init(ai_handle network);

/*!
* @brief Run the network and return the output
* @ingroup network
*
* @details Runs the network on the inputs and returns the corresponding output.
* The size of the input and output buffers is stored in this
* header generated by the code generation tool. See AI_NETWORK_*
* defines into file @ref network.h for all network sizes defines
*
* @param network an opaque handle to the network context
* @param[in] input buffer with the input data
* @param[out] output buffer with the output data
* @return the number of input batches processed (default 1) or <= 0 if it fails
* in case of error the error type could be queried by
* using @ref ai_network_get_error
*/
AI_API_ENTRY
ai_i32 ai_mnetwork_run(
ai_handle network, const ai_buffer* input, ai_buffer* output);

/*!
* @brief Runs the network on the inputs.
* @ingroup network
*
* @details Differently from @ref ai_network_run, no output is returned, e.g. for
* temporal models with a fixed step size.
*
* @param network the network to be run
* @param[in] input buffer with the input data
* @return the number of input batches processed (usually 1) or <= 0 if it fails
* in case of error the error type could be queried by
* using @ref ai_network_get_error
*/
AI_API_ENTRY
ai_i32 ai_mnetwork_forward(
ai_handle network, const ai_buffer* input);

AI_API_ENTRY
int ai_mnetwork_get_private_handle(ai_handle network,
ai_handle *phandle,
ai_network_params* pparams);

AI_API_DECLARE_END
#ifdef __cplusplus
}
#endif
#endif /*__STMicroelectronics_X-CUBE-AI_7_2_0_H */
