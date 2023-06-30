/**
 ******************************************************************************
 * @file   stm32ipl_object_det.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - object detection module
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
 * Viola-Jones object detector implementation.
 * Based on the work of Francesco Comaschi (f.comaschi@tue.nl)
 *
 ******************************************************************************
 */

#include "stm32ipl.h"
#include "stm32ipl_imlib_int.h"

#ifdef STM32IPL_ENABLE_OBJECT_DETECTION

#ifdef __cplusplus
extern "C" {
#endif

#ifdef STM32IPL_ENABLE_FRONTAL_FACE_CASCADE
/**
 * @brief Loads the frontal face cascade.
 * @param cascade 	Pointer to the cascade; if it is not valid, an error is returned.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_LoadFaceCascade(cascade_t *cascade)
{
	STM32IPL_CHECK_VALID_PTR_ARG(cascade)

	imlib_load_cascade(cascade, "frontalface");
	return stm32ipl_err_Ok;
}
#endif /* STM32IPL_ENABLE_FRONTAL_FACE_CASCADE */

#ifdef STM32IPL_ENABLE_EYE_CASCADE
/**
 * @brief Loads the eye cascade.
 * @param cascade 	Pointer to the cascade; if it is not valid, an error is returned.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_LoadEyeCascade(cascade_t *cascade)
{
	STM32IPL_CHECK_VALID_PTR_ARG(cascade)

	imlib_load_cascade(cascade, "eye");
	return stm32ipl_err_Ok;
}
#endif /* STM32IPL_ENABLE_EYE_CASCADE */

/**
 * @brief Detects objects, described by the given cascade. The detected object are stored in an array_t
 * structure containing the bounding boxes (rectangle_t), one for each object detected; the caller is
 * responsible to release the array. The supported formats are Grayscale, RGB565, RGB888.
 * @param img			Image; if it is not valid, an error is returned.
 * @param out			Pointer to pointer to the array structure that will contain the detected objects.
 * It must point to a valid, but empty structure. It MUST be released by the caller.
 * @param roi			Optional region of interest of the source image where the functions operates;
 * when defined, it must be contained in the source image and have positive dimensions, otherwise
 * an error is returned; when not defined, the whole image is considered.
 * @param cascade		Pointer to a cascade (must be already loaded with specific loading function).
 * @param scaleFactor	Tune the capability to detect objects at different scale (must be > 1.0f).
 * @param threshold		Tune the detection rate against the false positive rate (0.0f - 1.0f).
 * @return				stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_DetectObject(const image_t *img, array_t **out, const rectangle_t *roi, cascade_t *cascade,
		float scaleFactor, float threshold)
{
	rectangle_t realRoi;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, (stm32ipl_if_grayscale | stm32ipl_if_rgb565 | stm32ipl_if_rgb888))
	STM32IPL_CHECK_VALID_PTR_ARG(cascade)
	STM32IPL_GET_REAL_ROI(img, roi, &realRoi)

	cascade->scale_factor = scaleFactor;
	cascade->threshold = threshold;

	*out = imlib_detect_objects((image_t*)img, cascade, &realRoi);

	return stm32ipl_err_Ok;
}

#ifdef __cplusplus
}
#endif

#endif /* STM32IPL_ENABLE_OBJECT_DETECTION */
