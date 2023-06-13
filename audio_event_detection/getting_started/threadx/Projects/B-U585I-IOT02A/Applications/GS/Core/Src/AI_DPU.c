/**
 ******************************************************************************
 * @file    AI_DPU.c
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

/* Includes ------------------------------------------------------------------*/
#include "AI_DPU.h"
#include "AI_DPU_vtbl.h"
#include "services/sysmem.h"
#include "services/sysdebug.h"
#include "filter_gravity.h"
#include "aiTestHelper.h"

/* Private define ------------------------------------------------------------*/
#define SYS_DEBUGF(level, message)  SYS_DEBUGF3(SYS_DBG_AI, level, message)
#define AI_DPU_G_TO_MS_2 (9.8F)

#define AI_LOGGING_SHAPES_WIDTH  0
#define AI_LOGGING_SHAPES_HEIGHT 1
/**
 * Class object declaration.
 */
typedef struct _AI_DPU_Class
{
  /**
   * IDPU2_t class virtual table.
   */
  IDPU2_vtbl vtbl;

} AI_DPU_Class_t;

/* Objects instance */
/********************/

/**
 * The class object.
 */
static const AI_DPU_Class_t sTheClass =
{
    /* class virtual table */
    {
        ADPU2_vtblAttachToDataSource,
        ADPU2_vtblDetachFromDataSource,
        ADPU2_vtblAttachToDPU,
        ADPU2_vtblDetachFromDPU,
        ADPU2_vtblDispatchEvents,
        ADPU2_vtblRegisterNotifyCallback,
        AI_DPU_vtblProcess
    }
};

static void Preproc_3D_ACC(float *p_in,float *p_out,AI_DPU_t *p_obj)
{
  int nb_3_axis_sample = p_obj->super.in_data.shapes[AI_LOGGING_SHAPES_HEIGHT] ;
  assert_param(p_obj->scale != 0.0F);
  assert_param(p_obj->super.in_data.shapes[AI_LOGGING_SHAPES_WIDTH] == 3 );

#if CTRL_X_CUBE_AI_PREPROC==CTRL_AI_GRAV_ROT_SUPPR ||CTRL_X_CUBE_AI_PREPROC==CTRL_AI_GRAV_ROT
  for (int i=0 ; i < nb_3_axis_sample ; i++)  {
    float scale          = p_obj->scale;
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
#elif CTRL_X_CUBE_AI_PREPROC==CTRL_AI_SCALING
  for (int i=0 ; i < nb_3_axis_sample*3 ; i++){
    *p_out++ = *p_in++ * p_obj->scale;
  }
#else /* bypass */
  for (int i=0 ; i < nb_3_axis_sample*3 ; i++){
    *p_out++ = *p_in++;
  }
#endif
}

/* IDPU2 virtual functions definition */
/**************************************/
sys_error_code_t AI_DPU_vtblProcess(IDPU2_t *_this, EMData_t in_data, EMData_t out_data)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  AI_DPU_t *p_obj = (AI_DPU_t*)_this;
  ai_i32 batch;

  ai_u16 n_outputs;
  ai_buffer* ai_input  = ai_network_inputs_get(p_obj->net_exec_ctx->handle, NULL);
  ai_buffer* ai_output = ai_network_outputs_get(p_obj->net_exec_ctx->handle, &n_outputs);

#ifndef AI_NETWORK_INPUTS_IN_ACTIVATIONS
  ai_input->data = AI_HANDLE_PTR(p_obj->in);
#endif

#ifndef AI_NETWORK_OUTPUTS_IN_ACTIVATIONS
  ai_output[0].data = AI_HANDLE_PTR(p_obj->out1);
#if (AI_NETWORK_OUT_NUM==2)
  if (n_outputs==2){
    ai_output[1].data = AI_HANDLE_PTR(p_obj->out2);
  }
#endif
#endif

  if (p_obj->sensor_type==COM_TYPE_ACC)
  {
    Preproc_3D_ACC((float*)EMD_Data(&in_data),ai_input[0].data,p_obj);
  }
  else
  {
    ai_input[0].data = (ai_handle) EMD_Data(&in_data);
  }

  /* call Ai library. */
  batch = ai_network_run(p_obj->net_exec_ctx->handle, ai_input, ai_output);

  /* prepare output */
  if (batch != 1) aiLogErr(ai_network_get_error(p_obj->net_exec_ctx->handle),"ai_network_run");
  {
    float *p_out  = (float*)EMD_Data(&out_data);
    float *p_out0 = (float*)ai_output[0].data;
    int widthOut1, widthOut2;
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
  return res;
}


/* Exported functions --------------------------------------------------------*/

/* Public API functions definition */
/***********************************/
IDPU2_t *AI_DPU_Alloc(void)
{

  AI_DPU_t  *p_obj = (AI_DPU_t*) SysAlloc(sizeof(AI_DPU_t));

  if (p_obj != NULL)
  {
    ((IDPU2_t*)p_obj)->vptr = &sTheClass.vtbl;
  }
  return (IDPU2_t*)p_obj;
}

IDPU2_t *AI_DPU_StaticAlloc(void *p_mem_block)
{
  AI_DPU_t  *p_obj = (AI_DPU_t*) p_mem_block;

  if (p_obj != NULL)
  {
    ((IDPU2_t*)p_obj)->vptr = &sTheClass.vtbl;
  }
  return (IDPU2_t*)p_obj;
}

sys_error_code_t AI_DPU_SetSensitivity(AI_DPU_t *_this, float sensi)
{
  assert_param(_this != NULL);

  _this->scale = sensi * AI_DPU_G_TO_MS_2;

  return SYS_NO_ERROR_CODE;
}

sys_error_code_t AI_DPU_Init(AI_DPU_t *_this)
{
  assert_param(_this != NULL);

  /* Prepare the EMData_t to initialize the base class.*/
  EMData_t none = {0};
  _this->input_Q_inv_scale = 0.0F;
  _this->input_Q_offset    = 0;

  /*initialize the base class.*/
  if SYS_IS_ERROR_CODE(ADPU2_Init((ADPU2_t*)_this,none,none)){
    sys_error_handler();
  }
  return SYS_NO_ERROR_CODE;
}

static sys_error_code_t AiDPUCheckModel(AI_DPU_t *_this)
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
    if (AI_BUFFER_SHAPE_SIZE(p_buffer)                   != AI_DPU_SHAPE_SIZE        ||
        AI_BUFFER_SHAPE_ELEM(p_buffer, AI_SHAPE_BATCH)   >  AI_DPU_SHAPE_BATCH_MAX   ||
        AI_BUFFER_SHAPE_ELEM(p_buffer, AI_SHAPE_HEIGHT)  >  AI_DPU_SHAPE_HEIGHT_MAX  ||
        AI_BUFFER_SHAPE_ELEM(p_buffer, AI_SHAPE_WIDTH)   >  AI_DPU_SHAPE_WIDTH_MAX   ||
        AI_BUFFER_SHAPE_ELEM(p_buffer, AI_SHAPE_CHANNEL) >  AI_DPU_SHAPE_CHANNEL_MAX ||
        (AI_BUFFER_FMT_GET_TYPE(p_buffer->format)        != AI_BUFFER_FMT_TYPE_Q  &&
         AI_BUFFER_FMT_GET_TYPE(p_buffer->format)        != AI_BUFFER_FMT_TYPE_FLOAT))
    {
      res = SYS_INVALID_PARAMETER_ERROR_CODE;
    }
  }
  for (i=0; i< _this->net_exec_ctx->report.n_outputs ; i++ )
  {
    p_buffer = &_this->net_exec_ctx->report.outputs[i];
    if (AI_BUFFER_SHAPE_SIZE(p_buffer)                   != AI_DPU_SHAPE_SIZE       ||
        AI_BUFFER_SHAPE_ELEM(p_buffer, AI_SHAPE_BATCH)   >  AI_DPU_SHAPE_BATCH_MAX  ||
        AI_BUFFER_SHAPE_ELEM(p_buffer, AI_SHAPE_HEIGHT)  >  AI_DPU_SHAPE_HEIGHT_MAX ||
        AI_BUFFER_SHAPE_ELEM(p_buffer, AI_SHAPE_WIDTH)   >  AI_DPU_SHAPE_WIDTH_MAX  ||
        AI_BUFFER_SHAPE_ELEM(p_buffer, AI_SHAPE_CHANNEL) >  AI_DPU_SHAPE_CHANNEL_MAX||
        AI_BUFFER_FMT_GET_TYPE(p_buffer->format)         != AI_BUFFER_FMT_TYPE_FLOAT)
    {
      res = SYS_INVALID_PARAMETER_ERROR_CODE;
    }
  }

  if (res != SYS_NO_ERROR_CODE)
  {
    SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("AI_DPU: Model check failed \r\n"));
  }

  return res;
}

sys_error_code_t AiDPULoadModel(AI_DPU_t *_this, const char *name)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  ai_error err;
  EMData_t in_data, out_data;
  int widthIn,heigtIn,nOut;
  ai_handle activation_buffers[] = { _this->activation_buffer};
  int widthOut1 = 0;
  int widthOut2 = 0;
  ai_buffer input;

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
  input= _this->net_exec_ctx->report.inputs[0];

  /* init input data streams  */
  if ((_this->net_exec_ctx->report.n_inputs == 1) \
      && (AI_BUFFER_FMT_GET_TYPE(input.format)==AI_BUFFER_FMT_TYPE_FLOAT))
  {
#ifdef CTRL_X_CUBE_AI_VECTORIZE
    assert_param(AI_BUFFER_SHAPE_ELEM(&_this->net_exec_ctx->report.inputs[0], AI_SHAPE_CHANNEL)%AI_DPU_NB_AXIS==0);
    widthIn = AI_DPU_NB_AXIS;
    heigtIn = AI_BUFFER_SHAPE_ELEM(&_this->net_exec_ctx->report.inputs[0], AI_SHAPE_CHANNEL)/widthIn;
#else
    widthIn = AI_BUFFER_SHAPE_ELEM(&input, AI_SHAPE_WIDTH) ;
    heigtIn = AI_BUFFER_SHAPE_ELEM(&input, AI_SHAPE_HEIGHT);
#endif

#if CTRL_X_CUBE_AI_SENSOR_TYPE==COM_TYPE_ACC
    assert_param(widthIn==AI_DPU_NB_AXIS);
#endif

    if SYS_IS_ERROR_CODE(EMD_Init(&in_data, NULL, E_EM_FLOAT, E_EM_MODE_LINEAR,2 ,widthIn, heigtIn)){
      sys_error_handler();
    }
  }
  else if ((_this->net_exec_ctx->report.n_inputs == 1) \
      && (AI_BUFFER_FMT_GET_TYPE(input.format)==AI_BUFFER_FMT_TYPE_Q))
  {
    widthIn = AI_BUFFER_SHAPE_ELEM(&input, AI_SHAPE_WIDTH) ;
    heigtIn = AI_BUFFER_SHAPE_ELEM(&input, AI_SHAPE_HEIGHT);

    if SYS_IS_ERROR_CODE(EMD_Init(&in_data, NULL, E_EM_INT8, E_EM_MODE_LINEAR,2 ,widthIn, heigtIn)){
      sys_error_handler();
    }

    if (AI_BUFFER_FMT_TYPE_Q != AI_BUFFER_FMT_GET_TYPE(input.format) &&\
      ! AI_BUFFER_FMT_GET_SIGN(input.format) &&\
      8 != AI_BUFFER_FMT_GET_BITS(input.format))
    {
        SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("E: expected signed integer 8 bits\r\n"));
        return -1;
    }
    if (AI_BUFFER_META_INFO_INTQ(input.meta_info)) {
        float scale = AI_BUFFER_META_INFO_INTQ_GET_SCALE(input.meta_info, 0);
        if ( scale !=0 ){
          _this->input_Q_inv_scale =  1 / scale ;
          _this->input_Q_offset = AI_BUFFER_META_INFO_INTQ_GET_ZEROPOINT(input.meta_info, 0);
        }
    }
    else {
      SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("E: no meta info\r\n"));
      return -1;
    }
  }
  else
  {
    sys_error_handler();
  }
  /* init output data streams  */
  nOut = _this->net_exec_ctx->report.n_outputs;
  if (nOut == 2 )
  {
    widthOut2 = AI_BUFFER_SHAPE_ELEM(&_this->net_exec_ctx->report.outputs[1], AI_SHAPE_CHANNEL);
  }
  if (nOut == 1 || nOut == 2)
  {
    widthOut1 = AI_BUFFER_SHAPE_ELEM(&_this->net_exec_ctx->report.outputs[0], AI_SHAPE_CHANNEL);
  }
  else
  {
    sys_error_handler();
  }

  if SYS_IS_ERROR_CODE(EMD_Init(&out_data, NULL, E_EM_FLOAT, E_EM_MODE_LINEAR, 1,widthOut1+widthOut2))
	{
    sys_error_handler();
	}

  _this->super.in_data  = in_data;
  _this->super.out_data = out_data;

  return res;
}

sys_error_code_t AiDPUReleaseModel(AI_DPU_t *_this)
{
  assert_param(_this != NULL);
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
