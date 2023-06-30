/**
 ******************************************************************************
 * @file    platform.c
 * @author  MCD Application Team
 * @brief   Library to manage platform related operation
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2023 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */

#include "platform.h"

extern I2C_HandleTypeDef 	hi2c1;

uint8_t LMZ_platform_init(
		VL53LMZ_Platform *p_platform)
{
	p_platform->address = 0x52;

	return(0);
}

uint8_t RdByte(
		VL53LMZ_Platform *p_platform,
		uint16_t RegisterAdress,
		uint8_t *p_value)
{
	int8_t status = 0;
	uint8_t data_write[2];
	uint8_t data_read[1];

	data_write[0] = (RegisterAdress >> 8) & 0xFF;
	data_write[1] = RegisterAdress & 0xFF;
	status = HAL_I2C_Master_Transmit(&hi2c1, p_platform->address, data_write, 2, 100);
	status = HAL_I2C_Master_Receive(&hi2c1, p_platform->address, data_read, 1, 100);
	*p_value = data_read[0];

	return(status);
}

uint8_t WrByte(
		VL53LMZ_Platform *p_platform,
		uint16_t RegisterAdress,
		uint8_t value)
{
	uint8_t data_write[3];
	int8_t status = 0;

	data_write[0] = (RegisterAdress >> 8) & 0xFF;
	data_write[1] = RegisterAdress & 0xFF;
	data_write[2] = value & 0xFF;
	status = HAL_I2C_Master_Transmit(&hi2c1, p_platform->address, data_write, 3, 100);

	return(status);
}

uint8_t WrMulti(
		VL53LMZ_Platform *p_platform,
		uint16_t RegisterAdress,
		uint8_t *p_values,
		uint32_t size)
{
	int8_t status = HAL_I2C_Mem_Write(&hi2c1, p_platform->address, RegisterAdress,
			I2C_MEMADD_SIZE_16BIT, p_values, size, 65535);

	return(status);
}

uint8_t RdMulti(
		VL53LMZ_Platform *p_platform,
		uint16_t RegisterAdress,
		uint8_t *p_values,
		uint32_t size)
{
	uint8_t status;
	uint8_t data_write[2];
	data_write[0] = (RegisterAdress>>8) & 0xFF;
	data_write[1] = RegisterAdress & 0xFF;

	status = HAL_I2C_Master_Transmit(&hi2c1, p_platform->address, data_write, 2, 10);
	status += HAL_I2C_Master_Receive(&hi2c1, p_platform->address, p_values, size, 400);

	return status;
}

uint8_t Reset_Sensor(
		VL53LMZ_Platform *p_platform)
{
	uint8_t status = 0;

	/* (Optional) Need to be implemented by customer. This function returns 0 if OK */

	/* Set pin LPN to LOW */
//	HAL_GPIO_WritePin(LPn_C_GPIO_Port, LPn_C_Pin, GPIO_PIN_RESET);
	/* Set pin AVDD to LOW */
	/* Set pin VDDIO  to LOW */
	/* Set 0 to pin DUT_PWR */
//	HAL_GPIO_WritePin(PWR_EN_C_GPIO_Port, PWR_EN_C_Pin, GPIO_PIN_RESET);
	WaitMs(p_platform, 100);

	/* Set pin LPN of to HIGH */
//	HAL_GPIO_WritePin(LPn_C_GPIO_Port, LPn_C_Pin, GPIO_PIN_SET);
	/* Set pin AVDD of to HIGH */
	/* Set pin VDDIO of  to HIGH */
	/* Set 1 to pin DUT_PWR */
//	HAL_GPIO_WritePin(PWR_EN_C_GPIO_Port, PWR_EN_C_Pin, GPIO_PIN_RESET);
	WaitMs(p_platform, 100);

	return status;
}

void SwapBuffer(
		uint8_t 		*buffer,
		uint16_t 	 	 size)
{
	uint32_t i;
	uint32_t tmp;
	
	/* Example of possible implementation using <string.h> */
	for(i = 0; i < size; i = i + 4) 
	{
		tmp = (
		  buffer[i]<<24)
		|(buffer[i+1]<<16)
		|(buffer[i+2]<<8)
		|(buffer[i+3]);
		
		memcpy(&(buffer[i]), &tmp, 4);
	}
}	

uint8_t WaitMs(
		VL53LMZ_Platform *p_platform,
		uint32_t TimeMs)
{
	HAL_Delay(TimeMs);
	return 0;
}

uint8_t wait_for_ToF_interrupt(
	VL53LMZ_Platform *p_platform,
    volatile int *IntrCount)
{
	(void)p_platform;

	HAL_SuspendTick();
	__WFI(); /* Wait For Interrupt */
	HAL_ResumeTick();
	if (*IntrCount != 0) {
		*IntrCount = 0;
		return(0);
	}

	return(1);
}
