/**
 ******************************************************************************
 * @file    Int16toFloatDataBuilder.c
 * @author  STMicroelectronics - AIS - MCD Team
 * @version M.m.b
 * @date    May 21, 2022
 *
 * @brief
 *
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2022 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */

#include "Int16toFloatDataBuilder.h"
#include "Int16toFloatDataBuilder_vtbl.h"
#include "services/sysmem.h"
#include "services/sysdebug.h"

#define SYS_DEBUGF(level, message)                   SYS_DEBUGF3(SYS_DBG_DPU, level, message)


/**
 * Class object declaration.
 */
typedef struct _Int16toFloatDataBuilderClass {
  /**
   * IDataBuilder_t class virtual table.
   */
  IDataBuilder_vtbl vtbl;

} Int16toFloatDataBuilderClass_t;


/* Objects instance */
/********************/

/**
 * The class object.
 */
static const Int16toFloatDataBuilderClass_t sTheClass = {
    /* class virtual table */
    {
        Int16ToFloatDB_vtblOnReset,
        Int16ToFloatDB_vtblOnNewInData
    },
};


/* Private functions declaration */
/*********************************/


/* IDataBuilder_t virtual functions definition */
/***********************************************/

sys_error_code_t Int16ToFloatDB_vtblOnReset(IDataBuilder_t *_this, void *p_data_build_context)
{
  assert_param(_this != NULL);
  Int16toFloatDataBuilder_t *p_obj = (Int16toFloatDataBuilder_t*)_this;
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  p_obj->index = 0;
  p_obj->p_data_build_context = p_data_build_context;

  return res;
}

sys_error_code_t Int16ToFloatDB_vtblOnNewInData(IDataBuilder_t *_this, EMData_t *p_target_data, const EMData_t *p_new_in_data, IDB_BuildStrategy_e build_strategy, DataBuffAllocator_f data_buff_alloc)
{
  assert_param(_this != NULL);
  Int16toFloatDataBuilder_t *p_obj = (Int16toFloatDataBuilder_t*)_this;
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  EMData_t reshaped_target_data, reshaped_in_data;

  /*reshape the data as 1D because it is a more convenient format for this builder.*/
  uint32_t target_elements = EMD_GetElementsCount(p_target_data);
  uint32_t in_elements = EMD_GetElementsCount(p_new_in_data);
  EMD_1dInit(&reshaped_in_data, EMD_Data(p_new_in_data), EMD_GetType(p_new_in_data), in_elements);
  EMD_1dInit(&reshaped_target_data, EMD_Data(p_target_data), E_EM_FLOAT, target_elements);

  register float *p_target_val = (float*)EMD_1dDataAt(&reshaped_target_data, p_obj->index);
  register int16_t *p_src_val = (int16_t*)EMD_1dDataAt(&reshaped_in_data, 0);
  /*consume all the new input data*/
  while (in_elements > 0U)
  {
    /*how many elements can I copy in the target data? */
    uint32_t free_elements = target_elements - p_obj->index;
    uint32_t element_to_copy = (free_elements < in_elements ? free_elements : in_elements); // MIN(free_elements, in_elements)
    /*copy the input data elements in the target data payload*/
    for (uint32_t i=0; i<element_to_copy; ++i)
    {
      *p_target_val++ = (float)*p_src_val++;
    }

    in_elements -= element_to_copy;
    p_obj->index += element_to_copy;
    /*check if the target data is ready: did I fill all elements in the target data?*/
    if (p_obj->index >= target_elements)
    {
      if (in_elements > 0U)
      {
        /* target data is ready but there are still element to be processed.
         * What to do depends on the build strategy.*/
        switch (build_strategy)
        {
          case E_IDB_NO_DATA_LOSS:
            reshaped_target_data.p_payload = data_buff_alloc(_this, p_obj->p_data_build_context);
            if (reshaped_target_data.p_payload == NULL)
            {
              SYS_DEBUGF(SYS_DBG_LEVEL_SEVERE, ("IDB_int16_float: data lost!\r\r"));
              /*no more buffer => data lost!*/
              sys_error_handler();
            }
            else
            {
              /*I have a buffer to build a new data, so I reset the index.*/
              p_obj->index = 0;
              p_target_val = (float*)EMD_1dDataAt(&reshaped_target_data, p_obj->index);
            }
            break;

          case E_IDB_SKIP_DATA:
            /*ignore the remain input elements.*/
            in_elements = 0;
            res = SYS_IDB_DATA_READY_ERROR_CODE;
            break;

          default:
            SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("IDB_int16_float: unsupported strategy.\r\n"));
            res = SYS_IDB_UNSUPPORTED_STRATEGY_ERROR_CODE;
            break;
        }
      }
      else
      {
        /* target data is ready.*/
        res = SYS_IDB_DATA_READY_ERROR_CODE;
      }
    }
  }

  return res;
}


/* Public functions definition */
/*******************************/

IDataBuilder_t *Int16ToFloatDB_Alloc(void)
{
  IDataBuilder_t *p_new_obj = (IDataBuilder_t*)SysAlloc(sizeof(Int16toFloatDataBuilder_t));
  if (p_new_obj != NULL)
  {
    p_new_obj->vptr = &sTheClass.vtbl;
  }
  else
  {
    SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_OUT_OF_MEMORY_ERROR_CODE);
  }

  return p_new_obj;
}

IDataBuilder_t *Int16ToFloatDB_AllocStatic(Int16toFloatDataBuilder_t *_this)
{
  assert_param(_this != NULL);

  if (_this != NULL)
  {
    _this->super.vptr = &sTheClass.vtbl;
  }

  return (IDataBuilder_t*)_this;
}


