/**
 ******************************************************************************
 * @file    app_comm.c
 * @author  MCD Application Team
 * @brief   Library to manage communication related operation
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

/* Includes ------------------------------------------------------------------*/
#include "app_comm.h"
#include "app_sensor.h"

#include <string.h>

/* Global variables ----------------------------------------------------------*/
extern AppConfig_TypeDef App_Config;

/* Private macro -------------------------------------------------------------*/
#define UART_COMM_BUFFER_SIZE                     (512)

#define ONE_BYTE_INC                              (1)
#define FOUR_BYTE_INC                             (4)

#define PARSE_HELP_BUFFER_SIZE                    (1024)

/* Array size of a static declared array */
#ifndef ARRAY_SIZE
#   define ARRAY_SIZE(a)  ((sizeof(a) / sizeof(a[0])))
#endif

/* Private types -------------------------------------------------------------*/

/**
 * Parameter parser description
 * Give scanner/formatter pointer etc...
 */
typedef struct SetParam_t *pSetParam_t;

typedef int (*ScannerType)(const char *Buff, const char *fmt, ...);
typedef int (*CheckerType)(const pSetParam_t SetParam, const void *Param);
typedef char *(*PrinterType)(char *buffer, const pSetParam_t SetParam, const uint8_t *Param);

struct SetParam_t {
    const char *Name;     /* Parameter name */
    ScannerType Scanner;  /*!< if NULL, default to sscanf */
    char *ScanFmt;        /*!< scanner argument ptr ie sscanf fmt string. If NULL, default to "%d" */
    int ParamOffset;      /*!<offset in @ref DevParams_t to param */
    CheckerType Checker;  /*!< checker : if null return nob 0 form scanner as validation */
    PrinterType Printer;  /*!< printer : print name=value */
    int size;
};

struct BaseCommand_t{
    const char *Name;
    int (*Parse)(const struct BaseCommand_t *pCmd, const char *Buffer); /** !< Parser is invoked with the command and string right after the command itself*/
    const char *Help;
    const char *Syntax;
    const char *Example;
    int NoAnswer; /**!< When set , successful command do not issue "ok"
                    use it for command that always echo back some answer bad or not */
};

/* Private variables ---------------------------------------------------------*/
UART_HandleTypeDef huart2;

/**
 * List of parameters that can be changed by the "set param=value" command
 * This list is used by the Parse_SET() parser function (to be more generic)
 * Add a new entry in this list to expose a new parameter to the command parser
 */
struct SetParam_t SetableParams[]={
    { .Name= "Resolution",                .Scanner= (int(*)(const char*, const char *,...))sscanf,    .ScanFmt="%d",   .ParamOffset = offsetof(struct Params_t, Resolution), .size=1 },
    { .Name= "gesture_gui",               .Scanner= (int(*)(const char*, const char *,...))sscanf,    .ScanFmt="%d",   .ParamOffset = offsetof(struct Params_t, gesture_gui), .size=1 },
    { .Name= "RangingPeriod",             .Scanner= (int(*)(const char*, const char *,...))sscanf,    .ScanFmt="%d",   .ParamOffset = offsetof(struct Params_t, RangingPeriod), .size=1 },
    { .Name= "IntegrationTime",           .Scanner= (int(*)(const char*, const char *,...))sscanf,    .ScanFmt="%d",   .ParamOffset = offsetof(struct Params_t, IntegrationTime), .size=1 },
};

char UartComm_TmpBuffer[UART_COMM_BUFFER_SIZE];

/* Private function prototypes -----------------------------------------------*/
static int Parse_Enable(const struct BaseCommand_t *pCmd, const char *Buffer);
static int Parse_Disable(const struct BaseCommand_t *pCmd, const char *Buffer);
static int Parse_SET(const struct BaseCommand_t *pCmd, const char *Buffer);
static int Parse_Params(const struct BaseCommand_t *pCmd, const char *Buffer);
static int Parse_Help(const struct BaseCommand_t *, const char *);
static int SC_HandleCmd(const char *Buffer);

struct BaseCommand_t BaseCmd[]={
  { .Name= "enable", .Parse = Parse_Enable,
    .Help="Enable sensor ranging.",
    .Syntax="'enable'",
    .Example="'enable' => Enable sensor ranging"
  },
  { .Name= "disable", .Parse = Parse_Disable,
    .Help="Disable sensor ranging.",
    .Syntax="'disable'",
    .Example="'disable' => Disable sensor ranging",
  },
  { .Name= "params", .Parse = Parse_Params,
    .Help="Show all input parameters",
    .Syntax="'params'",
    .Example="'params' => Show all input parameters",
    .NoAnswer = 1,
  },
  { .Name= "set", .Parse = Parse_SET,
    .Help="Set a parameter. See params command to know available parameters and current values.",
    .Syntax="'set param_name=value'",
    .Example="'set RangingPeriod=1'",
  },
  { .Name= "help", .Parse = Parse_Help,
    .Help="Displays this help",
    .NoAnswer = 1,
  },
};

/* Private function definitions ----------------------------------------------*/

/* Parse functions */
static int Parse_Enable(const struct BaseCommand_t *pCmd, const char *Buffer){
  (void)pCmd;
  (void)Buffer;
  /* Start ranging */
  Sensor_StartRanging(&App_Config);
  /* Set application state as ranging */
  App_Config.app_run = true;
  App_Config.IntrCount = 0;
  return(0);
}
static int Parse_Disable(const struct BaseCommand_t *pCmd, const char *Buffer){
  (void)pCmd;
  (void)Buffer;
  /* Stop the sensor */
  Sensor_StopRanging(&App_Config);
  /* Set application state as stopped */
  App_Config.app_run = false;
  return(0);
}

int Parse_SET(const struct BaseCommand_t *pCmd, const char *Buffer){
  int n;
  char *Find;
  char *ParamValue;
  int Status=-1;
  uint8_t *ParamsPtr;
  int i;
  int j;

  Find=strchr(Buffer, '=');
  if( Find == NULL ){
    return(Status);
  }
  ParamValue = Find +1 ;
  for( i=0; i< ARRAY_SIZE(SetableParams); i++){
    int ParamLen;
    ParamLen=strlen(SetableParams[i].Name);
    if( strncmp(Buffer+1,SetableParams[i].Name, ParamLen) == 0 ){
      ParamsPtr=(uint8_t*)&(App_Config.Params);
      ParamsPtr+=SetableParams[i].ParamOffset;
      /* Go through each element (comma separated) if size is not 1 */
      for(j=0;j<SetableParams[i].size;j++){
        if (j!=0) {
          /* Search for the next comma */
          Find=strchr(ParamValue, ',');
          if(Find == NULL)
            return(Status);
        /* Jump to the string just after the comma */
        ParamValue = Find +1 ;
        }
        n = SetableParams[i].Scanner( ParamValue, SetableParams[i].ScanFmt, ParamsPtr );
        if( SetableParams[i].Checker != NULL ){
          /* Dedicate checker */
          Status=SetableParams[i].Checker( &SetableParams[i], ParamsPtr );
        }
        else{
          /* Simply use the n return */
          if( n==1 ){
            Status = 0;
          }
        }
        /* Manage data types : only %f (4 bytes), %d (4 bytes), %u (1 byte) supported */
        if( SetableParams[i].ScanFmt[1]=='f'){
          ParamsPtr += FOUR_BYTE_INC;
        }
        else if( SetableParams[i].ScanFmt[1]=='u'){
          ParamsPtr += ONE_BYTE_INC;
        }
        else{
          ParamsPtr += FOUR_BYTE_INC;
        }
      }
      /* Done: parameters found */
      break;
    }
  }
  if (!Status)
    /* Set the flag indicating the parameters has been modified */
    App_Config.params_modif = true;
  return(Status);
}

static int Parse_Params(const struct BaseCommand_t *pCmd, const char *Buffer){
  int i;
  int j;
  char *TmpStr;
  int n;
  printf("size : %d\n",ARRAY_SIZE(SetableParams));
  for( i=0; i<ARRAY_SIZE(SetableParams); i++){
    TmpStr=UartComm_TmpBuffer;
    uint8_t *ParamsPtr =(uint8_t*)&(App_Config.Params);
    ParamsPtr+=SetableParams[i].ParamOffset;

    if( SetableParams[i].Scanner==sscanf){
      sprintf(TmpStr, "%s=",SetableParams[i].Name);
      TmpStr=strstr(TmpStr,"=")+1;
      /* Go through each element (comma separated) if size is not 1 */
      for(j=0;j<SetableParams[i].size;j++){
        /* Separate each element by a comma */
        if (j!=0) {
          sprintf(TmpStr,",");
          TmpStr++;
        }
        /* Manage data types : only %f (4 bytes), %d (4 bytes), %u (1 byte) supported */
        if( SetableParams[i].ScanFmt[1]=='f'){
          n = sprintf(TmpStr, SetableParams[i].ScanFmt, *((float *)ParamsPtr));
          ParamsPtr = ParamsPtr+FOUR_BYTE_INC;
        }
        else if( SetableParams[i].ScanFmt[1]=='u'){
          n = sprintf(TmpStr, SetableParams[i].ScanFmt, *((uint8_t *)ParamsPtr));
          ParamsPtr = ParamsPtr+ONE_BYTE_INC;
        }
        else{
          n = sprintf(TmpStr, SetableParams[i].ScanFmt, *((uint32_t *)ParamsPtr));
          ParamsPtr = ParamsPtr+FOUR_BYTE_INC;
        }
        TmpStr = TmpStr+n;
      }
      sprintf(TmpStr, "\n");
      printf(UartComm_TmpBuffer);
    }
  }
  return(0);
}

static int Parse_Help(const struct BaseCommand_t *pCmd, const char *Unused)
{
  size_t i;
  char TmpBuffer[PARSE_HELP_BUFFER_SIZE];

  (void)pCmd;
  (void)Unused;

  for(i = 0 ; i < ARRAY_SIZE(BaseCmd) ; i++)
  {
    TmpBuffer[0] = 0;
    strcat(TmpBuffer, BaseCmd[i].Name);
    if(BaseCmd[i].Help != NULL)
    {
      strcat(TmpBuffer, "\t");
      strcat(TmpBuffer, BaseCmd[i].Help);
    }
    if(BaseCmd[i].Syntax != NULL)
    {
      strcat(TmpBuffer, "\n\tSyntax:\t");
      strcat(TmpBuffer, BaseCmd[i].Syntax);
    }
    if(BaseCmd[i].Example != NULL)
    {
      strcat(TmpBuffer, "\n\tExample:\t");
      strcat(TmpBuffer, BaseCmd[i].Example);
    }
    strcat(TmpBuffer, "\n");
    printf(TmpBuffer);
  }
  return(0);
}

/**
 * @brief  Handle a new command
 * @param  Buffer Command buffer
 * @retval 0 if success, -1 otherwise
 */
int SC_HandleCmd(const char *Buffer)
{
  int Status =-1;
  int CmdLen;
  size_t i;

  for(i = 0 ; i < ARRAY_SIZE(BaseCmd) ; i++)
  {
    int CmdRet;
    CmdLen=strlen(BaseCmd[i].Name);
    if (strncmp(Buffer, BaseCmd[i].Name, CmdLen) == 0 &&
            (Buffer[CmdLen]==' ' || Buffer[CmdLen]=='\t' || Buffer[CmdLen]==0 ))
    {
      CmdRet=BaseCmd[i].Parse(&BaseCmd[i], Buffer+CmdLen);
      if(CmdRet == 0)
      {
        Status = 0;
        if(BaseCmd[i].NoAnswer == 0)
        {
          printf("ok\n");
        }
      }
      break;
    }
  }
  return(Status);
}

/**
 * @brief  COMM Print from UART to terminal
 * @param  App_Config_Ptr Pointer to application context
 * @retval None
 */
static void Comm_PrintTerm(AppConfig_TypeDef *App_Config)
{
	printf("\x1b[2J");
	printf("\x1b[1;1H");
	printf("Hand Posture =  #%d {%s}                                          \r\n",
			(int) (App_Config->AI_Data.handposture_label),
			classes_table[(int)(App_Config->AI_Data.handposture_label)]);

	for (int i = 0; i<AI_NETWORK_OUT_1_SIZE; i++)
	{
		printf("Class #%d {%s} : %f                                           \r\n",
				i,
				classes_table[i],
				App_Config->aiOutData[i]);
	}

}

/**
 * @brief  COMM Print from UART to EVK GUI
 * @param  App_Config_Ptr Pointer to application context
 * @retval None
 */
static void Comm_PrintEvk(AppConfig_TypeDef *App_Config)
{
  /* Display by row, only working with a resolution 64 */
  size_t i;
  char print_buffer[2048];
  int size_global = 75;
  int size_zone;
  int char_pos;

  if (App_Config->frame_count < 99999)
  {
    App_Config->frame_count++;
  }
  else
  {
    App_Config->frame_count = 0;
  }

  /* Global data format */
  sprintf(&print_buffer[0],
      "RAN,%5ld,%3d,%10ld,,"
      ",,,,,"
      "%4d,,,,,"
      ",,,,,"
      ",,,,,"
      ",,,,,"
      ",,,,,"
      ",,,,,"
      ",,,,,"
      ",,,,,",
      App_Config->frame_count,
      App_Config->ToFDev.streamcount,
      (int32_t) HAL_GetTick(),
      evk_label_table[(int)(App_Config->AI_Data.handposture_label)]
      );

  /* Zone data format
   * RangingData.target_status       -> 2 digits + ',' = 3
   * RangingData.nb_target_detected  -> 2 digits + ',' = 3
   * RangingData.distance_mm         -> 7 digits + ',' = 8
   * RangingData.signal_per_spad     -> 6 digits + ',' = 7
   * dummy '0'                       -> 1 digit  + ',' = 2
   * To be compatible with HandTracking
   * sensor_data.valid               -> 1 digit  + ',' = 2
   * Total size for 1 zone = zone_size = 22 */
  size_zone = 22;
  char_pos = 0;
  for (i = 0 ; i < SENSOR__MAX_NB_OF_ZONES ; i++)
  {
    char_pos = size_zone*i+size_global;
    sprintf(&print_buffer[char_pos],",%2d",(App_Config->RangingData.target_status[i]));
    char_pos = char_pos + 3;
    sprintf(&print_buffer[char_pos],",%2d",(App_Config->RangingData.nb_target_detected[i]));
    char_pos = char_pos + 3;
    sprintf(&print_buffer[char_pos],",%4.0f",(float) (App_Config->RangingData.distance_mm[i]/FIXED_POINT_14_2_TO_FLOAT));
    char_pos = char_pos + 5;
    sprintf(&print_buffer[char_pos],",%6.0f",(float) (App_Config->RangingData.signal_per_spad[i]/FIXED_POINT_21_11_TO_FLOAT));
    char_pos = char_pos + 7;
    sprintf(&print_buffer[char_pos],",%1d",0);
    char_pos = char_pos + 2;
    sprintf(&print_buffer[char_pos],",%1d",(1));
  }
  sprintf(&print_buffer[size_global+size_zone*SENSOR__MAX_NB_OF_ZONES],"\n");
  printf(print_buffer);

}

/**
 * @brief  COMM Handle command
 * @param  App_Config_Ptr Pointer to application context
 * @retval None
 */
void Comm_HandleCmd(AppConfig_TypeDef *App_Config)
{
  /* Process the command */
  if (SC_HandleCmd(App_Config->Comm_RXBuffer) < 0)
  {
    printf("Bad command\n");
  }

  /* Reset the command ready flag */
  App_Config->UartComm_CmdReady = 0;

}


/* Public function definitions -----------------------------------------------*/

__attribute__((weak)) int __io_putchar(int ch)
{
  HAL_StatusTypeDef status = HAL_UART_Transmit(&huart2, (uint8_t *)&ch, 1, 0xFFFF);
  return (status == HAL_OK ? ch : 0);
}

__attribute__((weak)) int __io_getchar(void)
{
  int ch = 0;
  HAL_StatusTypeDef status = HAL_UART_Receive(&huart2, (uint8_t *)&ch, 1, 0xFFFF);
  return (status == HAL_OK ? ch : 0);
}

/**
 * @brief  COMM Initialization
 * @param  App_Config_Ptr Pointer to application context
 * @retval None
 */
void Comm_Init(AppConfig_TypeDef *App_Config)
{
  /* UART2 initialization */
  huart2.Instance = USART2;
  huart2.Init.BaudRate = 921600;
  huart2.Init.WordLength = UART_WORDLENGTH_8B;
  huart2.Init.StopBits = UART_STOPBITS_1;
  huart2.Init.Parity = UART_PARITY_NONE;
  huart2.Init.Mode = UART_MODE_TX_RX;
  huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart2.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart2) != HAL_OK)
  {
    printf("UART init failed\n");
    Error_Handler();
  }

}

/**
 * @brief  COMM Start
 * @param  App_Config_Ptr Pointer to application context
 * @retval None
 */
void Comm_Start(AppConfig_TypeDef *App_Config)
{
  /* If the UART is not busy receiving data, put it in receive interrupt mode */
  HAL_UART_StateTypeDef State;
  App_Config->UartComm_CmdReady = 0;
  App_Config->Uart_RxRcvIndex = 0;
  State = HAL_UART_GetState(&huart2);
  if (HAL_UART_STATE_BUSY_TX_RX != State && HAL_UART_STATE_BUSY_RX != State)
  {
    HAL_UART_Receive_IT(&huart2, (uint8_t *) (App_Config->Uart_RXBuffer), 1);
  }

}

/**
 * @brief  COMM Print through UART
 * @param  App_Config_Ptr Pointer to application context
 * @retval None
 */
void Comm_Print(AppConfig_TypeDef *App_Config)
{
  /* If a new data need to be printed */
  if (App_Config->new_data_received)
  {
    if (1 == App_Config->Params.gesture_gui)
    {
      /* Print the data using the template needed by the GUI */
      Comm_PrintEvk(App_Config);
    }
    else
    {
      /* Print the raw data */
      Comm_PrintTerm(App_Config);
    }
  }

}

/**
 * @brief  UART Receive interrupt handler
 * @param  huart UART instance
 * @retval None
 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
  /* The three following characters launch the processing of the received data
   * as a command */
  if (App_Config.Uart_RXBuffer[App_Config.Uart_RxRcvIndex] == '\r'
        || App_Config.Uart_RXBuffer[App_Config.Uart_RxRcvIndex] == '\n'
        || App_Config.Uart_RXBuffer[App_Config.Uart_RxRcvIndex] == '\x03')
  {
    /* '\x03' is Ctrl-c */
    if (App_Config.Uart_RXBuffer[App_Config.Uart_RxRcvIndex] != '\x03')
    {
      /* Clean the last char */
      App_Config.Uart_RXBuffer[App_Config.Uart_RxRcvIndex] = 0;
    }

    /* Copy data from the UART buffer to the comm buffer */
    memcpy(App_Config.Comm_RXBuffer,
        (char *) App_Config.Uart_RXBuffer,
        App_Config.Uart_RxRcvIndex + 1);
    /* Set a flag indicating a new command is ready to be handled */
    App_Config.UartComm_CmdReady = 1;
    /* Reset the UART buffer index */
    App_Config.Uart_RxRcvIndex = 0;
  }
  else
  {
    if (App_Config.Uart_RxRcvIndex < UART_BUFFER_SIZE)
    {
      /* Increase the index of the UART buffer */
      App_Config.Uart_RxRcvIndex++;
    }
    else
    {
      /* If the index is out of bounds, reset it and increment the overrun
       * counter */
      App_Config.Uart_RxRcvIndex = 0;
      App_Config.Uart_nOverrun++;
    }
  }

  /* Restart the UART in receive interrupt mode */
  HAL_UART_Receive_IT(huart,
      (uint8_t *) &(App_Config.Uart_RXBuffer[App_Config.Uart_RxRcvIndex]),
      1);

}

/**
 * @brief  UART error handler
 * @param  huart UART instance
 * @retval None
 */
void HAL_UART_ErrorCallback(UART_HandleTypeDef * huart)
{
    /* Clear error and  kick of next */
    huart->ErrorCode = 0;
    HAL_UART_Receive_IT(huart,
        (uint8_t *) &(App_Config.Uart_RXBuffer[App_Config.Uart_RxRcvIndex]),
        App_Config.Uart_RxRcvIndex);

}

/**
 * @brief  COMM If a UART command has been received, handle it
 * @param  App_Config_Ptr Pointer to application context
 * @retval None
 */
void Comm_HandleRxCMD(AppConfig_TypeDef *App_Config)
{
  /* If a command has been received */
  if (App_Config->UartComm_CmdReady)
  {
    /* Handle the command */
    Comm_HandleCmd(App_Config);
  }

}
