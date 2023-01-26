/**
 ******************************************************************************
 * @file    stm32_app_main.c
 * @author  MCD/AIS Team
 * @brief   Minimal main template to use the STM AI generated c-model
 ******************************************************************************
 * @attention
 *
 * <h2><center>&copy; Copyright (c) 2019,2021 STMicroelectronics.
 * All rights reserved.</center></h2>
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */

#include <stdio.h>
#include <string.h>
#include <errno.h>

#include "network.h"
#include "network_data.h"

// #define USE_AI_REPORT

/* Global handle to reference the instantiated C-model */
static ai_handle network = AI_HANDLE_NULL;

/* Global c-array to handle the activations buffer(s) */
% for idx, act in enumerate(activations):
AI_ALIGNED(32)
static ai_u8 activations_${loop.index+1}[AI_${name.upper()}_DATA_ACTIVATION_${loop.index+1}_SIZE];
% endfor 

/* Array to store the data of the input tensors */
% for idx, input in enumerate(inputs):
  % if allocate_inputs:
/* -> data_in_${loop.index+1} is allocated in activations buffer */
  % else:
AI_ALIGNED(32) static ai_i8 data_in_${loop.index+1}[AI_${name.upper()}_IN_${loop.index+1}_SIZE_BYTES];
  % endif
% endfor

/* Array to store the data of the output tensors */
% for idx, output in enumerate(outputs):
  % if allocate_outputs:
/* -> data_out_${loop.index+1} is allocated in activations buffer */
  % else:
AI_ALIGNED(32) static ai_i8 data_out_${loop.index+1}[AI_${name.upper()}_OUT_${loop.index+1}_SIZE_BYTES];
  % endif
% endfor


/* Array of pointer to manage the model's input/output tensors */
static ai_buffer *ai_input;
static ai_buffer *ai_output;

#ifdef USE_AI_REPORT
static ai_network_report report;
#endif

/* 
 * Bootstrap
 */
int aiInit(void) {
  
  /* Create and initialize the c-model */
  const ai_handle acts[] = {
% for idx, act in enumerate(activations):
% if idx == len(activations) - 1: 
    activations_${loop.index+1}
% else:
    activations_${loop.index+1},
% endif
% endfor
  };

  ai_${name}_create_and_init(&network, acts, NULL);

  /* Reteive pointers to the model's input/output tensors */
  ai_input = ai_${name}_inputs_get(network, NULL);
  ai_output = ai_${name}_outputs_get(network, NULL);

  /* Set the @ of the input/output buffers when not allocated in the activations buffer */
% for idx, input in enumerate(inputs):
  % if allocate_inputs:
  /* -> ai_input[${loop.index}].data = ai_input[${loop.index}].data */
  % else:
  ai_input[${loop.index}].data = AI_HANDLE_PTR(data_in_${loop.index+1});
  % endif
% endfor
% for idx, output in enumerate(outputs):
  % if allocate_outputs:
  /* -> ai_output[${loop.index}].data = ai_output[${loop.index}].data */
  % else:
  ai_output[${loop.index}].data = AI_HANDLE_PTR(data_out_${loop.index+1});
  % endif
% endfor

#ifdef USE_AI_REPORT
  ai_${name}_get_report(network, &report);
#endif

  return 0;
}

/* 
 * Run inference
 */
int aiRun() {
  int res;

  res = ai_${name}_run(network, &ai_input[0], &ai_output[0]);
  
  return res;
}

/* 
 * Example of main loop function
 */
void main_loop() {

  aiInit();

  
  while (1) {
    /* 1 - Acquire, pre-process and fill the input buffers */
    // acquire_and_process_data(...);

    /* 2 - Call inference engine */
    aiRun();

    /* 3 - Post-process the predictions */
    // post_process(...);
  }
}


int main(int argc, char* argv[])
{
  errno = 0;
  main_loop();
}



void SystemInit(void)
{

}