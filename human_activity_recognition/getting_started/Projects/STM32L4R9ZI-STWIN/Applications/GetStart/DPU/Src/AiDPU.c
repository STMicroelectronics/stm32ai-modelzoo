/**
 ******************************************************************************
 * @file    AiDPU.c
 * @author  STMicroelectronics - AIS - MCD Team
 * @brief
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

#include "AiDPU.h"
#include "AiDPU_vtbl.h"
#include "services/sysdebug.h"
#include "filter_gravity.h"
#include "aiTestHelper.h"

#include <stdio.h>

#define AIDPU_G_TO_MS_2 (9.8F)

/**
 * Specified the virtual table for the AiDPU_t class.
 */
static const IDPU_vtbl sAiDPU_vtbl = {
    AiDPU_vtblInit,
    ADPU_AttachToSensor_vtbl,
    ADPU_DetachFromSensor_vtbl,
    ADPU_AttachInputADPU_vtbl,
    ADPU_DetachFromADPU_vtbl,
    ADPU_DispatchEvents_vtbl,
    ADPU_RegisterNotifyCallbacks_vtbl,
    AiDPU_vtblProcess,
};

/* Public API functions definition */
/***********************************/

IDPU *AiDPUAlloc() {
  IDPU *p_obj = (IDPU*) pvPortMalloc(sizeof(AiDPU_t));

  if (p_obj != NULL)
  {
    p_obj->vptr = &sAiDPU_vtbl;
  }
  return p_obj;
}

IDPU *AiDPUStaticAlloc(void *p_mem_block)
{
  IDPU *p_obj = (IDPU*)p_mem_block;
  if (p_obj != NULL)
  {
    p_obj->vptr = &sAiDPU_vtbl;
  }

  return p_obj;
}

sys_error_code_t AiDPUSetSensitivity(AiDPU_t *_this, float sensi)
{
  assert_param(_this != NULL);

  _this->scale = sensi * AIDPU_G_TO_MS_2;

  return SYS_NO_ERROR_CODE;
}

static sys_error_code_t AiDPUCheckModel(AiDPU_t *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  int i;
  const ai_buffer *p_buffer;

  if (_this->net_exec_ctx->report.api_version.major != AI_DPU_X_CUBE_AI_API_MAJOR ||
      _this->net_exec_ctx->report.api_version.minor != AI_DPU_X_CUBE_AI_API_MINOR ||
      _this->net_exec_ctx->report.api_version.micro != AI_DPU_X_CUBE_AI_API_MICRO )
  {
    res = SYS_INVALID_PARAMETER_ERROR_CODE;
  }
  if (_this->net_exec_ctx->report.n_inputs > AI_DPU_NB_MAX_INPUT )
  {
    res = SYS_INVALID_PARAMETER_ERROR_CODE;
  }
  if (_this->net_exec_ctx->report.n_outputs > AI_DPU_NB_MAX_OUTPUT )
  {
    res = SYS_INVALID_PARAMETER_ERROR_CODE;
  }
  for (i=0; i< _this->net_exec_ctx->report.n_inputs ; i++ )
  {
    p_buffer = &_this->net_exec_ctx->report.inputs[i];
    if ((AI_BUFFER_SHAPE_SIZE(p_buffer) != AI_DPU_SHAPE_SIZE)                         ||
        (AI_BUFFER_SHAPE_ELEM(p_buffer, AI_SHAPE_BATCH)   >  AI_DPU_SHAPE_BATCH_MAX)  ||
        (AI_BUFFER_SHAPE_ELEM(p_buffer, AI_SHAPE_HEIGHT)  >  AI_DPU_SHAPE_HEIGHT_MAX) ||
        (AI_BUFFER_SHAPE_ELEM(p_buffer, AI_SHAPE_WIDTH)   >  AI_DPU_SHAPE_WIDTH_MAX)  ||
        (AI_BUFFER_SHAPE_ELEM(p_buffer, AI_SHAPE_CHANNEL) >  AI_DPU_SHAPE_CHANNEL_MAX)||
        (AI_BUFFER_FMT_GET_TYPE(p_buffer->format)         != AI_DPU_DATA_TYPE))
    {
      res = SYS_INVALID_PARAMETER_ERROR_CODE;
    }
  }
  for (i=0; i< _this->net_exec_ctx->report.n_outputs ; i++ )
  {
    p_buffer = &_this->net_exec_ctx->report.outputs[i];
    if ((AI_BUFFER_SHAPE_SIZE(p_buffer) != AI_DPU_SHAPE_SIZE)                         ||
        (AI_BUFFER_SHAPE_ELEM(p_buffer, AI_SHAPE_BATCH)   >  AI_DPU_SHAPE_BATCH_MAX)  ||
        (AI_BUFFER_SHAPE_ELEM(p_buffer, AI_SHAPE_HEIGHT)  >  AI_DPU_SHAPE_HEIGHT_MAX) ||
        (AI_BUFFER_SHAPE_ELEM(p_buffer, AI_SHAPE_WIDTH)   >  AI_DPU_SHAPE_WIDTH_MAX)  ||
        (AI_BUFFER_SHAPE_ELEM(p_buffer, AI_SHAPE_CHANNEL) >  AI_DPU_SHAPE_CHANNEL_MAX)||
        (AI_BUFFER_FMT_GET_TYPE(p_buffer->format)         != AI_DPU_DATA_TYPE))
    {
      res = SYS_INVALID_PARAMETER_ERROR_CODE;
    }
  }

  return res;
}

sys_error_code_t AiDPULoadModel(AiDPU_t *_this, const char *name)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  ai_error err;
  ai_handle activation_buffers[] = { _this->activation_buffer};

  /* Create and initialize an instance of the model */
  err = ai_network_create_and_init(&_this->net_exec_ctx->handle, activation_buffers, NULL);
  if (err.type != AI_ERROR_NONE) {
    aiLogErr(err, "ai_network_create_and_init");
    return -1;
  }

  ai_network_get_report(_this->net_exec_ctx->handle, &_this->net_exec_ctx->report);

  AiDPUCheckModel(_this);

  /* allocate input or outputs in case not allocated by the model */
  aiPrintNetworkInfo(&_this->net_exec_ctx->report);

  return res;
}
sys_error_code_t AiDPUReleaseModel(AiDPU_t *_this)
{
  assert_param(_this != NULL);
  //	  printf("Releasing %s...\r\n",_this->model_name);
  if (_this->net_exec_ctx->handle != AI_HANDLE_NULL) {
    if (ai_network_destroy(_this->net_exec_ctx->handle) != AI_HANDLE_NULL ){
      ai_error err;
      err = ai_network_get_error(_this->net_exec_ctx->handle);
      aiLogErr(err, "ai_network_destroy");
    }
    _this->net_exec_ctx->handle = AI_HANDLE_NULL;
  }
  return SYS_NO_ERROR_CODE;
}

uint16_t AiDPUSetStreamsParam(AiDPU_t *_this, uint8_t cb_items)
{
  assert_param(_this != NULL);

  if (_this->net_exec_ctx->report.n_inputs == 1)
    if (AI_BUFFER_FMT_GET_TYPE(_this->net_exec_ctx->report.inputs[0].format)==AI_BUFFER_FMT_TYPE_FLOAT)
    {
      int widthIn,heigtIn;
      _this->super.dpuWorkingStream.packet.payload_type  = AI_FMT;
      _this->super.dpuWorkingStream.packet.payload_fmt   = AI_SP_FMT_FLOAT32_RESET();
      _this->super.dpuWorkingStream.packet.shape.n_shape = 2 ;

#ifdef CTRL_X_CUBE_AI_VECTORIZE
      assert_param(AI_BUFFER_SHAPE_ELEM(&_this->net_exec_ctx->report.inputs[0], AI_SHAPE_CHANNEL)%AI_DPU_NB_AXIS==0);
      widthIn = AI_DPU_NB_AXIS;
      heigtIn = AI_BUFFER_SHAPE_ELEM(&_this->net_exec_ctx->report.inputs[0], AI_SHAPE_CHANNEL)/widthIn;
#else
      widthIn = AI_BUFFER_SHAPE_ELEM(&_this->net_exec_ctx->report.inputs[0], AI_SHAPE_WIDTH) ;
      heigtIn = AI_BUFFER_SHAPE_ELEM(&_this->net_exec_ctx->report.inputs[0], AI_SHAPE_HEIGHT);
      assert_param(widthIn==AI_DPU_NB_AXIS);
#endif
      _this->super.dpuWorkingStream.packet.shape.shapes[AI_LOGGING_SHAPES_WIDTH]  = widthIn;
      _this->super.dpuWorkingStream.packet.shape.shapes[AI_LOGGING_SHAPES_HEIGHT] = heigtIn;
      _this->super.n_bytes_for_item = widthIn*heigtIn*sizeof(float);
      _this->super.cb_items         = cb_items;

      if(_this->super.dpuOutStream.packet.payload != NULL)
      {
        vPortFree(_this->super.dpuOutStream.packet.payload);
      }
      if (_this->net_exec_ctx->report.n_outputs == 1 )
        if (AI_BUFFER_FMT_GET_TYPE(_this->net_exec_ctx->report.outputs[0].format)==AI_BUFFER_FMT_TYPE_FLOAT)
        {
          int widthOut1 = AI_BUFFER_SHAPE_ELEM(&_this->net_exec_ctx->report.outputs[0], AI_SHAPE_CHANNEL);
          _this->super.dpuOutStream.packet.shape.n_shape                         = 1;
          _this->super.dpuOutStream.packet.shape.shapes[AI_LOGGING_SHAPES_WIDTH] = 1;
          _this->super.dpuOutStream.packet.payload_type = AI_FMT;
          _this->super.dpuOutStream.packet.payload_fmt  = AI_SP_FMT_FLOAT32_RESET();
          _this->super.dpuOutStream.packet.payload_size =  (widthOut1)*sizeof(float);
          _this->super.dpuOutStream.packet.payload      =  pvPortMalloc(_this->super.dpuOutStream.packet.payload_size); // TODO to be deallocated somewhere
        }
      if (_this->net_exec_ctx->report.n_outputs == 2 )
        if (AI_BUFFER_FMT_GET_TYPE(_this->net_exec_ctx->report.outputs[0].format)==AI_BUFFER_FMT_TYPE_FLOAT)
          if (AI_BUFFER_FMT_GET_TYPE(_this->net_exec_ctx->report.outputs[1].format)==AI_BUFFER_FMT_TYPE_FLOAT)
          {
            int widthOut1 = AI_BUFFER_SHAPE_ELEM(&_this->net_exec_ctx->report.outputs[0], AI_SHAPE_CHANNEL);
            int widthOut2 = AI_BUFFER_SHAPE_ELEM(&_this->net_exec_ctx->report.outputs[1], AI_SHAPE_CHANNEL);		  /* Initialize the out stream */
            _this->super.dpuOutStream.packet.shape.n_shape                         = 1;
            _this->super.dpuOutStream.packet.shape.shapes[AI_LOGGING_SHAPES_WIDTH] = 2;
            _this->super.dpuOutStream.packet.payload_type = AI_FMT;
            _this->super.dpuOutStream.packet.payload_fmt  = AI_SP_FMT_FLOAT32_RESET();
            _this->super.dpuOutStream.packet.payload_size =  (widthOut1+widthOut2)*sizeof(float);
            _this->super.dpuOutStream.packet.payload      =  pvPortMalloc(_this->super.dpuOutStream.packet.payload_size); // TODO to be deallocated somewhere
          }
      /* compute the size in byte of one cb item, */
    }

  return (cb_items * _this->super.n_bytes_for_item);
}

sys_error_code_t AiDPUPrepareToProcessData(AiDPU_t *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  ADPU_Reset((ADPU*)_this);

  return res;
}


/* IDPU virtual functions definition */
/*************************************/

sys_error_code_t AiDPU_vtblInit(IDPU *_this) {
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  AiDPU_t *p_obj =(AiDPU_t*)_this;
  p_obj->scale = 1.0F;

  res = ADPU_Init_vtbl(_this);
  if (!SYS_IS_ERROR_CODE(res)) {
    p_obj->net_exec_ctx->handle = AI_HANDLE_NULL;

    // take the ownership of the Sensor Event IF
    IEventListenerSetOwner((IEventListener *) ADPU_GetEventListenerIF(&p_obj->super), &p_obj->super);
  }

  return res;
}

sys_error_code_t AiDPU_vtblProcess(IDPU *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  ADPU * super = (ADPU*)_this;
  AiDPU_t *p_obj = (AiDPU_t*)_this;
  CBItem **p_consumer_buff = NULL;
  CircularBuffer *p_circular_buffer = NULL;
  ai_i32 batch;

  //DPU has the priority
  if(!super->isADPUattached)
  {
    for(int i=0; i < ADPU_CFG_MAX_SENSOR; i++)
    {
      if(super->sensors[i].sensorIF != NULL)
      {
        uint32_t sensor_ready = CB_GetReadyItemFromTail(super->sensors[i].cb_handle.pCircularBuffer, &super->sensors[i].cb_handle.pConsumerDataBuff);
        if(sensor_ready == SYS_CB_NO_READY_ITEM_ERROR_CODE)
        {
          return SYS_NO_ERROR_CODE;
        }
        p_consumer_buff = &super->sensors[i].cb_handle.pConsumerDataBuff;
        p_circular_buffer = super->sensors[i].cb_handle.pCircularBuffer;
      }
    }
  }
  else
  {
    uint32_t process_ready = CB_GetReadyItemFromTail(super->AttachedAdpu.cb_handle.pCircularBuffer, &super->AttachedAdpu.cb_handle.pConsumerDataBuff);
    if(process_ready == SYS_CB_NO_READY_ITEM_ERROR_CODE)
    {
      return 0;
    }
    p_consumer_buff = &super->AttachedAdpu.cb_handle.pConsumerDataBuff;
    p_circular_buffer = super->AttachedAdpu.cb_handle.pCircularBuffer;
  }

  if ((*p_consumer_buff) != NULL)
  {
    assert_param(p_obj->scale != 0.0F);
    assert_param(p_obj->super.dpuWorkingStream.packet.shape.shapes[AI_LOGGING_SHAPES_WIDTH] = 3);
    ai_u16 n_outputs;
    float *p_in , *p_out ;
    int nb_3_axis_sample = p_obj->super.dpuWorkingStream.packet.shape.shapes[AI_LOGGING_SHAPES_HEIGHT] ;
    float scale          = p_obj->scale;
    ai_buffer* ai_input  = ai_network_inputs_get(p_obj->net_exec_ctx->handle, NULL);
    ai_buffer* ai_output = ai_network_outputs_get(p_obj->net_exec_ctx->handle, &n_outputs);

#ifndef AI_NETWORK_INPUTS_IN_ACTIVATIONS
    ai_input->data = AI_HANDLE_PTR(p_obj->in);
#endif
#ifndef AI_NETWORK_INPUTS_OUT_ACTIVATIONS
    ai_output[0].data = AI_HANDLE_PTR(p_obj->out1);
#if (AI_NETWORK_OUT_NUM==2)
    if (n_outputs==2){
      ai_output[1].data = AI_HANDLE_PTR(p_obj->out2);
    }
#endif
#endif

    p_in          = (float *)CB_GetItemData((*p_consumer_buff));
    p_out         = ai_input[0].data;

#if CTRL_X_CUBE_AI_PREPROC==CTRL_AI_GRAV_ROT_SUPPR ||CTRL_X_CUBE_AI_PREPROC==CTRL_AI_GRAV_ROT
    for (int i=0 ; i < nb_3_axis_sample ; i++)	{
      GRAV_input_t gravIn;
      GRAV_input_t gravOut;
      gravIn.AccX = *p_in++ * scale;
      gravIn.AccY = *p_in++ * scale;
      gravIn.AccZ = *p_in++ * scale;
#if CTRL_X_CUBE_AI_PREPROC==CTRL_AI_GRAV_ROT_SUPPR
      gravOut = gravity_suppress_rotate (&gravIn);
#elif CTRL_X_CUBE_AI_PREPROC==CTRL_AI_GRAV_ROT
      gravOut = gravity_rotate (&gravIn);
#endif
      *p_out++ = gravOut.AccX;
      *p_out++ = gravOut.AccY;
      *p_out++ = gravOut.AccZ;
    }
#else /* bypass */
    for (int i=0 ; i < nb_3_axis_sample*3 ; i++){
      *p_out++ = *p_in++ * scale;
    }
#endif

    /* call Ai library. */
    batch = ai_network_run(p_obj->net_exec_ctx->handle, ai_input, ai_output);

    /* prepare output */
    if (batch != 1) aiLogErr(ai_network_get_error(p_obj->net_exec_ctx->handle),"ai_network_run");
    {
      ai_logging_packet_t *p_pktOut = (ai_logging_packet_t*)&super->dpuOutStream;
      float * p_out = (float *) p_pktOut->payload;
      int widthOut1, widthOut2;
      float *p_out0 = (float*) ai_output[0].data;
      /* serialize outputs */
      widthOut1 = AI_BUFFER_SHAPE_ELEM(&p_obj->net_exec_ctx->report.outputs[0], AI_SHAPE_CHANNEL);
      for(int i= 0 ;  i < widthOut1 ; i++){
        *p_out++ = p_out0[i];
      }
      if (n_outputs==2){
        float *p_out1 = (float*) ai_output[1].data;
        widthOut2 = AI_BUFFER_SHAPE_ELEM(&p_obj->net_exec_ctx->report.outputs[1], AI_SHAPE_CHANNEL);
        for(int i= 0 ;  i < widthOut2 ; i++){
          *p_out++ = p_out1[i];
        }
      }
    }

    /* release the buffer as soon as possible */
    CB_ReleaseItem(p_circular_buffer, (*p_consumer_buff));
    (*p_consumer_buff) = NULL;

    ProcessEvent evt_acc;
    ProcessEventInit((IEvent*)&evt_acc, super->pProcessEventSrc, (ai_logging_packet_t*)&super->dpuOutStream, ADPU_GetTag(super));
    IDPU_DispatchEvents(_this, &evt_acc);
  }

  return xRes;
}

