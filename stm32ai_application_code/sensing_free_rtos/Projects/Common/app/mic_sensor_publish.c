/**
 ******************************************************************************
 * @file    mic_sensor_publish.c
 * @author  STMicroelectronics - AIS - MCD Team
 * @version V1.0.0
 * @date    26/5/2023
 *
 * @brief
 *
 * <DESCRIPTIOM>
 *
 *********************************************************************************
 * @attention
 *
 * Copyright (c) 2023 STMicroelectronics
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *********************************************************************************
 */

#include "logging.h"

/* Standard includes. */
#include <string.h>
#include <stdio.h>

/* Kernel includes. */
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

/* Sensor includes */
#include "b_u585i_iot02a_audio.h"

/* Preprocessing includes */
#include "preproc_dpu.h"

/* AI includes */
#include "ai_dpu.h"

extern UART_HandleTypeDef huart1;

#define MIC_SCRATCH_BUFF_LEN ( 512 )
#define MIC_EVT_DMA_HALF     ( 1<<0 )
#define MIC_EVT_DMA_CPLT     ( 1<<1 )

/* Private variables ---------------------------------------------------------*/
static uint8_t   pucAudioBuff[AUDIO_BUFF_SIZE];
static int8_t    pcSpectroGram[CTRL_X_CUBE_AI_SPECTROGRAM_COL*CTRL_X_CUBE_AI_SPECTROGRAM_NMEL];
static float32_t pfAIOutput[AI_NETWORK_OUT_1_SIZE];
static BaseType_t xExitFlag = pdFALSE;
static char pcScratchBuffer[ MIC_SCRATCH_BUFF_LEN ];

/**
 * Specifies the labels for the classes of the demo.
 */
static const char* sAiClassLabels[CTRL_X_CUBE_AI_MODE_CLASS_NUMBER] = CTRL_X_CUBE_AI_MODE_CLASS_LIST;
/**
 * DPUs context
 */
static AudioProcCtx_t xAudioProcCtx;
static AIProcCtx_t xAIProcCtx;
/**
 * Microphone task handle
 */
static TaskHandle_t  xMicTask;

/* CRC init function */
static void CRC_Init(void)
{
	CRC_HandleTypeDef hcrc;
	hcrc.Instance                     = CRC;
	hcrc.Init.DefaultPolynomialUse    = DEFAULT_POLYNOMIAL_ENABLE;
	hcrc.Init.DefaultInitValueUse     = DEFAULT_INIT_VALUE_ENABLE;
	hcrc.Init.InputDataInversionMode  = CRC_INPUTDATA_INVERSION_NONE;
	hcrc.Init.OutputDataInversionMode = CRC_OUTPUTDATA_INVERSION_DISABLE;
	hcrc.InputDataFormat              = CRC_INPUTDATA_FORMAT_BYTES;
	__HAL_RCC_CRC_CLK_ENABLE();
	if (HAL_CRC_Init(&hcrc) != HAL_OK)
	{
		LogError( "CRC Init Error" );
	}
}

static BaseType_t xInitSensors( void )
{
	int32_t lBspError = BSP_ERROR_NONE;

	BSP_AUDIO_Init_t AudioInit;

	/* Select device depending on the Instance */
	AudioInit.Device        = AUDIO_IN_DEVICE_DIGITAL_MIC1;
	AudioInit.SampleRate    = AUDIO_FREQUENCY_16K;
	AudioInit.BitsPerSample = AUDIO_RESOLUTION_16B;
	AudioInit.ChannelsNbr   = 1;
	AudioInit.Volume        = 100; /* Not used */
	lBspError = BSP_AUDIO_IN_Init(0, &AudioInit);
	return( lBspError == BSP_ERROR_NONE ? pdTRUE : pdFALSE );
}
void vMicSensorPublishTask( void * pvParameters )
{
	BaseType_t xResult = pdFALSE;
	uint32_t ulNotifiedValue = 0;
	unsigned char c;

	( void ) pvParameters; /* unused parameter */

	/**
	 * Initialize the CRC IP required by X-CUBE-AI.
	 * Must be called before any usage of the ai library API.
	 */
	CRC_Init();

	/**
	 * get task handle for notifications
	 */
	xMicTask = xTaskGetCurrentTaskHandle();

	xResult = xInitSensors();

	if( xResult != pdTRUE )
	{
		LogError( "Error while Audio sensor." );
		vTaskDelete( NULL );
	}

	xResult = PreProc_DPUInit( &xAudioProcCtx ) ;

	if( xResult != pdTRUE )
	{
		LogError( "Error while initializing Preprocessing." );
		vTaskDelete( NULL );
	}

	/**
	 * get the AI model
	 */
	AiDPULoadModel( &xAIProcCtx, "network" );

	/**
	 * transfer quantization parametres included in AI model to the Audio DPU
	 */
	xAudioProcCtx.output_Q_offset    = xAIProcCtx.input_Q_offset;
	xAudioProcCtx.output_Q_inv_scale = xAIProcCtx.input_Q_inv_scale;

	if (BSP_AUDIO_IN_Record(0, pucAudioBuff, AUDIO_BUFF_SIZE) != BSP_ERROR_NONE)
	{
		LogError("AUDIO IN : FAILED.\n");
	}

	LogInfo("\r\n--- Start Processing ---\r\n\n");

	xExitFlag = pdFALSE;
	UART_Start_Receive_IT(&huart1, &c, 1);

	while( xExitFlag == pdFALSE )
	{
		TimeOut_t xTimeOut;
		vTaskSetTimeOutState( &xTimeOut );

		if(xTaskNotifyWait(0, 0xFFFFFFFF , &ulNotifiedValue, portMAX_DELAY) == pdTRUE )
		{
			uint8_t * pucAudioIn = ( ulNotifiedValue & MIC_EVT_DMA_HALF ) ? pucAudioBuff : pucAudioBuff+AUDIO_HALF_BUFF_SIZE ;

			PreProc_DPU(&xAudioProcCtx, pucAudioIn, pcSpectroGram);

			AiDPUProcess(&xAIProcCtx, pcSpectroGram ,pfAIOutput);
		}
		if ( xAudioProcCtx.S_Spectr.spectro_sum > CTRL_X_CUBE_AI_SPECTROGRAM_SILENCE_THR)
		{
			/**
			 * if not silence frame
			 */
			float max_out = pfAIOutput[0];
			uint32_t max_idx = 0;
			for(uint32_t i = 1; i < CTRL_X_CUBE_AI_MODE_CLASS_NUMBER; i++)
			{
				if(pfAIOutput[i] > max_out)
				{
					max_idx = i;
					max_out = pfAIOutput[i];
				}
			}
			if (max_out > CTRL_X_CUBE_AI_OOD_THR )
			{
				LogInfo("{\"class\":\"%s\"}\r\n",sAiClassLabels[max_idx]);
				LogInfo("{\"predicted score\":\"%0.2f\"}\r\n",max_out);
			}
			else
			{
				LogInfo("{\"class\":\"%s\"}\r\n","unknown");
			}
		}
		xAudioProcCtx.S_Spectr.spectro_sum = 0 ;
	}
	LogInfo( "\r\nTerminating Audio Task.\r\n" );
    vTaskGetRunTimeStats(pcScratchBuffer);
    LogInfo("\n\rTasks statistics (unit is %0.2f us)\n\r", (1<<CORE_CLOCK_RSHIFT)*1000000.0F/SystemCoreClock);
    LogInfo("---------------------------------------------------\n\r");
    LogInfo("%s\r\n",pcScratchBuffer);
    vTaskDelete( NULL );
}
/**
 * @brief  Manage the BSP audio in half transfer complete event.
 * @param  Instance Audio in instance.
 * @retval None.
 */
void BSP_AUDIO_IN_HalfTransfer_CallBack(uint32_t Instance)
{
	(void) Instance;
	assert_param(Instance==0);
	BaseType_t xHigherPriorityTaskWoken = pdFALSE;
	BaseType_t rslt = pdFALSE;
	rslt = xTaskNotifyFromISR( xMicTask,
			MIC_EVT_DMA_HALF,
			eSetBits,
			&xHigherPriorityTaskWoken );
	configASSERT( rslt == pdTRUE );
	portYIELD_FROM_ISR( xHigherPriorityTaskWoken );
}

/**
 * @brief  Manage the BSP audio in transfer complete event.
 * @param  Instance Audio in instance.
 * @retval None.
 */
void BSP_AUDIO_IN_TransferComplete_CallBack(uint32_t Instance)
{
	(void) Instance;
	assert_param(Instance==0);
	BaseType_t xHigherPriorityTaskWoken = pdFALSE;
	BaseType_t rslt = pdFALSE;
	rslt = xTaskNotifyFromISR( xMicTask,
			MIC_EVT_DMA_CPLT,
			eSetBits,
			&xHigherPriorityTaskWoken );
	configASSERT( rslt == pdTRUE );
	portYIELD_FROM_ISR( xHigherPriorityTaskWoken );
}
/**
 * @brief  Rx Transfer completed callback
 * @param  UartHandle: UART handle
 * @retval None
 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *UartHandle)
{
	xExitFlag = pdTRUE;
}
