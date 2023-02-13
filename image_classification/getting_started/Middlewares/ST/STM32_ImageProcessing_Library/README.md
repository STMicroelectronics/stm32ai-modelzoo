![STMicroelectronics](_htmresc/st_logo.png)

*Copyright &copy; 2021 STMicroelectronics*

# STM32 Image Processing Library v1.0.0

## Introduction

This document is a quick guide that introduces ***STM32 Image Processing Library*** and provides advise about the preparation and the usage of the *STM32 Image Processing Library* in real applications.

*STM32 Image Processing Library* (in short, ***STM32IPL***) is a C software library for ***STMicroelectronics STM32 MCUs*** that provides specific functionalities that help the development of visual analysis applications.

The following sections are dedicated to:

-   Give a quick introduction to *STM32IPL*
-   Explain the fundamental elements of *STM32IPL*
-   Illustrate how to develop a working application exploiting *STM32IPL*
-   Show the source code of an application example

Please, note that this document does not contain detailed specifications of the functions provided by the library; the reader can find such details in *STM32IPL.chm*.

## Main characteristics

*STM32IPL* is an open-source software library, written in C, that offers image processing and computer vision functionalities for a faster development of visual analysis applications on ***STM32*** microcontrollers.

The main key characteristics of *STM32IPL* are:

-   Provide the developer with a useful and ready to use software component that allows reducing the development time of image processing and computer vision applications on *STM32* platforms

-   Satisfy the most common needs in terms of image processing and computer vision functionalities for embedded systems

-   Simplify and speed-up the development of applications by incapsulating and hiding, as much as possible, the complexity of the typical image processing and computer vision operations

*STM32IPL* is functionally organized in various modules, as depicted in the picture below:

![STM32IPL modules](_htmresc/picture1.png)

Such modules can be virtually grouped in the following macro groups:

-   Library initialization and de-initialization group (dark green module)

-   Group including functions for image creation, initialization, release, etc. (light green module)

-   Group including image transformation functions as filtering, color conversion, scaling, morphological operators, warping, etc. (dark yellow modules)

-   Group including feature and object extraction functions as edge and blob detectors, Hough transforms, etc. (light yellow modules)

-   Group including functions that operate on lines, rectangles, ellipses, etc. (dark blue modules)

-   Group including image reading and writing functions (light blue module)

-   Group including functions that draw graphical elements in an image (dark gray module)

-   Last group that includes the remaining modules for calculation of integral images and image statistics (light gray modules)

More information on *STM32IPL* functions can be found in *STM32IPL.chm*.

## Software architecture

The software architecture of a typical *STM32* application exploiting *STM32IPL* is depicted below.

![Typical software architecture](_htmresc/picture2.png)

*STM32IPL* is released as open source ***STM32Cube Middleware*** component; basically, all the *STM32IPL* functions are platform independent, with few exceptions:

-   The I/O functions that perform reading/writing operation on files, in particular, the two read/write functions that handle the supported image file formats as *BMP* (*Windows Bitmap*), *PPM* (*Portable PixMap*), *PGM* (*Portable GreyMap*), and *JPEG*: these functions depend on the following third-party open source libraries that are part of the set of *STM32Cube Middleware* components:

    -   ***FatFs***, that offers read/write operations on a *FatFS* file system (which can be, for example, mounted on an microSD card)

    -   ***LibJPEG***, that offers *JPEG* encoding and decoding functionalities

-   The *STM32IPL* function that allows a fast drawing of images on a screen thanks to the ***STM32 DMA2D***, a hardware accelerator for graphical operations

## Getting started with STM32IPL

This section describes the basic steps needed to develop an *STM32* application exploiting *STM32IPL*; it is assumed that the reader already knows how to develop an application for *STM32* MCUs. Look at [this site](https://wiki.st.com/stm32mcu/) to learn more about *STM32* programming.

*STM32IPL* is released as open source *STM32Cube Middleware* component and is organized in two directories:

-   *STM32_ImageProcessing_Library/Inc* containing the include files

-   *STM32_ImageProcessing_Library/Src* containing the source files

### Setting the project properties

As first step, it is necessary to add the *STM32_ImageProcessing_Library/Inc* folder to the list of the include directories of the application project.

Then, it is necessary to add `STM32IPL` to the list of define symbols of the compiler pre-processor.

As described in section 3, as *STM32IPL* uses *FatFs* and *LibJPEG* libraries, it is necessary to add their relative include directories to the application project as well; however, the inclusion of such directories depends on the particular configuration of *STM32IPL*, as explained in section 4.3,

### Adding the source code to the project

As next step, it is necessary to add the *STM32IPL* source code to the project, that is, all the files present in the *STM32_ImageProcessing_Library/Src* directory. Depending on the actual configuration of *STM32IPL* (as explained in section 4.3) it could be necessary to also add the source files relative to *FatFs* and *LibJPEG* libraries to the project.

After that, the developer should add the source files relative to his/her own application, together with the eventual source files specific to the target *STM32* board, as drivers, *BPS*, etc.

### Configuration of the library

The developer can configure *STM32IPL* by executing the following steps:

1.  Copy */STM32_ImageProcessing_Library/Inc/stm32ipl_conf_template.h* to the application folder

2.  Rename the copied *stm32ipl_conf_template.h to stm32ipl_conf.h*

3.  Edit *stm32ipl_conf.h* to:

    -   Comment/uncomment the symbols starting with `STM32IPL_ENABLE`  to disable/enable the usage of associated hardware resource

    -   Change the values relative to the other symbols

4.  Save *stm32ipl_conf.h*

*stm32ipl_conf.h* contains three main sections:

-   ***Platform specific settings***: this section defines the symbols specific to the target platform. The provided *stm32ipl_conf_template.h*, for instance, shows values that are suitable for the ***STM32H747I-DISCO*** reference board. In particular, the symbol `STM32IPL_ENABLE_HW_SCREEN_DRAWING`, when defined, enables the usage of the *STM32 DMA2D*, the hardware accelerator for graphical operations, to allow the rendering of *STM32IPL* images on the eventual screen connected to the target board

-   ***General settings***: this section defines the symbols used to configure the *JPEG* codec

-   ***Library modules enablers***: this section defines the symbols used to enable/disable the inclusion of some *STM32IPL* modules:
-   `STM32IPL_ENABLE_IMAGE_IO`: it controls the inclusion of image read/write functions
    
-   `STM32IPL_ENABLE_JPEG`: it controls the inclusion of the *JPEG* codec. When this symbol is defined, the user has to add the *LibJPEG* source files to his/her project
    
-   `STM32IPL_ENABLE_OBJECT_DETECTION`: it controls the inclusion of the object detector module
    
-   `STM32IPL_ENABLE_FRONTAL_FACE_CASCADE`: when the symbol `STM32IPL_ENABLE_OBJECT_DETECTION` is defined, it controls the inclusion of the provided frontal face cascade used to allow the detection of frontal faces
    
-   `STM32IPL_ENABLE_EYE_CASCADE`: when the symbol `STM32IPL_ENABLE_OBJECT_DETECTION` is defined, it controls the inclusion of the provided eye cascade used to allow the detection of eyes

### Initialization of the library

In order to use the *STM32IPL* API, it is necessary to include the following header file in the source code file:
```c
#include "stm32ipl.h"
```
Before calling any function belonging to *STM32IPL*, it is fundamental to correctly initialize the library by calling (typically in the `main()` function) the following function:
```c
void STM32Ipl_InitLib(void *memAddr, uint32_t memSize)
```
`STM32Ipl_InitLib()` allows the user to assign an entire block of memory to *STM32IPL*; such memory block is then used by *STM32IPL* functions that need memory buffers to properly execute.

To un-initialize *STM32IPL* and release the block of memory assigned to it with `STM32Ipl_InitLib()`, the user can call:
```c
void STM32Ipl_DeInitLib(void)
```
More details are explained in the *Memory management* section below.

### Memory management
Many of the functions provided by *STM32IPL* need memory to work properly. In order to facilitate the developer, the general mechanism adopted by *STM32IPL* is based on an initial allocation of a block of memory with a certain size; each library function that needs memory to work takes a portion of such memory, uses it and then release it when done. The management of these buffers is normally hidden to the user, as it is included in the implementation of the library function itself.

Differently, some other library functions, during their execution, get memory from the initial block, use it to save the results of the operation and then return it to the caller; in such cases, the caller is responsible of releasing such memory when done with it; the released memory gets back to the block initially reserved to *STM32IPL* and becomes available for subsequent usages.

It is up to the developer to define the size and the kind of memory (*SRAM*, *SDRAM*, etc.) that must be assigned to *STM32IPL*; in particular, the size depends on the kind of processing and algorithms that must be executed. There is no magic formula that can be used to define the right amount of memory to be reserved. Instead, the developer should estimate the right memory size by taking into account the resolution of the images to be processed, the quantity of memory needed by each function being part of the complete processing pipeline as well as the outputs themselves.

#### Memory initialization

The following couple of examples show how to assign a memory block to the library.

- *Case 1*: let us suppose that the image processing pipeline needs less than 256 KB to work, and that *SRAM* is the kind of memory to be reserved to *STM32IPL*: execute the following steps to correctly initialize the library:

1.  In *stm32ipl_conf.h*, change the value defined by `STM32IPL_INT_BUFFER_SIZE` to the desired size:
```c
#define STM32IPL_INT_BUFFER_SIZE (1024 * 256)
```
2.  Declare (typically in *main.c*) the memory buffer as:

```c
uint8_t stm32iplBuffer[STM32IPL_INT_BUFFER_SIZE];
```

3.  Finally, initialize *STM32IPL* with:

```c 
STM32Ipl_InitLib(stm32iplBuffer, STM32IPL_INT_BUFFER_SIZE);
```

- *Case 2*: let us suppose that the image processing pipeline needs less than 512 KB to work, and that *SDRAM* is the kind of memory to be reserved to *STM32IPL*: execute the following steps to correctly initialize the library:

1.  In *stm32ipl_conf.h*, change the value defined by `STM32IPL_EXT_BUFFER_SIZE` to the desired size:

```c
#define STM32IPL_EXT_BUFFER_SIZE (1024 * 512)
```

2.  Initialize *STM32IPL* with:

```c
STM32Ipl_InitLib(STM32IPL_EXT_MEM_ADDR, STM32IPL_INT_BUFFER_SIZE);
```

It is important to highlight that the default maximum size of memory that can be reserved to the library is 4 MB; the user can change it by modifying the value assigned to the symbol `UMM_BLOCK_BODY_SIZE` which is defined in */STM32_ImageProcessing_Library/Inc/umm_malloc_cfg.h*.

The default value (corresponding to 4 MB) is:

```c
#define UMM_BLOCK_BODY_SIZE 128
```

Follow the instructions given in *umm_malloc_cfg.h* to select the proper value to be assigned to `UMM_BLOCK_BODY_SIZE`.

#### Memory buffer management

As explained before, some library functions allocate memory for their execution; many times, the buffers are allocated, used and then automatically released when the function ends. In other cases, the function allocates a buffer, uses it, fills it with results and then returns it to the caller which must manage the proper release when done with it.

Here is an example:

```c
image_t img;

// Load the image from file.
if (stm32ipl_err_Ok == STM32Ipl_ReadImage(&img, "myImage.bmp")) {

	// Use the loaded image here...

	// Release the image data when it is not needed anymore.
	STM32Ipl_ReleaseData(&img);
}
```

In this example, the `STM32Ipl_ReadImage()` function gets the right amount of memory (from the block reserved to the library) to store the image data read from picture.bmp stored on the *microSD* card. Then the read image can used by the algorithm. Finally, the image data is released with `STM32Ipl_ReleaseData()` and the relative buffer gets back to the original block of memory reserved to the library.

So, in general, it is up to the developer to read the documentation to understand when it is needed to take care of the memory release.

#### Memory deinitialization

As soon as the *STM32IPL* is not needed anymore, the user can call `STM32Ipl_DeInitLib()` to release the whole memory block reserved at the beginning, so that it can be made available for further usages.

### Containers

*STM32IPL* uses two types of containers to store complex data: **list** and **array**. These containers are used as arguments to some *STM32IPL* functions, sometimes as input and sometimes as output parameters. In the following *Examples* section some handy examples that explain how to use such containers are reported.

## Examples

This section shows simple practical examples explaining how to use *STM32IPL* to develop applications. Such examples assume that *STM32IPL* has been properly initialized as explained in the section *Initialization of the library* above.

The examples below typically read image from files, so it is assumed that the user has properly initialized and mounted the *FatFs* file system, for instance on a microSD card, as the pertinent source code is not included here.

### Resize

This example explains how to:

- read an image
- resize it to a smaller destination image
- show both images to the screen

```c
void Resize(void)
{
	image_t srcImg; // Source image.
	image_t dstImg; // Destination image.
	uint16_t dstWidth = 200; // Destination width.
	uint16_t dstHeight = 100; // Destination height.

	// Load an image from file system.
	if (stm32ipl_err_Ok == STM32Ipl_ReadImage(&srcImg, "myImage.bmp")) {
		// Display the source image on the screen (left side).
		STM32Ipl_DrawScreen_DMA2D(&srcImg, 0, 0);

		// Allocate memory to the destination image.
		// The destination image must have the same format as the source image.
		if (stm32ipl_err_Ok == STM32Ipl_AllocData(&dstImg, dstWidth, dstHeight,
                                                  image_bpp_t)srcImg.bpp)) {
			// Resize the source image and store the results into the destination image.
			if (stm32ipl_err_Ok == STM32Ipl_Resize(&srcImg, &dstImg, NULL)) {
				// Display the destination image on the screen (right side).
				STM32Ipl_DrawScreen_DMA2D(&dstImg, 400, 0);
			}

			// Release the memory buffer containing the destination data image.
			STM32Ipl_ReleaseData(&dstImg);
		}

		// Release the memory buffer containing the source data image.
		STM32Ipl_ReleaseData(&srcImg);
	}
}
```

### Face Detection

This example explains how to:

- read an image
- detect the faces in the image
- use an array container to get the results (detected faces)
- draw the bounding boxes of the faces in the image
- show the image with the bounding boxes of the detected faces on the screen

```c
void FaceDetection(void)
{
	image_t img;
	cascade_t cascade;			// The cascade structure used by the object detector.
	uint16_t thickness = 2;		// Set the thickness of the rectangle (pixels).
	bool fill = false;			// Avoid to fill the rectangle.
	float scaleFactor = 1.25f;	// Modify this value to detect objects at 
								// different scale (must be > 1.0f).
	float threshold = 0.75f;	// Modify this value to tune the detection rate against
    							// the false positive rate (0.0f - 1.0f).
	
	// Load face cascade.
    if (stm32ipl_err_Ok == STM32Ipl_LoadFaceCascade(&cascade)) {
		// Load an image from file system.
		if (stm32ipl_err_Ok == STM32Ipl_ReadImage(&img, "myImage.bmp")) {
			uint32_t faceCount;
			array_t *faces = 0;

			// Detect faces. No ROI is passed, so the full image is analyzed.
			if (stm32ipl_err_Ok == STM32Ipl_DetectObject(&img, &faces, NULL, &cascade, 
                                                         scaleFactor, threshold)) {

				// Get the number of detected faces.
				faceCount = array_length(faces);

				// Get the bounding box for each detected face.
				for (int i = 0; i < faceCount; i++) {
					rectangle_t *r = array_at(faces, i);

					// Draw the bounding box around each detected face.
					STM32Ipl_DrawRectangle(&img, r->x, r->y, r->w, r->h, 	
                                           STM32IPL_COLOR_GREEN, thickness, fill);
				}

				// Release the array containing the faces.
				array_free(faces);
				faces = NULL;
			}

			// Display the image with the bounding boxes of the detected face 
			// on the top-left corner of the screen.
			STM32Ipl_DrawScreen_DMA2D(&img, 0, 0);

			// Release the memory buffer containing the source data image.
			STM32Ipl_ReleaseData(&img);
        }
    }
}
```

### Binarization

This example explains how to:

- read an image
- use a list container to set the proper thresholds needed for the binarization
- execute the binarization
- show the binary image on the screen

```c
void Binarization(void)
{
	image_t img;
	list_t thresholds;		// List of LAB thresholds used to binarize the image.
	color_thresholds_list_lnk_data_t colorTh;	// Structure used to set the thresholds.
	bool invert = false; 	// Take the values inside the threshold bounds.
	bool zero = false;		// The thresholded pixels in the destination image
    						// are set to 1, the others to 0.

    // Set the thresholds on LAB channels.
    colorTh.LMin = 0;
    colorTh.LMax = 100;
    colorTh.AMin = 0;
    colorTh.AMax = 127;
    colorTh.BMin = 0;
    colorTh.BMax = 127;

    // Init the list so that each element has the right size.
    list_init(&thresholds, sizeof(color_thresholds_list_lnk_data_t));

    // Push the thresholds used to binarize the image into the list.
    list_push_back(&thresholds, &colorTh);

    // Read the image from file system.
    if (stm32ipl_err_Ok == STM32Ipl_ReadImage(&img, "myImage.bmp")) {

        // Display the image on the screen (left side).
        STM32Ipl_DrawScreen_DMA2D(&img, 0, 0);

        // Execute the binarization. In this case, source and destination are the same,
        // so the source image is overwritten with the binarized image; no mask is used.
        if (stm32ipl_err_Ok == STM32Ipl_Binary(&img, &img, &thresholds,
                                               invert, zero, NULL)) {
            // Display the modified image on the screen (left side).
            STM32Ipl_DrawScreen_DMA2D(&img, 400, 0);
        }

        // Release the image data buffer.
        STM32Ipl_ReleaseData(&img);
    }

    // Finally, release the memory allocated to the list.
    list_free(&thresholds);
}
```
### Find circles

This example explains how to:

- read an image
- find circles in the image using the Hough transform
- use a list container to get the circles found
- draw the circles on the image
- show the image with the circles on the screen


```c
void FindCircle(void)
{
	image_t img;
	list_t circles;				// List of circles found.
	uint16_t thickness = 2;		// Set the thickness of the circles (pixels).
	bool fill = false;			// Avoid to fill the circle.
	uint32_t xStride = 2;		// Number of pixels to be skipped horizontally.
	uint32_t yStride = 2;		// Number of pixels to be skipped vertically.
	uint32_t threshold = 2000;	// Magnitude threshold; only circles with magnitude
    							// greater than or equal to such threshold are returned.
	uint32_t xMargin = 10;		// Circles having horizontal distance between their
    							// centers less than this value are merged.
	uint32_t yMargin = 10;		// Circles having vertical distance between their centers
    							// less than this value are merged.
	uint32_t rMargin = 30;		// Circles having difference between their radius less
    							// than this value are merged.
	uint32_t rMin = 18;			// Minimum circle radius detected; increase it to speed 
    							// up the execution.
	uint32_t rMax = 50;			// Maximum circle radius detected; decrease it to speed 
    							// up the execution.
	uint32_t rStep = 2;			// Radius step value.
	
     // Read the image from file system.
	if (stm32ipl_err_Ok == STM32Ipl_ReadImage(&img, "myImage.bmp")) {

        // Search for the circles in the full image (no ROI is used)
        if (stm32ipl_err_Ok == STM32Ipl_FindCircles(&img, &circles, NULL,
                xStride, yStride, threshold,
                xMargin, yMargin, rMargin,
                rMin, rMax, rStep)) {

            // Cycle through the circles found.
            while (list_size(&circles)) {
                find_circles_list_lnk_data_t circle;

                // Pop the first circle in the list.
                list_pop_front(&circles, &circle);

                // Now the list has one element less.

                // Draw the circle on the image
                STM32Ipl_DrawCircle(&img, circle.p.x, circle.p.y, circle.r, 
                                    TM32IPL_COLOR_GREEN, thickness, fill);
            }

            // Now the list is empty, so it is not necessary to free it.
        }

        // Display the image on the screen.
        STM32Ipl_DrawScreen_DMA2D(&img, 0, 0);

        // Release the image data buffer.
        STM32Ipl_ReleaseData(&img);
    }
}
```
