
/*
 * This file is part of the Arducam SPI Camera project.
 *
 * Copyright 2021 Arducam Technology co., Ltd. All Rights Reserved.
 *
 * This work is licensed under the MIT license, see the file LICENSE for details.
 *
 */

#ifndef __ARDUCAM_H
#define __ARDUCAM_H
#include "Stm32Hal.h"


/**
* @file Arducam.h
* @author Arducam
* @date 2021/12/6
* @version V1.0
* @copyright Arducam
*/
 
#ifdef __cplusplus
extern "C" {
#endif
/// @cond
#define SDK_VERSION  0X00010000 
/// @endcond

/// @cond
#define TRUE  1  
#define FALSE 0  
/// @endcond

/**
* @struct SdkInfo
* @brief Basic information of the sdk
*/
struct SdkInfo{
	unsigned long sdkVersion;		/**<Sdk version */
};

/**
* @struct CameraInfo
* @brief Basic information of the camera module
*/

struct CameraInfo{
	char* cameraId;		/**<Model of camera module */
	int supportResolution;	/**<Resolution supported by the camera module */
	int supportSpecialEffects;	/**<Special effects supported by the camera module */
	unsigned long exposureValueMax;	/**<Maximum exposure time supported by the camera module */
	unsigned int exposureValueMin;	/**<Minimum exposure time supported by the camera module */
	unsigned int gainValueMax;	/**<Maximum gain supported by the camera module */
	unsigned int gainValueMin;	/**<Minimum gain supported by the camera module */
	unsigned char supportFocus;	/**<Does the camera module support the focus function */
	unsigned char supportSharpness;	/**<Does the camera module support the sharpening function */
	unsigned char deviceAddress; 
};

/**
  * @enum CamStatus
  * @brief Camera status
  */
typedef enum  
{
	CAM_ERR_SUCCESS = 0,     /**<Operation succeeded*/
	CAM_ERR_NO_CALLBACK= -1, /**< No callback function is registered*/
}CamStatus; 


/**
  * @enum CAM_IMAGE_MODE
  * @brief Configure camera resolution
  */
typedef enum {
	CAM_IMAGE_MODE_QQVGA =0x00, /**<160x120 */
	CAM_IMAGE_MODE_QVGA = 0x01,  /**<320x240*/
	CAM_IMAGE_MODE_VGA = 0x02, 	/**<640x480*/
	CAM_IMAGE_MODE_SVGA = 0x03, /**<800x600*/
	CAM_IMAGE_MODE_HD = 0x04,   /**<1280x720*/
	CAM_IMAGE_MODE_SXGAM = 0x05, /**<1280x960*/
	CAM_IMAGE_MODE_UXGA = 0x06, /**<1600x1200*/
	CAM_IMAGE_MODE_FHD  = 0x07, /**<1920x1080*/
	CAM_IMAGE_MODE_QXGA = 0x08, /**<2048x1536*/
	CAM_IMAGE_MODE_WQXGA2 = 0x09, /**<2592x1944*/
	CAM_IMAGE_MODE_96X96 = 0x0a, /**<96x96*/
/// @cond
	CAM_IMAGE_MODE_128X128 = 0x0b, /**<128x128*/
	CAM_IMAGE_MODE_320X320 = 0x0c, /**<320x320*/
	CAM_IMAGE_MODE_12 = 0x0d, /**<Reserve*/
	CAM_IMAGE_MODE_13 = 0x0e, /**<Reserve*/
	CAM_IMAGE_MODE_14 = 0x0f, /**<Reserve*/
	CAM_IMAGE_MODE_15 = 0x10, /**<Reserve*/
/// @endcond
}CAM_IMAGE_MODE;


/**
  * @enum CAM_CONTRAST_LEVEL
  * @brief Configure camera contrast level
  */
typedef enum {
	CAM_CONTRAST_LEVEL_MINUS_3=6,         /**<Level -3 */
	CAM_CONTRAST_LEVEL_MINUS_2=4,         /**<Level -2 */
	CAM_CONTRAST_LEVEL_MINUS_1=2,         /**<Level -1 */
	CAM_CONTRAST_LEVEL_DEFAULT=0,   /**<Level Default*/
	CAM_CONTRAST_LEVEL_1=1,          /**<Level +1 */
	CAM_CONTRAST_LEVEL_2=3,          /**<Level +2 */
	CAM_CONTRAST_LEVEL_3=5,          /**<Level +3 */
}CAM_CONTRAST_LEVEL;

/**
  * @enum CAM_EV_LEVEL
  * @brief Configure camera EV level
  */
typedef enum {
	CAM_EV_LEVEL_MINUS_3=6,         /**<Level -3 */
	CAM_EV_LEVEL_MINUS_2=4,         /**<Level -2 */
	CAM_EV_LEVEL_MINUS_1=2,         /**<Level -1 */
	CAM_EV_LEVEL_DEFAULT=0,   /**<Level Default*/
	CAM_EV_LEVEL_1=1,          /**<Level +1 */
	CAM_EV_LEVEL_2=3,          /**<Level +2 */
	CAM_EV_LEVEL_3=5,          /**<Level +3 */
}CAM_EV_LEVEL;                       


/**
  * @enum CAM_STAURATION_LEVEL
  * @brief Configure camera stauration  level
  */                                    
typedef enum {
	CAM_STAURATION_LEVEL_MINUS_3=6,         /**<Level -3 */
	CAM_STAURATION_LEVEL_MINUS_2=4,         /**<Level -2 */
	CAM_STAURATION_LEVEL_MINUS_1=2,         /**<Level -1 */
	CAM_STAURATION_LEVEL_DEFAULT=0,   /**<Level Default*/
	CAM_STAURATION_LEVEL_1=1,          /**<Level +1 */
	CAM_STAURATION_LEVEL_2=3,          /**<Level +2 */
	CAM_STAURATION_LEVEL_3=5,          /**<Level +3 */
}CAM_STAURATION_LEVEL;

/**
  * @enum CAM_BRIGHTNESS_LEVEL
  * @brief Configure camera brightness level
  */       
typedef enum {
	CAM_BRIGHTNESS_LEVEL_MINUS_4=8,          /**<Level -4 */
	CAM_BRIGHTNESS_LEVEL_MINUS_3=6,          /**<Level -3 */
	CAM_BRIGHTNESS_LEVEL_MINUS_2=4,          /**<Level -2 */
	CAM_BRIGHTNESS_LEVEL_MINUS_1=2,          /**<Level -1 */
	CAM_BRIGHTNESS_LEVEL_DEFAULT=0,    /**<Level Default*/
	CAM_BRIGHTNESS_LEVEL_1=1,           /**<Level +1 */
	CAM_BRIGHTNESS_LEVEL_2=3,           /**<Level +2 */
	CAM_BRIGHTNESS_LEVEL_3=5,           /**<Level +3 */
	CAM_BRIGHTNESS_LEVEL_4=7,		   /**<Level +4 */
}CAM_BRIGHTNESS_LEVEL;


/**
  * @enum CAM_SHARPNESS_LEVEL
  * @brief Configure camera Sharpness level
  */  
typedef enum {
	CAM_SHARPNESS_LEVEL_AUTO=0, /**<Sharpness Auto */
	CAM_SHARPNESS_LEVEL_1,	/**<Sharpness Level 1 */
	CAM_SHARPNESS_LEVEL_2,	/**<Sharpness Level 2 */
	CAM_SHARPNESS_LEVEL_3,	/**<Sharpness Level 3 */
	CAM_SHARPNESS_LEVEL_4,	/**<Sharpness Level 4 */
	CAM_SHARPNESS_LEVEL_5,	/**<Sharpness Level 5 */
	CAM_SHARPNESS_LEVEL_6,	/**<Sharpness Level 6 */
	CAM_SHARPNESS_LEVEL_7,	/**<Sharpness Level 7 */
	CAM_SHARPNESS_LEVEL_8,	/**<Sharpness Level 8 */
}CAM_SHARPNESS_LEVEL;


/**
  * @enum CAM_VIDEO_MODE
  * @brief Configure resolution in video streaming mode 
  */  
typedef enum {
	CAM_VIDEO_MODE_0 = 1, /**< 320x240 */
	CAM_VIDEO_MODE_1 = 2, /**< 640x480 */
}CAM_VIDEO_MODE;


/**
  * @enum CAM_IMAGE_PIX_FMT
  * @brief Configure image pixel format
  */  
typedef enum  {
	CAM_IMAGE_PIX_FMT_RGB565 = 0x02, /**< RGB565 format */
	CAM_IMAGE_PIX_FMT_JPG    = 0x01, /**< JPEG format */
	CAM_IMAGE_PIX_FMT_YUV    = 0x03, /**< YUV format */
	CAM_IMAGE_PIX_FMT_NONE, /**< No defined format */
}CAM_IMAGE_PIX_FMT;


/**
  * @enum CAM_WHITE_BALANCE
  * @brief Configure white balance mode
  */  
typedef enum {
	CAM_WHITE_BALANCE_MODE_DEFAULT=0,/**< Auto */
	CAM_WHITE_BALANCE_MODE_SUNNY,	 /**< Sunny */
	CAM_WHITE_BALANCE_MODE_OFFICE,	 /**< Office */
	CAM_WHITE_BALANCE_MODE_CLOUDY,	/**< Cloudy*/
	CAM_WHITE_BALANCE_MODE_HOME,	/**< Home */
}CAM_WHITE_BALANCE;


/**
  * @enum CAM_COLOR_FX
  * @brief Configure special effects
  */  
typedef enum  {
	CAM_COLOR_FX_NONE = 0, /**< no effect   */
	CAM_COLOR_FX_BLUEISH, /**< cool light   */
	CAM_COLOR_FX_REDISH, /**< warm   */
	CAM_COLOR_FX_BW, /**< Black/white   */
	CAM_COLOR_FX_SEPIA, /**<Sepia   */
	CAM_COLOR_FX_NEGATIVE, /**<positive/negative inversion  */
	CAM_COLOR_FX_GRASS_GREEN, /**<Grass green */
	CAM_COLOR_FX_OVER_EXPOSURE, /**<Over exposure*/
	CAM_COLOR_FX_SOLARIZE,		/**< Solarize   */
	CAM_COLOR_FX_YELLOWISH,
}CAM_COLOR_FX;



typedef uint8_t (*BUFFER_CALLBACK)(uint8_t*buffer, uint8_t lenght);	/**<Callback function prototype  */



/**
* @struct ArducamCamera
* @brief Camera drive interface and information
*/
  
typedef struct {
	int csPin;					/**< CS pin */
	uint32_t totalLength;		/**< The total length of the picture */
	uint32_t receivedLength;	/**< The remaining length of the picture */
	uint8_t blockSize;			/**< The length of the callback function transmission */
	uint8_t cameraId;			/**< Model of camera module */
	uint8_t cameraDataFormat;	/**< The currently set image pixel format */
	uint8_t burstFirstFlag;		/**< Flag bit for reading data for the first time in burst mode */
	uint8_t previewMode;		/**< Stream mode flag */
	uint8_t currentPixelFormat;		/**< The currently set image pixel format */
	uint8_t currentPictureMode;		/**< Currently set resolution */
	struct CameraInfo myCameraInfo;	/**< Basic information of the current camera */
	const struct CameraOperations* arducamCameraOp;  /**< Camera function interface */
	BUFFER_CALLBACK callBackFunction;				/**< Camera callback function */
	uint8_t verDate[3];             /**< Camera firmware version*/
	struct SdkInfo* currentSDK;     /**< Current SDK version*/
}ArducamCamera;


/// @cond
struct CameraOperations{
	CamStatus (*begin)(ArducamCamera*);
	CamStatus (*takePicture)(ArducamCamera*,CAM_IMAGE_MODE,CAM_IMAGE_PIX_FMT);
	CamStatus (*takeMultiPictures)(ArducamCamera*,CAM_IMAGE_MODE,CAM_IMAGE_PIX_FMT,uint8_t);
	CamStatus (*startPreview)(ArducamCamera*,CAM_VIDEO_MODE);
	CamStatus (*stopPreview)(ArducamCamera*);
	CamStatus (*setAutoExposure)(ArducamCamera*,uint8_t);
	CamStatus (*setAbsoluteExposure)(ArducamCamera*,uint32_t);
	CamStatus (*setAutoISOSensitive)(ArducamCamera*,uint8_t);
	CamStatus (*setISOSensitivity)(ArducamCamera*,int);
	CamStatus (*setAutoWhiteBalance)(ArducamCamera*,uint8_t);
	CamStatus (*setAutoWhiteBalanceMode)(ArducamCamera*,CAM_WHITE_BALANCE);
	CamStatus (*setColorEffect)(ArducamCamera*,CAM_COLOR_FX);
	CamStatus (*setAutoFocus)(ArducamCamera*,uint8_t);
	CamStatus (*setSaturation)(ArducamCamera*,CAM_STAURATION_LEVEL);
	CamStatus (*setEV)(ArducamCamera*,CAM_EV_LEVEL);
	CamStatus (*setContrast)(ArducamCamera*,CAM_CONTRAST_LEVEL);
	CamStatus (*setBrightness)(ArducamCamera*,CAM_BRIGHTNESS_LEVEL);
	CamStatus (*setSharpness)(ArducamCamera*,CAM_SHARPNESS_LEVEL);
	uint32_t (*imageAvailable)(ArducamCamera*);
	void (*csHigh)(ArducamCamera*);
	void (*csLow)(ArducamCamera*);
	uint8_t (*readBuff)(ArducamCamera*,uint8_t*,uint8_t);
	uint8_t (*readByte)(ArducamCamera*);
	void (*debugWriteRegister)(ArducamCamera*,uint8_t*);
	void (*writeReg)(ArducamCamera*,uint8_t,uint8_t);
	uint8_t (*readReg)(ArducamCamera*,uint8_t);
	uint8_t (*busRead)(ArducamCamera*,int);
	uint8_t (*busWrite)(ArducamCamera*,int,int);
	void (*flushFifo)(ArducamCamera*);
	void (*startCapture)(ArducamCamera*);
	void (*clearFifoFlag)(ArducamCamera*);
	uint32_t (*readFifoLength)(ArducamCamera*);
	uint8_t (*getBit)(ArducamCamera*,uint8_t,uint8_t);
	void (*setFifoBurst)(ArducamCamera*);
	void (*setCapture)(ArducamCamera*);
	void (*waitI2cIdle)(ArducamCamera*);
	void (*lowPowerOn)(ArducamCamera*);
	void (*lowPowerOff)(ArducamCamera*);
	void (*registerCallback)(ArducamCamera*,BUFFER_CALLBACK,uint8_t);
};

/// @endcond

//**********************************************
//!
//! @brief Create a camera instance
//!
//! @param cs Chip select signal for SPI communication
//!
//! @return Return a ArducamCamera instance
//!
//**********************************************
ArducamCamera createArducamCamera(int cs);


//**********************************************
//!
//! @brief Initialize the configuration of the camera module
//! @param camera ArducamCamera instance
//! @return Return operation status 
//**********************************************

CamStatus begin(ArducamCamera* camera);

//**********************************************
//!
//! @brief Start a snapshot with specified resolution and pixel format
//!
//! @param camera ArducamCamera instance 
//! @param mode Resolution of the camera module
//! @param pixel_format Output image pixel format,which supports JPEG, RGB, YUV 
//!
//! @return Return operation status 
//!			
//! @note The mode parameter must be the resolution wh
CamStatus takePicture(ArducamCamera*camera, CAM_IMAGE_MODE mode, CAM_IMAGE_PIX_FMT pixel_format);


//**********************************************
//!
//! @brief Start multi capture with specified number of image. 
//!
//! @param camera ArducamCamera instance
//! @param mode Resolution of the camera module
//! @param pixel_format Output image pixel format,which supports JPEG, RGB, YUV 
//! @param number Number of pictures taken
//!
//! @return Return operation status 
//!			
//!
//! @note The mode parameter must be the resolution which the current camera supported
//**********************************************
CamStatus takeMultiPictures(ArducamCamera*camera, CAM_IMAGE_MODE mode, CAM_IMAGE_PIX_FMT pixel_format, uint8_t number);

//**********************************************
//!
//! @brief Start preview with specified resolution mode.
//!
//! @param camera ArducamCamera instance
//! @param mode Resolution of the camera module
//!
//! @return Return operation status 
//!			
//! @note Before calling this function, you need to register the callback function.The default image pixel format is JPEG
//**********************************************
CamStatus startPreview(ArducamCamera*camera, CAM_VIDEO_MODE mode);


//**********************************************
//!
//! @brief Stop preview
//!
//! @param camera ArducamCamera instance
//!
//! @return Return operation status 
//!			
//**********************************************
CamStatus stopPreview(ArducamCamera*camera);


//**********************************************
//!
//! @brief Set the exposure mode
//!
//! @param   camera ArducamCamera instance
//! @param   val `1` Turn on automatic exposure `0` Turn off automatic exposure
//!
//! @return Return operation status 
//!			
//**********************************************
CamStatus setAutoExposure(ArducamCamera*camera, uint8_t val);


//**********************************************
//!
//! @brief Set the exposure time Manually
//!
//! @param   camera ArducamCamera instance
//! @param   val Value of exposure line
//!
//! @return Return operation status 
//!			
//! @note Before calling this function, you need to use the @ref setAutoExposure() function to turn off the auto exposure function
//**********************************************
CamStatus setAbsoluteExposure(ArducamCamera*camera, uint32_t val);





//**********************************************
//!
//! @brief Set the gain mode
//!
//! @param   camera ArducamCamera instance
//! @param   val `1` turn on automatic gain `0` turn off automatic gain
//!
//! @return Return operation status 
//!			
//**********************************************
CamStatus setAutoISOSensitive(ArducamCamera*camera, uint8_t val);


//**********************************************
//!
//! @brief Set the exposure time Manually
//!
//! @param  camera ArducamCamera instance
//! @param  iso_sense Value of gain 
//!
//! @return Return operation status 
//!			
//! @note Before calling this function, you need to use the @ref setAutoISOSensitive() function to turn off the auto gain function
//**********************************************
CamStatus setISOSensitivity(ArducamCamera*camera, int iso_sense);


//**********************************************
//!
//! @brief Set white balance mode
//!
//! @param  camera ArducamCamera instance
//! @param  val `1` turn on automatic white balance `0` turn off automatic white balance
//!
//! @return Return operation status 
//!			
//**********************************************
CamStatus setAutoWhiteBalance(ArducamCamera*camera, uint8_t val);


//**********************************************
//!
//! @brief  Set the white balance mode Manually
//!
//! @param   camera ArducamCamera instance
//! @param   mode White balance mode
//!
//! @return Return operation status 
//!			
//**********************************************
CamStatus setAutoWhiteBalanceMode(ArducamCamera* camera, CAM_WHITE_BALANCE mode);


//**********************************************
//!
//! @brief Set special effects
//!
//! @param  camera ArducamCamera instance
//! @param  effect Special effects mode
//!
//! @return Return operation status 
//!			
//**********************************************
CamStatus setColorEffect(ArducamCamera* camera, CAM_COLOR_FX effect);

//**********************************************
//!
//! @brief Set auto focus mode
//!
//! @param  camera ArducamCamera instance
//! @param  val mode of autofocus
//!
//! @return Return operation status 
//!			
//!
//! @note Only `5MP` cameras support auto focus control
//**********************************************
CamStatus setAutoFocus(ArducamCamera*camera, uint8_t val);

//**********************************************
//!
//! @brief Set saturation level
//!
//! @param   camera ArducamCamera instance
//! @param   level Saturation level
//!
//! @return Return operation status 
//!			
//**********************************************
CamStatus setSaturation(ArducamCamera*camera, CAM_STAURATION_LEVEL level);


//**********************************************
//!
//! @brief Set EV level
//!
//! @param   camera ArducamCamera instance
//! @param   level EV level
//!
//! @return Return operation status 
//!			
//**********************************************
CamStatus setEV(ArducamCamera*camera, CAM_EV_LEVEL level);


//**********************************************
//!
//! @brief Set Contrast level
//!
//! @param   camera ArducamCamera instance
//! @param   level Contrast level
//!
//! @return Return operation status 
//!			
//********************************************
CamStatus setContrast(ArducamCamera*camera, CAM_CONTRAST_LEVEL level);


//**********************************************
//!
//! @brief Set Brightness level
//!
//! @param  camera ArducamCamera instance
//! @param  level Brightness level
//!
//! @return Return operation status 
//!			
//**********************************************
CamStatus setBrightness(ArducamCamera*camera, CAM_BRIGHTNESS_LEVEL level);


//**********************************************
//!
//! @brief Set Sharpness level
//!
//! @param  camera ArducamCamera instance
//! @param  level Sharpness level
//!
//! @return Return operation status 
//!			
//!
//! @note Only `3MP` cameras support sharpness control
//**********************************************
CamStatus setSharpness(ArducamCamera*camera, CAM_SHARPNESS_LEVEL level);


//**********************************************
//!
//! @brief Read image data with specified length to buffer 
//!
//! @param  camera ArducamCamera instance
//! @param  buff Buffer for storing camera data
//! @param  length The length of the available data to be read
//!
//! @return Returns the length actually read
//!
//! @note Transmission length should be less than `255`
//**********************************************
uint8_t readBuff(ArducamCamera*camera, uint8_t* buff, uint8_t length);

//**********************************************
//!
//! @brief Read a byte from FIFO
//!
//! @param camera ArducamCamera instance
//!
//! @return Returns Camera data
//!
//! @note Before calling this function, make sure that the data is available in the buffer
//**********************************************
uint8_t readByte(ArducamCamera*camera);


//**********************************************
//!
//! @brief Debug mode
//!
//! @param  camera ArducamCamera instance
//! @param  buff There are four bytes of buff Byte 1 indicates the device address, Byte 2 indicates the high octet of the register, Byte 3 indicates the low octet of the register, and Byte 4 indicates the value written to the register
//!
//**********************************************
void debugWriteRegister(ArducamCamera* camera, uint8_t* buff);


//**********************************************
//!
//! @brief Create callback function
//!
//! @param  camera ArducamCamera instance
//! @param  function Callback function name
//! @param  blockSize The length of the data transmitted by the callback function at one time
//!
//! @note Transmission length should be less than `255`
//**********************************************
void registerCallback(ArducamCamera* camera, BUFFER_CALLBACK function, uint8_t blockSize);


//**********************************************
//!
//! @brief Turn on low power mode
//!
//! @param camera ArducamCamera instance
//!
//**********************************************
void lowPowerOn(ArducamCamera*camera);

//**********************************************
//!
//! @brief Turn off low power mode
//!
//! @param camera ArducamCamera instance
//!
//**********************************************
void lowPowerOff(ArducamCamera*camera);



#ifdef __cplusplus
}
#endif
#endif /*__ARDUCAM_H*/

