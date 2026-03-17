
# Table of Contents
1. [Introduction](#1)
2. [Minimal Yaml Configs](#2)
3. [Tensor Override](#3)
4. [Various Operating Modes](#4)
   - [4.1 Operating_mode: inspection](#4-1)
   - [4.2 Operating mode: full_auto](#4-2)

<details open><summary><a href="#1"><b>1. Introduction </b></a></summary><a id="1"></a>
This library contains a collection of scripts that are useful for

- improving mAp of quantized models
- designing mixed precision models
- investigation of quantization issues  

It is based on ONNX quantizer only. To have good support of 4-bits and 16-bits, it is recommended to set 'quantization.target_opset' to 21 and thus ir_version 10.
The advanced quantization services 'inspection', 'full_auto' are only enabled when 'operation_mode' is 'quantization'.
</details>

<details open><summary><a href="#2"><b>2. Minimal Yaml Configs</b></a></summary><a id="2"></a>
The legacy 'quantization' section is mandatory. The description provided in this readme assumes that we use ONNX quantizer and not LiteRT. 
Therefore, 'quantization.quantizer' must be 'Onnx_quantizer'.
If 'quantization.operating_mode' is not defined or is set to 'default', we simply run legacy quantization with the yaml specified parameters.
If some parameters are left undefined, default values are used:

      WeightSymmetric: True
      ActivationSymmetric: False
      CalibMovingAverage: False
      QuantizeBias = True
      SmoothQuant: False
      SmoothQuantAlpha: 0.5
      SmoothQuantFolding: True
      TensorQuantOverrides: None
      op_types_to_quantize = None
      nodes_to_quantize = None
      nodes_to_exclude = None
      calibrate_method = CalibrationMethod.MinMax 
      weight_type = QuantType.QInt8
      activ_type = QuantType.QInt8

Calibration moving average is still controlled in configs.quantization.onnx_extra_options parameters.
'quantization.iterative_quant_parameters' are only taken into account for 'inspection', 'full_auto'.
'iterative_quant_parameters' first defines a parameter called 'inspection_split' used in 'inspection' for defining a subset of the quantization set
on which are performed SNR measurements.
To finish, 'iterative_quant_parameters' also defines 'accuracy_tolerance'. This parameter is only used for mode 'full_auto'.
In object detection, it corresponds to the mAp margin (in percent) we tolerate relatively to full 8 bits performance.
The purpose of this selection will be more detailed in operating modes description in this readme.
</details>

<details open><summary><a href="#3"><b>3. Tensor Override</b></a></summary><a id="3"></a>
It is managed by 'quantization.onnx_extra_options.weights_tensor_override' and 'quantization.onnx_extra_options.activations_tensor_override' parameters.

Examples for setting the override parameters:

    weights_tensor_override: [['efficientnetv2-b0_1/block6a_se_reduce_1/convolution/ReadVariableOp:0', {'quant_type': Int16, 'scale': 0.0025, 'zero_point': -12}],
                              ['efficientnetv2-b0_1/stem_conv_1/convolution/merged_input:0', {'quant_type': Int16, "axis": 0}]
                             ]
    activations_tensor_override: [['efficientnetv2-b0_1/block4a_se_reduce_1/mul_1:0', {'quant_type': Int16}],
                                  ['efficientnetv2-b0_1/block4a_se_expand_1/BiasAdd__79:0', {'quant_type': Int16, 'scale': 0.002, 'zero_point': 0}]
                                 ]
Common remarks:  
'zero_point' must be:
- one integer scalar or a list of one integer value for per-tensor
- a list of several integer values for per-channel

'scale' must be: 
- one float scalar or a list of one floating-point value for per-tensor
- a list of several floating-point values for per-channel

Remarks for the weights:
- When one specifies only 'quant_type' without 'axis': whatever 'quantization.granularity' value, the tensor will be quantized on a per-tensor basis. One 'scale' and one 'zero_point'
can optionally be specified. Since weights are quantized per-tensor, bias will automatically be quantized per-tensor too.
- if 'axis' is specified, then it must be an integer: 0 if the tensor corresponds to the weights of any type of Conv, 1 for a ConvTranspose, 1 too for a Gemm or a MatMul by default.
- when 'axis' is specified (meaning that we intend to quantize the given tensor per-channel), if 'scale' and 'zero_point' are specified too, they must be a list of values whose length corresponds 
to the number of output channels for the considered tensor.

Remarks for activations:
- They are not quantized per-channel. So if 'scale' and 'zero_point' are defined, one value for each is enough.

Potential parameters conflict:
- With current onnx and onnxruntime version we must not set 'onnx_quant_parameters.nodes_to_quantize' and 'onnx_extra_options.weights_tensor_override'. It seems they are mutually exclusive.
</details>

<details open><summary><a href="#4"><b>4. Various Operating Modes</b></a></summary><a id="4"></a>

<ul><details open><summary><a href="#4-1">4.1 Operating_mode: inspection</a></summary><a id="4-1"></a>
This mode is intended to output in stm32ai_main.log the metrics for estimating quantized tensor quality whether they are weights, bias or activation tensors.
It quantizes the model with the parameters specified in the yaml sections 'quantization', including 'onnx_quant_parameters' and 'onnx_extra_options', 
which define among others bit-width and potential tensor overrides.
It has to be noticed that bias is always quantized in INT32 whatever the scheme selected in the config file. So we expect biases are high in quality.
Knowing the tensor quality, one can further investigate potential quantization issues. So it is recommended at the first time to launch this mode without
any tensor override to get the complete view of tensors quantization quality.
Important remark: computing all tensors quality metrics can take time especially if there are many layers and the quantization set is large.
To reduce the latency of this task, it is possible to use the parameter 'inspection_split' in the section 'quantization.iterative_quant_parameters' 
to only consider a split of the quantization set.
</details></ul>

<ul><details open><summary><a href="#4-2">4.2 Operating mode: full_auto</a></summary><a id="4-2"></a>
The goal of this mode is to automatically search for which weight tensors could be quantized in 4 bits or must remain in 8 bits taken into account a mAp
degradation budget of 'quantization.iterative_quant_parameters.accuracy_tolerance' defined in percent with respect to full 8 bits. 
Activations are kept in 8 bits and biases in 32 bits in any case.
It is clear that the better the weight quantizer the higher the number of weights tensors could be moved to 4-bits.
However this algorithm can also be run with the basic 'min-max' quantization algorithm embedded into ONNX.
Several steps are sequentially performed: 
      
      1. Compute float model mAp for reference
      2. Perform a first quantization with parameters in the yaml. This provides a quantized reference mAp typically W8A8
      3. Perform a second quantization with 4 bits for all weights: gives an idea how much it degrades
      4. Rank the weight tensors with respect to a composite score involving some parameters like total number of weigths and number of weights per output channels.
      5. Based on the ranking, search which weights can stay in 4 bits and which one should be on 8 bits

The score computation does not require any training step. It is done statically based on layer parameters.
Among these parameters, we can mention (not restrictive):

      a. layer type (conv2D, point-wise, depthwise, dense...)
      b. kernel size (2x2, 3x3...)
      c. total number of weights
      d. number of weights associated to each output channel

Currently, we just consider c. and d. 
In a few words, we have a 3 steps ranking procedure:

      1. First, rank in decreasing order of each tensor total number of weights
      2. To break a possible tie, rank in ascending order of tensor number of weights per output channel
      3. To break all remaining ties if any, rank in descending order of execution in the network forward pass

So, the smaller the total number of weights for a given tensor, the lower the ranking of this tensor.
To break a possible tie, we use d. considering that if there is a lot of weights per output channel for a given tensor, it is likely this tensor will be
difficult to quantize on low number of bits, with just one 'scale and one 'zero-point'. 

Once the ranking is done, we can start the search which is iterative, by dichotomy. Lower ranking tensors are first candidates for a quantization on 8 bits. 
We report the model with the minimum number of layer weights on 8 bits whose mAp is not worse than 'iterative_quant_parameters.accuracy_tolerance' compared to full 8 bits.

To run 'full_auto', and search for which weights could be quantized just on 4 bits, we need to have: 

      weight_type = Int8
      activ_type = Int8


Although, all the parameters of 'quantization' section are taken into account, we recommend not to define 'onnx_quant_parameters.op_types_to_quantize', 
'onnx_quant_parameters.nodes_to_quantize', 'onnx_quant_parameters.nodes_to_exclude' to give a change to the algorithm to explore more combinations.
Same remark for 'onnx_extra_options.weights_tensor_override' and 'onnx_extra_options.activations_tensor_override'.

On the contrary, it can be beneficial to enable SmoothQuant algorithm, because it helps balancing the quantization difficulty between the weights and the activations.
In our case, since we would like to have most of the weights on 4-bits, we need to move the quantization complexity towards the activations.
This requires a smoothing parameter 'onnx_extra_options.SmoothQuantAlpha' lower than 0.5. A typical setting would then be: 

      SmoothQuant: False
      SmoothQuantAlpha: 0.1
      SmoothQuantFolding: True

</details></ul>

</details>