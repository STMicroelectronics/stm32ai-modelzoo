#  *---------------------------------------------------------------------------------------------*/
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

# Import necessary libraries
import pathlib
import numpy as np
import tensorflow as tf
import os, shutil
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
import onnxruntime
import onnx
from munch import DefaultMunch

# Import utility functions and modules
from common.utils import tf_dataset_to_np_array, torch_dataset_to_np_array
from common.quantization import quantize_onnx
from common.evaluation import model_is_quantized
from common.optimization import model_formatting_ptq_per_tensor, fold_bn
from common.onnx_utils import onnx_model_converter, fold_batch_norm
from common.quantization import define_extra_options, tensors_inspection, onnx_tensor_names, \
                                count_weights, update_bit_width, composite_score_layer_ranking

from common.model_utils.tf_model_loader import load_model_from_path
from common.utils import log_to_file
from object_detection.tf.src.evaluation.onnx_evaluator import ONNXModelEvaluator
from object_detection.tf.src.evaluation.keras_evaluator import KerasModelEvaluator

# Define a class for ONNX Post-Training Quantization (PTQ)
class OnnxPTQQuantizer:
    """
    A class to handle ONNX Post-Training Quantization (PTQ).

    Args:
        cfg (DictConfig): Configuration object for quantization.
        model (object): The model to quantize (TensorFlow or ONNX).
        dataloaders (dict): Dictionary containing datasets for quantization and testing.
        current_extra_options: ONNX quantizer extra options settings
    """
    def __init__(self, cfg: DictConfig = None, model: object = None, 
                 dataloaders: dict = None, current_extra_options: dict = None, q_mode: str = None):
        self.cfg = cfg
        self.model = model
        self.dataloaders = dataloaders
        self.quantization_ds = dataloaders['quantization']
        self.output_dir = HydraConfig.get().runtime.output_dir
        self.export_dir = cfg.quantization.export_dir
        self.quantized_model = None
        self.q_mode = q_mode
        self.extra_options = current_extra_options
        self.q_method = None

    def _prepare_quantization(self):
        """
        Prepares the quantization process by setting options and selecting the quantization method.
        """
        # Define extra options for ONNX quantization
        if self.extra_options is None:
            self.extra_options = define_extra_options(cfg=self.cfg)

        # Determine the quantization method based on the model type
        if isinstance(self.model, tf.keras.Model):
            self.q_method = self._quantize_keras_model
        elif isinstance(self.model, onnxruntime.InferenceSession):
            self.q_method = self._quantize_onnx_model
        else:
            raise ValueError(f"Unsupported model format: {type(self.model)}. ")


    def _quantize_keras_model(self):
        """
        Quantizes a TensorFlow Keras model using ONNX quantization tool and converts it to ONNX format.
        """
        # Optimize the model for per-tensor quantization if specified
        if self.cfg.quantization.granularity == 'per_tensor' and self.cfg.quantization.optimize:
            print("[INFO] : Optimizing the model for improved per_tensor quantization...")
            self.model = model_formatting_ptq_per_tensor(model_origin=self.model)
            models_dir = pathlib.Path(os.path.join(self.output_dir, f"{self.export_dir}/"))
            models_dir.mkdir(exist_ok=True, parents=True)
            model_path = models_dir / "optimized_model.keras"
            self.model.save(model_path)

        print("[INFO] : Starting ONNX PTQ quantization for Keras model.")
        # Convert the dataset to NumPy array
        if self.quantization_ds:
            data, _ = tf_dataset_to_np_array(self.quantization_ds, nchw=True)
        else:
            print(f'[INFO] : Quantizing by using fake dataset...')
            data = None

        # Convert the Keras model to ONNX format
        converted_model_path = os.path.join(self.output_dir, 'converted_model', 'converted_model.onnx')
        input_shape = self.model.inputs[0].shape
        print(f"[INFO] : Converting Keras model to ONNX at {converted_model_path} with input shape {input_shape}")
        onnx_model_converter(input_model_path=self.model.model_path,
                             target_opset=17,
                             output_dir=converted_model_path,
                             static_input_shape=input_shape)

        # Perform ONNX quantization
        print(f"[INFO] : Running ONNX quantization on {converted_model_path}")
        self.quantized_model = quantize_onnx(
            quantization_samples=data,
            model_path=converted_model_path,
            configs=self.cfg,
            extra_options=self.extra_options
        )

    def _quantize_onnx_model(self):
        """
        Quantizes an ONNX model using ONNX quantization tools.
        """
        if self.cfg.quantization.quantizer.lower() == "onnx_quantizer" and self.cfg.quantization.quantization_type == "PTQ":
            print("[INFO] : Starting ONNX PTQ quantization for ONNX model.")
            if self.cfg.model.framework == "tf":
                # Convert the tf dataset to NumPy array as dataloader was based on TF framework
                if self.quantization_ds:
                    data, _ = tf_dataset_to_np_array(self.quantization_ds, nchw=True)
                else:
                    print(f'[INFO] : Quantizing by using fake dataset...')
                    data = None
            elif self.cfg.model.framework == "torch":
                if self.quantization_ds:
                    data, _ = torch_dataset_to_np_array(self.quantization_ds, nchw=False,labels_included=False)
                else:
                    print(f'[INFO] : Quantizing by using fake dataset...')
                    data = None
            # Ensure the ONNX model has a model_path attribute
            if getattr(self.model, 'model_path', None) is None:
                raise ValueError('ONNX InferenceSession must have a model_path attribute for quantization.')
            # Check if the model is already quantized
            if model_is_quantized(self.model.model_path):
                print('[INFO]: The input ONNX model is already quantized!\n\tReturning the same model!')
                self.quantized_model = self.model
            else:
                print(f"[INFO] : Running ONNX quantization on {self.model.model_path}")
                self.quantized_model = quantize_onnx(
                    quantization_samples=data,
                    model_path=self.model.model_path,
                    configs=self.cfg,
                    extra_options=self.extra_options
                )
        else:
            raise TypeError("Quantizer or quantization type not supported. "
                            "Check the `quantization` section of your user_config.yaml file!")
                            

    def _search_weight_bit_width(self, onnx_flp_model, w_tensor_names, axis_list, ref_map, out_model_name):
        """
            Iteratively search for a good mixed precision quantization

            Args:
                onnx_flp_model (InferenceSession): onnx float model
                w_tensor_names: list of weight tensor for the considered model, ordered in decreasing metric order
                axis_list: 'axis' parameter for every weight tensor
                ref_map (float): float number, reference mAp - accuracy_tolerance is the minimum mAp
                accepted as output of this algo
                out_model_name (str): root name of output mixed precision model

            Returns:

            """

        if self.cfg.quantization.iterative_quant_parameters:
            tolerance = self.cfg.quantization.iterative_quant_parameters.accuracy_tolerance
        else: tolerance = 1.0
        tolerance = tolerance if tolerance is not None else 1.0

        updated_bit_width_w = update_bit_width(tensor_type=self.cfg.quantization.onnx_quant_parameters.weightType, order=1, direction='up')

        total_nb_weights_tensors = len(w_tensor_names)
        step_values_list = [np.round(total_nb_weights_tensors / pow(2, i+1)) for i in range(int(np.round(np.log2(total_nb_weights_tensors))))]
        step_values_list = [int(i) for i in step_values_list]

        # sum of the steps should be equal to total_nb_weights_tensors to cover all the weights tensor list
        while np.sum(step_values_list) < total_nb_weights_tensors:
            step_values_list.append(1)

        n_w_tensors = 0
        map_quant = 0
        n_weights_match_value = total_nb_weights_tensors

        for idx, step in enumerate(step_values_list):
            if map_quant >= (ref_map - tolerance) and idx !=0:
                new_path_suffix = '_w4_{}%_w8_{}%_a8_100%_map_{}.onnx'.format(w4_ratio, w8_ratio, map_quant)
                out_file_name = out_model_name + new_path_suffix
                mixed_qt_model_path = os.path.join(self.output_dir, 'quantized_models', out_file_name)
                shutil.copy(quantized_model.model_path, mixed_qt_model_path)

                n_weights_match_value = n_w_tensors
                n_w_tensors -= step
            else:
                n_w_tensors += step

            selected_w_names = w_tensor_names[-n_w_tensors:]
            selected_axis = axis_list[-n_w_tensors:]
            current_extra_options = define_extra_options(cfg=self.cfg, list_weights_tensors=selected_w_names,
                                                        axis_list=selected_axis, bit_width_w=updated_bit_width_w)
            current_extra_options = DefaultMunch(None, current_extra_options)

            # new quantization, with parameters updated bit-widths for the current iteration
            log_to_file(self.output_dir, f"\nNew quantization with updated bit-widths for {n_w_tensors} / "
                                    f"{total_nb_weights_tensors} selected weights in {updated_bit_width_w}: ")
            for t in selected_w_names:
                log_to_file(self.output_dir, f"{t}")
            log_to_file(self.output_dir, f"Quantization granularity: same as on first trial.")
            log_to_file(self.output_dir, f"Quantization parameters: same as on first trial except the bit-widths.")
            if self.cfg.quantization.onnx_extra_options:
                log_to_file(self.output_dir, f"Quantization extra options: {self.cfg.quantization.onnx_extra_options}")

            quantizer = OnnxPTQQuantizer(cfg=self.cfg, model=onnx_flp_model, dataloaders=self.dataloaders, 
                                        current_extra_options=current_extra_options, q_mode='default')
            quantized_model = quantizer.quantize()

            # Estimate how many weights are in 4 bits and 8 bits
            w_4bits_count, w_8bits_count, total_n_weights = count_weights(onnx_model_path_quant=quantized_model.model_path,
                                                                        w_tensor_name=w_tensor_names)
            w8_ratio = np.round(w_8bits_count/total_n_weights * 100.0, 2)
            w4_ratio = np.round(100.0 - w8_ratio, 2)
            log_to_file(self.output_dir, 
                        f"In this quantization attempt we have {w_8bits_count} weights in {updated_bit_width_w}"
                        f" over a total of {total_n_weights} weights so a ratio of {w8_ratio} %")

            # Evaluation of new quantized model
            print(f"\nEvaluation of the quantized model for {n_w_tensors} / {total_nb_weights_tensors} weights on "
                f"{updated_bit_width_w}...")
            # mAp is the only metric considered so far
            evaluator = ONNXModelEvaluator(cfg=self.cfg, model=quantized_model, dataloaders=self.dataloaders)
            metrics = evaluator.evaluate()
            map_quant = np.round(metrics[0]['ap'] * 100.0, 2)

        # latest model quantized. Could be the full 8 bit weights if not possible to find better
        if map_quant >= ref_map - tolerance or n_weights_match_value==total_nb_weights_tensors:
            new_path_suffix = '_w4_{}%_w8_{}%_a8_100%_map_{}.onnx'.format(w4_ratio, w8_ratio, map_quant)
            out_file_name = out_model_name + new_path_suffix
            mixed_qt_model_path = os.path.join(self.output_dir, 'quantized_models', out_file_name)
            shutil.copy(quantized_model.model_path, mixed_qt_model_path)

    def _full_auto(self):
        """
            Processing:
                1. Compute float model mAp for reference
                2. Perform a first quantization with parameters in the yaml. This provides a quantized reference mAp
                    typically W8A8
                3. Perform a second quantization with 4 bits for all weights: gives an idea how much it degrades
                4. Compute score for each weight tensor on the float model. Rank them in descending order
                5. Based on the ranking, search which weights can stay in 4 bits and which one should be on 8 bits

            Inputs:

            Returns:
                    log quantization inspection results
        """
        # root model name
        input_model_name = getattr(self.model, 'model_path')
        extension = pathlib.Path(input_model_name).suffix  #.keras or .onnx
        input_model_name = os.path.split(input_model_name)[1]
        root_model_name = input_model_name.split(extension)[0]

        # name for saving output files
        common_suffix = '_qdq'

        if self.cfg.quantization.onnx_extra_options:
            if self.cfg.quantization.onnx_extra_options.SmoothQuant and self.cfg.quantization.onnx_extra_options.SmoothQuantAlpha:
                common_suffix += '_squant' + str(self.cfg.quantization.onnx_extra_options.SmoothQuantAlpha)

        full_8bits_filename = root_model_name + common_suffix + '.onnx'
        path_full8bits_model = os.path.join(self.output_dir, 'quantized_models', full_8bits_filename)

        # Before evaluation, batch normalizations are folded.
        # This will be necessary in case in later releases we introduce more advanced quantizers.
        # Then, we determine the evaluation method based on the model type and evaluate
        if isinstance(self.model, tf.keras.Model):
            folded_model = fold_bn(self.model)
            folded_model_path = os.path.join(self.output_dir, root_model_name + '_folded' + extension)
            folded_model.save(folded_model_path)
            self.model = folded_model
            setattr(self.model, 'model_path', folded_model_path)
            evaluator = KerasModelEvaluator(cfg=self.cfg,
                                            model=self.model, 
                                            dataloaders=self.dataloaders)
        elif isinstance(self.model, onnxruntime.InferenceSession):
            model_flp = onnx.load(getattr(self.model, 'model_path'))
            folded_model = fold_batch_norm(model_flp)
            folded_model_path = os.path.join(self.output_dir, root_model_name + '_folded' + extension)
            onnx.save(folded_model, folded_model_path)
            self.model = onnxruntime.InferenceSession(folded_model.SerializeToString())
            setattr(self.model, 'model_path', folded_model_path)
            evaluator = ONNXModelEvaluator(cfg=self.cfg,
                                            model=self.model,
                                            dataloaders=self.dataloaders)
        else:
            raise ValueError(f"Unsupported model format: {type(self.model)}. ")

        # From now on we only work with BN folded models
        # Evaluation float model, mAp is the only metric considered so far
        metrics_float = evaluator.evaluate()
        map_float = metrics_float[0]['ap']

        # 1st quantization, with parameters specified in config yaml
        log_to_file(self.output_dir, f"\nBaseline quantization with parameters specified in config file:")
        if self.cfg.quantization.granularity:
            log_to_file(self.output_dir, f"Quantization granularity: {self.cfg.quantization.granularity}")
        else:
            log_to_file(self.output_dir, f"Quantization granularity: per-channel")
        if self.cfg.quantization.onnx_quant_parameters:
            log_to_file(self.output_dir, f"Quantization parameters: {self.cfg.quantization.onnx_quant_parameters}")
        if self.cfg.quantization.onnx_extra_options:
            log_to_file(self.output_dir, f"Quantization extra options: {self.cfg.quantization.onnx_extra_options}")
        self.q_method()

        # Evaluation of 1st baseline quantized model
        print("Evaluation of the baseline quantized model with config file parameters.......")
        # mAp is the only metric considered so far
        evaluator = ONNXModelEvaluator(cfg=self.cfg,
                                        model=self.quantized_model,
                                        dataloaders=self.dataloaders)
        metrics_ref_quant = evaluator.evaluate()
        # we need metrics in percentage for further usage
        map_ref_quant = np.round(metrics_ref_quant[0]['ap'] * 100.0, 2)

        # For validation, we save full 8 bits model
        shutil.copy(getattr(self.quantized_model, 'model_path'), path_full8bits_model)

        # 2nd quantization, with all weights in 4 bits, all the others parameters as specified in config yaml
        log_to_file(self.output_dir, f"\nBaseline quantization with parameters specified in config file, except all weights "
                    f"in 4 bits:")
        if self.cfg.quantization.onnx_quant_parameters is None:
            self.cfg.quantization.onnx_quant_parameters = DefaultMunch(None, {'weightType': 'Int4'})
        elif self.cfg.quantization.onnx_quant_parameters.weightType:
            self.cfg.quantization.onnx_quant_parameters.weightType = 'Int4'

        if self.cfg.quantization.granularity:
            log_to_file(self.output_dir, f"Quantization granularity: {self.cfg.quantization.granularity}")
        else:
            log_to_file(self.output_dir, f"Quantization granularity: per-channel")
        if self.cfg.quantization.onnx_quant_parameters:
            log_to_file(self.output_dir, f"Quantization parameters: {self.cfg.quantization.onnx_quant_parameters}")
        if self.cfg.quantization.onnx_extra_options:
            log_to_file(self.output_dir, f"Quantization extra options: {self.cfg.quantization.onnx_extra_options}")
        # at this step either the model was in ONNX in the cfg file or it was converted to ONNX
        self.q_method()

        # Evaluation of all weights in 4 bits quantized model
        print("Evaluation of all weights in 4 bits quantized model..........")
        evaluator = ONNXModelEvaluator(cfg=self.cfg,
                                        model=self.quantized_model,
                                        dataloaders=self.dataloaders)
        # mAp is the only metric considered so far
        metrics_base_quant = evaluator.evaluate()
        map_base_quant = metrics_base_quant[0]['ap']

        # During quantization, if original model was .keras it was automatically converted to ONNX and upgraded to opset
        # target if needed and saved with following name.
        if extension == '.keras':
            onnx_flp_model_path = os.path.join(self.output_dir, f"converted_model_opset{self.cfg.quantization.target_opset}.onnx")
        else:
            onnx_flp_model_path = getattr(self.model, 'model_path')
        # From now on we only work with ONNX models in which BN was folded
        extension = '.onnx'
        onnx_flp_model = onnx.load(onnx_flp_model_path)

        # ONNX layer ranking
        layer_rank = composite_score_layer_ranking(onnx_flp_model, extension)

        log_to_file(self.output_dir, f"\nModel layers scores (layer name, layer type, number of weights, number of weights "
                                f"per output scale):")
        for layer in layer_rank:
            log_to_file(self.output_dir, f"{layer[0]}: {layer[1]:.4f}, {layer[2]:.4f}, {layer[3]:.4f}")

        onnx_w_tensor_names, axis_list = onnx_tensor_names(onnx_model_path_flp=onnx_flp_model_path,
                                                        onnx_model_path_quant=self.quantized_model.model_path,
                                                        layer_rank=layer_rank)

        # Need an InferenceSession object to enter search function
        onnx_flp_model = load_model_from_path(self.cfg, onnx_flp_model_path)
        self._search_weight_bit_width(onnx_flp_model=onnx_flp_model, w_tensor_names=onnx_w_tensor_names,
                                        axis_list=axis_list, ref_map=map_ref_quant,
                                        out_model_name=root_model_name + common_suffix)
        print('full_auto execution completed')

    def _inspection(self):
        """
            Generate inspection metrics for quantization.
            1. Quantize with parameters specified in yaml
            2. Generate weights and activation tensors inspection metrics

            Inputs:

            Returns:
                    log quantization inspection results
        """

        # 1st quantization, with parameters specified in config yaml
        log_to_file(self.output_dir, f"\nBaseline quantization with parameters specified in config file:")
        if self.cfg.quantization.granularity:
            log_to_file(self.output_dir, f"Quantization granularity: {self.cfg.quantization.granularity}")
        else:
            log_to_file(self.output_dir, f"Quantization granularity: per-channel")
        if self.cfg.quantization.onnx_quant_parameters:
            log_to_file(self.output_dir, f"Quantization parameters: {self.cfg.quantization.onnx_quant_parameters}")
        if self.cfg.quantization.onnx_extra_options:
            log_to_file(self.output_dir, f"Quantization extra options: {self.cfg.quantization.onnx_extra_options}")
        self.q_method()

        # During quantization, onnx model was automatically converted to ONNX and upgraded to target opset if needed
        if self.cfg.model.model_path.endswith(".onnx"):
            onnx_flp_model_path = self.cfg.model.model_path
        else:
            onnx_flp_model_path = os.path.join(self.output_dir, f"converted_model_opset{self.cfg.quantization.target_opset}.onnx")

        if self.cfg.quantization.iterative_quant_parameters:
            inspection_split = float(self.cfg.quantization.iterative_quant_parameters.inspection_split)
        else:
            inspection_split = None
        inspection_split = inspection_split if inspection_split is not None else 1.0
        inspect_ds = self.quantization_ds.take(int(len(self.quantization_ds) * inspection_split))

        # Inspect tensors
        log_to_file(self.output_dir, f"\nBaseline quantized model (config file parameters), SNR analysis (dB):")
        list_worst_weights_tensors, list_worst_activations_tensors, axis_per_channel_weights = (
            tensors_inspection(self.cfg, float_model_path=onnx_flp_model_path, 
                                quantized_model_path=self.quantized_model.model_path,
                                insp_set=inspect_ds, threshold_weights=None, threshold_activation=None, 
                                output_dir=self.output_dir))

    def _run_quantization(self):
        """
        Executes the quantization process based on the selected operating mode.
        """
        if self.q_mode is None:
            self.q_mode = self.cfg.quantization.operating_mode

        if self.q_mode is None or self.q_mode == 'default':
            self.q_method()
        elif self.q_mode == 'inspection':
            self._inspection()
        elif self.q_mode == 'full_auto':
            self._full_auto()
        else:
            raise ValueError(f"Invalid quantization operating mode: {self.q_mode}")

    def quantize(self):
        """
        Executes the full quantization process.

        Returns:
            object: The quantized model (ONNX or TensorFlow).
        """
        print("[INFO] : Quantizing the model ... This might take few minutes ...")
        self._prepare_quantization()    # Prepare the quantization process
        self._run_quantization()        # Run the quantization process
        print('[INFO] : Quantization complete.')
        return self.quantized_model     # Return the quantized model


