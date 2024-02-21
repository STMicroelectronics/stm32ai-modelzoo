
//	MIT License
//
//	Copyright (c) 2017 Matej Artnak
//
//	Permission is hereby granted, free of charge, to any person obtaining a copy
//	of this software and associated documentation files (the "Software"), to deal
//	in the Software without restriction, including without limitation the rights
//	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
//	copies of the Software, and to permit persons to whom the Software is
//	furnished to do so, subject to the following conditions:
//
//	The above copyright notice and this permission notice shall be included in all
//	copies or substantial portions of the Software.
//
//	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
//	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
//	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
//	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
//	SOFTWARE.

/* Includes ------------------------------------------------------------------*/
#include "ILI9341_STM32_Driver.h"
#include "main.h"

/* Global Variables ----------------------------------------------------------*/
volatile uint16_t LCD_HEIGHT = LCD_RES_HEIGHT;
volatile uint16_t LCD_WIDTH	 = LCD_RES_WIDTH;
SPI_HandleTypeDef hspi2;

/* Functions definition ------------------------------------------------------*/
void MX_SPI2_Init(void)
{
  hspi2.Instance = SPI2;
  hspi2.Init.Mode = SPI_MODE_MASTER;
  hspi2.Init.Direction = SPI_DIRECTION_2LINES_TXONLY;
  hspi2.Init.DataSize = SPI_DATASIZE_8BIT;
  hspi2.Init.CLKPolarity = SPI_POLARITY_LOW;
  hspi2.Init.CLKPhase = SPI_PHASE_1EDGE;
  hspi2.Init.NSS = SPI_NSS_SOFT;
  hspi2.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_8;
  hspi2.Init.FirstBit = SPI_FIRSTBIT_MSB;
  hspi2.Init.TIMode = SPI_TIMODE_DISABLE;
  hspi2.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
  hspi2.Init.CRCPolynomial = 0x0;
  hspi2.Init.NSSPMode = SPI_NSS_PULSE_DISABLE;
  hspi2.Init.NSSPolarity = SPI_NSS_POLARITY_LOW;
  hspi2.Init.FifoThreshold = SPI_FIFO_THRESHOLD_01DATA;
  hspi2.Init.TxCRCInitializationPattern = SPI_CRC_INITIALIZATION_ALL_ZERO_PATTERN;
  hspi2.Init.RxCRCInitializationPattern = SPI_CRC_INITIALIZATION_ALL_ZERO_PATTERN;
  hspi2.Init.MasterSSIdleness = SPI_MASTER_SS_IDLENESS_00CYCLE;
  hspi2.Init.MasterInterDataIdleness = SPI_MASTER_INTERDATA_IDLENESS_00CYCLE;
  hspi2.Init.MasterReceiverAutoSusp = SPI_MASTER_RX_AUTOSUSP_DISABLE;
  hspi2.Init.MasterKeepIOState = SPI_MASTER_KEEP_IO_STATE_DISABLE;
  hspi2.Init.IOSwap = SPI_IO_SWAP_DISABLE;
  if (HAL_SPI_Init(&hspi2) != HAL_OK)
  {
    Error_Handler();
  }
}

void MX_GPIO_Init(void)
{

  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOB, ILI9341_LED_Pin|ILI9341_CS_Pin|ILI9341_DC_Pin|ILI9341_RST_Pin, 
                            GPIO_PIN_RESET);

  /*Configure GPIO pins : PBPin PBPin PBPin PBPin */
  GPIO_InitStruct.Pin = ILI9341_CS_Pin|ILI9341_DC_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /*Configure GPIO pin : PtPin */
  GPIO_InitStruct.Pin = ILI9341_LED_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
  HAL_GPIO_Init(ILI9341_LED_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : PtPin */
  GPIO_InitStruct.Pin = ILI9341_RST_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
  HAL_GPIO_Init(ILI9341_RST_GPIO_Port, &GPIO_InitStruct);
}

/* Initialize SPI */
void ILI9341_SPI_Init(void)
{
	MX_SPI2_Init();																							//SPI INIT
	MX_GPIO_Init();																							//GPIO INIT
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_SET);		//CS OFF
}

/*Send data (char) to LCD*/
void ILI9341_SPI_Send(unsigned char SPI_Data)
{
	HAL_SPI_Transmit(HSPI_INSTANCE, &SPI_Data, 1, 1);
}

/* Send command (char) to LCD */
void ILI9341_Write_Command(uint8_t Command)
{
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_RESET);
	ILI9341_SPI_Send(Command);
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_SET);
}

/* Send Data (char) to LCD */
void ILI9341_Write_Data(uint8_t Data)
{
	HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_SET);	
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_RESET);
	ILI9341_SPI_Send(Data);	
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_SET);
}

/* Set Address - Location block - to draw into */
void ILI9341_Set_Address(uint16_t X1, uint16_t Y1, uint16_t X2, uint16_t Y2)
{
	ILI9341_Write_Command(0x2A);
	ILI9341_Write_Data(X1>>8);
	ILI9341_Write_Data(X1);
	ILI9341_Write_Data(X2>>8);
	ILI9341_Write_Data(X2);

	ILI9341_Write_Command(0x2B);
	ILI9341_Write_Data(Y1>>8);
	ILI9341_Write_Data(Y1);
	ILI9341_Write_Data(Y2>>8);
	ILI9341_Write_Data(Y2);

	ILI9341_Write_Command(0x2C);
}

/*HARDWARE RESET*/
void ILI9341_Reset(void)
{
	HAL_GPIO_WritePin(LCD_RST_PORT, LCD_RST_PIN, GPIO_PIN_RESET);
	HAL_Delay(100);
	HAL_GPIO_WritePin(LCD_RST_PORT, LCD_RST_PIN, GPIO_PIN_SET);
	HAL_Delay(200);
}

/*Ser rotation of the screen - changes x0 and y0*/
void ILI9341_Set_Rotation(uint8_t Rotation) 
{
	uint8_t screen_rotation = Rotation;

	ILI9341_Write_Command(0x36);
	HAL_Delay(1);
		
	switch(screen_rotation) 
	{
		case SCREEN_VERTICAL_1:
			ILI9341_Write_Data(0x40|0x08);
			LCD_WIDTH = 240;
			LCD_HEIGHT = 320;
			break;
		case SCREEN_HORIZONTAL_1:
			ILI9341_Write_Data(0x20|0x08);
			LCD_WIDTH  = 320;
			LCD_HEIGHT = 240;
			break;
		case SCREEN_VERTICAL_2:
			ILI9341_Write_Data(0x80|0x08);
			LCD_WIDTH  = 240;
			LCD_HEIGHT = 320;
			break;
		case SCREEN_HORIZONTAL_2:
			ILI9341_Write_Data(0x40|0x80|0x20|0x08);
			LCD_WIDTH  = 320;
			LCD_HEIGHT = 240;
			break;
		default:
			//EXIT IF SCREEN ROTATION NOT VALID!
			break;
	}
}

/*Enable LCD display*/
void ILI9341_Enable(void)
{
	HAL_GPIO_WritePin(LCD_RST_PORT, LCD_RST_PIN, GPIO_PIN_SET);
}

/*Initialize LCD display*/
int ILI9341_Init(uint32_t Orientation)
{
  int ret = BSP_ERROR_NONE;

  /* Configure LCD instance */
  Lcd_Ctx.BppFactor = 2;
  Lcd_Ctx.PixelFormat = LCD_PIXEL_FORMAT_RGB565;
  Lcd_Ctx.XSize = LCD_DEFAULT_WIDTH;
  Lcd_Ctx.YSize = LCD_DEFAULT_HEIGHT;

  if (Orientation != LCD_ORIENTATION_LANDSCAPE)
  {
    ret = BSP_ERROR_WRONG_PARAM;
  }
  else
  {
    /* Initializes peripherals instance value */
    hlcd_dma2d.Instance = DMA2D;
    DMA2D_MspInit(&hlcd_dma2d);
  }

	ILI9341_Enable();
	ILI9341_SPI_Init();
	ILI9341_Reset();

	//SOFTWARE RESET
	ILI9341_Write_Command(0x01);
	HAL_Delay(10);
		
	//POWER CONTROL A
	ILI9341_Write_Command(0xCB);
	ILI9341_Write_Data(0x39);
	ILI9341_Write_Data(0x2C);
	ILI9341_Write_Data(0x00);
	ILI9341_Write_Data(0x34);
	ILI9341_Write_Data(0x02);

	//POWER CONTROL B
	ILI9341_Write_Command(0xCF);
	ILI9341_Write_Data(0x00);
	ILI9341_Write_Data(0xC1);
	ILI9341_Write_Data(0x30);

	//DRIVER TIMING CONTROL A
	ILI9341_Write_Command(0xE8);
	ILI9341_Write_Data(0x85);
	ILI9341_Write_Data(0x00);
	ILI9341_Write_Data(0x78);

	//DRIVER TIMING CONTROL B
	ILI9341_Write_Command(0xEA);
	ILI9341_Write_Data(0x00);
	ILI9341_Write_Data(0x00);

	//POWER ON SEQUENCE CONTROL
	ILI9341_Write_Command(0xED);
	ILI9341_Write_Data(0x64);
	ILI9341_Write_Data(0x03);
	ILI9341_Write_Data(0x12);
	ILI9341_Write_Data(0x81);

	//PUMP RATIO CONTROL
	ILI9341_Write_Command(0xF7);
	ILI9341_Write_Data(0x20);

	//POWER CONTROL,VRH[5:0]
	ILI9341_Write_Command(0xC0);
	ILI9341_Write_Data(0x23);

	//POWER CONTROL,SAP[2:0];BT[3:0]
	ILI9341_Write_Command(0xC1);
	ILI9341_Write_Data(0x10);

	//VCM CONTROL
	ILI9341_Write_Command(0xC5);
	ILI9341_Write_Data(0x3E);
	ILI9341_Write_Data(0x28);

	//VCM CONTROL 2
	ILI9341_Write_Command(0xC7);
	ILI9341_Write_Data(0x86);

	//MEMORY ACCESS CONTROL
	ILI9341_Write_Command(0x36);
	ILI9341_Write_Data(0x48);

	//VERTICAL SCROLL
	ILI9341_Write_Command(0x37);
	ILI9341_Write_Data(0x00);
	ILI9341_Write_Data(0x00);

	//PIXEL FORMAT
	ILI9341_Write_Command(0x3A);
	ILI9341_Write_Data(0x55);

	//FRAME RATIO CONTROL, STANDARD RGB COLOR
	ILI9341_Write_Command(0xB1);
	ILI9341_Write_Data(0x00);
	ILI9341_Write_Data(0x10);

	//DISPLAY FUNCTION CONTROL
	ILI9341_Write_Command(0xB6);
	ILI9341_Write_Data(0x08);
	ILI9341_Write_Data(0x82);
	ILI9341_Write_Data(0x27);

	//GAMMA FUNCTION DISABLE
	ILI9341_Write_Command(0xF2);
	ILI9341_Write_Data(0x00);

	//GAMMA CURVE SELECTED
	ILI9341_Write_Command(0x26);
	ILI9341_Write_Data(0x01);

	//POSITIVE GAMMA CORRECTION
	ILI9341_Write_Command(0xE0);
	ILI9341_Write_Data(0x0F);
	ILI9341_Write_Data(0x31);
	ILI9341_Write_Data(0x2B);
	ILI9341_Write_Data(0x0C);
	ILI9341_Write_Data(0x0E);
	ILI9341_Write_Data(0x08);
	ILI9341_Write_Data(0x4E);
	ILI9341_Write_Data(0xF1);
	ILI9341_Write_Data(0x37);
	ILI9341_Write_Data(0x07);
	ILI9341_Write_Data(0x10);
	ILI9341_Write_Data(0x03);
	ILI9341_Write_Data(0x0E);
	ILI9341_Write_Data(0x09);
	ILI9341_Write_Data(0x00);

	//NEGATIVE GAMMA CORRECTION
	ILI9341_Write_Command(0xE1);
	ILI9341_Write_Data(0x00);
	ILI9341_Write_Data(0x0E);
	ILI9341_Write_Data(0x14);
	ILI9341_Write_Data(0x03);
	ILI9341_Write_Data(0x11);
	ILI9341_Write_Data(0x07);
	ILI9341_Write_Data(0x31);
	ILI9341_Write_Data(0xC1);
	ILI9341_Write_Data(0x48);
	ILI9341_Write_Data(0x08);
	ILI9341_Write_Data(0x0F);
	ILI9341_Write_Data(0x0C);
	ILI9341_Write_Data(0x31);
	ILI9341_Write_Data(0x36);
	ILI9341_Write_Data(0x0F);

	//EXIT SLEEP
	ILI9341_Write_Command(0x11);
	HAL_Delay(120);

	//TURN ON DISPLAY
	ILI9341_Write_Command(0x29);

	//STARTING ROTATION
	ILI9341_Set_Rotation(SCREEN_HORIZONTAL_1);

  return ret;
}

//INTERNAL FUNCTION OF LIBRARY, USAGE NOT RECOMENDED, USE Draw_Pixel INSTEAD
/*Sends single pixel colour information to LCD*/
void ILI9341_Draw_Colour(uint16_t Colour)
{
	//SENDS COLOUR
	unsigned char TempBuffer[2] = {Colour>>8, Colour};

	HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_SET);
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_RESET);
	HAL_SPI_Transmit(HSPI_INSTANCE, TempBuffer, 2, 1);
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_SET);
}

//INTERNAL FUNCTION OF LIBRARY
/*Sends block colour information to LCD*/
void ILI9341_Draw_Colour_Burst(uint16_t Colour, uint32_t Size)
{
	//SENDS COLOUR
	uint32_t Buffer_Size = 0;
	unsigned char chifted = 	Colour>>8;
	unsigned char burst_buffer[Buffer_Size];
	uint32_t Sending_Size = Size*2;
	uint32_t Sending_in_Block = Sending_Size/Buffer_Size;
	uint32_t Remainder_from_block = Sending_Size%Buffer_Size;

	if((Size*2) < BURST_MAX_SIZE)
	{
		Buffer_Size = Size;
	}
	else
	{
		Buffer_Size = BURST_MAX_SIZE;
	}
		
	HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_SET);	
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_RESET);

	for(uint32_t j = 0; j < Buffer_Size; j+=2)
		{
			burst_buffer[j] = 	chifted;
			burst_buffer[j+1] = Colour;
		}

	if(Sending_in_Block != 0)
	{
		for(uint32_t j = 0; j < (Sending_in_Block); j++)
			{
			HAL_SPI_Transmit(HSPI_INSTANCE, (unsigned char *)burst_buffer, Buffer_Size, 10);	
			}
	}

	//REMAINDER!
	HAL_SPI_Transmit(HSPI_INSTANCE, (unsigned char *)burst_buffer, Remainder_from_block, 10);	
		
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_SET);
}

//FILL THE ENTIRE SCREEN WITH SELECTED COLOUR (either #define-d ones or custom 16bit)
/*Sets address (entire screen) and Sends Height*Width ammount of colour information to LCD*/
void ILI9341_Fill_Screen(uint16_t Colour)
{
	ILI9341_Set_Address(0,0,LCD_WIDTH,LCD_HEIGHT);	
	ILI9341_Draw_Colour_Burst(Colour, LCD_WIDTH*LCD_HEIGHT);	
}

//DRAW PIXEL AT XY POSITION WITH SELECTED COLOUR
//
//Location is dependant on screen orientation. x0 and y0 locations change with orientations.
//Using pixels to draw big simple structures is not recommended as it is really slow
//Try using either rectangles or lines if possible
//
void ILI9341_Draw_Pixel(uint16_t X,uint16_t Y,uint16_t Colour) 
{
	if((X >=LCD_WIDTH) || (Y >=LCD_HEIGHT)) return;	//OUT OF BOUNDS!
		
	//ADDRESS
	HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_RESET);	
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_RESET);
	ILI9341_SPI_Send(0x2A);
	HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_SET);	
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_SET);		

	//XDATA
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_RESET);	
	unsigned char Temp_Buffer[4] = {X>>8,X, (X+1)>>8, (X+1)};
	HAL_SPI_Transmit(HSPI_INSTANCE, Temp_Buffer, 4, 1);
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_SET);

	//ADDRESS
	HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_RESET);	
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_RESET);	
	ILI9341_SPI_Send(0x2B);
	HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_SET);			
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_SET);			

	//YDATA
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_RESET);
	unsigned char Temp_Buffer1[4] = {Y>>8,Y, (Y+1)>>8, (Y+1)};
	HAL_SPI_Transmit(HSPI_INSTANCE, Temp_Buffer1, 4, 1);
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_SET);

	//ADDRESS	
	HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_RESET);	
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_RESET);	
	ILI9341_SPI_Send(0x2C);
	HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_SET);			
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_SET);			

	//COLOUR	
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_RESET);
	unsigned char Temp_Buffer2[2] = {Colour>>8, Colour};
	HAL_SPI_Transmit(HSPI_INSTANCE, Temp_Buffer2, 2, 1);
	HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_SET);
}

//DRAW RECTANGLE OF SET SIZE AND HEIGTH AT X and Y POSITION WITH CUSTOM COLOUR
//
//Rectangle is hollow. X and Y positions mark the upper left corner of rectangle
//As with all other draw calls x0 and y0 locations dependant on screen orientation
//
void ILI9341_Draw_Rectangle(uint16_t X, uint16_t Y, uint16_t Width, uint16_t Height, uint16_t Colour)
{
	if((X >=LCD_WIDTH) || (Y >=LCD_HEIGHT)) return;
	if((X+Width-1)>=LCD_WIDTH)
	{
		Width=LCD_WIDTH-X;
	}
	if((Y+Height-1)>=LCD_HEIGHT)
	{
		Height=LCD_HEIGHT-Y;
	}
	ILI9341_Set_Address(X, Y, X+Width-1, Y+Height-1);
	ILI9341_Draw_Colour_Burst(Colour, Height*Width);
}

//DRAW LINE FROM X,Y LOCATION to X+Width,Y LOCATION
void ILI9341_Draw_Horizontal_Line(uint16_t X, uint16_t Y, uint16_t Width, uint16_t Colour)
{
	if((X >=LCD_WIDTH) || (Y >=LCD_HEIGHT)) return;
	if((X+Width-1)>=LCD_WIDTH)
	{
		Width=LCD_WIDTH-X;
	}
	ILI9341_Set_Address(X, Y, X+Width-1, Y);
	ILI9341_Draw_Colour_Burst(Colour, Width);
}

//DRAW LINE FROM X,Y LOCATION to X,Y+Height LOCATION
void ILI9341_Draw_Vertical_Line(uint16_t X, uint16_t Y, uint16_t Height, uint16_t Colour)
{
	if((X >=LCD_WIDTH) || (Y >=LCD_HEIGHT)) return;
	if((Y+Height-1)>=LCD_HEIGHT)
	{
		Height=LCD_HEIGHT-Y;
	}
	ILI9341_Set_Address(X, Y, X, Y+Height-1);
	ILI9341_Draw_Colour_Burst(Colour, Height);
}

/* Draws a full screen picture. */
void ILI9341_Draw_Image(const char* Image_Array, uint8_t Orientation)
{
	static unsigned char Temp_small_buffer[BURST_MAX_SIZE];
	uint32_t counter = 0;
	
	HAL_GPIO_WritePin(GPIOB, ILI9341_LED_Pin, GPIO_PIN_SET);

	if(Orientation == SCREEN_HORIZONTAL_1)
	{
		ILI9341_Set_Rotation(SCREEN_HORIZONTAL_1);
		ILI9341_Set_Address(0,0,LCD_DEFAULT_WIDTH,LCD_DEFAULT_HEIGHT);
			
		HAL_GPIO_WritePin(GPIOB, ILI9341_DC_Pin, GPIO_PIN_SET);
		HAL_GPIO_WritePin(GPIOB, ILI9341_CS_Pin, GPIO_PIN_RESET);

		for(uint32_t i = 0; i < LCD_FRAME_BUFFER_SIZE/BURST_MAX_SIZE; i++)
		{
			for(uint32_t k = 0; k < BURST_MAX_SIZE; k+=2)
			{
				Temp_small_buffer[k]	= Image_Array[counter+k+1];
				Temp_small_buffer[k+1]	= Image_Array[counter+k];
			}
			HAL_SPI_Transmit(&hspi2, (unsigned char*)Temp_small_buffer, BURST_MAX_SIZE, 100);
			counter += BURST_MAX_SIZE;
		}
		for(uint32_t k = 0; k < LCD_FRAME_BUFFER_SIZE - counter; k+=2)
		{
			Temp_small_buffer[k]	= Image_Array[counter+k+1];
			Temp_small_buffer[k+1]	= Image_Array[counter+k];
		}
		HAL_SPI_Transmit(&hspi2, (unsigned char*)Temp_small_buffer, LCD_FRAME_BUFFER_SIZE - counter, 100);			
			
		HAL_GPIO_WritePin(GPIOB, ILI9341_CS_Pin, GPIO_PIN_SET);
	}
	else if(Orientation == SCREEN_HORIZONTAL_2)
	{
		ILI9341_Set_Rotation(SCREEN_HORIZONTAL_2);
		ILI9341_Set_Address(0,0,LCD_RES_WIDTH,LCD_RES_HEIGHT);
			
		HAL_GPIO_WritePin(GPIOB, ILI9341_DC_Pin, GPIO_PIN_SET);	
		HAL_GPIO_WritePin(GPIOB, ILI9341_CS_Pin, GPIO_PIN_RESET);
		
		for(uint32_t i = 0; i < LCD_FRAME_BUFFER_SIZE/BURST_MAX_SIZE; i++)
		{
			for(uint32_t k = 0; k < BURST_MAX_SIZE; k+=2)
			{
				Temp_small_buffer[k]	= Image_Array[counter+k+1];
				Temp_small_buffer[k+1]	= Image_Array[counter+k];
			}
			HAL_SPI_Transmit(&hspi2, (unsigned char*)Temp_small_buffer, BURST_MAX_SIZE, 100);
			counter += BURST_MAX_SIZE;
		}
		for(uint32_t k = 0; k < LCD_FRAME_BUFFER_SIZE - counter; k+=2)
		{
			Temp_small_buffer[k]	= Image_Array[counter+k+1];
			Temp_small_buffer[k+1]	= Image_Array[counter+k];
		}
		HAL_SPI_Transmit(&hspi2, (unsigned char*)Temp_small_buffer, LCD_FRAME_BUFFER_SIZE - counter, 100);			
			
		HAL_GPIO_WritePin(GPIOB, ILI9341_CS_Pin, GPIO_PIN_SET);
	}
	else if(Orientation == SCREEN_VERTICAL_2)
	{
		ILI9341_Set_Rotation(SCREEN_VERTICAL_2);
		ILI9341_Set_Address(0,0,LCD_RES_HEIGHT,LCD_RES_WIDTH);
			
		HAL_GPIO_WritePin(GPIOB, ILI9341_DC_Pin, GPIO_PIN_SET);	
		HAL_GPIO_WritePin(GPIOB, ILI9341_CS_Pin, GPIO_PIN_RESET);
		
		for(uint32_t i = 0; i < LCD_FRAME_BUFFER_SIZE/BURST_MAX_SIZE; i++)
		{
			for(uint32_t k = 0; k < BURST_MAX_SIZE; k+=2)
			{
				Temp_small_buffer[k]	= Image_Array[counter+k+1];
				Temp_small_buffer[k+1]	= Image_Array[counter+k];
			}
			HAL_SPI_Transmit(&hspi2, (unsigned char*)Temp_small_buffer, BURST_MAX_SIZE, 100);
			counter += BURST_MAX_SIZE;
		}
		for(uint32_t k = 0; k < LCD_FRAME_BUFFER_SIZE - counter; k+=2)
		{
			Temp_small_buffer[k]	= Image_Array[counter+k+1];
			Temp_small_buffer[k+1]	= Image_Array[counter+k];
		}
		HAL_SPI_Transmit(&hspi2, (unsigned char*)Temp_small_buffer, LCD_FRAME_BUFFER_SIZE - counter, 100);			
			
		HAL_GPIO_WritePin(GPIOB, ILI9341_CS_Pin, GPIO_PIN_SET);
	}
	else if(Orientation == SCREEN_VERTICAL_1)
	{
		ILI9341_Set_Rotation(SCREEN_VERTICAL_1);
		ILI9341_Set_Address(0,0,LCD_RES_HEIGHT,LCD_RES_WIDTH);
			
		HAL_GPIO_WritePin(GPIOB, ILI9341_DC_Pin, GPIO_PIN_SET);	
		HAL_GPIO_WritePin(GPIOB, ILI9341_CS_Pin, GPIO_PIN_RESET);
		
		for(uint32_t i = 0; i < LCD_FRAME_BUFFER_SIZE/BURST_MAX_SIZE; i++)
		{
			for(uint32_t k = 0; k < BURST_MAX_SIZE; k+=2)
			{
				Temp_small_buffer[k]	= Image_Array[counter+k+1];
				Temp_small_buffer[k+1]	= Image_Array[counter+k];
			}
			HAL_SPI_Transmit(&hspi2, (unsigned char*)Temp_small_buffer, BURST_MAX_SIZE, 100);
			counter += BURST_MAX_SIZE;
		}
		for(uint32_t k = 0; k < LCD_FRAME_BUFFER_SIZE - counter; k+=2)
		{
			Temp_small_buffer[k]	= Image_Array[counter+k+1];
			Temp_small_buffer[k+1]	= Image_Array[counter+k];
		}
		HAL_SPI_Transmit(&hspi2, (unsigned char*)Temp_small_buffer, LCD_FRAME_BUFFER_SIZE - counter, 100);			
			
		HAL_GPIO_WritePin(GPIOB, ILI9341_CS_Pin, GPIO_PIN_SET);
	}
}

