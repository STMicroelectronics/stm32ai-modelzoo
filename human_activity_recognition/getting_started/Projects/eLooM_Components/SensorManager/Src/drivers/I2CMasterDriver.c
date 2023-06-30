/**
  ******************************************************************************
  * @file    I2CMasterDriver.c
  * @author  SRA - MCD
  * @brief   I2C driver definition.
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
  *
  ******************************************************************************
  */

#include "drivers/I2CMasterDriver.h"
#include "drivers/I2CMasterDriver_vtbl.h"
#include "gpdma.h"
#include "services/sysdebug.h"
#include "SensorManager.h"
#include "drivers/HWDriverMap.h"

#ifndef I2CDRV_CFG_HARDWARE_PERIPHERALS_COUNT
#define I2CDRV_CFG_HARDWARE_PERIPHERALS_COUNT   1
#endif

#define SYS_DEBUGF(level, message)              SYS_DEBUGF3(SYS_DBG_DRIVERS, level, message)

/**
  * I2CMasterDriver Driver virtual table.
  */
static const IIODriver_vtbl sI2CMasterDriver_vtbl =
{
  I2CMasterDriver_vtblInit,
  I2CMasterDriver_vtblStart,
  I2CMasterDriver_vtblStop,
  I2CMasterDriver_vtblDoEnterPowerMode,
  I2CMasterDriver_vtblReset,
  I2CMasterDriver_vtblWrite,
  I2CMasterDriver_vtblRead
};

/**
  * Data associated to the hardware peripheral.
  */
typedef struct _I2CPeripheralResources_t
{
  /**
    * Synchronization object used by the driver to synchronize the I2C ISR with the task using the driver;
    */
  TX_SEMAPHORE *sync_obj;
} I2CPeripheralResources_t;


/**
  *
  */
static I2CPeripheralResources_t sI2CHwResources[I2CDRV_CFG_HARDWARE_PERIPHERALS_COUNT];
static HWDriverMapElement_t sI2CDrvMapElements[I2CDRV_CFG_HARDWARE_PERIPHERALS_COUNT];
static HWDriverMap_t sI2CDrvMap = { 0 };
static uint8_t sInstances = 0;

/* Private member function declaration */
/***************************************/

static void I2CMasterDrvMemTxRxCpltCallback(I2C_HandleTypeDef *p_i2c);
static void I2CMasterDrvErrorCallback(I2C_HandleTypeDef *p_i2c);

/* Public API definition */
/*************************/

sys_error_code_t I2CMasterDriverSetDeviceAddr(I2CMasterDriver_t *_this, uint16_t address)
{
  assert_param(_this);

  _this->target_device_addr = address;

  return SYS_NO_ERROR_CODE;
}

/* IIODriver virtual function definition */
/*****************************************/

IIODriver *I2CMasterDriverAlloc(void)
{
  IIODriver *res = NULL;

  if(sI2CDrvMap.size == 0)
  {
    HWDriverMap_Init(&sI2CDrvMap, sI2CDrvMapElements, I2CDRV_CFG_HARDWARE_PERIPHERALS_COUNT);
  }

  HWDriverMapElement_t *p_element = NULL;
  p_element = HWDriverMap_GetFreeElement(&sI2CDrvMap);

  if(p_element != NULL)
  {
    /* Check if there is room to allocate a new instance */
    p_element->p_driver_obj = (IDriver *) SysAlloc(sizeof(I2CMasterDriver_t));

    if (p_element->p_driver_obj == NULL)
    {
      SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_OUT_OF_MEMORY_ERROR_CODE);
      SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("I2CMasterDriver - alloc failed.\r\n"));
    }
    else
    {
      p_element->p_driver_obj->vptr = (IDriver_vtbl*)&sI2CMasterDriver_vtbl;
      p_element->p_static_param = (void*)&sI2CHwResources[sInstances];
      sInstances++;
    }
    res = (IIODriver*)p_element->p_driver_obj;
  }
  return res;
}

sys_error_code_t I2CMasterDriver_vtblInit(IDriver *_this, void *p_params)
{
  assert_param(_this != NULL);
  assert_param(p_params != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  UINT nRes = TX_SUCCESS;
  I2CMasterDriver_t *p_obj = (I2CMasterDriver_t *) _this;
  p_obj->mx_handle.p_mx_i2c_cfg = ((I2CMasterDriverParams_t *) p_params)->p_mx_i2c_cfg;
  I2C_HandleTypeDef *p_i2c = p_obj->mx_handle.p_mx_i2c_cfg->p_i2c_handle;

  p_obj->mx_handle.p_mx_i2c_cfg->p_mx_dma_init_f();
  p_obj->mx_handle.p_mx_i2c_cfg->p_mx_init_f();

  /* Register SPI DMA complete Callback*/
  if (HAL_OK != HAL_I2C_RegisterCallback(p_i2c, HAL_I2C_MEM_RX_COMPLETE_CB_ID, I2CMasterDrvMemTxRxCpltCallback))
  {
    SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
    res = SYS_UNDEFINED_ERROR_CODE;
  }
  else if (HAL_OK != HAL_I2C_RegisterCallback(p_i2c, HAL_I2C_MEM_TX_COMPLETE_CB_ID, I2CMasterDrvMemTxRxCpltCallback))
  {
    SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
    res = SYS_UNDEFINED_ERROR_CODE;
  }
  else if (HAL_OK != HAL_I2C_RegisterCallback(p_i2c, HAL_I2C_ERROR_CB_ID, I2CMasterDrvErrorCallback))
  {
    SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
    res = SYS_UNDEFINED_ERROR_CODE;
  }
  else
  {
    HWDriverMapElement_t *p_element;
    p_element = HWDriverMap_FindByInstance(&sI2CDrvMap, _this);

    if(p_element == NULL)
    {
      SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_INVALID_PARAMETER_ERROR_CODE);
      res = SYS_INVALID_PARAMETER_ERROR_CODE;
    }
    else
    {
      nRes = tx_semaphore_create(&p_obj->sync_obj, "I2CDrv", 0);
      if(nRes != TX_SUCCESS)
      {
        SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_OUT_OF_MEMORY_ERROR_CODE);
        res = SYS_OUT_OF_MEMORY_ERROR_CODE;
      }
      else
      {
        /* Use the peripheral address as unique key for the map */
        p_element->key = (uint32_t) p_obj->mx_handle.p_mx_i2c_cfg->p_i2c_handle->Instance;

        ((I2CPeripheralResources_t*) p_element->p_static_param)->sync_obj = &p_obj->sync_obj;

        /* initialize the software resources*/
        p_obj->target_device_addr = 0;
        SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("I2CMasterDriver: initialization done.\r\n"));
      }
    }
  }

  return res;
}

sys_error_code_t I2CMasterDriver_vtblStart(IDriver *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  I2CMasterDriver_t *p_obj = (I2CMasterDriver_t *) _this;

  /* I2C interrupt enable */
  HAL_NVIC_EnableIRQ(p_obj->mx_handle.p_mx_i2c_cfg->i2c_ev_irq_n);
  HAL_NVIC_EnableIRQ(p_obj->mx_handle.p_mx_i2c_cfg->i2c_er_irq_n);

  /* DMA RX and TX Channels IRQn interrupt enable */
  HAL_NVIC_EnableIRQ(p_obj->mx_handle.p_mx_i2c_cfg->i2c_dma_rx_irq_n);
  HAL_NVIC_EnableIRQ(p_obj->mx_handle.p_mx_i2c_cfg->i2c_dma_tx_irq_n);

  return res;
}

sys_error_code_t I2CMasterDriver_vtblStop(IDriver *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  I2CMasterDriver_t *p_obj = (I2CMasterDriver_t *) _this;

  /* I2C interrupt disable */
  HAL_NVIC_DisableIRQ(p_obj->mx_handle.p_mx_i2c_cfg->i2c_ev_irq_n);
  HAL_NVIC_DisableIRQ(p_obj->mx_handle.p_mx_i2c_cfg->i2c_er_irq_n);

  /* DMA RX and TX Channels IRQn interrupt disable */
  HAL_NVIC_DisableIRQ(p_obj->mx_handle.p_mx_i2c_cfg->i2c_dma_rx_irq_n);
  HAL_NVIC_DisableIRQ(p_obj->mx_handle.p_mx_i2c_cfg->i2c_dma_tx_irq_n);

  return res;
}

sys_error_code_t I2CMasterDriver_vtblDoEnterPowerMode(IDriver *_this, const EPowerMode active_power_mode,
                                                      const EPowerMode new_powerMode)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  /*I2CMasterDriver_t *p_obj = (I2CMasterDriver_t*)_this;*/

  return res;
}

sys_error_code_t I2CMasterDriver_vtblReset(IDriver *_this, void *p_params)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  /*I2CMasterDriver_t *p_obj = (I2CMasterDriver_t*)_this;*/

  return res;
}

sys_error_code_t I2CMasterDriver_vtblWrite(IIODriver *_this, uint8_t *p_data_buffer, uint16_t data_size,
                                           uint16_t channel)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  I2CMasterDriver_t *p_obj = (I2CMasterDriver_t *) _this;
  I2C_HandleTypeDef *p_i2c = p_obj->mx_handle.p_mx_i2c_cfg->p_i2c_handle;

  if (HAL_I2C_Mem_Write_DMA(p_i2c, p_obj->target_device_addr, channel, I2C_MEMADD_SIZE_8BIT, p_data_buffer,
                            data_size) != HAL_OK)
  {
    if (HAL_I2C_GetError(p_i2c) != (uint32_t)HAL_BUSY)
    {
      SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_I2C_M_WRITE_ERROR_CODE);
      SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("I2CMasterDriver - Write failed.\r\n"));
    }
  }
  /* Suspend the calling task until the operation is completed.*/
  tx_semaphore_get(&p_obj->sync_obj, TX_WAIT_FOREVER);

  return res;
}

sys_error_code_t I2CMasterDriver_vtblRead(IIODriver *_this, uint8_t *p_data_buffer, uint16_t data_size,
                                          uint16_t channel)
{
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  I2CMasterDriver_t *p_obj = (I2CMasterDriver_t *) _this;
  I2C_HandleTypeDef *p_i2c = p_obj->mx_handle.p_mx_i2c_cfg->p_i2c_handle;

  if (HAL_I2C_Mem_Read_DMA(p_i2c, p_obj->target_device_addr, channel, I2C_MEMADD_SIZE_8BIT, p_data_buffer,
                           data_size) != HAL_OK)
  {
    if (HAL_I2C_GetError(p_i2c) != (uint32_t)HAL_BUSY)
    {
      SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_I2C_M_READ_ERROR_CODE);
      SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("I2CMasterDriver - Read failed.\r\n"));
    }
  }
  /* Suspend the calling task until the operation is completed.*/
  tx_semaphore_get(&p_obj->sync_obj, TX_WAIT_FOREVER);

  return res;
}

/* Private function definition */
/*******************************/

/* CubeMX integration */
/**********************/

static void I2CMasterDrvMemTxRxCpltCallback(I2C_HandleTypeDef *p_i2c)
{
  HWDriverMapElement_t *p_element;
  TX_SEMAPHORE *sync_obj;

  p_element = HWDriverMap_FindByKey(&sI2CDrvMap, (uint32_t)p_i2c->Instance);

  if(p_element != NULL)
  {
    sync_obj = ((I2CPeripheralResources_t*) p_element->p_static_param)->sync_obj;

    if(sync_obj != NULL)
    {
      tx_semaphore_put(sync_obj);
    }
  }
}


static void I2CMasterDrvErrorCallback(I2C_HandleTypeDef *p_i2c)
{
  UNUSED(p_i2c);
}
