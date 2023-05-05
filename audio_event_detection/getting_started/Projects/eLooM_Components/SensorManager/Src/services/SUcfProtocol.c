/**
  ******************************************************************************
  * @file    SUcfProtocol.c
  * @author  SRA - MCD
  * @brief
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

#include "services/SUcfProtocol.h"
#include "tx_api.h"
#include <stdio.h>

#define COMPRESSED_UCF_LINE_WIDTH  4U


sys_error_code_t UCFP_Init(SUcfProtocol_t *_this, ISensorLL_t *sensor_ll)
{
  assert_param(_this != NULL);
  assert_param(sensor_ll != NULL);

  _this->sensor_ll = sensor_ll;
  return SYS_NO_ERROR_CODE;
}

sys_error_code_t UCFP_LoadCompressedUcf(SUcfProtocol_t *_this, const char *p_ucf, uint32_t size)
{
  assert_param(_this != NULL);
  assert_param(p_ucf != NULL);
  assert_param(size > 0U);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  uint32_t ucf_lines = size / COMPRESSED_UCF_LINE_WIDTH;
  uint32_t i;
  char ucf_reg[3];
  char ucf_data[4];
  uint8_t reg;
  uint8_t data;

  /* Add string termination */
  ucf_reg[2] = '\0';
  ucf_data[2] = '\0';
  ucf_data[3] = '\0';

  for (i = 0; i < ucf_lines; i++)
  {
    if(*p_ucf == 'W' || *p_ucf == 'w')
    {
      /* Wait command */
      p_ucf++;
      ucf_data[0] = *(p_ucf++);
      ucf_data[1] = *(p_ucf++);
      ucf_data[2] = *(p_ucf++);

      uint16_t ms = (uint16_t)strtol(ucf_data, NULL, 16);

      tx_thread_sleep(ms);

      ucf_data[2] = '\0'; /* put back termination character for write commands */
    }
    else
    {
      /* Write command */
      ucf_reg[0] = *(p_ucf++);
      ucf_reg[1] = *(p_ucf++);
      reg = (uint8_t)strtol(ucf_reg, NULL, 16);

      ucf_data[0] = *(p_ucf++);
      ucf_data[1] = *(p_ucf++);
      data = (uint8_t)strtol(ucf_data, NULL, 16);

      res = ISensorWriteReg(_this->sensor_ll, reg, &data, 1);
      if(SYS_IS_ERROR_CODE(res))
      {
        break;
      }
    }
  }

  /* Sync sensor internal model with the sensor registers written by the ucf */
  if(ISensorSyncModel(_this->sensor_ll) != SYS_NO_ERROR_CODE)
  {
    res = SYS_BASE_ERROR_CODE;
  }

  return res;
}

sys_error_code_t UCFP_LoadUcf(SUcfProtocol_t *_this, const char *p_ucf, uint32_t size)
{
  assert_param(_this != NULL);
  assert_param(p_ucf != NULL);
  assert_param(size > 0U);
  sys_error_code_t res = SYS_NOT_IMPLEMENTED_ERROR_CODE;

  return res;
}


sys_error_code_t UCFP_LoadUcfHeader(SUcfProtocol_t *_this, const ucf_line_ispu_t *p_ucf, uint32_t size)
{
  assert_param(_this != NULL);
  assert_param(p_ucf != NULL);
  assert_param(size > 0U);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  uint32_t ucf_lines = size / sizeof(ucf_line_ispu_t);
  uint32_t i;

  for(i = 0; i < ucf_lines; i++)
  {
    if(p_ucf[i].op == MEMS_UCF_OP_WRITE)
    {
      res = ISensorWriteReg(_this->sensor_ll, p_ucf[i].address, &p_ucf[i].data, 1);
      if(SYS_IS_ERROR_CODE(res))
      {
        break;
      }
    }
    else if(p_ucf[i].op == MEMS_UCF_OP_DELAY)
    {
      tx_thread_sleep(p_ucf[i].data);
    }
    else
    {
      res = SYS_INVALID_PARAMETER_ERROR_CODE;
      break;
    }
  }

  /* Sync sensor internal model with the sensor registers written by the ucf */
  if(ISensorSyncModel(_this->sensor_ll) != SYS_NO_ERROR_CODE)
  {
    res = SYS_BASE_ERROR_CODE;
  }

  return res;
}


sys_error_code_t UCFP_GetCompressedUcf(const char *p_ucf, uint32_t ucf_size, char *p_compressed_ucf, uint32_t compressed_ucf_size, uint32_t *compressed_ucf_size_actual)
{
  char *p_ch = NULL;
  p_compressed_ucf[0] = 0;
  uint32_t i = 0;
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  p_ch = strtok((char*)p_ucf, " -,_\r\n");
  while(p_ch != NULL)
  {
    if(i >= compressed_ucf_size)
    {
      res = SYS_OUT_OF_MEMORY_ERROR_CODE;
      return res;
    }
    if(strncmp(p_ch, "Ac", 2) == 0)
    {
      p_ch = strtok(NULL, " -,_\r\n");
      p_compressed_ucf[i++] = p_ch[0];
      p_compressed_ucf[i++] = p_ch[1];
      p_ch = strtok(NULL, " -,_\r\n");
      p_compressed_ucf[i++] = p_ch[0];
      p_compressed_ucf[i++] = p_ch[1];
    }
    else if(strncmp(p_ch, "WAIT", 2) == 0)
    {
      p_ch = strtok(NULL, " -,_\r\n");
      uint16_t number = atol(p_ch);
      char tmp[10];
      sprintf(tmp, "W%03d", number);  /* Example --> W005 */
      p_compressed_ucf[i++] = tmp[0];
      p_compressed_ucf[i++] = tmp[1];
      p_compressed_ucf[i++] = tmp[2];
      p_compressed_ucf[i++] = tmp[3];
    }
    p_ch = strtok(NULL, " -,_\r\n");
  }
  p_compressed_ucf[i] = 0;
  *compressed_ucf_size_actual = i;

  return res;
}


sys_error_code_t UCFP_GetUcf(const char *p_compressed_ucf, uint32_t compressed_ucf_size, char *p_ucf, uint32_t ucf_size, uint32_t *ucf_size_actual)
{
  uint32_t i;
  uint32_t out_size = 0;
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  for(i = 0; i < compressed_ucf_size / 4; i++)
  {
    if(out_size >= ucf_size)
    {
      res = SYS_OUT_OF_MEMORY_ERROR_CODE;
      return res;
    }
    if(p_compressed_ucf[4U * i] != 'W')
    {
      *p_ucf++ = 'A';
      *p_ucf++ = 'c';
      *p_ucf++ = ' ';
      *p_ucf++ = p_compressed_ucf[4U * i];
      *p_ucf++ = p_compressed_ucf[4U * i + 1U];
      *p_ucf++ = ' ';
      *p_ucf++ = p_compressed_ucf[4U * i + 2U];
      *p_ucf++ = p_compressed_ucf[4U * i + 3U];
      *p_ucf++ = '\n';
      out_size += 9;
    }
    else
    {
      *p_ucf++ = 'W';
      *p_ucf++ = 'A';
      *p_ucf++ = 'I';
      *p_ucf++ = 'T';
      *p_ucf++ = ' ';
      /* copy the first 2 numbers only if they are != '0' */
      if(p_compressed_ucf[4 * i + 1] != '0')
      {
        *p_ucf++ = p_compressed_ucf[4 * i + 1];
        out_size++;
      }
      if(p_compressed_ucf[4 * i + 2] != '0')
      {
        *p_ucf++ = p_compressed_ucf[4 * i + 2];
        out_size++;
      }
      *p_ucf++ = p_compressed_ucf[4 * i + 3];
      *p_ucf++ = '\n';
      out_size += 7;
    }
  }
  *ucf_size_actual = out_size;

  return res;
}

uint32_t UCFP_CompressedUcfSize(uint32_t ucf_size)
{
  return (ucf_size / 9U * 4U) + 4;
}

uint32_t UCFP_UcfSize(uint32_t compressed_ucf_size)
{
  return (compressed_ucf_size / 4U * 9U) + 4;
}
