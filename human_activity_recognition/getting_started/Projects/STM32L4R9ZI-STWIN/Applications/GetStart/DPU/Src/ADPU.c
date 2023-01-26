/**
  ******************************************************************************
  * @file    ADPU.c
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

#include "ADPU.h"
#include "ADPU_vtbl.h"
#include <string.h>

#include "features_extraction_loc.h"
#include "services/sysdebug.h"


/* Inline functions definition */
/*******************************/

/* GCC requires one function forward declaration in only one .c source
* in order to manage the inline.
* See also http://stackoverflow.com/questions/26503235/c-inline-function-and-gcc
*/
#if defined (__GNUC__) || defined (__ICCARM__)

#endif

/* Private functions declaration */
/*********************************/
static SensorObs_t *GetSensor(ADPU *_this, uint8_t id);
static void SetNextDPU(ADPU *_this, ADPU *target);
static sys_error_code_t CB_storing_int16_toInt16_helper(ADPU * _this, CBHandle_t *sTemp, AI_SP_Stream_t *stream );
static sys_error_code_t CB_storing_int16_toFloat_helper(ADPU * _this, CBHandle_t *sTemp, AI_SP_Stream_t *stream );
static sys_error_code_t CB_storing_float_toFloat_helper(ADPU * _this, CBHandle_t *sTemp, AI_SP_Stream_t *stream );

static sys_error_code_t ADPU_NotifyDPUDataReady_vtbl(IDPU *_this,  ProcessEvent *pxEvt);


static const ISensorEventListener_vtbl ADPUSensorListener_vtbl = {
  NULL,//Concrete class has to implement
  ADPU_SetOwner_vtbl,
  ADPU_GetOwner_vtbl,
  ADP_OnNewDataReady_vtbl
};


// IDPU virtual functions definition
// *****************************************
sys_error_code_t ADPU_Init_vtbl(IDPU *_this) 
{
  assert_param(_this);
  ADPU *pObj = (ADPU*)_this;
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  
  pObj->sensorListener.vptr = &ADPUSensorListener_vtbl;
  
  pObj->cb_items = 0;
  pObj->isADPUattached = 0;
  pObj->n_bytes_for_item = 0;
  pObj->p_callback_param = NULL;
  
  pObj->pProcessEventSrc = ProcessEventSrcAlloc();
  if (pObj->pProcessEventSrc == NULL) 
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_OUT_OF_MEMORY_ERROR_CODE);
    xRes = SYS_OUT_OF_MEMORY_ERROR_CODE;
    return xRes;
  }
  IEventSrcInit(pObj->pProcessEventSrc);
  pObj->active = true;
  
  return xRes;
}

sys_error_code_t ADPU_AttachToSensor_vtbl(IDPU *_this, ISourceObservable *s, void *buffer)
{
  assert_param(_this != NULL);
  assert_param(s != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  ADPU *pObj = (ADPU*)_this;
  
  uint8_t id = ISourceGetId(s);
  if(id > ADPU_CFG_MAX_SENSOR)
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
    xRes = SYS_UNDEFINED_ERROR_CODE;
    return xRes;
  }
  pObj->sensors[id].sensor_id = id;
  pObj->sensors[id].sensorIF = s;
  
  if(buffer != NULL)
  {
    pObj->sensors[id].cb_handle.pCircularBuffer = CB_Alloc(pObj->cb_items);
    if(CB_Init(pObj->sensors[ISourceGetId(s)].cb_handle.pCircularBuffer, buffer, pObj->n_bytes_for_item) != CB_NO_ERROR_CODE)
    {
      sys_error_handler();
    }
    
    pObj->sensors[id].cb_handle.pProducerDataBuff = NULL;
    pObj->sensors[id].cb_handle.pConsumerDataBuff = NULL;
    pObj->sensors[id].cb_handle.DataIdx = 0;
  }
  else
  {
    pObj->sensors[id].cb_handle.pCircularBuffer = NULL;
  }
  
  IEventSrc * eventSource = ISourceGetEventSrcIF(s);
  if (eventSource == NULL) {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
    xRes = SYS_UNDEFINED_ERROR_CODE;
    return xRes;
  }
  
  if(IEventSrcAddEventListener(eventSource, ADPU_GetEventListenerIF(pObj)) != SYS_NO_ERROR_CODE)
  {
    sys_error_handler();
  }
  
  pObj->nSensor++;
  
  return xRes;
}

sys_error_code_t ADPU_DetachFromSensor_vtbl(IDPU *_this, ISourceObservable *s)
{
  assert_param(_this);
  assert_param(s != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  ADPU *pObj = (ADPU*)_this;
  
  uint8_t id = ISourceGetId(s);
  if (pObj->sensors[id].sensorIF == s)
  {
    IEventSrc * eventSource = ISourceGetEventSrcIF(s);
    if (eventSource == NULL) 
    {
      SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
      xRes = SYS_UNDEFINED_ERROR_CODE;
      return xRes;
    }
    
    if(IEventSrcRemoveEventListener(eventSource, ADPU_GetEventListenerIF(pObj)) != SYS_NO_ERROR_CODE)
    {
      sys_error_handler();
    }
    
    pObj->sensors[id].sensorIF = NULL;
    if(pObj->sensors[id].cb_handle.pCircularBuffer != NULL)
    {
      CB_Free(pObj->sensors[id].cb_handle.pCircularBuffer);
    }
    pObj->nSensor--;
  }
  
  else
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
    xRes = SYS_UNDEFINED_ERROR_CODE;
    return xRes;
  }
  
  return xRes;
}

sys_error_code_t ADPU_AttachInputADPU_vtbl(IDPU *_this, IDPU *adpu, void *buffer)
{
  assert_param(_this != NULL);
  assert_param(adpu != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  ADPU *pObj = (ADPU*)_this;
  ADPU *target =  (ADPU*) adpu;
  
  if(pObj->isADPUattached)
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(ADPU_ALREADY_ATTACHED);
    xRes = ADPU_ALREADY_ATTACHED;
    return xRes;
  }
  
  if(adpu == NULL)
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
    xRes = SYS_UNDEFINED_ERROR_CODE;
    return xRes;
  }
  
  pObj->AttachedAdpu.adpu = adpu;
  
  if(buffer != NULL)
  {
    pObj->AttachedAdpu.cb_handle.pCircularBuffer = CB_Alloc(pObj->cb_items);
    if(CB_Init(pObj->AttachedAdpu.cb_handle.pCircularBuffer, buffer, pObj->n_bytes_for_item) != CB_NO_ERROR_CODE)
    {
      sys_error_handler();
    }
    
    pObj->AttachedAdpu.cb_handle.pProducerDataBuff = NULL;
    pObj->AttachedAdpu.cb_handle.pConsumerDataBuff = NULL;
    pObj->AttachedAdpu.cb_handle.DataIdx = 0;
  }
  else
  {
    pObj->AttachedAdpu.cb_handle.pCircularBuffer = NULL;
  }
  
  SetNextDPU(target, pObj);
  pObj->isADPUattached = 1;
  return xRes;
}

sys_error_code_t ADPU_DetachFromADPU_vtbl(IDPU *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  ADPU *pObj = (ADPU*)_this;
  
  if(NULL == pObj->nextADPU || pObj->isADPUattached == 0)
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(ADPU_NOT_ATTACHED);
    xRes = ADPU_NOT_ATTACHED;
    return xRes;
  }
  
  pObj->nextADPU = NULL;
  pObj->isADPUattached = 0;
  if(pObj->AttachedAdpu.cb_handle.pCircularBuffer != NULL)
  {
    CB_Free(pObj->AttachedAdpu.cb_handle.pCircularBuffer);
  }
  
  return xRes;
}

sys_error_code_t ADPU_DispatchEvents_vtbl(IDPU *_this,  ProcessEvent *pxEvt)
{
  assert_param(_this != NULL);
  assert_param(pxEvt != NULL);
  
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  ADPU *pObj = (ADPU*)_this;
  
  xRes = IEventSrcSendEvent((IEventSrc *)pObj->pProcessEventSrc, (IEvent *) pxEvt, NULL);
  if(xRes != SYS_NO_ERROR_CODE)
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
  }
  
  if(pObj->nextADPU != NULL)
  {
    xRes = ADPU_NotifyDPUDataReady_vtbl((IDPU*) pObj->nextADPU, pxEvt);
  }
  
  if(xRes != SYS_NO_ERROR_CODE)
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
  }
  
  return xRes;
}

static sys_error_code_t ADPU_NotifyDPUDataReady_vtbl(IDPU *_this,  ProcessEvent *pxEvt)
{
  assert_param(_this != NULL);
  assert_param(pxEvt != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  ADPU *pObj = (ADPU*)_this;
  
  CBHandle_t *cb_dpu = & pObj->AttachedAdpu.cb_handle;
  
  pObj->sourceStream.mode = ((AI_SP_Stream_t *)pxEvt->stream)->mode;
  pObj->sourceStream.packet.payload_fmt = pxEvt->stream->payload_fmt;
  pObj->sourceStream.packet.payload = pxEvt->stream->payload;
  pObj->sourceStream.packet.shape.shapes[AI_LOGGING_SHAPES_WIDTH] = pxEvt->stream->shape.shapes[AI_LOGGING_SHAPES_WIDTH];
  pObj->sourceStream.packet.shape.shapes[AI_LOGGING_SHAPES_HEIGHT] = pxEvt->stream->shape.shapes[AI_LOGGING_SHAPES_HEIGHT];
  pObj->sourceStream.packet.shape.n_shape =  pxEvt->stream->shape.n_shape;
  
  if(cb_dpu->pCircularBuffer != NULL)
  {
    if(pObj->sourceStream.packet.payload_fmt == AI_SP_FMT_INT16_RESET() && pObj->dpuWorkingStream.packet.payload_fmt == AI_SP_FMT_FLOAT32_RESET())
    {
      xRes = CB_storing_int16_toFloat_helper(pObj, cb_dpu, (AI_SP_Stream_t *)pxEvt->stream);
    }
    else if(pObj->sourceStream.packet.payload_fmt ==  AI_SP_FMT_FLOAT32_RESET() && pObj->dpuWorkingStream.packet.payload_fmt == AI_SP_FMT_FLOAT32_RESET())
    {
      xRes = CB_storing_float_toFloat_helper(pObj, cb_dpu, (AI_SP_Stream_t *)pxEvt->stream);
    }
    else
    {
      xRes = CB_storing_int16_toInt16_helper(pObj, cb_dpu, (AI_SP_Stream_t *)pxEvt->stream);
    }
  }
  else
  {
    xRes = IDPU_Process((IDPU *)_this);
  }
  
  return xRes;
}

sys_error_code_t ADPU_RegisterNotifyCallbacks_vtbl(IDPU *_this, DPU_ReadyToProcessCallback_t callback, void *p_param)
{
  assert_param(_this != NULL);
  assert_param(callback != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  ADPU *pObj = (ADPU*)_this;
  
  pObj->notifyCall = callback;
  pObj->p_callback_param = p_param;
  
  return xRes;
}

// IEventListener virtual functions definition
// ***************************
void ADPU_SetOwner_vtbl(IEventListener *_this, void *pOwner) 
{
  assert_param(_this);
  assert_param(pOwner);
  ADPU* pObj = (ADPU*) ((uint32_t) _this - offsetof (ADPU , sensorListener));
  
  pObj->pOwner = pOwner;
}

void *ADPU_GetOwner_vtbl(IEventListener *_this) 
{
  assert_param(_this);
  ADPU* pObj = (ADPU*) ((uint32_t) _this - offsetof (ADPU , sensorListener));
  
  return pObj->pOwner;
}


// ISensorEventListener virtual functions
// ***************************
sys_error_code_t ADP_OnNewDataReady_vtbl(IEventListener *_this, const SensorEvent *pxEvt)
{
  assert_param(_this != NULL);
  assert_param(pxEvt != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  
  ADPU *pObj =  (ADPU*) IEventListenerGetOwner(_this);
  
  if(pObj->active)
  {
    SensorObs_t *sensor = GetSensor(pObj, pxEvt->nSensorID);
    if(sensor != NULL)
    {
      CBHandle_t *cb_sensor = &sensor->cb_handle;
      
      pObj->sourceStream.mode = ((AI_SP_Stream_t *)pxEvt->stream)->mode;
      pObj->sourceStream.packet.payload_fmt = pxEvt->stream->payload_fmt;
      pObj->sourceStream.packet.payload = pxEvt->stream->payload;
      pObj->sourceStream.packet.shape.shapes[AI_LOGGING_SHAPES_WIDTH] = pxEvt->stream->shape.shapes[AI_LOGGING_SHAPES_WIDTH];
      pObj->sourceStream.packet.shape.shapes[AI_LOGGING_SHAPES_HEIGHT] = pxEvt->stream->shape.shapes[AI_LOGGING_SHAPES_HEIGHT];
      pObj->sourceStream.packet.shape.n_shape =  pxEvt->stream->shape.n_shape;
      pObj->id_sensor_ready = pxEvt->nSensorID;
      
      if(cb_sensor->pCircularBuffer != NULL)
      {
        if(pObj->sourceStream.packet.payload_fmt == AI_SP_FMT_INT16_RESET() && pObj->dpuWorkingStream.packet.payload_fmt == AI_SP_FMT_FLOAT32_RESET())
        {
          xRes = CB_storing_int16_toFloat_helper(pObj, cb_sensor, (AI_SP_Stream_t *)pxEvt->stream);
        }
        else if(pObj->sourceStream.packet.payload_fmt ==  AI_SP_FMT_FLOAT32_RESET() && pObj->dpuWorkingStream.packet.payload_fmt == AI_SP_FMT_FLOAT32_RESET())
        {
          xRes = CB_storing_float_toFloat_helper(pObj, cb_sensor, (AI_SP_Stream_t *)pxEvt->stream);
        }
        else
        {
          xRes = CB_storing_int16_toInt16_helper(pObj, cb_sensor, (AI_SP_Stream_t *)pxEvt->stream);
        }
      }
      else
      {
        xRes = IDPU_Process((IDPU *)pObj);
      }
    }
  }
  return xRes;
}


// Public functions definition
// ***************************
IEventListener *ADPU_GetEventListenerIF(ADPU *_this)
{
  assert_param(_this);
  return (IEventListener*) &_this->sensorListener;
}

IEventSrc *ADPU_GetEventSrcIF(ADPU * _this)
{
  assert_param(_this != NULL);
  return (IEventSrc*) _this->pProcessEventSrc;
}

sys_error_code_t ADPU_SetTag(ADPU *_this, uint32_t tag) 
{
  assert_param(_this != NULL);
  return ProcessEventSrcSetTag((ProcessEventSrc*)(_this->pProcessEventSrc), tag);
}

uint32_t ADPU_GetTag(ADPU *_this) 
{
  assert_param(_this != NULL);
  return ProcessEventSrcGetTag((ProcessEventSrc*)(_this->pProcessEventSrc));
}

sys_error_code_t ADPU_Reset(ADPU *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  ADPU *pObj = (ADPU*)_this;
  
  for(int i=0; i < ADPU_CFG_MAX_SENSOR; i++)
  {
    if(pObj->sensors[i].sensorIF != NULL)
    {
      if(pObj->sensors[i].cb_handle.pCircularBuffer != NULL)
      {
        CB_Init(pObj->sensors[i].cb_handle.pCircularBuffer, CB_GetItemsBuffer(pObj->sensors[i].cb_handle.pCircularBuffer), CB_GetItemSize(pObj->sensors[i].cb_handle.pCircularBuffer));
        pObj->sensors[i].cb_handle.DataIdx = 0;
        pObj->sensors[i].cb_handle.pConsumerDataBuff = NULL;
        pObj->sensors[i].cb_handle.pProducerDataBuff = NULL;
      }
    }
  }
  
  if(pObj->isADPUattached)
  {
    if(pObj->AttachedAdpu.cb_handle.pCircularBuffer != NULL)
    {
      CB_Init(pObj->AttachedAdpu.cb_handle.pCircularBuffer, CB_GetItemsBuffer(pObj->AttachedAdpu.cb_handle.pCircularBuffer), CB_GetItemSize(pObj->AttachedAdpu.cb_handle.pCircularBuffer));
      pObj->AttachedAdpu.cb_handle.DataIdx = 0;
      pObj->AttachedAdpu.cb_handle.pConsumerDataBuff = NULL;
      pObj->AttachedAdpu.cb_handle.pProducerDataBuff = NULL;
    }
  }
  
  return xRes;
}

sys_error_code_t ADPU_Resume(ADPU *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  
  _this->active = true;
  return xRes;
}

sys_error_code_t ADPU_Suspend(ADPU *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  
  _this->active = false;
  return xRes;
}

// Private functions definition
// ***************************

static sys_error_code_t CB_storing_int16_toInt16_helper(ADPU * _this, CBHandle_t *p_workingCB, AI_SP_Stream_t *p_stream )
{
  assert_param(_this != NULL);
  assert_param(p_workingCB != NULL);
  assert_param(p_stream != NULL);
  
  sys_error_code_t xRes         = SYS_NO_ERROR_CODE;
  ai_logging_packet_t packetIn  = p_stream->packet;
  ai_logging_packet_t packetOut = _this->dpuWorkingStream.packet;
  uint16_t width_in             = 0;
  uint16_t height_in            = 0;
  uint16_t width_out            = 0;
  uint16_t height_out           = 0;
  boolean_t auto_transpose      = false;
  
  uint16_t nbXfer=0, CB_ItemSize=0;
  int16_t *p_inData=NULL;
  int16_t *p_outData=NULL;
  
  /* check supported data types
  todo : reenable when fixed in data manager
  assert_param(packetIn.payload_type == AI_INT16 ||
  (packetIn.payload_type== AI_FMT &&
  packetIn.payload_fmt == AI_SP_FMT_INT16_RESET() ));
  assert_param(packetOut.payload_type == AI_FLOAT ||
  (packetOut.payload_type == AI_FMT &&
  packetOut.payload_fmt == AI_SP_FMT_FLOAT32_RESET() ));
  temporary code to fix :
  */
  
  assert_param(packetIn.payload_fmt == AI_SP_FMT_INT16_RESET());
  assert_param(packetOut.payload_fmt == AI_SP_FMT_INT16_RESET());
  
  /* different dimension shapes not implemented for now */
  if  (packetIn.shape.n_shape != packetOut.shape.n_shape )
  {
    xRes = SYS_NOT_IMPLEMENTED_ERROR_CODE ;
  }
  switch (packetIn.shape.n_shape)
  {
  case 0:
    xRes  = SYS_NOT_IMPLEMENTED_ERROR_CODE ;
    break;
  case 1:
    width_in  = packetIn.shape.shapes[AI_LOGGING_SHAPES_WIDTH];
    height_in = 1 ;
    break;
  case 2:
    width_in   = packetIn.shape.shapes[AI_LOGGING_SHAPES_WIDTH];
    height_in  = packetIn.shape.shapes[AI_LOGGING_SHAPES_HEIGHT];
    width_out  = packetOut.shape.shapes[AI_LOGGING_SHAPES_WIDTH];
    height_out = packetOut.shape.shapes[AI_LOGGING_SHAPES_HEIGHT];
    auto_transpose  = (width_in == height_out) || (height_in == width_out);
    auto_transpose &= (width_in != height_in) ;
    
    break;
  default:
    xRes = SYS_NOT_IMPLEMENTED_ERROR_CODE ;
  }
  
  /*
  todo fix the payload size settings first
  assert_param(p_stream->packet.payload_size == nbXfer * sizeof(int16));
  */

  if (xRes != SYS_NO_ERROR_CODE)
  {
    return xRes;
  }
  
  if (p_workingCB->pProducerDataBuff == NULL)
  {
    xRes = CB_GetFreeItemFromHead(p_workingCB->pCircularBuffer, &p_workingCB->pProducerDataBuff);
  }
  
  if (xRes != CB_NO_ERROR_CODE)
  {
    if(_this->notifyCall != NULL)
    {
      _this->notifyCall((IDPU*)_this, _this->p_callback_param);
    }
    else
    {
      IDPU_Process((IDPU *)_this);
    }
    return xRes;
  }
  
  /* initialize the loop */
  CB_ItemSize = (uint16_t) CB_GetItemSize(p_workingCB->pCircularBuffer) / sizeof(int16_t);
  p_inData    = (int16_t *)(p_stream->packet.payload);
  p_outData   = ((int16_t *) CB_GetItemData(p_workingCB->pProducerDataBuff));
  p_outData  +=  auto_transpose ?  p_workingCB->DataIdx / width_in : p_workingCB->DataIdx;
  nbXfer      = width_in * height_in;
  
  while (nbXfer)
  {
    uint16_t CB_remains = CB_ItemSize - p_workingCB->DataIdx;
    uint16_t n_loop = ( nbXfer > CB_remains ) ? CB_remains : nbXfer ;
    if (auto_transpose)
    {
        uint16_t outer_loop = n_loop/width_out;
        assert_param(n_loop == outer_loop * width_out);
        for (int i = 0; i < outer_loop ; i++)
        {
          for (int j = 0; j < width_out ; j++)
          {
            *(p_outData+j*height_out) = (int16_t) *p_inData++;
          }
          p_outData++;
      }
    }
    else
    {
      for (int i = 0; i < n_loop ; i++)
      {
        *p_outData++ = (int16_t) *p_inData++;
      }
    }
    
    nbXfer               -= n_loop;
    CB_remains           -= n_loop;
    p_workingCB->DataIdx += n_loop;
    
    if (CB_remains == 0 ) /* a CB item is full , can proceed with processing */
    {
			if (p_workingCB->pProducerDataBuff == NULL)
			{
				while(1){}
			}
			
      /* set CB item ready and claim another free one if possible , if not this we are breaking RT */
      CB_SetItemReady(p_workingCB->pCircularBuffer, p_workingCB->pProducerDataBuff);
			
			if (p_workingCB->pProducerDataBuff == NULL)
			{
				while(1){}
			}			
			
      xRes = CB_GetFreeItemFromHead(p_workingCB->pCircularBuffer, &p_workingCB->pProducerDataBuff);
      p_workingCB->DataIdx =  0;
      if(xRes != CB_NO_ERROR_CODE)
      {        
        if(_this->notifyCall != NULL)
        {
          _this->notifyCall((IDPU*)_this, _this->p_callback_param);
        }
        else
        {
          IDPU_Process((IDPU *)_this);
        }
        return xRes;
      }
      p_outData =  CB_GetItemData(p_workingCB->pProducerDataBuff);
      
      if(_this->notifyCall != NULL)
      {
        _this->notifyCall((IDPU*)_this, _this->p_callback_param);
      }
      else
      {
        IDPU_Process((IDPU *)_this);
      }
    }
  }
  return xRes;
}

static sys_error_code_t CB_storing_int16_toFloat_helper(ADPU * _this, CBHandle_t *p_workingCB, AI_SP_Stream_t *p_stream )
{
  assert_param(_this != NULL);
  assert_param(p_workingCB != NULL);
  assert_param(p_stream != NULL);
  
  sys_error_code_t xRes         = SYS_NO_ERROR_CODE;
  ai_logging_packet_t packetIn  = p_stream->packet;
  ai_logging_packet_t packetOut = _this->dpuWorkingStream.packet;
  uint16_t width_in             = 0;
  uint16_t height_in            = 0;
  uint16_t width_out            = 0;
  uint16_t height_out           = 0;
  boolean_t auto_transpose      = false;
  
  uint16_t nbXfer, CB_ItemSize;
  int16_t *p_inData;
  float   *p_outData;
  
  /* check supported data types
  todo : reenable when fixed in data manager
  assert_param(packetIn.payload_type == AI_INT16 ||
  (packetIn.payload_type== AI_FMT &&
  packetIn.payload_fmt == AI_SP_FMT_INT16_RESET() ));
  assert_param(packetOut.payload_type == AI_FLOAT ||
  (packetOut.payload_type == AI_FMT &&
  packetOut.payload_fmt == AI_SP_FMT_FLOAT32_RESET() ));
  temporary code to fix :
  */
  
  assert_param(packetIn.payload_fmt == AI_SP_FMT_INT16_RESET());
  assert_param(packetOut.payload_fmt == AI_SP_FMT_FLOAT32_RESET());
  
  /* different dimension shapes not implemented for now */
  if  (packetIn.shape.n_shape != packetOut.shape.n_shape )
  {
    xRes = SYS_NOT_IMPLEMENTED_ERROR_CODE ;
  }
  switch (packetIn.shape.n_shape)
  {
  case 0:
    xRes  = SYS_NOT_IMPLEMENTED_ERROR_CODE ;
    break;
  case 1:
    width_in  = packetIn.shape.shapes[AI_LOGGING_SHAPES_WIDTH];
    height_in = 1 ;
    break;
  case 2:
    width_in   = packetIn.shape.shapes[AI_LOGGING_SHAPES_WIDTH];
    height_in  = packetIn.shape.shapes[AI_LOGGING_SHAPES_HEIGHT];
    width_out  = packetOut.shape.shapes[AI_LOGGING_SHAPES_WIDTH];
    height_out = packetOut.shape.shapes[AI_LOGGING_SHAPES_HEIGHT];
    auto_transpose  = (width_in == height_out) || (height_in == width_out);
    auto_transpose &= (width_in != height_in) ;
    
    break;
  default:
    xRes = SYS_NOT_IMPLEMENTED_ERROR_CODE ;
  }
  
  /*
  todo fix the payload size settings first
  assert_param(p_stream->packet.payload_size == nbXfer * sizeof(int16));
  */
  if (xRes != SYS_NO_ERROR_CODE)
  {
    return xRes;
  }
  
  if (p_workingCB->pProducerDataBuff == NULL)
  {
    xRes = CB_GetFreeItemFromHead(p_workingCB->pCircularBuffer, &p_workingCB->pProducerDataBuff);
  }
  
  if (xRes != SYS_NO_ERROR_CODE)
  {
    return xRes;
  }
  
  /* initialize the loop */
  CB_ItemSize = (uint16_t) CB_GetItemSize(p_workingCB->pCircularBuffer) / sizeof(float);
  p_inData    = (int16_t *)(p_stream->packet.payload);
  p_outData   = ((float *) CB_GetItemData(p_workingCB->pProducerDataBuff));
  p_outData  +=  auto_transpose ?  p_workingCB->DataIdx / width_in : p_workingCB->DataIdx;
  nbXfer      = width_in * height_in;
  
  while (nbXfer)
  {
    uint16_t CB_remains = CB_ItemSize - p_workingCB->DataIdx;
    uint16_t n_loop = ( nbXfer > CB_remains ) ? CB_remains : nbXfer ;
    if (auto_transpose)
    {
        uint16_t outer_loop = n_loop/width_out;
        assert_param(n_loop == outer_loop * width_out);
        for (int i = 0; i < outer_loop ; i++)
        {
          for (int j = 0; j < width_out ; j++)
          {
            *(p_outData+j*height_out) = (float) *p_inData++;
          }
          p_outData++;
      }
    }
    else
    {
      for (int i = 0; i < n_loop ; i++)
      {
        *p_outData++ = (float) *p_inData++;
      }
    }
    
    nbXfer               -= n_loop;
    CB_remains           -= n_loop;
    p_workingCB->DataIdx += n_loop;
    
    if (CB_remains == 0 ) /* a CB item is full , can proceed with processing */
    {
      /* set CB item ready and claim another free one if possible , if not this we are breaking RT */
      CB_SetItemReady(p_workingCB->pCircularBuffer, p_workingCB->pProducerDataBuff);
      xRes = CB_GetFreeItemFromHead(p_workingCB->pCircularBuffer, &p_workingCB->pProducerDataBuff);
      p_workingCB->DataIdx =  0;
      if(xRes != CB_NO_ERROR_CODE)
      {
        sys_error_handler();
        return xRes;
      }
      p_outData =  CB_GetItemData(p_workingCB->pProducerDataBuff);
      
      if(_this->notifyCall != NULL)
      {
        _this->notifyCall((IDPU*)_this, _this->p_callback_param);
      }
      else
      {
        IDPU_Process((IDPU *)_this);
      }
    }
  }
  return xRes;
}

static sys_error_code_t CB_storing_float_toFloat_helper(ADPU * _this, CBHandle_t *p_workingCB, AI_SP_Stream_t *p_stream )
{
  assert_param(_this != NULL);
  assert_param(p_workingCB != NULL);
  assert_param(p_stream != NULL);
  
  sys_error_code_t xRes         = SYS_NO_ERROR_CODE;
  ai_logging_packet_t packetIn  = p_stream->packet;
  ai_logging_packet_t packetOut = _this->dpuWorkingStream.packet;
  uint16_t width_in             = 0;
  uint16_t height_in            = 0;
  uint16_t width_out            = 0;
  uint16_t height_out           = 0;
  boolean_t auto_transpose      = false;
  
  uint16_t nbXfer, CB_ItemSize;
  float *p_inData;
  float   *p_outData;
  
  /* check supported data types
  todo : reenable when fixed in data manager
  assert_param(packetIn.payload_type == AI_INT16 ||
  (packetIn.payload_type== AI_FMT &&
  packetIn.payload_fmt == AI_SP_FMT_INT16_RESET() ));
  assert_param(packetOut.payload_type == AI_FLOAT ||
  (packetOut.payload_type == AI_FMT &&
  packetOut.payload_fmt == AI_SP_FMT_FLOAT32_RESET() ));
  temporary code to fix :
  */
  
  assert_param(packetIn.payload_fmt == AI_SP_FMT_FLOAT32_RESET());
  assert_param(packetOut.payload_fmt == AI_SP_FMT_FLOAT32_RESET());
  
  /* different dimension shapes not implemented for now */
  if  (packetIn.shape.n_shape != packetOut.shape.n_shape )
  {
    xRes = SYS_NOT_IMPLEMENTED_ERROR_CODE ;
  }
  switch (packetIn.shape.n_shape)
  {
  case 0:
    xRes  = SYS_NOT_IMPLEMENTED_ERROR_CODE ;
    break;
  case 1:
    width_in  = packetIn.shape.shapes[AI_LOGGING_SHAPES_WIDTH];
    height_in = 1 ;
    break;
  case 2:
    width_in   = packetIn.shape.shapes[AI_LOGGING_SHAPES_WIDTH];
    height_in  = packetIn.shape.shapes[AI_LOGGING_SHAPES_HEIGHT];
    width_out  = packetOut.shape.shapes[AI_LOGGING_SHAPES_WIDTH];
    height_out = packetOut.shape.shapes[AI_LOGGING_SHAPES_HEIGHT];
    auto_transpose  = (width_in == height_out) || (height_in == width_out);
    auto_transpose &= (width_in != height_in) ;
    
    break;
  default:
    xRes = SYS_NOT_IMPLEMENTED_ERROR_CODE ;
  }
  
  /*
  todo fix the payload size settings first
  assert_param(p_stream->packet.payload_size == nbXfer * sizeof(int16));
  */
  if (xRes != SYS_NO_ERROR_CODE)
  {
    return xRes;
  }
  
  if (p_workingCB->pProducerDataBuff == NULL)
  {
    xRes = CB_GetFreeItemFromHead(p_workingCB->pCircularBuffer, &p_workingCB->pProducerDataBuff);
  }

  if (xRes != SYS_NO_ERROR_CODE)
  {
    return xRes;
  }
  
  /* initialize the loop */
  CB_ItemSize = (uint16_t) CB_GetItemSize(p_workingCB->pCircularBuffer) / sizeof(float);
  p_inData    = (float *)(p_stream->packet.payload);
  p_outData   = ((float *) CB_GetItemData(p_workingCB->pProducerDataBuff));
  p_outData  +=  auto_transpose ?  p_workingCB->DataIdx / width_in : p_workingCB->DataIdx;
  nbXfer      = width_in * height_in;
  
  while (nbXfer)
  {
    uint16_t CB_remains = CB_ItemSize - p_workingCB->DataIdx;
    uint16_t n_loop = ( nbXfer > CB_remains ) ? CB_remains : nbXfer ;
    if (auto_transpose)
    {
      uint16_t outer_loop = n_loop/width_out;
      assert_param(n_loop == outer_loop * width_out);
      for (int i = 0; i < outer_loop ; i++)
      {
        for (int j = 0; j < width_out ; j++)
        {
          *(p_outData+j*height_out) = (float) *p_inData++;
        }
        p_outData++;
      }
    }
    else
    {
      for (int i = 0; i < n_loop ; i++)
      {
        *p_outData++ = (float) *p_inData++;
      }
    }
    
    nbXfer               -= n_loop;
    CB_remains           -= n_loop;
    p_workingCB->DataIdx += n_loop;
    
    if (CB_remains == 0 ) /* a CB item is full , can proceed with processing */
    {
      /* set CB item ready and claim another free one if possible , if not this we are breaking RT */
      CB_SetItemReady(p_workingCB->pCircularBuffer, p_workingCB->pProducerDataBuff);
      xRes = CB_GetFreeItemFromHead(p_workingCB->pCircularBuffer, &p_workingCB->pProducerDataBuff);
      p_workingCB->DataIdx =  0;
      if(xRes != CB_NO_ERROR_CODE)
      {
        sys_error_handler();
        return xRes;
      }
      p_outData =  CB_GetItemData(p_workingCB->pProducerDataBuff);
      
      if(_this->notifyCall != NULL)
      {
        _this->notifyCall((IDPU*)_this, _this->p_callback_param);
      }
      else
      {
        IDPU_Process((IDPU *)_this);
      }
    }
  }
  return xRes;
}

static SensorObs_t *GetSensor(ADPU *_this, uint8_t id)
{
  assert_param(_this != NULL);
  return &_this->sensors[id];
}

static void SetNextDPU(ADPU *_this, ADPU *target)
{
  assert_param(_this != NULL);
  assert_param(target != NULL);
  _this->nextADPU = (IDPU*)target;
}
