/**
 ******************************************************************************
 * @file    SPIMasterDriver.c
 * @author  SRA - MCD
 * @version 1.1.0
 * @date    10-Dec-2021
 *
 * @brief SPI driver definition.
 *
 * SPI driver definition.
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2021 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 *
 ******************************************************************************
 */

#include "drivers/SPIMasterDriver.h"
#include "drivers/SPIMasterDriver_vtbl.h"
#include "FreeRTOS.h"
#include "services/sysdebug.h"

#define SPIDRV_CFG_HARDWARE_PERIPHERALS_COUNT   1

#define SYS_DEBUGF(level, message)              SYS_DEBUGF3(SYS_DBG_DRIVERS, level, message)


/**
 * SPIMasterDriver Driver virtual table.
 */
static const IIODriver_vtbl sSPIMasterDriver_vtbl = {
    SPIMasterDriver_vtblInit,
    SPIMasterDriver_vtblStart,
    SPIMasterDriver_vtblStop,
    SPIMasterDriver_vtblDoEnterPowerMode,
    SPIMasterDriver_vtblReset,
    SPIMasterDriver_vtblWrite,
    SPIMasterDriver_vtblRead
};

/**
 * Data associated to the hardware peripheral.
 */
typedef struct _SPIPeripheralResources_t
{
  /**
   * Synchronization object used by the driver to synchronize the I2C ISR with the task using the driver.
   */
  SemaphoreHandle_t sync_obj;

#if (SYS_DBG_ENABLE_TA4 == 1)
  traceHandle m_xSpiTraceHandle;
#endif
} SPIPeripheralResources_t;

/**
 *
 */
static SPIPeripheralResources_t spHwResouces[SPIDRV_CFG_HARDWARE_PERIPHERALS_COUNT] = {
#if (SYS_DBG_ENABLE_TA4 == 1)
  {NULL, 0}
#else
  { NULL }
#endif
};


/* Private member function declaration */
/***************************************/

/**
 * HAL callback.
 * @param hspi [IN] specifies an handle of an SPI.
 */
static void SPIMasterDriverTxRxCpltCallback(SPI_HandleTypeDef *hspi);


/* Public API definition */
/*************************/

IIODriver* SPIMasterDriverAlloc(void)
{
  IIODriver *p_new_obj = (IIODriver*) pvPortMalloc(sizeof(SPIMasterDriver_t));

  if(p_new_obj == NULL)
  {
    SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_OUT_OF_MEMORY_ERROR_CODE);
    SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("SPIMasterDriver - alloc failed.\r\n"));
  }
  else
  {
    p_new_obj->vptr = &sSPIMasterDriver_vtbl;
  }

  return p_new_obj;
}

sys_error_code_t SPIMasterDriver_vtblInit(IDriver *_this, void *p_params)
{
  assert_param(_this != NULL);
  assert_param(p_params != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  SPIMasterDriver_t *p_obj = (SPIMasterDriver_t*) _this;
  p_obj->mx_handle.p_mx_spi_cfg = ((SPIMasterDriverParams_t*)p_params)->p_mx_spi_cfg;
  SPI_HandleTypeDef *p_spi = p_obj->mx_handle.p_mx_spi_cfg->p_spi_handle;

  p_obj->mx_handle.p_mx_spi_cfg->p_mx_dma_init_f();
  p_obj->mx_handle.p_mx_spi_cfg->p_mx_init_f();

  /* Register SPI DMA complete Callback */
  if(HAL_OK != HAL_SPI_RegisterCallback(p_spi, HAL_SPI_RX_COMPLETE_CB_ID, SPIMasterDriverTxRxCpltCallback))
  {
    SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
    res = SYS_UNDEFINED_ERROR_CODE;
  }
  else if(HAL_OK != HAL_SPI_RegisterCallback(p_spi, HAL_SPI_TX_COMPLETE_CB_ID, SPIMasterDriverTxRxCpltCallback))
  {
    SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
    res = SYS_UNDEFINED_ERROR_CODE;
  }
  else
  {
    /* initialize the software resources */
    p_obj->sync_obj = xSemaphoreCreateBinary();
    if(p_obj->sync_obj == NULL)
    {
      SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_OUT_OF_MEMORY_ERROR_CODE);
      res = SYS_OUT_OF_MEMORY_ERROR_CODE;
    }

    spHwResouces[0].sync_obj = p_obj->sync_obj;

#if (SYS_DBG_ENABLE_TA4 == 1)
    spHwResouces[0].m_xSpiTraceHandle = xTraceSetISRProperties("SPI3", 3);
#endif
  }

#ifdef DEBUG
  if(p_obj->sync_obj)
  {
    vQueueAddToRegistry(p_obj->sync_obj, "SPI3Drv");
  }
#endif

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("SPIMasterDriver: initialization done.\r\n"));

  return res;
}

sys_error_code_t SPIMasterDriver_vtblStart(IDriver *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  SPIMasterDriver_t *p_obj = (SPIMasterDriver_t*)_this;

  /*enable the IRQ*/
  HAL_NVIC_EnableIRQ(p_obj->mx_handle.p_mx_spi_cfg->spi_dma_rx_irq_n);
  HAL_NVIC_EnableIRQ(p_obj->mx_handle.p_mx_spi_cfg->spi_dma_tx_irq_n);

  return res;
}

sys_error_code_t SPIMasterDriver_vtblStop(IDriver *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  SPIMasterDriver_t *p_obj = (SPIMasterDriver_t*)_this;

  /*disable the IRQ*/
  /*enable the IRQ*/
  HAL_NVIC_DisableIRQ(p_obj->mx_handle.p_mx_spi_cfg->spi_dma_rx_irq_n);
  HAL_NVIC_DisableIRQ(p_obj->mx_handle.p_mx_spi_cfg->spi_dma_tx_irq_n);

  return res;
}

sys_error_code_t SPIMasterDriver_vtblDoEnterPowerMode(IDriver *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  /*SPIMasterDriver *p_obj = (SPIMasterDriver*)_this;*/

  return res;
}

sys_error_code_t SPIMasterDriver_vtblReset(IDriver *_this, void *p_params)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  /*SPIMasterDriver *p_obj = (SPIMasterDriver*)_this;*/

  return res;
}

sys_error_code_t SPIMasterDriver_vtblWrite(IIODriver *_this, uint8_t *p_data_buffer, uint16_t data_size, uint16_t channel)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  SPIMasterDriver_t *p_obj = (SPIMasterDriver_t*) _this;
  SPI_HandleTypeDef *p_spi = p_obj->mx_handle.p_mx_spi_cfg->p_spi_handle;

  res = SPIMasterDriverTransmitRegAddr(p_obj, channel, 500);
  if(!SYS_IS_ERROR_CODE(res))
  {
    while(HAL_SPI_Transmit_DMA(p_spi, p_data_buffer, data_size) != HAL_OK)
    {
      if(HAL_SPI_GetError(p_spi) != HAL_BUSY)
      {
        SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_SPI_M_WRITE_READ_ERROR_CODE);
        sys_error_handler();
      }
    }
    /* Suspend the calling task until the operation is completed.*/
    xSemaphoreTake(p_obj->sync_obj, portMAX_DELAY);
  }

  return res;
}

sys_error_code_t SPIMasterDriver_vtblRead(IIODriver *_this, uint8_t *p_data_buffer, uint16_t data_size, uint16_t channel)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  SPIMasterDriver_t *p_obj = (SPIMasterDriver_t*) _this;
  SPI_HandleTypeDef *p_spi = p_obj->mx_handle.p_mx_spi_cfg->p_spi_handle;

  res = SPIMasterDriverTransmitRegAddr(p_obj, channel, 500);
  if(!SYS_IS_ERROR_CODE(res))
  {
    while(HAL_SPI_Receive_DMA(p_spi, p_data_buffer, data_size) != HAL_OK)
    {
      if(HAL_SPI_GetError(p_spi) != HAL_BUSY)
      {
        SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_SPI_M_WRITE_READ_ERROR_CODE);
        sys_error_handler();
      }
    }
    /* Suspend the calling task until the operation is completed.*/
    xSemaphoreTake(p_obj->sync_obj, portMAX_DELAY);
  }

  return res;
}

sys_error_code_t SPIMasterDriverTransmitRegAddr(SPIMasterDriver_t *_this, uint8_t reg_addr, uint32_t timeout_ms)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  SPIMasterDriver_t *p_obj = (SPIMasterDriver_t*) _this;
  SPI_HandleTypeDef *p_spi = p_obj->mx_handle.p_mx_spi_cfg->p_spi_handle;

  if(HAL_OK != HAL_SPI_Transmit(p_spi, &reg_addr, 1, timeout_ms))
  {
    res = SYS_SPI_M_WRITE_ERROR_CODE;
    SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_SPI_M_WRITE_ERROR_CODE);
    /* block the application*/
    sys_error_handler();
  }

  return res;
}

sys_error_code_t SPIMasterDriverWriteRead(SPIMasterDriver_t *_this, uint8_t *p_tx_data_buffer, uint8_t *p_rx_data_buffer, uint16_t data_size)
{
  assert_param(_this != NULL);
  assert_param(p_tx_data_buffer != NULL);
  assert_param(p_tx_data_buffer != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  SPIMasterDriver_t *p_obj = (SPIMasterDriver_t*) _this;
  SPI_HandleTypeDef *p_spi = p_obj->mx_handle.p_mx_spi_cfg->p_spi_handle;

  while(HAL_SPI_TransmitReceive_DMA(p_spi, p_tx_data_buffer, p_rx_data_buffer, data_size) != HAL_OK)
  {
    if(HAL_SPI_GetError(p_spi) != HAL_BUSY)
    {
      SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_SPI_M_WRITE_READ_ERROR_CODE);
      sys_error_handler();
    }
  }

  /* Suspend the calling task until the operation is completed.*/
  xSemaphoreTake(p_obj->sync_obj, portMAX_DELAY);

  return res;
}

sys_error_code_t SPIMasterDriverSelectDevice(SPIMasterDriver_t *_this, GPIO_TypeDef *p_device_gpio_port, uint16_t device_gpio_pin)
{
  /* this is a class method so pointer _this is not used*/
  UNUSED(_this);

  HAL_GPIO_WritePin(p_device_gpio_port, device_gpio_pin, GPIO_PIN_RESET);

  return SYS_NO_ERROR_CODE;
}

sys_error_code_t SPIMasterDriverDeselectDevice(SPIMasterDriver_t *_this, GPIO_TypeDef *device_gpio_port, uint16_t device_gpio_pin)
{
  /* this is a class method so pointer _this is not used*/
  UNUSED(_this);

  HAL_GPIO_WritePin(device_gpio_port, device_gpio_pin, GPIO_PIN_SET);

  return SYS_NO_ERROR_CODE;
}


/* Private function definition */
/*******************************/

/* CubeMX integration */
/**********************/

static void SPIMasterDriverTxRxCpltCallback(SPI_HandleTypeDef *hspi)
{
  UNUSED(hspi);

#if (SYS_DBG_ENABLE_TA4 == 1)
  if (xTraceIsRecorderEnabled()) {
    vTraceStoreISRBegin(spHwResouces[0].m_xSpiTraceHandle);
  }
#endif

  if(spHwResouces[0].sync_obj)
  {
    if(pdTRUE != xSemaphoreGiveFromISR(spHwResouces[0].sync_obj, NULL))
    {
      /* error*/
      sys_error_handler();
    }
  }
  else
  {
    /* error*/
    sys_error_handler();
  }

#if (SYS_DBG_ENABLE_TA4 == 1)
  if (xTraceIsRecorderEnabled()) {
    vTraceStoreISREnd(0);
  }
#endif
}
