/**
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

#include <stdlib.h>
#include <string.h>


#include "vl53lmz_api.h"

#include "vl53lmz_buffers.h"


static uint32_t g_output_config[NUM_OUTPUT_CONFIG_WORDS];


static uint32_t g_output_bh_enable[NUM_OUTPUT_ENABLE_WORDS] = {
		0x00000007U,
		0x00000000U,
		0x00000000U,
		0xC0000000U };
/**
 * @brief Inner function, not available outside this file. This function is used
 * to wait for an answer from VL53L5CX sensor.
 */

static uint8_t _vl53lmz_poll_for_answer(
		VL53LMZ_Configuration	*p_dev,
		uint8_t					size,
		uint8_t					pos,
		uint16_t				address,
		uint8_t					mask,
		uint8_t					expected_value)
{
	uint8_t status = VL53LMZ_STATUS_OK;
	uint8_t timeout = 0;

	do {
		status |= RdMulti(&(p_dev->platform), address,
				p_dev->temp_buffer, size);
		status |= WaitMs(&(p_dev->platform), 10);

		if(timeout >= (uint8_t)200)	/* 2s timeout */
		{
			status |= (uint8_t)VL53LMZ_STATUS_TIMEOUT_ERROR;
			break;
		}else if((size >= (uint8_t)4) 
						 && (p_dev->temp_buffer[2] >= (uint8_t)0x7f))
		{
			status |= VL53LMZ_MCU_ERROR;
			break;
		}
		else
		{
			timeout++;
		}
	}while ((p_dev->temp_buffer[pos] & mask) != expected_value);

	return status;
}

/*
 * Inner function, not available outside this file. This function is used to
 * wait for the MCU to boot.
 */
static uint8_t _vl53lmz_poll_for_mcu_boot(
			  VL53LMZ_Configuration		 *p_dev)
{
   uint8_t go2_status0, go2_status1, status = VL53LMZ_STATUS_OK;
   uint16_t timeout = 0;

   do {
		status |= RdByte(&(p_dev->platform), 0x06, &go2_status0);
		if((go2_status0 & (uint8_t)0x80) != (uint8_t)0){
			status |= RdByte(&(p_dev->platform), 0x07, &go2_status1);
			if(go2_status1 & (uint8_t)0x01)
			{
				status |= VL53LMZ_STATUS_OK;
				break;
			}
		}
		(void)WaitMs(&(p_dev->platform), 1);
		timeout++;

		if((go2_status0 & (uint8_t)0x1) != (uint8_t)0){
			break;
		}
	}while (timeout < (uint16_t)500);

   return status;
}

/**
 * @brief Inner function, not available outside this file. This function is used
 * to set the offset data gathered from NVM.
 */

static uint8_t _vl53lmz_send_offset_data(
		VL53LMZ_Configuration		*p_dev,
		uint8_t						resolution)
{
	uint8_t status = VL53LMZ_STATUS_OK;
	uint32_t signal_grid[64];
	int16_t range_grid[64];
	uint8_t dss_4x4[] = {0x0F, 0x04, 0x04, 0x00, 0x08, 0x10, 0x10, 0x07};
	uint8_t footer[] = {0x00, 0x00, 0x00, 0x0F, 0x03, 0x01, 0x01, 0xE4};
	int8_t i, j;
	uint16_t k;

	(void)memcpy(p_dev->temp_buffer,
			   p_dev->offset_data, VL53LMZ_OFFSET_BUFFER_SIZE);

	/* Data extrapolation is required for 4X4 offset */
	if(resolution == (uint8_t)VL53LMZ_RESOLUTION_4X4){
		(void)memcpy(&(p_dev->temp_buffer[0x10]), dss_4x4, sizeof(dss_4x4));
		SwapBuffer(p_dev->temp_buffer, VL53LMZ_OFFSET_BUFFER_SIZE);
		(void)memcpy(signal_grid,&(p_dev->temp_buffer[0x3C]),
			sizeof(signal_grid));
		(void)memcpy(range_grid,&(p_dev->temp_buffer[0x140]),
			sizeof(range_grid));

		for (j = 0; j < (int8_t)4; j++)
		{
			for (i = 0; i < (int8_t)4 ; i++)
			{
				signal_grid[i+(4*j)] =
				(signal_grid[(2*i)+(16*j)+ (int8_t)0]
				+ signal_grid[(2*i)+(16*j)+(int8_t)1]
				+ signal_grid[(2*i)+(16*j)+(int8_t)8]
				+ signal_grid[(2*i)+(16*j)+(int8_t)9])
								  /(uint32_t)4;
				range_grid[i+(4*j)] =
				(range_grid[(2*i)+(16*j)]
				+ range_grid[(2*i)+(16*j)+1]
				+ range_grid[(2*i)+(16*j)+8]
				+ range_grid[(2*i)+(16*j)+9])
								  /(int16_t)4;
			}
		}
		(void)memset(&range_grid[0x10], 0, (uint16_t)96);
		(void)memset(&signal_grid[0x10], 0, (uint16_t)192);
		(void)memcpy(&(p_dev->temp_buffer[0x3C]),
					signal_grid, sizeof(signal_grid));
		(void)memcpy(&(p_dev->temp_buffer[0x140]),
					range_grid, sizeof(range_grid));
		SwapBuffer(p_dev->temp_buffer, VL53LMZ_OFFSET_BUFFER_SIZE);
	}

	for(k = 0; k < (VL53LMZ_OFFSET_BUFFER_SIZE - (uint16_t)4); k++)
	{
		p_dev->temp_buffer[k] = p_dev->temp_buffer[k + (uint16_t)8];
	}

	(void)memcpy(&(p_dev->temp_buffer[0x1E0]), footer, 8);
	status |= WrMulti(&(p_dev->platform), 0x2e18, p_dev->temp_buffer,
		VL53LMZ_OFFSET_BUFFER_SIZE);
	status |=_vl53lmz_poll_for_answer(p_dev, 4, 1,
		VL53LMZ_UI_CMD_STATUS, 0xff, 0x03);

	return status;
}

/**
 * @brief Inner function, not available outside this file. This function is used
 * to set the Xtalk data from generic configuration, or user's calibration.
 */

static uint8_t _vl53lmz_send_xtalk_data(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				resolution)
{
	uint8_t status = VL53LMZ_STATUS_OK;
	uint8_t res4x4[] = {0x0F, 0x04, 0x04, 0x17, 0x08, 0x10, 0x10, 0x07};
	uint8_t dss_4x4[] = {0x00, 0x78, 0x00, 0x08, 0x00, 0x00, 0x00, 0x08};
	uint8_t profile_4x4[] = {0xA0, 0xFC, 0x01, 0x00};
	uint32_t signal_grid[64];
	int8_t i, j;

	(void)memcpy(p_dev->temp_buffer, &(p_dev->xtalk_data[0]),
		VL53LMZ_XTALK_BUFFER_SIZE);

	/* Data extrapolation is required for 4X4 Xtalk */
	if(resolution == (uint8_t)VL53LMZ_RESOLUTION_4X4)
	{
		(void)memcpy(&(p_dev->temp_buffer[0x8]),
			res4x4, sizeof(res4x4));
		(void)memcpy(&(p_dev->temp_buffer[0x020]),
			dss_4x4, sizeof(dss_4x4));

		SwapBuffer(p_dev->temp_buffer, VL53LMZ_XTALK_BUFFER_SIZE);
		(void)memcpy(signal_grid, &(p_dev->temp_buffer[0x34]),
			sizeof(signal_grid));

		for (j = 0; j < (int8_t)4; j++)
		{
			for (i = 0; i < (int8_t)4 ; i++)
			{
				signal_grid[i+(4*j)] =
				(signal_grid[(2*i)+(16*j)+0]
				+ signal_grid[(2*i)+(16*j)+1]
				+ signal_grid[(2*i)+(16*j)+8]
				+ signal_grid[(2*i)+(16*j)+9])/(uint32_t)4;
			}
		}
		(void)memset(&signal_grid[0x10], 0, (uint32_t)192);
		(void)memcpy(&(p_dev->temp_buffer[0x34]),
				  signal_grid, sizeof(signal_grid));
		SwapBuffer(p_dev->temp_buffer, VL53LMZ_XTALK_BUFFER_SIZE);
		(void)memcpy(&(p_dev->temp_buffer[0x134]),
		profile_4x4, sizeof(profile_4x4));
		(void)memset(&(p_dev->temp_buffer[0x078]),0 ,
						 (uint32_t)4*sizeof(uint8_t));
	}

	status |= WrMulti(&(p_dev->platform), 0x2cf8,
			p_dev->temp_buffer, VL53LMZ_XTALK_BUFFER_SIZE);
	status |=_vl53lmz_poll_for_answer(p_dev, 4, 1,
			VL53LMZ_UI_CMD_STATUS, 0xff, 0x03);

	return status;
}

#define REVISION_CUT11	0x01
#define REVISION_CUT12	0x02
#define REVISION_L8		0x0C

uint8_t vl53lmz_is_alive(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				*p_is_alive)
{
	uint8_t status = VL53LMZ_STATUS_OK;
	uint8_t device_id, revision_id;

	status |= WrByte(&(p_dev->platform), 0x7fff, 0x00);
	status |= RdByte(&(p_dev->platform), 0, &device_id);
	status |= RdByte(&(p_dev->platform), 1, &revision_id);
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x02);

if((device_id==(uint8_t)0xF0) && ((revision_id==(uint8_t)REVISION_CUT11) || (revision_id==(uint8_t)REVISION_CUT12) || (revision_id==(uint8_t)REVISION_L8)))
	{
		*p_is_alive = 1;
	}
	else
	{
		*p_is_alive = 0;
	}

	return status;
}

uint8_t vl53lmz_init(
		VL53LMZ_Configuration		*p_dev)
{
	uint8_t tmp, status = VL53LMZ_STATUS_OK;
	uint8_t pipe_ctrl[] = {VL53LMZ_NB_TARGET_PER_ZONE, 0x00, 0x01, 0x00};
	uint32_t single_range = 0x01;

	p_dev->is_auto_stop_enabled = (uint8_t)0x0;

	/* method below copied from vl52l5cx_is_alive() */
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x00);
	status |= RdByte(&(p_dev->platform), 0, &(p_dev->device_id));
	status |= RdByte(&(p_dev->platform), 1, &(p_dev->revision_id));
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x02);
	if((p_dev->device_id!=(uint8_t)0xF0)
		|| ((p_dev->revision_id!=(uint8_t)REVISION_CUT11) && (p_dev->revision_id!=(uint8_t)REVISION_CUT12) && (p_dev->revision_id!=(uint8_t)REVISION_L8))) {
		/* unexpected combination of device and revision IDs */
		status = VL53LMZ_STATUS_UNKNOWN_DEVICE;
		goto exit;
	}

	/* SW reboot sequence */
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x00);

	status |= WrByte(&(p_dev->platform), 0x0009, 0x04);
	status |= WrByte(&(p_dev->platform), 0x000F, 0x40);
	status |= WrByte(&(p_dev->platform), 0x000A, 0x03);
	status |= RdByte(&(p_dev->platform), 0x7FFF, &tmp);
	status |= WrByte(&(p_dev->platform), 0x000C, 0x01);

	status |= WrByte(&(p_dev->platform), 0x0101, 0x00);
	status |= WrByte(&(p_dev->platform), 0x0102, 0x00);
	status |= WrByte(&(p_dev->platform), 0x010A, 0x01);
	status |= WrByte(&(p_dev->platform), 0x4002, 0x01);
	status |= WrByte(&(p_dev->platform), 0x4002, 0x00);
	status |= WrByte(&(p_dev->platform), 0x010A, 0x03);
	status |= WrByte(&(p_dev->platform), 0x0103, 0x01);
	status |= WrByte(&(p_dev->platform), 0x000C, 0x00);
	status |= WrByte(&(p_dev->platform), 0x000F, 0x43);
	status |= WaitMs(&(p_dev->platform), 1);

	status |= WrByte(&(p_dev->platform), 0x000F, 0x40);
	status |= WrByte(&(p_dev->platform), 0x000A, 0x01);
	status |= WaitMs(&(p_dev->platform), 100);

	/* Wait for sensor booted (several ms required to get sensor ready ) */
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x00);
	status |= _vl53lmz_poll_for_answer(p_dev, 1, 0, 0x06, 0xff, 1);
	if(status != (uint8_t)0){
		goto exit;
	}

	status |= WrByte(&(p_dev->platform), 0x000E, 0x01);

	/* Enable FW access */
	if ( p_dev->revision_id == (uint8_t)REVISION_L8 ) {
		status |= WrByte(&(p_dev->platform), 0x7fff, 0x01);
		status |= WrByte(&(p_dev->platform), 0x06, 0x01);
		status |= _vl53lmz_poll_for_answer(p_dev, 1, 0, 0x21, 0xFF, 0x4);
	}
	else {
		status |= WrByte(&(p_dev->platform), 0x7fff, 0x02);
		status |= WrByte(&(p_dev->platform), 0x03, 0x0D);
		status |= WrByte(&(p_dev->platform), 0x7fff, 0x01);
		status |= _vl53lmz_poll_for_answer(p_dev, 1, 0, 0x21, 0x10, 0x10);
	}
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x00);

	/* Enable host access to GO1 */
	status |= RdByte(&(p_dev->platform), 0x7fff, &tmp);
	status |= WrByte(&(p_dev->platform), 0x0C, 0x01);

	/* Power ON status */
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x00);
	status |= WrByte(&(p_dev->platform), 0x101, 0x00);
	status |= WrByte(&(p_dev->platform), 0x102, 0x00);
	status |= WrByte(&(p_dev->platform), 0x010A, 0x01);
	status |= WrByte(&(p_dev->platform), 0x4002, 0x01);
	status |= WrByte(&(p_dev->platform), 0x4002, 0x00);
	status |= WrByte(&(p_dev->platform), 0x010A, 0x03);
	status |= WrByte(&(p_dev->platform), 0x103, 0x01);
	status |= WrByte(&(p_dev->platform), 0x400F, 0x00);
	status |= WrByte(&(p_dev->platform), 0x21A, 0x43);
	status |= WrByte(&(p_dev->platform), 0x21A, 0x03);
	status |= WrByte(&(p_dev->platform), 0x21A, 0x01);
	status |= WrByte(&(p_dev->platform), 0x21A, 0x00);
	status |= WrByte(&(p_dev->platform), 0x219, 0x00);
	status |= WrByte(&(p_dev->platform), 0x21B, 0x00);

	/* Wake up MCU */
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x00);
	status |= RdByte(&(p_dev->platform), 0x7fff, &tmp);
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x01);
	status |= WrByte(&(p_dev->platform), 0x20, 0x07);
	status |= WrByte(&(p_dev->platform), 0x20, 0x06);

	/* Download FW into VL53LMZ */
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x09);
	status |= WrMulti(&(p_dev->platform),0,
		(uint8_t*)&VL53LMZ_FIRMWARE[0],0x8000);
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x0a);
	status |= WrMulti(&(p_dev->platform),0,
		(uint8_t*)&VL53LMZ_FIRMWARE[0x8000],0x8000);
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x0b);
	status |= WrMulti(&(p_dev->platform),0,
		(uint8_t*)&VL53LMZ_FIRMWARE[0x10000],0x5000);
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x01);

	/* Check if FW correctly downloaded */
	if ( p_dev->revision_id == (uint8_t)REVISION_L8 ) {
		status |= WrByte(&(p_dev->platform), 0x7fff, 0x01);
		status |= WrByte(&(p_dev->platform), 0x06, 0x03);
		status |= WaitMs(&(p_dev->platform), 5);
	}
	else {
		status |= WrByte(&(p_dev->platform), 0x7fff, 0x02);
		status |= WrByte(&(p_dev->platform), 0x03, 0x0D);
		status |= WrByte(&(p_dev->platform), 0x7fff, 0x01);
		status |= _vl53lmz_poll_for_answer(p_dev, 1, 0, 0x21, 0x10, 0x10);
	}
	if(status != (uint8_t)0) {
		goto exit;
	}
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x00);
	status |= RdByte(&(p_dev->platform), 0x7fff, &tmp);
	status |= WrByte(&(p_dev->platform), 0x0C, 0x01);

	/* Reset MCU and wait boot */
	status |= WrByte(&(p_dev->platform), 0x7FFF, 0x00);
	status |= WrByte(&(p_dev->platform), 0x114, 0x00);
	status |= WrByte(&(p_dev->platform), 0x115, 0x00);
	status |= WrByte(&(p_dev->platform), 0x116, 0x42);
	status |= WrByte(&(p_dev->platform), 0x117, 0x00);
	status |= WrByte(&(p_dev->platform), 0x0B, 0x00);
	status |= RdByte(&(p_dev->platform), 0x7fff, &tmp);
	status |= WrByte(&(p_dev->platform), 0x0C, 0x00);
	status |= WrByte(&(p_dev->platform), 0x0B, 0x01);

	status |= _vl53lmz_poll_for_mcu_boot(p_dev);
	if(status != (uint8_t)0){
		goto exit;
	}

	status |= WrByte(&(p_dev->platform), 0x7fff, 0x02);

	/* Get offset NVM data and store them into the offset buffer */
	status |= WrMulti(&(p_dev->platform), 0x2fd8,
		(uint8_t*)VL53LMZ_GET_NVM_CMD, sizeof(VL53LMZ_GET_NVM_CMD));
	status |= _vl53lmz_poll_for_answer(p_dev, 4, 0,
		VL53LMZ_UI_CMD_STATUS, 0xff, 2);
	status |= RdMulti(&(p_dev->platform), VL53LMZ_UI_CMD_START,
		p_dev->temp_buffer, VL53LMZ_NVM_DATA_SIZE);
	(void)memcpy(p_dev->offset_data, p_dev->temp_buffer,
		VL53LMZ_OFFSET_BUFFER_SIZE);
	status |= _vl53lmz_send_offset_data(p_dev, VL53LMZ_RESOLUTION_4X4);

	/* Set default Xtalk shape. Send Xtalk to sensor */
	p_dev->default_xtalk = (uint8_t*)VL53LMZ_DEFAULT_XTALK;
	(void)memcpy(p_dev->xtalk_data, (uint8_t*)VL53LMZ_DEFAULT_XTALK,
		VL53LMZ_XTALK_BUFFER_SIZE);
	status |= _vl53lmz_send_xtalk_data(p_dev, VL53LMZ_RESOLUTION_4X4);

	/* Send default configuration to VL53L5CX firmware */
	if ( p_dev->revision_id == (uint8_t)REVISION_L8 ) {
		p_dev->default_configuration = (uint8_t*)VL53L8_DEFAULT_CONFIGURATION;
		status |= WrMulti(&(p_dev->platform), 0x2c34,
							p_dev->default_configuration,
							sizeof(VL53L8_DEFAULT_CONFIGURATION));
	}
	else {
		p_dev->default_configuration = (uint8_t*)VL53L7_DEFAULT_CONFIGURATION;
		status |= WrMulti(&(p_dev->platform), 0x2c34,
							p_dev->default_configuration,
							sizeof(VL53L7_DEFAULT_CONFIGURATION));
	}

	status |= _vl53lmz_poll_for_answer(p_dev, 4, 1, VL53LMZ_UI_CMD_STATUS, 0xff, 0x03);

	status |= vl53lmz_dci_write_data(p_dev, (uint8_t*)&pipe_ctrl,
		VL53LMZ_DCI_PIPE_CONTROL, (uint16_t)sizeof(pipe_ctrl));
#if VL53LMZ_NB_TARGET_PER_ZONE != 1
	tmp = VL53LMZ_NB_TARGET_PER_ZONE;
	status |= vl53lmz_dci_replace_data(p_dev, p_dev->temp_buffer,
		VL53LMZ_DCI_FW_NB_TARGET, 16,
	(uint8_t*)&tmp, 1, 0x0C);
#endif

	status |= vl53lmz_dci_write_data(p_dev, (uint8_t*)&single_range,
			VL53LMZ_DCI_SINGLE_RANGE,
			(uint16_t)sizeof(single_range));

exit:
	return status;
}

uint8_t vl53lmz_set_i2c_address(
		VL53LMZ_Configuration		*p_dev,
		uint16_t				i2c_address)
{
	uint8_t status = VL53LMZ_STATUS_OK;

	status |= WrByte(&(p_dev->platform), 0x7fff, 0x00);
	status |= WrByte(&(p_dev->platform), 0x4, (uint8_t)(i2c_address >> 1));
	p_dev->platform.address = i2c_address;
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x02);

	return status;
}

uint8_t vl53lmz_get_power_mode(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				*p_power_mode)
{
	uint8_t tmp, status = VL53LMZ_STATUS_OK;

	status |= WrByte(&(p_dev->platform), 0x7FFF, 0x00);
	status |= RdByte(&(p_dev->platform), 0x009, &tmp);

	switch(tmp)
	{
		case 0x4:
			*p_power_mode = VL53LMZ_POWER_MODE_WAKEUP;
			break;
		case 0x2:
			*p_power_mode = VL53LMZ_POWER_MODE_SLEEP;

			break;
		default:
			*p_power_mode = 0;
			status = VL53LMZ_STATUS_ERROR;
			break;
	}

	status |= WrByte(&(p_dev->platform), 0x7FFF, 0x02);

	return status;
}

uint8_t vl53lmz_set_power_mode(
		VL53LMZ_Configuration		*p_dev,
		uint8_t					power_mode)
{
	uint8_t current_power_mode, status = VL53LMZ_STATUS_OK;

	status |= vl53lmz_get_power_mode(p_dev, &current_power_mode);
	if(power_mode != current_power_mode)
	{
	switch(power_mode)
	{
		case VL53LMZ_POWER_MODE_WAKEUP:
			status |= WrByte(&(p_dev->platform), 0x7FFF, 0x00);
			status |= WrByte(&(p_dev->platform), 0x09, 0x04);
			status |= _vl53lmz_poll_for_answer(
						p_dev, 1, 0, 0x06, 0x01, 1);
			break;

		case VL53LMZ_POWER_MODE_SLEEP:
			status |= WrByte(&(p_dev->platform), 0x7FFF, 0x00);
			status |= WrByte(&(p_dev->platform), 0x09, 0x02);
			status |= _vl53lmz_poll_for_answer(
						p_dev, 1, 0, 0x06, 0x01, 0);
			break;

		default:
			status = VL53LMZ_STATUS_ERROR;
			break;
		}
		status |= WrByte(&(p_dev->platform), 0x7FFF, 0x02);
	}

	return status;
}

uint8_t vl53lmz_start_ranging(
		VL53LMZ_Configuration		*p_dev)
{
	uint8_t status = VL53LMZ_STATUS_OK;

	status = vl53lmz_create_output_config( p_dev );
	if (status != VL53LMZ_STATUS_OK)
		return status;

	status = vl53lmz_send_output_config_and_start( p_dev );

	return status;
}

uint8_t vl53lmz_stop_ranging(
		VL53LMZ_Configuration		*p_dev)
{
	uint8_t tmp = 0, status = VL53LMZ_STATUS_OK;
	uint16_t timeout = 0;
	uint32_t auto_stop_flag = 0;

	status |= RdMulti(&(p_dev->platform),
						  0x2FFC, (uint8_t*)&auto_stop_flag, 4);

	if((auto_stop_flag != (uint32_t)0x4FF)
		&& (p_dev->is_auto_stop_enabled == (uint8_t)1))
	{
			status |= WrByte(&(p_dev->platform), 0x7fff, 0x00);

			/* Provoke MCU stop */
			status |= WrByte(&(p_dev->platform), 0x15, 0x16);
			status |= WrByte(&(p_dev->platform), 0x14, 0x01);

			/* Poll for G02 status 0 MCU stop */
			while(((tmp & (uint8_t)0x80) >> 7) == (uint8_t)0x00)
			{
				status |= RdByte(&(p_dev->platform), 0x6, &tmp);
				status |= WaitMs(&(p_dev->platform), 10);
				timeout++;	/* Timeout reached after 5 seconds */

				if(timeout > (uint16_t)500)
				{
					status |= tmp;
					break;
				}
			}
		}

	/* Check GO2 status 1 if status is still OK */
	status |= RdByte(&(p_dev->platform), 0x6, &tmp);
	if((tmp & (uint8_t)0x80) != (uint8_t)0){
		status |= RdByte(&(p_dev->platform), 0x7, &tmp);
		if((tmp != (uint8_t)0x84) && (tmp != (uint8_t)0x85)){
		   status |= tmp;
		}
	}

	/* Undo MCU stop */
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x00);
	status |= WrByte(&(p_dev->platform), 0x14, 0x00);
	status |= WrByte(&(p_dev->platform), 0x15, 0x00);

	/* Stop xshut bypass */
	status |= WrByte(&(p_dev->platform), 0x09, 0x04);
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x02);

	return status;
}

uint8_t vl53lmz_check_data_ready(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				*p_isReady)
{
	uint8_t status = VL53LMZ_STATUS_OK;
	*p_isReady = 0;

	status |= RdMulti(&(p_dev->platform), 0x0, p_dev->temp_buffer, 4);

	if ( status == VL53LMZ_STATUS_OK ){
		if((p_dev->temp_buffer[0] != p_dev->streamcount)
				&& (p_dev->temp_buffer[0] != (uint8_t)255)
				&& (p_dev->temp_buffer[1] == (uint8_t)0x5)
				&& ((p_dev->temp_buffer[2] & (uint8_t)0x5) == (uint8_t)0x5)
				&& ((p_dev->temp_buffer[3] & (uint8_t)0x10) ==(uint8_t)0x10)
				)
		{
			*p_isReady = (uint8_t)1;
			 p_dev->streamcount = p_dev->temp_buffer[0];
		}
		else
		{
			if ((p_dev->temp_buffer[3] & (uint8_t)0x80) != (uint8_t)0)
			{
				status |= p_dev->temp_buffer[2];	/* Return GO2 error status */
			}

			*p_isReady = 0;
		}
	}
	return status;
}

uint8_t vl53lmz_get_ranging_data(
		VL53LMZ_Configuration		*p_dev,
		VL53LMZ_ResultsData		*p_results)
{
	uint8_t status = VL53LMZ_STATUS_OK;
	union Block_header *bh_ptr;
	uint16_t header_id, footer_id;
	uint32_t i, msize;
	status |= RdMulti(&(p_dev->platform), 0x0,
			p_dev->temp_buffer, p_dev->data_read_size);
	p_dev->streamcount = p_dev->temp_buffer[0];
	SwapBuffer(p_dev->temp_buffer, (uint16_t)p_dev->data_read_size);

	/* Start conversion at position 16 to avoid headers */
	for (i = (uint32_t)16; i < (uint32_t)p_dev->data_read_size; i+=(uint32_t)4)
	{
		bh_ptr = (union Block_header *)&(p_dev->temp_buffer[i]);
		if ((bh_ptr->type > (uint32_t)0x1) 
					&& (bh_ptr->type < (uint32_t)0xd))
		{
			msize = bh_ptr->type * bh_ptr->size;
		}
		else
		{
			msize = bh_ptr->size;
		}

		switch(bh_ptr->idx){
			case VL53LMZ_METADATA_IDX:
				p_results->silicon_temp_degc =
						(int8_t)p_dev->temp_buffer[i + (uint32_t)12];
				break;

#ifndef VL53LMZ_DISABLE_AMBIENT_PER_SPAD
			case VL53LMZ_AMBIENT_RATE_IDX:
				(void)memcpy(p_results->ambient_per_spad,
				&(p_dev->temp_buffer[i + (uint32_t)4]), msize);
				break;
#endif
#ifndef VL53LMZ_DISABLE_NB_SPADS_ENABLED
			case VL53LMZ_SPAD_COUNT_IDX:
				(void)memcpy(p_results->nb_spads_enabled,
				&(p_dev->temp_buffer[i + (uint32_t)4]), msize);
				break;
#endif
#ifndef VL53LMZ_DISABLE_NB_TARGET_DETECTED
			case VL53LMZ_NB_TARGET_DETECTED_IDX:
				(void)memcpy(p_results->nb_target_detected,
				&(p_dev->temp_buffer[i + (uint32_t)4]), msize);
				break;
#endif
#ifndef VL53LMZ_DISABLE_SIGNAL_PER_SPAD
			case VL53LMZ_SIGNAL_RATE_IDX:
				(void)memcpy(p_results->signal_per_spad,
				&(p_dev->temp_buffer[i + (uint32_t)4]), msize);
				break;
#endif
#ifndef VL53LMZ_DISABLE_RANGE_SIGMA_MM
			case VL53LMZ_RANGE_SIGMA_MM_IDX:
				(void)memcpy(p_results->range_sigma_mm,
				&(p_dev->temp_buffer[i + (uint32_t)4]), msize);
				break;
#endif
#ifndef VL53LMZ_DISABLE_DISTANCE_MM
			case VL53LMZ_DISTANCE_IDX:
				(void)memcpy(p_results->distance_mm,
				&(p_dev->temp_buffer[i + (uint32_t)4]), msize);
				break;
#endif
#ifndef VL53LMZ_DISABLE_REFLECTANCE_PERCENT
			case VL53LMZ_REFLECTANCE_EST_PC_IDX:
				(void)memcpy(p_results->reflectance,
				&(p_dev->temp_buffer[i + (uint32_t)4]), msize);
				break;
#endif
#ifndef VL53LMZ_DISABLE_TARGET_STATUS
			case VL53LMZ_TARGET_STATUS_IDX:
				(void)memcpy(p_results->target_status,
				&(p_dev->temp_buffer[i + (uint32_t)4]), msize);
				break;
#endif
#ifndef VL53LMZ_DISABLE_MOTION_INDICATOR
			case VL53LMZ_MOTION_DETEC_IDX:
				(void)memcpy(&p_results->motion_indicator,
				&(p_dev->temp_buffer[i + (uint32_t)4]), msize);
				break;
#endif
			default:
				break;
		}
		i += msize;
	}

#ifndef VL53LMZ_USE_RAW_FORMAT

	/* Convert data into their real format */
#ifndef VL53LMZ_DISABLE_AMBIENT_PER_SPAD
	for(i = 0; i < (uint32_t)VL53LMZ_RESOLUTION_8X8; i++)
	{
		p_results->ambient_per_spad[i] /= (uint32_t)2048;
	}
#endif

	for(i = 0; i < (uint32_t)(VL53LMZ_RESOLUTION_8X8
			*VL53LMZ_NB_TARGET_PER_ZONE); i++)
	{
#ifndef VL53LMZ_DISABLE_DISTANCE_MM
		p_results->distance_mm[i] /= 4;
		if(p_results->distance_mm[i] < 0)
		{
			p_results->distance_mm[i] = 0;
		}
#endif
#ifndef VL53LMZ_DISABLE_REFLECTANCE_PERCENT
		p_results->reflectance[i] /= (uint8_t)2;
#endif
#ifndef VL53LMZ_DISABLE_RANGE_SIGMA_MM
		p_results->range_sigma_mm[i] /= (uint16_t)128;
#endif
#ifndef VL53LMZ_DISABLE_SIGNAL_PER_SPAD
		p_results->signal_per_spad[i] /= (uint32_t)2048;
#endif
	}

	/* Set target status to 255 if no target is detected for this zone */
#ifndef VL53LMZ_DISABLE_NB_TARGET_DETECTED
	uint32_t j;
	for(i = 0; i < (uint32_t)VL53LMZ_RESOLUTION_8X8; i++)
	{
		if(p_results->nb_target_detected[i] == (uint8_t)0){
			for(j = 0; j < (uint32_t)
				VL53LMZ_NB_TARGET_PER_ZONE; j++)
			{
#ifndef VL53LMZ_DISABLE_TARGET_STATUS
				p_results->target_status
				[((uint32_t)VL53LMZ_NB_TARGET_PER_ZONE*(uint32_t)i) + j]=(uint8_t)255;
#endif
			}
		}
	}
#endif

#ifndef VL53LMZ_DISABLE_MOTION_INDICATOR
	for(i = 0; i < (uint32_t)32; i++)
	{
		p_results->motion_indicator.motion[i] /= (uint32_t)65535;
	}
#endif

#endif

	/* Check if footer id and header id are matching. This allows to detect
	 * corrupted frames */
	header_id = ((uint16_t)(p_dev->temp_buffer[0x8])<<8) & 0xFF00U;
	header_id |= ((uint16_t)(p_dev->temp_buffer[0x9])) & 0x00FFU;

	footer_id = ((uint16_t)(p_dev->temp_buffer[p_dev->data_read_size
		- (uint32_t)4]) << 8) & 0xFF00U;
	footer_id |= ((uint16_t)(p_dev->temp_buffer[p_dev->data_read_size
		- (uint32_t)3])) & 0xFFU;

	if(header_id != footer_id)
	{
		status |= VL53LMZ_STATUS_CORRUPTED_FRAME;
	}

	return status;
}

uint8_t vl53lmz_get_resolution(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				*p_resolution)
{
	uint8_t status = VL53LMZ_STATUS_OK;

	status |= vl53lmz_dci_read_data(p_dev, p_dev->temp_buffer,
			VL53LMZ_DCI_ZONE_CONFIG, 8);
	*p_resolution = p_dev->temp_buffer[0x00]*p_dev->temp_buffer[0x01];

	return status;
}



uint8_t vl53lmz_set_resolution(
		VL53LMZ_Configuration		 *p_dev,
		uint8_t				resolution)
{
	uint8_t status = VL53LMZ_STATUS_OK;

	switch(resolution){
		case VL53LMZ_RESOLUTION_4X4:
			status |= vl53lmz_dci_read_data(p_dev,
					p_dev->temp_buffer,
					VL53LMZ_DCI_DSS_CONFIG, 16);
			p_dev->temp_buffer[0x04] = 64;
			p_dev->temp_buffer[0x06] = 64;
			p_dev->temp_buffer[0x09] = 4;
			status |= vl53lmz_dci_write_data(p_dev,
					p_dev->temp_buffer,
					VL53LMZ_DCI_DSS_CONFIG, 16);

			status |= vl53lmz_dci_read_data(p_dev,
					p_dev->temp_buffer,
					VL53LMZ_DCI_ZONE_CONFIG, 8);
			p_dev->temp_buffer[0x00] = 4;
			p_dev->temp_buffer[0x01] = 4;
			p_dev->temp_buffer[0x04] = 8;
			p_dev->temp_buffer[0x05] = 8;
			status |= vl53lmz_dci_write_data(p_dev,
					p_dev->temp_buffer,
					VL53LMZ_DCI_ZONE_CONFIG, 8);
			break;

		case VL53LMZ_RESOLUTION_8X8:
			status |= vl53lmz_dci_read_data(p_dev,
					p_dev->temp_buffer,
					VL53LMZ_DCI_DSS_CONFIG, 16);
			p_dev->temp_buffer[0x04] = 16;
			p_dev->temp_buffer[0x06] = 16;
			p_dev->temp_buffer[0x09] = 1;
			status |= vl53lmz_dci_write_data(p_dev,
					p_dev->temp_buffer,
					VL53LMZ_DCI_DSS_CONFIG, 16);

			status |= vl53lmz_dci_read_data(p_dev,
					p_dev->temp_buffer,
					VL53LMZ_DCI_ZONE_CONFIG, 8);
			p_dev->temp_buffer[0x00] = 8;
			p_dev->temp_buffer[0x01] = 8;
			p_dev->temp_buffer[0x04] = 4;
			p_dev->temp_buffer[0x05] = 4;
			status |= vl53lmz_dci_write_data(p_dev,
					p_dev->temp_buffer,
					VL53LMZ_DCI_ZONE_CONFIG, 8);

			break;

		default:
			status = VL53LMZ_STATUS_INVALID_PARAM;
			break;
		}

	status |= _vl53lmz_send_offset_data(p_dev, resolution);
	status |= _vl53lmz_send_xtalk_data(p_dev, resolution);

	return status;
}

uint8_t vl53lmz_get_ranging_frequency_hz(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				*p_frequency_hz)
{
	uint8_t status = VL53LMZ_STATUS_OK;

	status |= vl53lmz_dci_read_data(p_dev, (uint8_t*)p_dev->temp_buffer,
			VL53LMZ_DCI_FREQ_HZ, 4);
	*p_frequency_hz = p_dev->temp_buffer[0x01];

	return status;
}

uint8_t vl53lmz_set_ranging_frequency_hz(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				frequency_hz)
{
	uint8_t status = VL53LMZ_STATUS_OK;

	status |= vl53lmz_dci_replace_data(p_dev, p_dev->temp_buffer,
					VL53LMZ_DCI_FREQ_HZ, 4,
					(uint8_t*)&frequency_hz, 1, 0x01);

	return status;
}

uint8_t vl53lmz_get_integration_time_ms(
		VL53LMZ_Configuration		*p_dev,
		uint32_t			*p_time_ms)
{
	uint8_t status = VL53LMZ_STATUS_OK;

	status |= vl53lmz_dci_read_data(p_dev, (uint8_t*)p_dev->temp_buffer,
			VL53LMZ_DCI_INT_TIME, 20);

	(void)memcpy(p_time_ms, &(p_dev->temp_buffer[0x0]), 4);
	*p_time_ms /= (uint32_t)1000;

	return status;
}

uint8_t vl53lmz_set_integration_time_ms(
		VL53LMZ_Configuration		*p_dev,
		uint32_t			integration_time_ms)
{
	uint8_t status = VL53LMZ_STATUS_OK;
		uint32_t integration = integration_time_ms;

	/* Integration time must be between 2ms and 1000ms */
	if((integration < (uint32_t)2)
		   || (integration > (uint32_t)1000))
	{
		status |= VL53LMZ_STATUS_INVALID_PARAM;
	}else
	{
		integration *= (uint32_t)1000;

		status |= vl53lmz_dci_replace_data(p_dev, p_dev->temp_buffer,
				VL53LMZ_DCI_INT_TIME, 20,
				(uint8_t*)&integration, 4, 0x00);
	}

	return status;
}

uint8_t vl53lmz_get_sharpener_percent(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				*p_sharpener_percent)
{
	uint8_t status = VL53LMZ_STATUS_OK;

	status |= vl53lmz_dci_read_data(p_dev,p_dev->temp_buffer,
			VL53LMZ_DCI_SHARPENER, 16);

	*p_sharpener_percent = (p_dev->temp_buffer[0xD]
								*(uint8_t)100)/(uint8_t)255;

	return status;
}

uint8_t vl53lmz_set_sharpener_percent(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				sharpener_percent)
{
	uint8_t status = VL53LMZ_STATUS_OK;
		uint8_t sharpener;

	if(sharpener_percent >= (uint8_t)100)
	{
		status |= VL53LMZ_STATUS_INVALID_PARAM;
	}
	else
	{
		sharpener = (sharpener_percent*(uint8_t)255)/(uint8_t)100;
		status |= vl53lmz_dci_replace_data(p_dev, p_dev->temp_buffer,
				VL53LMZ_DCI_SHARPENER, 16,
								(uint8_t*)&sharpener, 1, 0xD);
	}

	return status;
}

uint8_t vl53lmz_get_target_order(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				*p_target_order)
{
	uint8_t status = VL53LMZ_STATUS_OK;

	status |= vl53lmz_dci_read_data(p_dev, (uint8_t*)p_dev->temp_buffer,
			VL53LMZ_DCI_TARGET_ORDER, 4);
	*p_target_order = (uint8_t)p_dev->temp_buffer[0x0];

	return status;
}

uint8_t vl53lmz_set_target_order(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				target_order)
{
	uint8_t status = VL53LMZ_STATUS_OK;

	if((target_order == (uint8_t)VL53LMZ_TARGET_ORDER_CLOSEST)
		|| (target_order == (uint8_t)VL53LMZ_TARGET_ORDER_STRONGEST))
	{
		status |= vl53lmz_dci_replace_data(p_dev, p_dev->temp_buffer,
				VL53LMZ_DCI_TARGET_ORDER, 4,
								(uint8_t*)&target_order, 1, 0x0);
	}else
	{
		status |= VL53LMZ_STATUS_INVALID_PARAM;
	}

	return status;
}

uint8_t vl53lmz_get_ranging_mode(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				*p_ranging_mode)
{
	uint8_t status = VL53LMZ_STATUS_OK;

	status |= vl53lmz_dci_read_data(p_dev, p_dev->temp_buffer,
			VL53LMZ_DCI_RANGING_MODE, 8);

	if(p_dev->temp_buffer[0x01] == (uint8_t)0x1)
	{
		*p_ranging_mode = VL53LMZ_RANGING_MODE_CONTINUOUS;
	}
	else
	{
		*p_ranging_mode = VL53LMZ_RANGING_MODE_AUTONOMOUS;
	}

	return status;
}

uint8_t vl53lmz_set_ranging_mode(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				ranging_mode)
{
	uint8_t status = VL53LMZ_STATUS_OK;
	uint32_t single_range = 0x00;

	status |= vl53lmz_dci_read_data(p_dev, p_dev->temp_buffer,
			VL53LMZ_DCI_RANGING_MODE, 8);

	switch(ranging_mode)
	{
		case VL53LMZ_RANGING_MODE_CONTINUOUS:
			p_dev->temp_buffer[0x01] = 0x1;
			p_dev->temp_buffer[0x03] = 0x3;
			single_range = 0x00;
			break;

		case VL53LMZ_RANGING_MODE_AUTONOMOUS:
			p_dev->temp_buffer[0x01] = 0x3;
			p_dev->temp_buffer[0x03] = 0x2;
			single_range = 0x01;
			break;

		default:
			status = VL53LMZ_STATUS_INVALID_PARAM;
			break;
	}

	status |= vl53lmz_dci_write_data(p_dev, p_dev->temp_buffer,
			VL53LMZ_DCI_RANGING_MODE, (uint16_t)8);

	status |= vl53lmz_dci_write_data(p_dev, (uint8_t*)&single_range,
			VL53LMZ_DCI_SINGLE_RANGE,
						(uint16_t)sizeof(single_range));

	return status;
}

uint8_t vl53lmz_enable_internal_cp(
		VL53LMZ_Configuration *p_dev)
{
	uint8_t status = VL53LMZ_STATUS_OK;
	uint8_t vcsel_bootup_fsm = 1;
	uint8_t analog_dynamic_pad_0 = 0;

	if 	( p_dev->revision_id==(uint8_t)REVISION_L8 )
		return( VL53LMZ_STATUS_FUNC_NOT_AVAILABLE );

	status |= vl53lmz_dci_replace_data(p_dev, p_dev->temp_buffer,
			VL53LMZ_DCI_INTERNAL_CP, 16,
			(uint8_t*)&vcsel_bootup_fsm, 1, 0x0A);

	status |= vl53lmz_dci_replace_data(p_dev, p_dev->temp_buffer,
			VL53LMZ_DCI_INTERNAL_CP, 16,
			(uint8_t*)&analog_dynamic_pad_0, 1, 0x0E);

	return status;
}

uint8_t vl53lmz_disable_internal_cp(
		VL53LMZ_Configuration *p_dev)
{
	uint8_t status = VL53LMZ_STATUS_OK;
	uint8_t vcsel_bootup_fsm = 0;
	uint8_t analog_dynamic_pad_0 = 1;

	status |= vl53lmz_dci_replace_data(p_dev, p_dev->temp_buffer,
			VL53LMZ_DCI_INTERNAL_CP, 16,
			(uint8_t*)&vcsel_bootup_fsm, 1, 0x0A);

	status |= vl53lmz_dci_replace_data(p_dev, p_dev->temp_buffer,
			VL53LMZ_DCI_INTERNAL_CP, 16,
			(uint8_t*)&analog_dynamic_pad_0, 1, 0x0E);

	return status;
}


uint8_t vl53lmz_get_external_sync_pin_enable(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				*p_is_sync_pin_enabled)
{
	uint8_t status = VL53LMZ_STATUS_OK;

	if 	( p_dev->revision_id!=(uint8_t)REVISION_L8 )
		return( VL53LMZ_STATUS_FUNC_NOT_AVAILABLE );

	status |= vl53lmz_dci_read_data(p_dev, p_dev->temp_buffer,
			VL53LMZ_DCI_SYNC_PIN, 4);

	/* Check bit 1 value (get sync pause bit) */
	if((p_dev->temp_buffer[3] & (uint8_t)0x2) != (uint8_t)0)
	{
		*p_is_sync_pin_enabled = (uint8_t)1;
	}
	else
	{
		*p_is_sync_pin_enabled = (uint8_t)0;
	}

	return status;
}

uint8_t vl53lmz_set_external_sync_pin_enable(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				enable_sync_pin)
{
	uint8_t status = VL53LMZ_STATUS_OK;
	uint32_t tmp;

	if 	( p_dev->revision_id!=(uint8_t)REVISION_L8 )
		return( VL53LMZ_STATUS_FUNC_NOT_AVAILABLE );

	status |= vl53lmz_dci_read_data(p_dev, p_dev->temp_buffer,
			VL53LMZ_DCI_SYNC_PIN, 4);
		tmp = (uint32_t)p_dev->temp_buffer[3];

	/* Update bit 1 with mask (set sync pause bit) */
	if(enable_sync_pin == (uint8_t)0)
	{
				tmp &= ~(1UL << 1);

	}
	else
	{
				tmp |= 1UL << 1;
	}

		p_dev->temp_buffer[3] = (uint8_t)tmp;
	status |= vl53lmz_dci_write_data(p_dev, p_dev->temp_buffer,
			VL53LMZ_DCI_SYNC_PIN, 4);

	return status;
}

uint8_t vl53lmz_get_glare_filter_cfg(
		VL53LMZ_Configuration	*p_dev,
		uint8_t					*p_threshold_pc_x10,
		int16_t					*p_max_range )
{
	uint8_t status = VL53LMZ_STATUS_OK;

	status = vl53lmz_dci_read_data(p_dev, (uint8_t*)p_dev->temp_buffer,
									VL53LMZ_DCI_GLARE_FILTER_CFG, 40);

	*p_threshold_pc_x10 = (uint8_t)((*((uint16_t *)&(p_dev->temp_buffer[30])) * 10U) / 256U);
	*p_max_range =  *((int16_t *)&(p_dev->temp_buffer[2]));

	return status;
}

uint8_t vl53lmz_set_glare_filter_cfg(
		VL53LMZ_Configuration	*p_dev,
		uint8_t					threshold_pc_x10,
		int16_t					max_range )
{
	uint8_t status = VL53LMZ_STATUS_OK;
	int16_t *p_int16;
	uint16_t *p_uint16;
	uint16_t scaled_threshold;

	status = vl53lmz_dci_read_data(p_dev, (uint8_t*)p_dev->temp_buffer,
									VL53LMZ_DCI_GLARE_FILTER_CFG, 40);

	/* updated the entries in reflectance threshold LUT	*/
	scaled_threshold = ((uint16_t)threshold_pc_x10 * 256U) / 10U;
	p_uint16 = (uint16_t *)&(p_dev->temp_buffer[30]);
	*p_uint16 = scaled_threshold;
	p_uint16++;
	*p_uint16 = scaled_threshold;
	p_uint16++;
	*p_uint16 = scaled_threshold;
	p_uint16++;

	/* update the max_filter_range field 	*/
	p_int16 = (int16_t *)&(p_dev->temp_buffer[2]);
	*p_int16 = max_range;

	if (threshold_pc_x10 == 0U) {
		/* threshold of zero means request to disabled GF entirely */
		p_dev->temp_buffer[37] = 1;	/* disable Glare Detection */
		p_dev->temp_buffer[38] = 1;	/* disable Glare Filtering */
	}
	else {
		p_dev->temp_buffer[37] = 0;	/* enable Glare Detection */
		p_dev->temp_buffer[38] = 0;	/* enable Glare Filtering */
	}

	status = vl53lmz_dci_write_data(p_dev, p_dev->temp_buffer,
								VL53LMZ_DCI_GLARE_FILTER_CFG, 40);

	return status;
}


uint8_t vl53lmz_dci_read_data(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				*data,
		uint32_t			index,
		uint16_t			data_size)
{
	int16_t i;
	uint8_t status = VL53LMZ_STATUS_OK;
		uint32_t rd_size = (uint32_t) data_size + (uint32_t)12;
	uint8_t cmd[] = {0x00, 0x00, 0x00, 0x00,
			0x00, 0x00, 0x00, 0x0f,
			0x00, 0x02, 0x00, 0x08};

	/* Check if tmp buffer is large enough */
	if((data_size + (uint16_t)12)>(uint16_t)VL53LMZ_TEMPORARY_BUFFER_SIZE)
	{
		status |= VL53LMZ_STATUS_ERROR;
	}
	else
	{
		cmd[0] = (uint8_t)(index >> 8);	
		cmd[1] = (uint8_t)(index & (uint32_t)0xff);			
		cmd[2] = (uint8_t)((data_size & (uint16_t)0xff0) >> 4);
		cmd[3] = (uint8_t)((data_size & (uint16_t)0xf) << 4);

	/* Request data reading from FW */
		status |= WrMulti(&(p_dev->platform),
			(VL53LMZ_UI_CMD_END-(uint16_t)11),cmd, sizeof(cmd));
		status |= _vl53lmz_poll_for_answer(p_dev, 4, 1,
			VL53LMZ_UI_CMD_STATUS,
			0xff, 0x03);

	/* Read new data sent (4 bytes header + data_size + 8 bytes footer) */
		status |= RdMulti(&(p_dev->platform), VL53LMZ_UI_CMD_START,
			p_dev->temp_buffer, rd_size);
		SwapBuffer(p_dev->temp_buffer, data_size + (uint16_t)12);

	/* Copy data from FW into input structure (-4 bytes to remove header) */
		for(i = 0 ; i < (int16_t)data_size;i++){
			data[i] = p_dev->temp_buffer[i + 4];
		}
	}

	return status;
}

uint8_t vl53lmz_dci_write_data(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				*data,
		uint32_t			index,
		uint16_t			data_size)
{
	uint8_t status = VL53LMZ_STATUS_OK;
	int16_t i;

	uint8_t headers[] = {0x00, 0x00, 0x00, 0x00};
	uint8_t footer[] = {0x00, 0x00, 0x00, 0x0f, 0x05, 0x01,
			(uint8_t)((data_size + (uint16_t)8) >> 8), 
			(uint8_t)((data_size + (uint16_t)8) & (uint8_t)0xFF)};

	uint16_t address = (uint16_t)VL53LMZ_UI_CMD_END -
		(data_size + (uint16_t)12) + (uint16_t)1;

	/* Check if cmd buffer is large enough */
	if((data_size + (uint16_t)12) 
		   > (uint16_t)VL53LMZ_TEMPORARY_BUFFER_SIZE)
	{
		status |= VL53LMZ_STATUS_ERROR;
	}
	else
	{
		headers[0] = (uint8_t)(index >> 8);
		headers[1] = (uint8_t)(index & (uint32_t)0xff);
		headers[2] = (uint8_t)(((data_size & (uint16_t)0xff0) >> 4));
		headers[3] = (uint8_t)((data_size & (uint16_t)0xf) << 4);

	/* Copy data from structure to FW format (+4 bytes to add header) */
		SwapBuffer(data, data_size);
		for(i = (int16_t)data_size - (int16_t)1 ; i >= 0; i--)
		{
			p_dev->temp_buffer[i + 4] = data[i];
		}

	/* Add headers and footer */
		(void)memcpy(&p_dev->temp_buffer[0], headers, sizeof(headers));
		(void)memcpy(&p_dev->temp_buffer[data_size + (uint16_t)4],
			footer, sizeof(footer));

	/* Send data to FW */
		status |= WrMulti(&(p_dev->platform),address,
			p_dev->temp_buffer,
			(uint32_t)((uint32_t)data_size + (uint32_t)12));
		status |= _vl53lmz_poll_for_answer(p_dev, 4, 1,
			VL53LMZ_UI_CMD_STATUS, 0xff, 0x03);

		SwapBuffer(data, data_size);
	}

	return status;
}

uint8_t vl53lmz_dci_replace_data(
		VL53LMZ_Configuration		*p_dev,
		uint8_t				*data,
		uint32_t			index,
		uint16_t			data_size,
		uint8_t				*new_data,
		uint16_t			new_data_size,
		uint16_t			new_data_pos)
{
	uint8_t status = VL53LMZ_STATUS_OK;

	status |= vl53lmz_dci_read_data(p_dev, data, index, data_size);
	(void)memcpy(&(data[new_data_pos]), new_data, new_data_size);
	status |= vl53lmz_dci_write_data(p_dev, data, index, data_size);

	return status;
}
uint8_t vl53lmz_create_output_config(
		VL53LMZ_Configuration	  *p_dev ) {

	uint8_t status = VL53LMZ_STATUS_OK;

	/* Send addresses of possible output */
	uint32_t default_output_config[] ={
		VL53LMZ_START_BH,
		VL53LMZ_METADATA_BH,
		VL53LMZ_COMMONDATA_BH,
		VL53LMZ_AMBIENT_RATE_BH,
		VL53LMZ_SPAD_COUNT_BH,
		VL53LMZ_NB_TARGET_DETECTED_BH,
		VL53LMZ_SIGNAL_RATE_BH,
		VL53LMZ_RANGE_SIGMA_MM_BH,
		VL53LMZ_DISTANCE_BH,
		VL53LMZ_REFLECTANCE_BH,
		VL53LMZ_TARGET_STATUS_BH,
		VL53LMZ_MOTION_DETECT_BH };

	memset(g_output_config, 0x00, sizeof(g_output_config));
	memcpy(g_output_config, default_output_config, sizeof(default_output_config));

	/* Enable mandatory output (meta and common data) */
	g_output_bh_enable[0] = 0x00000007U;
	g_output_bh_enable[1] = 0x00000000U;
	g_output_bh_enable[2] = 0x00000000U;
	g_output_bh_enable[3] = 0x00000000U;

	/* Enable selected outputs in the 'platform.h' file */
#ifndef VL53LMZ_DISABLE_AMBIENT_PER_SPAD
	g_output_bh_enable[0] += (uint32_t)8;
#endif
#ifndef VL53LMZ_DISABLE_NB_SPADS_ENABLED
	g_output_bh_enable[0] += (uint32_t)16;
#endif
#ifndef VL53LMZ_DISABLE_NB_TARGET_DETECTED
	g_output_bh_enable[0] += (uint32_t)32;
#endif
#ifndef VL53LMZ_DISABLE_SIGNAL_PER_SPAD
	g_output_bh_enable[0] += (uint32_t)64;
#endif
#ifndef VL53LMZ_DISABLE_RANGE_SIGMA_MM
	g_output_bh_enable[0] += (uint32_t)128;
#endif
#ifndef VL53LMZ_DISABLE_DISTANCE_MM
	g_output_bh_enable[0] += (uint32_t)256;
#endif
#ifndef VL53LMZ_DISABLE_REFLECTANCE_PERCENT
	g_output_bh_enable[0] += (uint32_t)512;
#endif
#ifndef VL53LMZ_DISABLE_TARGET_STATUS
	g_output_bh_enable[0] += (uint32_t)1024;
#endif
#ifndef VL53LMZ_DISABLE_MOTION_INDICATOR
	g_output_bh_enable[0] += (uint32_t)2048;
#endif

	return status;
}


uint8_t vl53lmz_send_output_config_and_start(
		VL53LMZ_Configuration	  *p_dev ) {

	uint8_t resolution, status = VL53LMZ_STATUS_OK;
	uint16_t tmp;
	uint32_t i;
	uint32_t header_config[2] = {0, 0};

	union Block_header *bh_ptr;
	uint8_t cmd[] = {0x00, 0x03, 0x00, 0x00};

	status |= vl53lmz_get_resolution(p_dev, &resolution);
	p_dev->data_read_size = 0;
	p_dev->streamcount = 255;

	/* Update data size */
	for (i = 0; i < (uint32_t)(sizeof(g_output_config)/sizeof(uint32_t)); i++)
	{
		if ((g_output_config[i] == (uint8_t)0)
					|| ((g_output_bh_enable[i/(uint32_t)32]
						 &((uint32_t)1 << (i%(uint32_t)32))) == (uint32_t)0))
		{
			continue;
		}

		bh_ptr = (union Block_header *)&(g_output_config[i]);
		if ( (bh_ptr->type >= 0x1) && (bh_ptr->type < 0x0d))
		{
			if ( bh_ptr->idx >= 0x54d0 ) {
				/* might be a zone or target data block */
				if ( bh_ptr->idx < (0x5890) )
				{
					/* it is zone data (does not depend on NB_TARGET_PER_ZONE) */
					bh_ptr->size = resolution;
				}
				else if (bh_ptr->idx < (uint16_t)(0x6C90))
				{
					/* it is a per-target data block (depends on NB_TARGET_PER_ZONE) */
					bh_ptr->size = resolution * VL53LMZ_NB_TARGET_PER_ZONE;
				}
			}
			p_dev->data_read_size += bh_ptr->type * bh_ptr->size;
		}
		else
		{
			p_dev->data_read_size += bh_ptr->size;
		}
		p_dev->data_read_size += (uint32_t)4;
	}
	p_dev->data_read_size += (uint32_t)24;


	if (p_dev->data_read_size > VL53LMZ_MAX_RESULTS_SIZE) {
		status |= VL53LMZ_STATUS_ERROR;
		return status;
	}

	status |= vl53lmz_dci_write_data(p_dev,
			(uint8_t*)&(g_output_config), VL53LMZ_DCI_OUTPUT_LIST,
			(uint16_t)sizeof(g_output_config));

	header_config[0] = p_dev->data_read_size;
	header_config[1] = i + (uint32_t)1;

	status |= vl53lmz_dci_write_data(p_dev,
			(uint8_t*)&(header_config), VL53LMZ_DCI_OUTPUT_CONFIG,
			(uint16_t)sizeof(header_config));

	status |= vl53lmz_dci_write_data(p_dev,
			(uint8_t*)&(g_output_bh_enable), VL53LMZ_DCI_OUTPUT_ENABLES,
			(uint16_t)sizeof(g_output_bh_enable));

	/* Start xshut bypass (interrupt mode) */
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x00);
	status |= WrByte(&(p_dev->platform), 0x09, 0x05);
	status |= WrByte(&(p_dev->platform), 0x7fff, 0x02);

	/* Start ranging session */
	status |= WrMulti(&(p_dev->platform), VL53LMZ_UI_CMD_END -
			(uint16_t)(4 - 1), (uint8_t*)cmd, sizeof(cmd));
	status |= _vl53lmz_poll_for_answer(p_dev, 4, 1,
			VL53LMZ_UI_CMD_STATUS, 0xff, 0x03);

	/* Read ui range data content and compare if data size is the correct one */
	status |= vl53lmz_dci_read_data(p_dev,
			(uint8_t*)p_dev->temp_buffer, 0x5440, 12);
	(void)memcpy(&tmp, &(p_dev->temp_buffer[0x8]), sizeof(tmp));
	if(tmp != p_dev->data_read_size) {
		status |= VL53LMZ_STATUS_ERROR;
	}

	return status;
}

uint8_t vl53lmz_add_output_block(
		VL53LMZ_Configuration	  *p_dev,
		uint32_t				block_header ) {
	uint8_t status = VL53LMZ_STATUS_OK;
	uint8_t i;

	for(i=0;i<NUM_OUTPUT_CONFIG_WORDS;i++) {
		if ( (g_output_config[i] == VL53L5_NULL_BH)   		/* reached current end of list      */
				|| (g_output_config[i] == block_header) )	/* OR, block already exists in list */
			break;
	}

	if ( i == NUM_OUTPUT_CONFIG_WORDS ) {
		/* no space found in output config list */
		status = VL53LMZ_STATUS_ERROR;
	}
	else {
		g_output_config[i] = block_header;
		g_output_bh_enable[0] |= ((uint32_t)1U)<<i;
	}

	return status;
}

uint8_t vl53lmz_disable_output_block(
		VL53LMZ_Configuration	  *p_dev,
		uint32_t				block_header ) {
	uint8_t status = VL53LMZ_STATUS_OK;
	uint8_t i;

	for(i=0;i<NUM_OUTPUT_CONFIG_WORDS;i++) {
		if (g_output_config[i] == block_header) {
			g_output_bh_enable[0] &= ~(((uint32_t)1)<<i);
			break;
		}

		if (g_output_config[i] == VL53L5_NULL_BH)
			break;
	}
	return status;
}


uint8_t vl53lmz_results_extract_block(
		VL53LMZ_Configuration		*p_dev,
		uint32_t					blk_index,
		uint8_t						*p_data,
		uint16_t					data_size ) {

	uint8_t status = VL53LMZ_STATUS_INVALID_PARAM;

	union Block_header *bh_ptr;
	uint32_t i, msize=0;

	for (i = 16; i < p_dev->data_read_size; )
	{
		bh_ptr = (union Block_header *)&(p_dev->temp_buffer[i]);

		if ((bh_ptr->type > 0x1) && (bh_ptr->type < 0xd)){
			msize = bh_ptr->size * bh_ptr->type;
		}
		else {
			msize = bh_ptr->size;
		}

		i += 4; /* skip over the block header */

		if ( bh_ptr->idx == blk_index ) {
			if (msize < data_size) {
				/* not enough data in block to fill requested buffer */
				status = VL53LMZ_STATUS_INVALID_PARAM;
			}
			else {
				memcpy(p_data, (uint8_t *)&(p_dev->temp_buffer[i]), data_size);
				status = VL53LMZ_STATUS_OK;
			}
			break;
		}
		i = i + msize;  /* add size of data block */
	}

	return status;
}

