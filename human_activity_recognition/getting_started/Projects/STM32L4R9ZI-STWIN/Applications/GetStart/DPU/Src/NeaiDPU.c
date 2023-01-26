/**
  ******************************************************************************
  * @file    NeaiDPU.c
  * @author  SRA - MCD
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

#include "NeaiDPU.h"
#include "NeaiDPU_vtbl.h"
#include "knowledge_ncc.h"
#include "services/sysdebug.h"

#define SYS_DEBUGF(level, message)  SYS_DEBUGF3(SYS_DBG_NAI, level, message)

/**
* Specified the virtual table for the NeaiDPU_t class.
*/
static const IDPU_vtbl sNeaiDPU_vtbl = {
  NeaiDPU_vtblInit,
  ADPU_AttachToSensor_vtbl,
  ADPU_DetachFromSensor_vtbl,
  ADPU_AttachInputADPU_vtbl,
  ADPU_DetachFromADPU_vtbl,
  ADPU_DispatchEvents_vtbl,
  ADPU_RegisterNotifyCallbacks_vtbl,
  NeaiDPU_vtblProcess
};


/* Inline functions definition */
/*******************************/


/* GCC requires one function forward declaration in only one .c source
* in order to manage the inline.
* See also http://stackoverflow.com/questions/26503235/c-inline-function-and-gcc
*/
#if defined (__GNUC__) || defined (__ICCARM__)
extern ENeaiMode_t NeaiDPUGetProcessingMode(NeaiDPU_t *_this);
extern float NeaiDPUGetProcessResult(NeaiDPU_t *_this);
#endif


/* Private member function declaration */
/***************************************/

/**
* Check if the DPU is initialized and ready to receive and process data.
*
* @param _this [IN] specifies a pointer to the object.
* @return TRUE if the object is initialized, FALSE otherwise.
*/
static inline boolean_t NeaiDPUAreStreamsInitialized(NeaiDPU_t *_this);


/* Public API functions definition */
/***********************************/

IDPU *NeaiDPUAlloc()
{
  IDPU *p_obj = (IDPU*) pvPortMalloc(sizeof(NeaiDPU_t));
  
  if (p_obj != NULL)
  {
    p_obj->vptr = &sNeaiDPU_vtbl;
  }
  
  return p_obj;
}

IDPU *NeaiDPUStaticAlloc(void *p_mem_block)
{
  IDPU *p_obj = (IDPU*)p_mem_block;
  if (p_obj != NULL)
  {
    p_obj->vptr = &sNeaiDPU_vtbl;
  }
  
  return p_obj;
}

sys_error_code_t NeaiDPUSetProcessingMode(NeaiDPU_t *_this, ENeaiMode_t mode)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  switch (mode) {
    case E_NEAI_MODE_NONE:
      _this->proc_mode                    = mode;
    case E_NEAI_ANOMALY_LEARN:
      _this->proc_init.anomalyInit        = neai_anomalydetection_init;
      _this->proc.anomalyLearn            = neai_anomalydetection_learn;
      _this->proc_mode                    = mode;
      break;
    case E_NEAI_ANOMALY_DETECT:
      _this->proc_init.anomalyInit        = neai_anomalydetection_init;
      _this->proc.anomalyDetect           = neai_anomalydetection_detect;
	  _this->proc_mode                    = mode;
	  break;
    case E_NEAI_CLASSIFICATION:
      _this->proc_init.classificationInit = neai_classification_init_ncc;
	  _this->proc.classification          = neai_classification_ncc;
      _this->proc_mode                    = mode;
	  break;
    case E_NEAI_ONE_CLASS:
    case E_NEAI_EXTRAPOLATION:
    default:
	  res = SYS_NOT_IMPLEMENTED_ERROR_CODE;
   }
   return res;
}

sys_error_code_t NeaiDPUProcessingInitialize(NeaiDPU_t *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  switch (_this->proc_mode) {
    case E_NEAI_ANOMALY_LEARN:
    case E_NEAI_ANOMALY_DETECT:
    	_this->proc_init.anomalyInit();
    	break;
    case E_NEAI_CLASSIFICATION:
    	_this->proc_init.classificationInit(knowledge_ncc);
    	break;
    case E_NEAI_MODE_NONE:
    case E_NEAI_ONE_CLASS:
    case E_NEAI_EXTRAPOLATION:
    default:
    	res = SYS_NOT_IMPLEMENTED_ERROR_CODE;
   }
   return res;
}
uint32_t NeaiDPUSetStreamsParam(NeaiDPU_t *_this, uint16_t signal_size, uint8_t axes, uint8_t cb_items)
{
  assert_param(_this != NULL);
  
  if (!NeaiDPUAreStreamsInitialized(_this))
  {
    /* DPU has been already initialized, so first reset it, if needed */
  }
  
  /* DPU converts input data in float */
  _this->super.dpuWorkingStream.packet.payload_type  = AI_FMT;
  _this->super.dpuWorkingStream.packet.payload_fmt   = AI_SP_FMT_FLOAT32_RESET();
  _this->super.dpuWorkingStream.packet.shape.n_shape = 2;
  _this->super.dpuWorkingStream.packet.shape.shapes[AI_LOGGING_SHAPES_WIDTH]  = axes ;
  _this->super.dpuWorkingStream.packet.shape.shapes[AI_LOGGING_SHAPES_HEIGHT] = signal_size ;

    /* Initialize the out stream */
  _this->super.dpuOutStream.packet.payload_type  = AI_FMT;
  _this->super.dpuOutStream.packet.payload_fmt   = AI_SP_FMT_FLOAT32_RESET();
  _this->super.dpuOutStream.packet.shape.n_shape = 0;
  _this->super.dpuOutStream.packet.payload_size = sizeof(float);
  _this->super.dpuOutStream.packet.payload      = (uint8_t*)&_this->neai_out;

  /* compute the size in byte of one cb item, */
  _this->super.n_bytes_for_item =  axes * signal_size * sizeof(float);
  _this->super.cb_items         = cb_items;
  
  _this->stream_ready = TRUE;
  
  return (cb_items * _this->super.n_bytes_for_item);
}

sys_error_code_t NeaiDPUPrepareToProcessData(NeaiDPU_t *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  
  ADPU_Reset((ADPU*)_this);
  _this->neai_out = 0.0f;
  
  return res;
}

sys_error_code_t NeaiDPUSetSensitivity(NeaiDPU_t *_this, float sensitivity)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  
  _this->sensitivity = sensitivity;
  
  neai_anomalydetection_set_sensitivity(_this->sensitivity);
  
  return res;
}


/* IDPU virtual functions definition */
/*************************************/

sys_error_code_t NeaiDPU_vtblInit(IDPU *_this) {
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  NeaiDPU_t *p_obj =(NeaiDPU_t*)_this;
  
  res = ADPU_Init_vtbl(_this);
  if (!SYS_IS_ERROR_CODE(res)) {
    p_obj->neai_out = 0;
    p_obj->stream_ready = FALSE;
    /* take the ownership of the Sensor Event IF */
    IEventListenerSetOwner((IEventListener *) ADPU_GetEventListenerIF(&p_obj->super), &p_obj->super);
    
    /* initialize AI libraries */
    NeaiDPUSetProcessingMode(p_obj,E_NEAI_CLASSIFICATION);
    NeaiDPUProcessingInitialize(p_obj);
    NeaiDPUSetProcessingMode(p_obj,E_NEAI_ANOMALY_LEARN);
    NeaiDPUProcessingInitialize(p_obj);
  }
  return res;
}

sys_error_code_t NeaiDPU_vtblProcess(IDPU *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  ADPU * super = (ADPU*)_this;
  NeaiDPU_t *p_obj = (NeaiDPU_t*)_this;
  
  CBItem **p_consumer_buff = NULL;
  CircularBuffer *p_circular_buffer = NULL;
  
  /* DPU has the priority */
  if(!super->isADPUattached)
  {
    for(int i=0; i < ADPU_CFG_MAX_SENSOR; i++)
    {
      if(super->sensors[i].sensorIF != NULL)
      {
        uint32_t sensor_ready = CB_GetReadyItemFromTail(super->sensors[i].cb_handle.pCircularBuffer, &super->sensors[i].cb_handle.pConsumerDataBuff);
        if(sensor_ready == CB_NO_READY_ITEM_ERROR_CODE)
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
    if(process_ready == CB_NO_READY_ITEM_ERROR_CODE)
    {
      return xRes;
    }
    p_consumer_buff = &super->AttachedAdpu.cb_handle.pConsumerDataBuff;
    p_circular_buffer = super->AttachedAdpu.cb_handle.pCircularBuffer;
  }
  
  if ((*p_consumer_buff) != NULL)
  {
	enum neai_state status;
    float *p_signal =  (float*) CB_GetItemData((*p_consumer_buff));
    if (p_obj->proc_mode ==  E_NEAI_ANOMALY_LEARN && p_obj->proc.anomalyLearn)
    {
      status = p_obj->proc.anomalyLearn(p_signal);
      p_obj->neai_out = (float) status;
   }
    else if (p_obj->proc_mode ==  E_NEAI_ANOMALY_DETECT && p_obj->proc.anomalyDetect)
	{
	  uint8_t proc_out;
	  status = p_obj->proc.anomalyDetect(p_signal,&proc_out);
	  p_obj->neai_out = (float) proc_out;
	}

    else if (p_obj->proc_mode ==  E_NEAI_CLASSIFICATION && p_obj->proc.classification)
	{
	  uint16_t id_class;
	  float    output_buffer[CLASS_NUMBER_NCC];
	  status = p_obj->proc.classification(p_signal,output_buffer,&id_class);
	  p_obj->neai_out = (float) id_class;
	}
    else
    {
      SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("NEAI mode (% d) not initialized\r\n", p_obj->proc_mode));
      xRes = SYS_UNDEFINED_ERROR_CODE;
    }

    /* release the buffer as soon as possible */
    CB_ReleaseItem(p_circular_buffer, (*p_consumer_buff));
    (*p_consumer_buff) = NULL;
    if (xRes == SYS_NO_ERROR_CODE)
    {
      if (status != NEAI_OK)
      {
       	if (status == NEAI_INIT_FCT_NOT_CALLED)
			SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("NEAI Init function not called\r\n"));
		else if (status == NEAI_NOT_ENOUGH_CALL_TO_LEARNING)
			SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("NEAI need more learning signals \r\n"));
		else if (status == NEAI_MINIMAL_RECOMMENDED_LEARNING_DONE)
			SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("NEAI minimal recommended learning done \r\n"));
		else
			SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("NEAI (mode % d ) status :  %d \r\n", p_obj->proc_mode, status));
      }
      if (status == NEAI_NOT_ENOUGH_CALL_TO_LEARNING || status == NEAI_MINIMAL_RECOMMENDED_LEARNING_DONE || status == NEAI_OK ) /* OK status, forward to listener */
      {
        ProcessEvent evt_acc;
		ProcessEventInit((IEvent*)&evt_acc, super->pProcessEventSrc, (ai_logging_packet_t*)&super->dpuOutStream, ADPU_GetTag(super));
		IDPU_DispatchEvents(_this, &evt_acc);
      }
    }
  }
  return xRes;
}

/* Private member function definition */
/**************************************/

static inline boolean_t NeaiDPUAreStreamsInitialized(NeaiDPU_t *_this)
{
  assert_param(_this != NULL);
  
  return _this->stream_ready;
}
