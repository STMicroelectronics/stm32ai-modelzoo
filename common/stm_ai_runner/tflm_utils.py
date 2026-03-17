###################################################################################
#   Copyright (c) 2021 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
ST AI runner - Common helper services to manage the TFLM type
"""

# TFL OP NAME (see tensorflow/lite/schema/schema_generated.h)
_TFLM_OPERATORS = [
    "ADD",  # 0
    "AVERAGE_POOL_2D",
    "CONCATENATION",
    "CONV_2D",
    "DEPTHWISE_CONV_2D",
    "DEPTH_TO_SPACE",
    "DEQUANTIZE",
    "EMBEDDING_LOOKUP",
    "FLOOR",
    "FULLY_CONNECTED",
    "HASHTABLE_LOOKUP",  # 10
    "L2_NORMALIZATION",
    "L2_POOL_2D",
    "LOCAL_RESPONSE_NORMALIZATION",
    "LOGISTIC",
    "LSH_PROJECTION",
    "LSTM",
    "MAX_POOL_2D",
    "MUL",
    "RELU",
    "RELU_N1_TO_1",  # 20
    "RELU6",
    "RESHAPE",
    "RESIZE_BILINEAR",
    "RNN",
    "SOFTMAX",
    "SPACE_TO_DEPTH",
    "SVDF",
    "TANH",
    "CONCAT_EMBEDDINGS",
    "SKIP_GRAM",  # 30
    "CALL",
    "CUSTOM",
    "EMBEDDING_LOOKUP_SPARSE",
    "PAD",
    "UNIDIRECTIONAL_SEQUENCE_RNN",
    "GATHER",
    "BATCH_TO_SPACE_ND",
    "SPACE_TO_BATCH_ND",
    "TRANSPOSE",
    "MEAN",  # 40
    "SUB",
    "DIV",
    "SQUEEZE",
    "UNIDIRECTIONAL_SEQUENCE_LSTM",
    "STRIDED_SLICE",
    "BIDIRECTIONAL_SEQUENCE_RNN",
    "EXP",
    "TOPK_V2",
    "SPLIT",
    "LOG_SOFTMAX",  # 50
    "DELEGATE",
    "BIDIRECTIONAL_SEQUENCE_LSTM",
    "CAST",
    "PRELU",
    "MAXIMUM",
    "ARG_MAX",
    "MINIMUM",
    "LESS",
    "NEG",
    "PADV2",  # 60
    "GREATER",
    "GREATER_EQUAL",
    "LESS_EQUAL",
    "SELECT",
    "SLICE",
    "SIN",
    "TRANSPOSE_CONV",
    "SPARSE_TO_DENSE",
    "TILE",
    "EXPAND_DIMS",  # 70
    "EQUAL",
    "NOT_EQUAL",
    "LOG",
    "SUM",
    "SQRT",
    "RSQRT",
    "SHAPE",
    "POW",
    "ARG_MIN",
    "FAKE_QUANT",  # 80
    "REDUCE_PROD",
    "REDUCE_MAX",
    "PACK",
    "LOGICAL_OR",
    "ONE_HOT",
    "LOGICAL_AND",
    "LOGICAL_NOT",
    "UNPACK",
    "REDUCE_MIN",
    "FLOOR_DIV",  # 90
    "REDUCE_ANY",
    "SQUARE",
    "ZEROS_LIKE",
    "FILL",
    "FLOOR_MOD",
    "RANGE",
    "RESIZE_NEAREST_NEIGHBOR",
    "LEAKY_RELU",
    "SQUARED_DIFFERENCE",
    "MIRROR_PAD",  # 100
    "ABS",
    "SPLIT_V",
    "UNIQUE",
    "CEIL",
    "REVERSE_V2",
    "ADD_N",
    "GATHER_ND",
    "COS",
    "WHERE",
    "RANK",  # 110
    "ELU",
    "REVERSE_SEQUENCE",
    "MATRIX_DIAG",
    "QUANTIZE",
    "MATRIX_SET_DIAG",
    "ROUND",
    "HARD_SWISH",
    "IF",
    "WHILE",
    "NON_MAX_SUPPRESSION_V4",  # 120
    "NON_MAX_SUPPRESSION_V5",
    "SCATTER_ND",
    "SELECT_V2",
    "DENSIFY",
    "SEGMENT_SUM",
    "BATCH_MATMUL",
    "PLACEHOLDER_FOR_GREATER_OP_CODES",
    "CUMSUM",
    "CALL_ONCE",
    "BROADCAST_TO",  # 130
    "RFFT2D",
    "CONV_3D",
    "IMAG",
    "REAL",
    "COMPLEX_ABS",
    "HASHTABLE",
    "HASHTABLE_FIND",
    "HASHTABLE_IMPORT",
    "HASHTABLE_SIZE",
    "REDUCE_ALL",  # 140
    "CONV_3D_TRANSPOSE",
    "VAR_HANDLE",
    "READ_VARIABLE",
    "ASSIGN_VARIABLE",
    "BROADCAST_ARGS",
    "RANDOM_STANDARD_NORMAL",
    "BUCKETIZE",
    "RANDOM_UNIFORM",
    "MULTINOMIAL",
    "GELU",  # 150
    "DYNAMIC_UPDATE_SLICE",
    "RELU_0_TO_1",
    "UNSORTED_SEGMENT_PROD",
    "UNSORTED_SEGMENT_MAX",
    "UNSORTED_SEGMENT_SUM",
    "ATAN2",
    "UNSORTED_SEGMENT_MIN",
    "SIGN"
]


def tflm_node_type_to_str(op_type_id, with_id=True):
    """  # noqa: DAR005
    Return a human readable description of a TFLM-node

    see <TF>::Tensorflow git (tensorflow/lite/schema/schema_generated.h file)

    Parameters
    ----------
    op_type_id
        TFLM operator id/index
    with_id:
        add numerical value in the description

    Returns
    -------
    str
        human readable description of the c-node
    """

    if 0 <= op_type_id < len(_TFLM_OPERATORS):
        desc_ = '{}'.format(_TFLM_OPERATORS[op_type_id])
    else:
        desc_ = 'custom or unknown'
        with_id = True
    if with_id:
        desc_ += f' ({op_type_id})'
    return desc_
