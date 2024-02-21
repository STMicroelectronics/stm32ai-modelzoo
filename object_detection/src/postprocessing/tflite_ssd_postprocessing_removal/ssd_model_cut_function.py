# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


import tensorflow as tf
import os
import shutil

def ssd_post_processing_removal(path_to_model,TFLite_Detection_PostProcess_id,anchors_path):

	# execution of the patch_tflite.py script and creation of the .c & .h files

	command = 'python postprocessing/tflite_ssd_postprocessing_removal/patch_tflite.py '+path_to_model+' --cut '+str(TFLite_Detection_PostProcess_id)+' -e '+str(TFLite_Detection_PostProcess_id)

	#print(command)

	outp = os.system(command)

	if outp:
		print('ERROR IN TFLITE CUT : this model post-process format is not supported')

		path_cut_model  = None
		path_c_file     = None
		path_h_file     = None

	else:
		cut_model_name = os.path.split(path_to_model)[-1][:-7]+'_mod.tflite'

		path_cut_model  = 'generate/' + cut_model_name
		path_c_file     = 'generate/network_pp_nms_params.c'
		path_h_file     = 'generate/network_pp_nms_params.h'
		path_anchors    = 'generate/anchors.h'

	shutil.copyfile(path_anchors,anchors_path)


	# go into the .h file to search for the post-process parameters

	file = open(path_h_file)

	s = file.read()

	list_str_parameters  = list(filter(lambda x : '#define AI' in x ,s.split('\n')))

	list_dict_parameters = list(map(lambda x : {x.split(' ')[-3] : x.split(' ')[-1][1:-1]}, list_str_parameters))

	parameters_dict = {}

	for d in list_dict_parameters :
		parameters_dict = {**parameters_dict,**d}

	XY = float(parameters_dict['AI_NETWORK_X_SCALE'])
	WH = float(parameters_dict['AI_NETWORK_W_SCALE'])

	return path_cut_model, XY, WH

