# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import re

from flexbuffers import Loads as decode_flexbuf

from collections import OrderedDict

_BYTES_BY_LINE = 16
_ALIGN_PARAM_TABLE = 4

def _write_c_data_line(data, f_out, last=False, indent=2):
    """Write a list of byte"""
    l_val = ['0x{:02x}'.format(b) for b in data]
    l_str = ' ' * indent + ', '.join(l_val)
    if not last:
        l_str += ','
    f_out.write(l_str + '\n')


def _write_multilines(lines, f_out, indent=0):
    """Strip the left space before to write a line"""
    for cur_l in lines.split('\n'):
        print(' ' * indent + cur_l, file=f_out)


def _write_tensor(name, ts_name, data, fmt, shape, scale, zp, f_out):
    """Write an array as a C-table"""

    _c_table_h_tpl = ("\n"
                      "/* {name} - {fmt} - {shape} */\n"
                      "\n"
                      "AI_ALIGNED({align})\n"
                      "static const ai_u8 s_{name}[ {size} ] = {{")

    _c_table_f_tpl = ("{c};")

    m_lines = _c_table_h_tpl.format(name=ts_name, fmt=fmt,
                                    size=len(data),
                                    shape=shape,
                                    align=_ALIGN_PARAM_TABLE)

    _write_multilines(m_lines, f_out)

    pos = 0
    while True:
        last = pos + _BYTES_BY_LINE >= len(data)
        size = _BYTES_BY_LINE if not last else len(data) - pos
        _write_c_data_line(data[pos:pos + size], f_out, last)
        pos += size
        if last:
            break

    _write_multilines(_c_table_f_tpl.format(c='}'), f_out)

    if scale:
        szp = 'U8' if 'U8' in fmt else 'S8'
        _tpl = ("\nAI_INTQ_INFO_LIST_OBJ_DECLARE(s_{name}_intq, AI_STATIC_CONST,\n"
                "   AI_BUFFER_META_FLAG_SCALE_FLOAT|AI_BUFFER_META_FLAG_ZEROPOINT_{szp}, 1,\n"
                "   AI_PACK_INTQ_INFO(\n"
                "     AI_PACK_INTQ_SCALE({scale}),\n"
                "     AI_PACK_UINTQ_ZP({zp})))\n"
                "\n"
                "static ai_buffer_meta_info s_{name}_meta_info =\n"
                "  {bc} AI_BUFFER_META_HAS_INTQ_INFO, (ai_handle)&s_{name}_intq {ec};\n")
    
        print(_tpl.format(name=ts_name, scale=scale, zp=zp, szp=szp, bc='{', ec='}'), file=f_out)

    _anchors = '{} {}, 1, {}, 1, {}, (ai_handle)&s_{}[0], {} {}'.format('{',
        fmt,
        shape[0], shape[1], ts_name,
        '&s_{}_meta_info'.format(ts_name) if scale else 'NULL',
        '}'
        )

    print('const ai_buffer* ai_{}_get_{}(void) {}'.format(name, ts_name, '{'), file=f_out)

    print(' static const ai_buffer s_{}_buffer =\n  {};'.format(ts_name, _anchors), file=f_out)
    print(' return &s_{}_buffer; \n{}'.format(ts_name, '}'), file=f_out)

    return len(data)


def _write_header(name_op, name, f_out):
    """Write header of the data C-file"""
    import datetime

    c_h_tpl = ("/*\n"
               " * Generated file with attributes for the {name_op} operator\n"
               " *  network   : {name}\n"
               " *  generator : {file} v{ver}\n"
               " *\n"
               " * Created date and time : {dt}\n"
               " */\n\n")

    print(c_h_tpl.format(name_op=name_op, ver='0.0',
                         name=name,
                         file=os.path.basename(__file__),
                         dt=str(datetime.datetime.now())),
                         file=f_out)

    if name_op:
        fname = '__AI_{}_{}__'.format(name.upper(), name_op.upper())
        m_lines = '#ifndef {fname}\n#define {fname}\n'.format(fname=fname)
        _write_multilines(m_lines, f_out)

    print("#include \"ai_platform.h\"", file=f_out)
    print("#include \"ai_platform_interface.h\"", file=f_out)


def _write_footer(name_op, name, f_out):
    """Write footer of the data C-file"""
    if name_op:
        fname = '__AI_{}_{}__'.format(name.upper(), name_op.upper())
        m_lines = '\n#endif /*  {fname} */\n'.format(fname=fname)
        _write_multilines(m_lines, f_out)
    else:
        print('\n', file=f_out)


def _write_params_detection_pp(name, ts_name, attrs, type_buf, shape_buf, scale, zp, f_out):
    """Write the attributes for the TFLite_Detection_PostProcess operator"""

    print('\n', file=f_out)
    for i, (k, attr) in enumerate(attrs.items()):
        val = attr['value'] if attr['value'] else attr['default']
        m_lines = '#define AI_{}_{}  ({})'.format(name.upper(), k.upper(), val)
        _write_multilines(m_lines, f_out)

    print('\nconst ai_buffer* ai_{}_get_{}(void);'.format(name, ts_name), file=f_out)


def extract_params_detection_pp(op, tensors, buffers, output, name, verbosity):
    """Extract params for TFLite_Detection_PostProcess operator"""

    hdr = 'TFLite_Detection_PostProcess'

    print('Extracting attributes/params for TFLite_Detection_PostProcess operator (name={})'.format(name))

    # see C++ code ref. == tensorflow/tensorflow/lite/kernels/detection_postprocess.cc
    TFLite_DP_OpData = OrderedDict([
        ("max_detections" , { 'c_type': 'ai_i32', 'default' : '10' , 'value': None}),
        ("max_classes_per_detection" , { 'c_type': 'ai_i32', 'default' : '1' , 'value': None}),
        ("detections_per_class" , { 'c_type': 'ai_i32', 'default' : '100' , 'value': None}),
        ("nms_score_threshold" , { 'c_type': 'ai_float', 'default' : '0.0f' , 'value': None}),
        ("nms_iou_threshold" , { 'c_type': 'ai_float', 'default' : '0.0f' , 'value': None}),
        ("num_classes" , { 'c_type': 'ai_i32', 'default' : '1' , 'value': None}),
        ("use_regular_nms" , { 'c_type': 'ai_bool', 'default' : 'false' , 'value': None}),
        ("y_scale" , { 'c_type': 'ai_float', 'default' : '0.0f', 'value': None }),
        ("x_scale" , { 'c_type': 'ai_float', 'default' : '0.0f', 'value': None }),
        ("h_scale" , { 'c_type': 'ai_float', 'default' : '0.0f', 'value': None }),
        ("w_scale" , { 'c_type': 'ai_float', 'default' : '0.0f', 'value': None }),
        ("boxes_scale", { 'c_type': 'ai_float', 'default' : '1.0f', 'value': None }),
        ("boxes_offset", { 'c_type': 'ai_float', 'default' : '0.0f', 'value': None }),
        ("scores_scale", { 'c_type': 'ai_float', 'default' : '1.0f', 'value': None }),
        ("scores_offset", { 'c_type': 'ai_float', 'default' : '0.0f', 'value': None }),
    ])

    # Check input tensors
    if len(op['inputs']) != 3:
        raise ValueError('{}: Number of input tensors is invalid {} instead 3'.format(hdr, len(op['inputs'])))

    shape_buf = tensors[op['inputs'][0]]['shape']
    if len(shape_buf) != 3:
        raise ValueError('{}: Dim of box encodings tensor is invalid {} instead 2'.format(hdr, len(shape_buf)))

    shape_buf = tensors[op['inputs'][1]]['shape']
    if len(shape_buf) != 3:
        raise ValueError('{}: Dim of class predictions tensor is invalid {} instead 2'.format(hdr, len(shape_buf)))

    shape_buf = tensors[op['inputs'][2]]['shape']
    if len(shape_buf) != 2:
        raise ValueError('{}: Dim of anchors tensor is invalid {} instead 2'.format(hdr, len(shape_buf)))

    # Retreive the operator attributes (custom options)
    op_data = decode_flexbuf(bytearray(op['custom_options']))

    for key in op_data:
        if key in TFLite_DP_OpData:
            val = op_data[key]
            if TFLite_DP_OpData[key]['c_type'] == 'ai_bool':
                val = 'false' if val == False else True
            TFLite_DP_OpData[key]['value'] = val
            #print("key: ",key," value: ",val)
        else:
            print('W: attribute "{}" is not considered (val={})'.format(key,  op_data[key]))

    

    # Retreive the anchors tensor
    idx_buf = tensors[op['inputs'][2]]['buffer']
    type_buf = tensors[op['inputs'][2]]['type']
    quant = tensors[op['inputs'][2]]['quantization']

    type_buf = 'AI_BUFFER_FORMAT_U8' if type_buf == 'UINT8' else\
        'AI_BUFFER_FORMAT_S8' if type_buf == 'INT8' else 'AI_BUFFER_FORMAT_FLOAT'

    scale = quant['scale'][0] if 'scale' in quant else None
    zp = quant['zero_point'][0] if 'zero_point' in quant else 0


    regex = re.compile('score')

    if regex.search(tensors[op['inputs'][1]]['name']):
        quant_boxes  = tensors[op['inputs'][0]]['quantization'] if 'quantization' in tensors[op['inputs'][0]] else None
        quant_scores = tensors[op['inputs'][1]]['quantization'] if 'quantization' in tensors[op['inputs'][1]] else None
        #print('Scores in the second input')
        #bfirst = 1
    elif regex.search(tensors[op['inputs'][0]]['name']):
        quant_boxes  = tensors[op['inputs'][1]]['quantization'] if 'quantization' in tensors[op['inputs'][1]] else None
        quant_scores = tensors[op['inputs'][0]]['quantization'] if 'quantization' in tensors[op['inputs'][0]] else None
        #print('Scores in the first input')
        #bfirst = 0
    else:
        quant_boxes  = tensors[op['inputs'][0]]['quantization'] if 'quantization' in tensors[op['inputs'][0]] else None
        quant_scores = tensors[op['inputs'][1]]['quantization'] if 'quantization' in tensors[op['inputs'][1]] else None
        #print('The names of the tensors dont match the search so by default the scores will be the second input')
        #bfirst = 1


    TFLite_DP_OpData["boxes_scale"]['value'] = (quant_boxes['scale'][0] if 'scale' in quant_boxes else None) if quant_boxes!=None else None
    TFLite_DP_OpData["boxes_offset"]['value'] = (quant_boxes['zero_point'][0] if 'zero_point' in quant_boxes else 0) if quant_boxes!=None else 0
    TFLite_DP_OpData["scores_scale"]['value'] = (quant_scores['scale'][0] if 'scale' in quant_scores else None) if quant_boxes!=None else None
    TFLite_DP_OpData["scores_offset"]['value'] = (quant_scores['zero_point'][0] if 'zero_point' in quant_scores else 0) if quant_boxes!=None else 0
    #TFLite_DP_OpData["boxes_first"]['value'] = str(bfirst)
            

    #print(quant_boxes['scale'][0] if 'scale' in quant_boxes else None)
    #print(quant_boxes['zero_point'][0] if 'zero_point' in quant_boxes else 0)
    #print(quant_scores['scale'][0] if 'scale' in quant_scores else None)
    #print(quant_scores['zero_point'][0] if 'zero_point' in quant_scores else 0)

    #print(tensors[op['inputs'][0]]['name'])
    #print(tensors[op['inputs'][1]]['name'])


    #print("TFLITE post-processing parameters : ",TFLite_DP_OpData)


    buf = bytearray(buffers[idx_buf]['data'])

    if not output:
        return

    file_path = os.path.join(output, name + '_pp_nms_params')

    # Create H file
    print('Creating file : {}.h'.format(file_path))
    with open(file_path + '.h', mode='w') as f_out:
        _write_header(hdr, name, f_out)
        _write_params_detection_pp(name, 'anchors', TFLite_DP_OpData, type_buf, shape_buf, scale, zp, f_out)
        _write_footer(hdr, name, f_out)

    # Create C file
    print('Creating file : {}.c'.format(file_path))
    with open(file_path + '.c', mode='w') as f_out:
        _write_header(None, name, f_out)
        _write_tensor(name, 'anchors', buf, type_buf, shape_buf, scale, zp, f_out)
        _write_footer(None, name, f_out)


def extract_attributes(data, loc, output, name, verbosity):
    """Extract specific operator attributs"""

    sg = data['subgraphs'][0]
    op_codes = data['operator_codes']
    buffers = data['buffers']
    tensors = sg['tensors']
    
    op = sg['operators'][loc]
    op_idx = op['opcode_index']

    if op_codes[op_idx]['builtin_code'] == 'CUSTOM' and\
        op_codes[op_idx]['custom_code'] == 'TFLite_Detection_PostProcess':
        f_path_out = os.path.join(output, 'detection_pp_params') if output else None
        extract_params_detection_pp(op, tensors, buffers, output, name, verbosity)
        return
    
    print('W: Attributes extraction for "{}" is not supported'.format(op_codes[op_idx]['builtin_code']))


def test():
    """Unit test for flex buf decoder"""

    custom_00 = [
        121, 95, 115, 99, 97, 108, 101, 0, 95, 111, 117,
        116, 112, 117, 116, 95, 113, 117, 97, 110, 116, 105,
        122, 101, 100, 0, 109, 97, 120, 95, 100, 101, 116, 101,
        99, 116, 105, 111, 110, 115, 0, 110, 109, 115, 95, 115,
        99, 111, 114, 101, 95, 116, 104, 114, 101, 115, 104, 111,
        108, 100, 0, 119, 95, 115, 99, 97, 108, 101, 0, 120,
        95, 115, 99, 97, 108, 101, 0, 110, 109, 115, 95,
        105, 111, 117, 95, 116, 104, 114, 101, 115, 104, 111,
        108, 100, 0, 104, 95, 115, 99, 97, 108, 101, 0, 109, 97,
        120, 95, 99, 108, 97, 115, 115, 101, 115, 95, 112, 101,
        114, 95, 100, 101, 116, 101, 99, 116, 105, 111, 110, 0,
        110, 117, 109, 95, 99, 108, 97, 115, 115, 101, 115, 0,
        10, 134, 48, 41, 119, 69, 106, 19, 88, 81, 151, 10, 0,
        0, 0, 1, 0, 0, 0, 10, 0, 0, 0, 1, 0, 0, 0, 0, 0, 160, 64,
        1, 0, 0, 0, 10, 0, 0, 0, 154, 153, 25, 63, 119, 204, 43,
        50, 90, 0, 0, 0, 0, 0, 160, 64, 0, 0, 32, 65, 0, 0, 32,
        65, 106, 14, 6, 6, 14, 14, 6, 14, 14, 14, 50, 38, 1
    ]

    data = decode_flexbuf(bytearray(custom_00))

    for i, (k, v) in enumerate(data.items()):
        print(i, k, v, type(v))

    return 0


if __name__ == '__main__':
    sys.exit(test())