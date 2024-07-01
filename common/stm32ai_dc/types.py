# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from datetime import datetime
from enum import Enum
import typing
from typing import Optional

from marshmallow import Schema, fields, post_dump

LOGGER_NAME = "STM32AI_API"


class CliParameterType(str, Enum):
    """
    Define the types that can be used to indicate the type of the model
    """
    KERAS = "keras"
    TFLITE = "tflite"
    ONNX = "onnx"


class CliParameterCompression(str, Enum):
    """
    Define the compression values that can be used to compress a model
    """
    NONE = "none"
    LOSSLESS = "lossless"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CliParameterVerbosity(int, Enum):
    """
    Define the log verbosity of the command
    """
    NONE = 0
    NORMAL = 1
    HIGH = 2

class MpuEngine(str, Enum):
    """
    Define the log verbosity of the command
    """
    CPU = 'cpu'
    """
        Benchmark will run on CPU only
    """
    HW_ACCELERATOR = 'hw_accelerator'
    """
        Benchmark will run on Hardware Accelerator (NPU/GPU) if available. 

        Will fallback to CPU if needed
    """

class BackendVersionType(str, Enum):
    """
    Define the backend service associated to a version
    """
    STM32 = "stm32"
    STELLAR_E = "stellar-e"
    STM32MPU = "stm32mpu"
    ISPU = "ispu"

class CliParameterOptimization(str, Enum):
    """
    Define the optimization to be used with the CLI
    """
    BALANCED = "balanced"
    TIME = "time"
    RAM = "ram"


class CliLibrarySerie(str, Enum):
    STM32H7 = "STM32H7"
    STM32F7 = "STM32F7"
    STM32F4 = "STM32F4"
    STM32L4 = "STM32L4"
    STM32G4 = "STM32G4"
    STM32F3 = "STM32F3"
    STM32U5 = "STM32U5"
    STM32L5 = "STM32L5"
    STM32F0 = "STM32F0"
    STM32L0 = "STM32L0"
    STM32G0 = "STM32G0"
    STM32C0 = "STM32C0"
    STM32WL = "STM32WL"
    STM32MP1 = "STM32MP1"


class CliLibraryIde(str, Enum):
    GCC = "gcc"
    IAR = "iar"
    KEIL = "keil"


class AtonParameters(typing.NamedTuple):

    name: Optional[str] = None

    help: Optional[bool] = None
    """
     Print this help message and exit 
    """
    version: Optional[bool] = None
    """
	 Display program version information and exit 
    """
    onnx_input: Optional[str] = None
    """
	 Input ONNX Filename 
	"""
    onnx_dir_prefix: Optional[str] = None
    """
	 Ouput Prefix used to specify output Directory for generated files 
	"""
    onnx_output: Optional[str] = None
    """
	 Output ONNX Filename 
	"""
    """
	 Converts Input ONNX file to most current opset if needed 
	"""
    convert: Optional[bool] = None
    """
	 Orlando Output Filename 
	"""
    orlando_file: Optional[str] = None
    """
	 Network Name (used as post-fix for NN interface function names in generated Orlando output `.c` file) 
	"""
    network_name: Optional[str] = None
    """
	 Do not emit memory pools initialization files 
	"""
    no_emit_pools_init: Optional[bool] = None
    """
	 Defines a symbol to be used for undefined graph input shapes dimensions (can be used multiple times), format is name:x where name is a graph input name and x is a shape dimension index (0 leftmost position) if x='b' it sets the memory batch format e.g. -D input:0=2 sets first shape dim to 2 
	"""
    def_sym: Optional[str] = None
    """
	  Requests ONNX memory format (CHW) for all graph outputs (can be overriden for individual outputs with --def-sym,-D option), default is HWC 
	"""
    onnx_out_format: Optional[str] = None
    """
	 Attemps to continue compilation on ONNX file import errors 
	"""
    continue_on_errors: Optional[bool] = None
    """
	 Emits in generated code a function to retrieve all internal graph edges buffer info structures (useful to debug/inspect buffers at epoch completion with epoch hook) 
	"""
    all_buffers_info: Optional[bool] = None
    """
	   Disable the software fallback on Embednets libraries 
	"""
    disable_sw_fallback: Optional[bool] = None
    """
	   Enable the scratch buffers generation for MVEI arm Cortex M55 core. 
	"""
    mvei: Optional[bool] = None
    """
	   Runs only the ONNX phases 
	"""
    onnx_only: Optional[bool] = None
    """
	   Save all temporary/Output files 
	"""
    save_all: Optional[bool] = None
    """
	   verbosity on 
	"""
    verbose: Optional[bool] = None

    """
	 Hidden reserved options: 
	"""
    """
	 Displays full help message (including hidden options) 
	"""
    help_full: Optional[bool] = None
    """
	 Enable the emission of dot graph after each lowering iteration 
	"""
    d_lower_iter_graph: Optional[bool] = None
    """
	 Do not emit tool version info in generated files 
	"""
    skip_version_generation: Optional[bool] = None
    """
	 Avoid configuration of Decomp  CodeBooks from the bus 
	"""
    disable_decomp_bus: Optional[bool] = None
    """
	 Enable the software fallback on Embednets libraries DEPRECATED: please use '--native-float' instead 
	"""
    sw_fallback: Optional[bool] = None
    """
	 Do not generate code which executes HW & SW nodes belonging to same epoch in parallel 
	"""
    no_hw_sw_parallelism: Optional[bool] = None
    """
	 Disable Optimizations specific for HW mapping. Suggested only in case of Hybrid HW/SW mapping or Pure SW mapping. 
	"""
    disable_orlando_opt: Optional[bool] = None
    """
	 Simulate the qmn format for hybrid tests without quantization files. (it forces also the sw-mapped nodes input to floating point when needed) DEPRECATED: please use '--fake-Qmn' instead 
	"""
    simulate_qmn_format: Optional[bool] = None
    """
	 Do not perform deadlock removal pass (potentially unsafe as it can generate a schedule with deadlocks) 
	"""
    dont_remove_deadlocks: Optional[bool] = None
    """
	 Automagically converts all scale/offset quantized tensors to QMN attempting to choose a fixed point representation that fits the original range (final accuracy might be affected) 
	"""
    convert_scaleoffset_to_qmn: Optional[bool] = None
    """
	 Enable generation of NPU/MCU cache maintenance code 
	"""
    cache_maintenance: Optional[bool] = None
    """
	 Enables alternate scheduler node priority option 
	"""
    Oalt_sched: Optional[bool] = None
    """
	 KMeans vector quantizer algorithm maximum no of iterations 
	"""
    vq_max_iter: Optional[int] = None
    """
	 Force usage of cache for all cachable regions 
	"""
    force_cache_use: Optional[bool] = None
    """
	 Developers only do not use 
	"""
    hidden_param: Optional[int] = None
    """
	 Enable automatic use of adjacent memory pool with the same properties for large buffer allocation and only use that in lieu of all pool composing it 
	"""
    enable_virtual_mem_pools_only: Optional[bool] = None
    """
	 Enable Experimental support of HW lowering 
	"""
    experimental_hw_lowering: Optional[bool] = None
    """
	 Emit custom helpers and getters used by validation scripts 
	"""
    emit_validation_info: Optional[bool] = None

    """
	 Target Description options: 
	"""
    """
	 Specifies target machine to use: a predefined one from the config dir or a file name with '.mdesc' extension 
	"""
    load_mdesc_file: Optional[str] = None
    load_mdesc: Optional[str] = None
    target: Optional[str] = None
    """
	   Dumps machine description in use to file name with '.mdesc' extension ('-' means cout) 
	"""
    save_mdesc_file: Optional[str] = None
    """
	   Specifies file name with '.mpool' extension with the platform memory pool definition to use 
	"""
    load_mpool_file: Optional[str] = None
    load_mpool: Optional[str] = None
    """
	   Dumps memory pool configuration in use to file name with '.mpool' extension ('-' means cout) 
	"""
    save_mpool_file: Optional[str] = None
    """
	   Sets maximum amount of internal memory in KB for buffer allocations (temp option) has no effect with verif/stice4/zc706 pools options 
	"""
    max_ram_size: Optional[int] = None
    """
	   Enable automatic use of adjacent memory pool with the same properties for large buffer allocation 
	"""
    enable_virtual_mem_pools: Optional[bool] = None

    """
	 Quantization options: 
	"""
    """
	 Consider all Floats without quantization info as Fake integers with precision derived by options --w-bits and --f-bits 
	"""
    fake_Qmn: Optional[bool] = None
    """
	   Consider all Floats without quantization info as native floats 
	"""
    native_float: Optional[bool] = None
    """
	   Sets number of bits assumed to be used for all network weights (temporary option) 
	"""
    w_bits: Optional[int] = None
    """
	   Sets number of bits assumed to be used for all activations (temporary option) 
	"""
    f_bits: Optional[int] = None
    """
	   CSV file name with tensor Qmn and scaling infor (as produced by external quantization script), for tensors named in the file it will overwrite w-bits and f-bits DEPRECATED: please use '--json-quant-file' instead 
	"""
    quant_file: Optional[str] = None
    """
	   Quantization File 
	"""
    json_quant_file: Optional[str] = None
    """
	   Quantization File 
	"""
    save_json_quant_file: Optional[str] = None

    """
	 Optimization options: 
	"""
    """
	 Optimization level one of [0-3] (speed) 
	"""
    optimization: Optional[int] = None

    """
	   Attempts to reduce memory buffers size 
	"""
    Os: Optional[bool] = None
    M: Optional[bool] = None
    """
	   Enables all experimental optimizations 
	"""
    Ox: Optional[bool] = None
    x: Optional[bool] = None
    """
	   Enables experimental optimization to split convolutions channel-wise 
	"""
    Oconv_split_cw: Optional[bool] = None
    """
	   Enables experimental optimization to split convolutions Kernel-wise 
	"""
    Oconv_split_kw: Optional[bool] = None
    """
	   Enables experimental optimization to split convolutions stripe-wise for 1xN kernels 
	"""
    Oconv_split_stripe: Optional[bool] = None
    """
	   Enables experimental optimization to split convolutions stripe-wise for any kernel size 
	"""
    Oconv_split_stripe_full: Optional[bool] = None
    """
	   Specfies file name ONNX optimization passes one per line 
	"""
    onnx_optimizations_file: Optional[str] = None
    """
	   Comma separated list of ONNX optimizations to be executed 
	"""
    onnx_optimizations: Optional[str] = None
    """
	   Comma separated list of extra ONNX optimizations to be added to default passes 
	"""
    onnx_extra_opts: Optional[str] = None
    """
	   Omits named option from the final list of ONNX optimizations 
	"""
    onnx_omit_opt: Optional[str] = None
    """
	   Rounds of ONNX optimizations to be executed 
	"""
    optimization_rounds: Optional[int] = None
    """
	   Do not reuse buffers allocated for inputs for anything else (initialiers are always preserved) 
	"""
    Opreserve_inputs: Optional[int] = None
    """
	   Maximum number of Conv Acc used in a pipelined configuration (default is 0 meaning unlimited) 
	"""
    Omax_ca_pipe: Optional[int] = None
    """
	   Attempts to clone DMA for compatible input ports iterations (experimental) 
	"""
    Oclone_dma: Optional[bool] = None
    """
	   Reshuffles DMAs in each epoch attempting to load balance memory ports traffic (experimental) 
	"""
    Oshuffle_dma: Optional[bool] = None
    """
	   If a cache is enable on the memory pools enables heuristic annotation for it, implies --enable-bus-signals (experimental) 
	"""
    Ocache_opt: Optional[bool] = None

    """
	 Additional info request options: 
	"""
    """
	 DOT Output Filename (default vertical layout) 
	"""
    dot_file: Optional[str] = None
    """
	   Selects horizontal orientation for dot output 
	"""
    doth: Optional[bool] = None
    """
	   Set maximum length of node/edge labels names 
	"""
    dot_maxlabel: Optional[int] = None
    """
	   CSV Output Filename for memory traffic statistics 
	"""
    csv_file: Optional[str] = None
    """
	   gnuplot memory bandwidth chart output Filenames prefix (.gnuplot and .data will be appended to it) for memory traffic statistics 
	"""
    gnuplot_mem_file: Optional[str] = None
    """
	   gnuplot buffer graph per memory pool output Filenames prefix (.gnuplot appended to it) for buffer allocation across schedule 
	"""
    gnuplot_buf_file: Optional[str] = None
    """
	   Sets multiple plots to be generated int the same gnuplot file (if relevant) 
	"""
    gnuplot_multi: Optional[bool] = None
    """
	   Initializers histogram Output Filename Prefix (added suffixes .c, .gplot, .gplot.data) 
	"""
    initializers_infofile: Optional[str] = None
    """
	   Dump num ops info 
	"""
    num_ops_info: Optional[bool] = None
    """
	   Enable the mapping recap during the Code Generation phase 
	"""
    mapping_recap: Optional[bool] = None
    """
	   Skip Parameters nodes when emitting DOT file 
	"""
    dot_skip_params: Optional[bool] = None

    """
	 Debug options: 
	"""
    """
	 debug onnx proto level 
	"""
    d_onnx_p: Optional[int] = None
    """
	   debug onnx graph level 
	"""
    d_onnx_g: Optional[int] = None
    """
	   debug Quantization info 
	"""
    d_qinfo: Optional[int] = None
    """
	   debug CFG level 
	"""
    d_CFG: Optional[int] = None
    """
	   debug live range level 
	"""
    d_lv: Optional[int] = None
    """
	   debug scheduler level 
	"""
    d_sched: Optional[int] = None
    """
	   debug canonic form level 
	"""
    d_canonic: Optional[int] = None
    """
	   debug lowering level 
	"""
    d_lower: Optional[int] = None
    """
	   debug orlando dump level 
	"""
    d_o_dump: Optional[int] = None
    """
	   debug buffer alloc level 
	"""
    d_b_alloc: Optional[int] = None
    """
	   debug onnx optimize level 
	"""
    d_onnx_o: Optional[int] = None
    """
	   debug machine description level 
	"""
    d_mach: Optional[int] = None
    """
	   debug graph inference pass level 
	"""
    d_ginf: Optional[int] = None
    """
	   debug epoch deadlock analisys and removal 
	"""
    d_dead: Optional[int] = None
    """
	   debug epoch post optmizer 
	"""
    d_post: Optional[int] = None
    """
	   debug epoch creation 
	"""
    d_epoch: Optional[int] = None
    """
	   debug performance statistics dump 
	"""
    d_stat: Optional[int] = None
    """
	   debug KMeans vector quantizer algorithm 
	"""
    d_vq: Optional[int] = None
    """
	   debug dma configuration pass level 
	"""
    d_dma: Optional[int] = None
    """
	   debug emitted cache coherency operations 
	"""
    d_cache_ops: Optional[bool] = None
    """
	   Promotes all nodes outputs to be graph outputs (for debug only, it has a large impact on memory size and performance) 
	"""
    d_onnx_all_temps: Optional[bool] = None
    """
	   Promotes only named edges named in a comma separated list to be graph outputs (for debug only, it has a large impact on memory size and performance) 
	"""
    d_onnx_temps: Optional[str] = None

    """
	 Auto optimizer options: 
	"""
    """
	 Enables iterative automatic optimization options selection for all options supported (increases compilation time) 
	"""
    Oauto: Optional[bool] = None
    """
	 Enables iterative automatic optimization selection for scheduler (--Oalt-sched) 
	"""
    Oauto_sched: Optional[bool] = None
    """
	 Enables iterative automatic optimization selection for experimental (-x, --Ox) 
	"""
    Oauto_x: Optional[bool] = None
    """
	 Enables iterative automatic optimization selection for pipelining (--Omax-ca-pipe) 
	"""
    Oauto_pipe: Optional[bool] = None
    """
	 Enables iterative automatic optimization selection for optimization level (-O, --optimization) 
	"""
    Oauto_O: Optional[bool] = None
    """
	 Debug level for automatic optimization mode (if > 1 it will also generate intermediate .dot outputs for all options tried) 
	"""
    d_auto: Optional[int] = None
    """
	 Sets threshold [0.0-1.0] for automatic optimization mode 0 -> only cycles are considered 1 -> only total memory is considered 
	"""
    Oauto_th: Optional[bool] = None
    """
	 Sets % threshold [0.0-1.0] for convolutional layers splitting heuristic, layers which contribute to less than the threshold to the cumulative no of ops are not transformed (0.0 all conv are considered, 1.0 none are considered) 
	"""
    Oconv_split_th: Optional[bool] = None


class AtonParametersSchema(Schema):
    SKIP_VALUES = set([None])

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items() if value not in self.SKIP_VALUES
        }

    name = fields.Bool(required=False)

    help = fields.Bool(required=False)
    """
     Print this help message and exit 
    """
    version = fields.Bool(required=False)
    """
	 Display program version information and exit 
    """
    onnx_input = fields.Str(required=False, data_key='onnx_input')
    """
	 Input ONNX Filename 
	"""
    onnx_dir_prefix = fields.Str(required=False, data_key='onnx-dir-prefix')
    """
	 Ouput Prefix used to specify output Directory for generated files 
	"""
    onnx_output = fields.Str(required=False, data_key='onnx-output')
    """
	 Output ONNX Filename 
	"""
    """
	 Converts Input ONNX file to most current opset if needed 
	"""
    convert = fields.Bool(required=False)
    """
	 Orlando Output Filename 
	"""
    orlando_file = fields.Str(required=False, data_key='orlando-file')
    """
	 Network Name (used as post-fix for NN interface function names in generated Orlando output `.c` file) 
	"""
    network_name = fields.Str(required=False, data_key='network_name')
    """
	 Do not emit memory pools initialization files 
	"""
    no_emit_pools_init = fields.Bool(required=False)
    """
	 Defines a symbol to be used for undefined graph input shapes dimensions (can be used multiple times), format is name:x where name is a graph input name and x is a shape dimension index (0 leftmost position) if x='b' it sets the memory batch format e.g. -D input:0=2 sets first shape dim to 2 
	"""
    def_sym = fields.Str(required=False, data_key='def-sym')
    """
	  Requests ONNX memory format (CHW) for all graph outputs (can be overriden for individual outputs with --def-sym,-D option), default is HWC 
	"""
    onnx_out_format = fields.Str(required=False, data_key='onnx-out-format')
    """
	 Attemps to continue compilation on ONNX file import errors 
	"""
    continue_on_errors = fields.Bool(
        required=False, data_key='continue-on-errors')
    """
	 Emits in generated code a function to retrieve all internal graph edges buffer info structures (useful to debug/inspect buffers at epoch completion with epoch hook) 
	"""
    all_buffers_info = fields.Bool(required=False, data_key='all-buffers-info')
    """
	   Disable the software fallback on Embednets libraries 
	"""
    disable_sw_fallback = fields.Bool(
        required=False, data_key='disable-sw-fallback')
    """
	   Enable the scratch buffers generation for MVEI arm Cortex M55 core. 
	"""
    mvei = fields.Bool(required=False)
    """
	   Runs only the ONNX phases 
	"""
    onnx_only = fields.Bool(required=False, data_key='onnx-only')
    """
	   Save all temporary/Output files 
	"""
    save_all = fields.Bool(required=False, data_key='save-all')
    """
	   verbosity on 
	"""
    verbose = fields.Bool(required=False)

    """
	 Hidden reserved options: 
	"""
    """
	 Displays full help message (including hidden options) 
	"""
    help_full = fields.Bool(required=False, data_key='help-full')
    """
	 Enable the emission of dot graph after each lowering iteration 
	"""
    d_lower_iter_graph = fields.Bool(
        required=False, data_key='d-lower-iter-graph')
    """
	 Do not emit tool version info in generated files 
	"""
    skip_version_generation = fields.Bool(
        required=False, data_key='skip-version-generator')
    """
	 Avoid configuration of Decomp  CodeBooks from the bus 
	"""
    disable_decomp_bus = fields.Bool(
        required=False, data_key='disable-decomp-bus')
    """
	 Enable the software fallback on Embednets libraries DEPRECATED: please use '--native-float' instead 
	"""
    sw_fallback = fields.Bool(required=False, data_key='sw-fallback')
    """
	 Do not generate code which executes HW & SW nodes belonging to same epoch in parallel 
	"""
    no_hw_sw_parallelism = fields.Bool(
        required=False, data_key='no-hw-sw-parallelism')
    """
	 Disable Optimizations specific for HW mapping. Suggested only in case of Hybrid HW/SW mapping or Pure SW mapping. 
	"""
    disable_orlando_opt = fields.Bool(
        required=False, data_key='disable-orlando-opt')
    """
	 Simulate the qmn format for hybrid tests without quantization files. (it forces also the sw-mapped nodes input to floating point when needed) DEPRECATED: please use '--fake-Qmn' instead 
	"""
    simulate_qmn_format = fields.Bool(
        required=False, data_key='simulate-qmn-format')
    """
	 Do not perform deadlock removal pass (potentially unsafe as it can generate a schedule with deadlocks) 
	"""
    dont_remove_deadlocks = fields.Bool(
        required=False, data_key='dont-remove-deadlocks')
    """
	 Automagically converts all scale/offset quantized tensors to QMN attempting to choose a fixed point representation that fits the original range (final accuracy might be affected) 
	"""
    convert_scaleoffset_to_qmn = fields.Bool(
        required=False, data_key='convert-scaleoffset-to-qmn')
    """
	 Enable generation of NPU/MCU cache maintenance code 
	"""
    cache_maintenance = fields.Bool(
        required=False, data_key='cache-maintenance')
    """
	 Enables alternate scheduler node priority option 
	"""
    Oalt_sched = fields.Bool(required=False, data_key='Oalt-sched')
    """
	 KMeans vector quantizer algorithm maximum no of iterations 
	"""
    vq_max_iter = fields.Int(required=False, data_key='vq-max-iter')
    """
	 Force usage of cache for all cachable regions 
	"""
    force_cache_use = fields.Bool(required=False, data_key='force-cache-use')
    """
	 Developers only do not use 
	"""
    hidden_param = fields.Int(required=False, data_key='hidden-param')
    """
	 Enable automatic use of adjacent memory pool with the same properties for large buffer allocation and only use that in lieu of all pool composing it 
	"""
    enable_virtual_mem_pools_only = fields.Bool(
        required=False, data_key='enable-virtual-mem-pools-only')
    """
	 Enable Experimental support of HW lowering 
	"""
    experimental_hw_lowering = fields.Bool(
        required=False, data_key='experimental-hw-lowering')
    """
	 Emit custom helpers and getters used by validation scripts 
	"""
    emit_validation_info = fields.Bool(
        required=False, data_key='emit-validation-info')

    """
	 Target Description options: 
	"""
    """
	 Specifies target machine to use: a predefined one from the config dir or a file name with '.mdesc' extension 
	"""
    load_mdesc_file = fields.Str(required=False, data_key='load-mdesc-file')
    load_mdesc = fields.Str(required=False, data_key='load-mdesc')
    target = fields.Str(required=False, data_key='target')
    """
	   Dumps machine description in use to file name with '.mdesc' extension ('-' means cout) 
	"""
    save_mdesc_file = fields.Str(required=False, data_key='save-mdesc-file')
    """
	   Specifies file name with '.mpool' extension with the platform memory pool definition to use 
	"""
    load_mpool_file = fields.Str(required=False, data_key='load-mpool-file')
    load_mpool = fields.Str(required=False, data_key='load-mpool')
    """
	   Dumps memory pool configuration in use to file name with '.mpool' extension ('-' means cout) 
	"""
    save_mpool_file = fields.Str(required=False, data_key='save-mpool-file')
    """
	   Sets maximum amount of internal memory in KB for buffer allocations (temp option) has no effect with verif/stice4/zc706 pools options 
	"""
    max_ram_size = fields.Int(required=False, data_key='max-ram-size')
    """
	   Enable automatic use of adjacent memory pool with the same properties for large buffer allocation 
	"""
    enable_virtual_mem_pools = fields.Bool(
        required=False, data_key='enable-virtual-mem-pools')

    """
	 Quantization options: 
	"""
    """
	 Consider all Floats without quantization info as Fake integers with precision derived by options --w-bits and --f-bits 
	"""
    fake_Qmn = fields.Bool(required=False, data_key='fake-Qmn')
    """
	   Consider all Floats without quantization info as native floats 
	"""
    native_float = fields.Bool(required=False, data_key='native-float')
    """
	   Sets number of bits assumed to be used for all network weights (temporary option) 
	"""
    w_bits = fields.Int(required=False, data_key='w-bits')
    """
	   Sets number of bits assumed to be used for all activations (temporary option) 
	"""
    f_bits = fields.Int(required=False, data_key='f-bits')
    """
	   CSV file name with tensor Qmn and scaling infor (as produced by external quantization script), for tensors named in the file it will overwrite w-bits and f-bits DEPRECATED: please use '--json-quant-file' instead 
	"""
    quant_file = fields.Str(required=False, data_key='quant-file')
    """
	   Quantization File 
	"""
    json_quant_file = fields.Str(required=False, data_key='json-quant-file')
    """
	   Quantization File 
	"""
    save_json_quant_file = fields.Str(
        required=False, data_key='save-json-quant-file')

    """
	 Optimization options: 
	"""
    """
	 Optimization level one of [0-3](speed) 
	"""
    optimization: 0 | 1 | 2 | 3

    """
	   Attempts to reduce memory buffers size 
	"""
    Os = fields.Bool(required=False)
    M = fields.Bool(required=False)
    """
	   Enables all experimental optimizations 
	"""
    Ox = fields.Bool(required=False)
    x = fields.Bool(required=False)
    """
	   Enables experimental optimization to split convolutions channel-wise 
	"""
    Oconv_split_cw = fields.Bool(required=False, data_key='Oconv-split-cw')
    """
	   Enables experimental optimization to split convolutions Kernel-wise 
	"""
    Oconv_split_kw = fields.Bool(required=False, data_key='Oconv-split-kw')
    """
	   Enables experimental optimization to split convolutions stripe-wise for 1xN kernels 
	"""
    Oconv_split_stripe = fields.Bool(
        required=False, data_key='Oconv-split-stripe')
    """
	   Enables experimental optimization to split convolutions stripe-wise for any kernel size 
	"""
    Oconv_split_stripe_full = fields.Bool(
        required=False, data_key='Oconv-split-stripe-full')
    """
	   Specfies file name ONNX optimization passes one per line 
	"""
    onnx_optimizations_file = fields.Str(
        required=False, data_key='onnx-optimizations-file')
    """
	   Comma separated list of ONNX optimizations to be executed 
	"""
    onnx_optimizations = fields.Str(
        required=False, data_key='onnx-optimizations')
    """
	   Comma separated list of extra ONNX optimizations to be added to default passes 
	"""
    onnx_extra_opts = fields.Str(required=False, data_key='onnx-extra-opts')
    """
	   Omits named option from the final list of ONNX optimizations 
	"""
    onnx_omit_opt = fields.Str(required=False, data_key='onnx-omit-opt')
    """
	   Rounds of ONNX optimizations to be executed 
	"""
    optimization_rounds = fields.Int(
        required=False, data_key='optimization-rounds')
    """
	   Do not reuse buffers allocated for inputs for anything else (initialiers are always preserved) 
	"""
    Opreserve_inputs = fields.Int(required=False, data_key='Opreserve-inputs')
    """
	   Maximum number of Conv Acc used in a pipelined configuration (default is 0 meaning unlimited) 
	"""
    Omax_ca_pipe = fields.Int(required=False, data_key='Omax-ca-pipe')
    """
	   Attempts to clone DMA for compatible input ports iterations (experimental) 
	"""
    Oclone_dma = fields.Bool(required=False, data_key='Oclone-dma')
    """
	   Reshuffles DMAs in each epoch attempting to load balance memory ports traffic (experimental) 
	"""
    Oshuffle_dma = fields.Bool(required=False, data_key='Oshuffle-dma')
    """
	   If a cache is enable on the memory pools enables heuristic annotation for it, implies --enable-bus-signals (experimental) 
	"""
    Ocache_opt = fields.Bool(required=False, data_key='Ocache-opt')

    """
	 Additional info request options: 
	"""
    """
	 DOT Output Filename (default vertical layout) 
	"""
    dot_file = fields.Str(required=False, data_key='dot-file')
    """
	   Selects horizontal orientation for dot output 
	"""
    doth = fields.Bool(required=False)
    """
	   Set maximum length of node/edge labels names 
	"""
    dot_maxlabel = fields.Int(required=False)
    """
	   CSV Output Filename for memory traffic statistics 
	"""
    csv_file = fields.Str(required=False, data_key='csv-file')
    """
	   gnuplot memory bandwidth chart output Filenames prefix (.gnuplot and .data will be appended to it) for memory traffic statistics 
	"""
    gnuplot_mem_file = fields.Str(required=False, data_key='gnuplot-mem-file')
    """
	   gnuplot buffer graph per memory pool output Filenames prefix (.gnuplot appended to it) for buffer allocation across schedule 
	"""
    gnuplot_buf_file = fields.Str(required=False, data_key='gnuplot-buf-file')
    """
	   Sets multiple plots to be generated int the same gnuplot file (if relevant) 
	"""
    gnuplot_multi = fields.Bool(required=False)
    """
	   Initializers histogram Output Filename Prefix (added suffixes .c, .gplot, .gplot.data) 
	"""
    initializers_infofile = fields.Str(
        required=False, data_key='initializers-infofile')
    """
	   Dump num ops info 
	"""
    num_ops_info = fields.Bool(required=False)
    """
	   Enable the mapping recap during the Code Generation phase 
	"""
    mapping_recap = fields.Bool(required=False)
    """
	   Skip Parameters nodes when emitting DOT file 
	"""
    dot_skip_params = fields.Bool(required=False)

    """
	 Debug options: 
	"""
    """
	 debug onnx proto level 
	"""
    d_onnx_p = fields.Int(required=False, data_key='d-onnx-p')
    """
	   debug onnx graph level 
	"""
    d_onnx_g = fields.Int(required=False, data_key='d-onnx-g')
    """
	   debug Quantization info 
	"""
    d_qinfo = fields.Int(required=False, data_key='d-qinfo')
    """
	   debug CFG level 
	"""
    d_CFG = fields.Int(required=False, data_key='d-CFG')
    """
	   debug live range level 
	"""
    d_lv = fields.Int(required=False, data_key='d-lv')
    """
	   debug scheduler level 
	"""
    d_sched = fields.Int(required=False, data_key='d-sched')
    """
	   debug canonic form level 
	"""
    d_canonic = fields.Int(required=False, data_key='d-canonic')
    """
	   debug lowering level 
	"""
    d_lower = fields.Int(required=False, data_key='d-lower')
    """
	   debug orlando dump level 
	"""
    d_o_dump = fields.Int(required=False, data_key='d-o_dump')
    """
	   debug buffer alloc level 
	"""
    d_b_alloc = fields.Int(required=False, data_key='d-b_alloc')
    """
	   debug onnx optimize level 
	"""
    d_onnx_o = fields.Int(required=False, data_key='d-onnx_o')
    """
	   debug machine description level 
	"""
    d_mach = fields.Int(required=False, data_key='d-mach')
    """
	   debug graph inference pass level 
	"""
    d_ginf = fields.Int(required=False, data_key='d-ginf')
    """
	   debug epoch deadlock analisys and removal 
	"""
    d_dead = fields.Int(required=False, data_key='d-dead')
    """
	   debug epoch post optmizer 
	"""
    d_post = fields.Int(required=False, data_key='d-post')
    """
	   debug epoch creation 
	"""
    d_epoch = fields.Int(required=False, data_key='d-epoch')
    """
	   debug performance statistics dump 
	"""
    d_stat = fields.Int(required=False, data_key='d-stat')
    """
	   debug KMeans vector quantizer algorithm 
	"""
    d_vq = fields.Int(required=False, data_key='d-vq')
    """
	   debug dma configuration pass level 
	"""
    d_dma = fields.Int(required=False, data_key='d-dma')
    """
	   debug emitted cache coherency operations 
	"""
    d_cache_ops = fields.Bool(required=False, data_key='d-cache-ops')
    """
	   Promotes all nodes outputs to be graph outputs (for debug only, it has a large impact on memory size and performance) 
	"""
    d_onnx_all_temps = fields.Bool(required=False, data_key='d-onnx-all-temps')
    """
	   Promotes only named edges named in a comma separated list to be graph outputs (for debug only, it has a large impact on memory size and performance) 
	"""
    d_onnx_temps = fields.Str(required=False, data_key='d-onnx-temps')

    """
	 Auto optimizer options: 
	"""
    """
	 Enables iterative automatic optimization options selection for all options supported (increases compilation time) 
	"""
    Oauto = fields.Bool(required=False)
    """
	 Enables iterative automatic optimization selection for scheduler (--Oalt-sched) 
	"""
    Oauto_sched = fields.Bool(required=False, data_key='Oauto-sched')
    """
	 Enables iterative automatic optimization selection for experimental (-x, --Ox) 
	"""
    Oauto_x = fields.Bool(required=False, data_key='Oauto-x')
    """
	 Enables iterative automatic optimization selection for pipelining (--Omax-ca-pipe) 
	"""
    Oauto_pipe = fields.Bool(required=False, data_key='Oauto-pipe')
    """
	 Enables iterative automatic optimization selection for optimization level (-O, --optimization) 
	"""
    Oauto_O = fields.Bool(required=False, data_key='Oauto-O')
    """
	 Debug level for automatic optimization mode (if > 1 it will also generate intermediate .dot outputs for all options tried) 
	"""
    d_auto = fields.Int(required=False, data_key='d-auto')
    """
	 Sets threshold [0.0-1.0] for automatic optimization mode 0 -> only cycles are considered 1 -> only total memory is considered 
	"""
    Oauto_th = fields.Bool(required=False, data_key='Oauto-th')
    """
	 Sets % threshold [0.0-1.0] for convolutional layers splitting heuristic, layers which contribute to less than the threshold to the cumulative no of ops are not transformed (0.0 all conv are considered, 1.0 none are considered) 
	"""
    Oconv_split_th = fields.Bool(required=False, data_key='Oconv-split-th')


class CliParameters(typing.NamedTuple):
    """
        Define the parameters that can be sent to the underlying command line call
    """
    # --------------------------------------------------------------------------------------
    #
    # Common Arguments
    # --------------------------------------------------------------------------------------
    model: str
    """ Required: model file """

    verbosity: CliParameterVerbosity = CliParameterVerbosity.NORMAL
    """  Optional: Command verbosity. Defaults to NORMAL """

    type: Optional[CliParameterType] = None
    """ Optional: Force model type detection when running command. Defaults to None """

    name: Optional[str] = None
    """ Optional: Name which will be used when generating C Code. Defaults to "network """

    compression: Optional[CliParameterCompression] = None
    """ Optional: Compression level. Defaults to "lossless" """

    allocateInputs: bool = True
    """ When set to true, activations buffer will be also used to handle the input buffers. Defaults to True """

    allocateOutputs: bool = True
    """ Optional: When set to true, activations buffer will be also used to handle the output buffers. Defaults to True """

    target: Optional[str] = None
    """ Optional: Defines a serie which will be used to calculate more accurate memory footprint. Defaults to "stm32f4" """

    series: str = 'stm32f4'
    """ Optional: Defines a serie which will be used to calculate more accurate memory footprint. Defaults to "stm32f4" """

    splitWeights: Optional[bool] = False
    """ Optional:  generate a C-data file with a C-table by layer (not supported with the optional '--binary' option) """

    optimization: Optional[CliParameterOptimization] = None
    """ 
        define global optimization objectives 
        - time: optimize the inference time, 
        - ram: minimize the size  of the requested ram, 
        - balanced: default, trade-off between the inference time and ram size
    """

    noOnnxOptimizer: Optional[bool] = None
    """ Optional: disable the ONNX optimizer pass """

    noOnnxIoTranspose: Optional[bool] = None
    """ Optional: disable the adding of the IO transpose layer if ONNX model is channel first """

    prefetchCompressedWeights: Optional[bool] = None
    """ Optional enable the prefetch of the compressed x4,x8 weights (extra space will be reserved in activations buffer) """

    target_info: Optional[str] = None
    """ Provides information for memory layout which will be used by the allocator """
    # --------------------------------------------------------------------------------------
    #
    # Generate Arguments only
    # --------------------------------------------------------------------------------------
    binary: Optional[bool] = None
    """ Optional: generate model weights as a binary file """

    dll: Optional[bool] = None
    """ Optional:  generate the X86 library """

    ihex: Optional[bool] = None
    """ Optional: generate Intel hexadecimal object file format for relocatable model """

    address: Optional[str] = None
    """ Optional: address of the weight array (can be external memory) """

    copyWeightsAt: Optional[str] = None
    """ Optional: Include code to copy weights to specified address """

    relocatable: Optional[bool] = None
    """ Optional:  generate model as a relocatable binary file """

    noCFiles: Optional[bool] = False
    """ Optional: only the relocatable binary file is generated """
    # --------------------------------------------------------------------------------------
    #
    # Validate Arguments only
    # --------------------------------------------------------------------------------------
    batchSize: Optional[int] = None
    """ Optional: number of samples for the validation. Defaults to 10 """

    valinput: Optional[str] = None
    """ Optional: file to use as input for validation """

    valoutput: Optional[str] = None
    """ Optional: files to use as output for validation """

    range: Optional[list] = None
    """ Optional: requested range to generate randomly the input data (default=[0,1]) """

    full: Optional[bool] = None
    """ Optional: enable a full validation process """

    saveCsv: Optional[bool] = None
    """ Optional: force the storage of all io data in csv files """

    classifier: Optional[bool] = None
    """ Optional: force ACC metric computation (default: auto-detection) """

    noCheck: Optional[bool] = None
    """ Optional: disable internal checks (mode/model type dependent) """

    noExecModel: Optional[bool] = None
    """ Optional: Disable execution of the original model """

    seed: Optional[int] = None
    """ Optional: random seed used to initialize the pseudo-randomnumber generator [0, 2**32 - 1] """

    output: str = 'output'
    """ Optional: Output folder """

    # --------------------------------------------------------------------------------------
    #
    # Aton Options
    # --------------------------------------------------------------------------------------
    stNeuralArt: Optional[str] = None

    atonnOptions: Optional[AtonParameters] = None

    # --------------------------------------------------------------------------------------
    #
    # Superset Arguments
    # --------------------------------------------------------------------------------------

    """ Optional: Extra command line arguments as string """
    extraCommandLineArguments: Optional[str] = None

    useCloud: bool = False
    """ Optional: Use Developer Cloud """

    includeLibraryForSerie: Optional[CliLibrarySerie] = None
    """ Optional: Include specific library for a given serie """

    includeLibraryForIde: CliLibraryIde = CliLibraryIde.GCC
    """ Optional: Include library for a given toolchain. Defaults to GCC """

    fromModel: Optional[str] = None
    """ 
        Optional: Defines, for statistics purpose, a model origin. 
        
        Should apply when model used is from STM32 Model Zoo
    """

class MpuParameters(typing.NamedTuple):
    """
        Define the parameters that can be sent to the underlying command line call
    """
    # --------------------------------------------------------------------------------------
    #
    # Common Arguments
    # --------------------------------------------------------------------------------------
    model: str
    """ Required: model file """

    engine: MpuEngine = MpuEngine.CPU
    """ Engine: can be CPU or Hardware Accelerator """

    nbCores: int = 1
    """" Number of cores. Required for multi-core MPU to increase performance """

    

class AnalyzeResult(typing.NamedTuple):
    """
    Provide a simplified interface to access analyze results
    """
    activations_size: int
    weights: int
    macc: int
    rom_size: int
    total_ram_io_size: int
    ram_size: int
    report: dict    # Complete output report
    graph: dict     # Graph report
    info: dict      # info report
    date_time: str
    cli_version_str: str
    cli_parameters: str
    estimated_library_flash_size: int
    estimated_library_ram_size: int

    def __str__(self) -> str:
        data = self._asdict()
        data.pop('report', None)  # Removing report from displayed output
        data.pop('graph', None)  # Removing graph from displayed output
        data.pop('info', None)
        return f"AnalyzeResult({data})"


class GenerateResult(typing.NamedTuple):
    server_url: str
    zipfile_path: str
    output_path: str
    graph: dict
    report: dict

    def __str__(self) -> str:
        data = self._asdict()
        data.pop('report', None)  # Removing report from displayed output
        data.pop('graph', None)  # Removing graph from displayed output
        return f"GenerateResult({data})"


class ValidateResultMetrics(typing.NamedTuple):
    """
    Provide a simplified interface to access validation metrics
    """
    accuracy: str
    description: str
    l2r: float
    mae: float
    mean: float
    rmse: float
    std: float
    ts_name: str


class ValidateResult(typing.NamedTuple):
    """
    Provide a simplified interface to access validation results and metrics
    """
    # AnalyzeResult
    macc: int
    rom_size: int
    total_ram_io_size: int
    ram_size: int
    date_time: str
    cli_version_str: str
    cli_parameters: str
    report: Optional[dict]  # Complete output report

    estimated_library_flash_size: int
    estimated_library_ram_size: int
    graph: Optional[dict] # Complete graph
    info = Optional[dict]
    validation_metrics: typing.List[ValidateResultMetrics]
    validation_error: float
    validation_error_description: str

    def __str__(self) -> str:
        data = self._asdict()
        data.pop('report', None)  # Removing report from displayed output
        data.pop('graph', None)  # Removing report from displayed output
        return f"ValidateResult({data})"


class MpuBenchmarkResult(typing.NamedTuple):
    # AnalyzeResult
    rom_size: int
    ram_size: int
    date_time: str
    cli_version_str: str

    # BenchmarkResult
    info: Optional[dict]
    duration_ms: int
    npu_percent: int
    cpu_percent: int
    gpu_percent: int
    device: str

    def __str__(self) -> str:
        data = self._asdict()
        data.pop('info', None)
        return f"BenchmarkResult({data})"

class BenchmarkResult(typing.NamedTuple):
    # AnalyzeResult
    macc: int
    rom_size: int
    total_ram_io_size: int
    ram_size: int
    date_time: str
    cli_version_str: str
    cli_parameters: str
    report: Optional[dict]  # Complete output report

    # ValidationResult
    validation_metrics: typing.List[ValidateResultMetrics]
    validation_error: float
    validation_error_description: str

    # BenchmarkResult
    graph: Optional[dict]
    info: Optional[dict]
    cycles: int
    duration_ms: int
    device: str
    cycles_by_macc: int
    estimated_library_flash_size: int
    estimated_library_ram_size: int
    use_external_ram: bool
    use_external_flash: bool
    internal_ram_consumption: int
    external_ram_consumption: int
    internal_flash_consumption: int
    external_flash_consumption: int

    def __str__(self) -> str:
        data = self._asdict()
        data.pop('report', None)  # Removing report from displayed output
        data.pop('graph', None)
        data.pop('info', None)
        return f"BenchmarkResult({data})"


class BoardData(typing.NamedTuple):
    """ Provide interface to get data about a board"""
    name: str
    boardCount: int
    flashSize: str
    deviceCpu: str
    deviceId: str


class Stm32AiBackend:
    """"
    Interface used to define backend commands
    It throws an error if the command is not supported by the backend
    """
    # Standard commdands

    def analyze(self, options: CliParameters) -> AnalyzeResult:
        raise NotImplementedError("Analyze not implemented on this backend")

    def generate(self, options: CliParameters) -> GenerateResult:
        raise NotImplementedError("Generate not implemented on this backend")

    def validate(self, options: CliParameters) -> ValidateResult:
        raise NotImplementedError("Validate not implemented on this backend")

    def quantize(self, options: CliParameters):
        raise NotImplementedError("Quantize not implemented on this backend")

    # Cloud enabled commands
    def benchmark(self, options: CliParameters, board_name: str, timeout: int):
        raise NotImplementedError("Benchmark not implemented on this backend")

    def get_benchmark_boards(self) -> typing.List[BoardData]:
        raise NotImplementedError("Get benchmark boards not implemented on \
            this backend")

    def get_user(self):
        raise NotImplementedError("get_user not implemented on \
            this backend")

    def list_models(self):
        raise NotImplementedError("list_models not implemented on this\
             backend")

    def list_validation_input_files(self):
        raise NotImplementedError("list_validation_input_files not implemented\
             on this backend")

    def list_validation_output_files(self):
        raise NotImplementedError("list_validation_output_files not \
            implemented on this backend")

    def list_generated_files(self):
        raise NotImplementedError("list_generated_files not implemented on \
            this backend")

    def upload_model(self, modelPath: str):
        raise NotImplementedError("upload_model not implemented on this\
             backend")

    def upload_validation_input_file(self, filePath: str):
        raise NotImplementedError("upload_validation_input_file not \
            implemented on this backend")

    def upload_validation_output_file(self, filePath: str):
        raise NotImplementedError("upload_validation_output_file not\
             implemented on this backend")

    def download_model(self, modelPath):
        raise NotImplementedError("download_model not implemented on this\
             backend")

    def download_validation_input_file(self, filePath):
        raise NotImplementedError("download_validation_input_file not \
            implemented on this backend")

    def download_validation_output_file(self, filePath):
        raise NotImplementedError("download_validation_output_file not \
            implemented on this backend")

    def download_generated_file(self, filePath):
        raise NotImplementedError("download_generated_file not \
            implemented on this backend")

    def delete_model(self, modelName: str):
        raise NotImplementedError("delete_model not implemented on this \
            backend")

    def delete_validation_input_file(self, fileName: str):
        raise NotImplementedError("delete_validation_input_file not \
            implemented on this backend")

    def delete_validation_output_file(self, fileName: str):
        raise NotImplementedError("delete_validation_output_file not \
            implemented on this backend")

    def delete_generated_file(self, fileName: str):
        raise NotImplementedError("delete_generated_file not implemented on \
            this backend")
