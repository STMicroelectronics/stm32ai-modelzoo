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

import os, sys
import pathlib
import json
from tqdm import tqdm
from os import path
import numpy as np
import re

from collections import OrderedDict


_STR_DEFAULT_OUTPUT_DIR = 'generate'
_SCHEMA_FILE_PATH = path.join(path.split(__file__)[0], 'schema.fbs')

def toJSON(filepath, output='generate', schema=_SCHEMA_FILE_PATH, verbosity=0):
    """Call flatc utility to convert the TFLite file to JSON format"""
    from distutils import spawn
    from subprocess import check_call, CalledProcessError

    if os.name == 'posix':
        cmd_exe = 'utils/flatc/unix/flatc'
    elif os.name == 'nt':
        cmd_exe = 'utils/flatc/windows/flatc.exe'

    cmd = [cmd_exe, '-t', '--strict-json', '--defaults-json','-o', output, schema, '--', filepath]
    if verbosity:
        print('Calling "{}"'.format(' '.join(cmd)))
    check_call(cmd)


def toTFlite(filepath, output='generate', schema=_SCHEMA_FILE_PATH, verbosity=0):
    """Call flatc utility to convert the TFLite file to JSON format"""
    from distutils import spawn
    from subprocess import check_call, CalledProcessError

    if os.name == 'posix':
        cmd_exe = 'utils/flatc/unix/flatc'
    elif os.name == 'nt':
        cmd_exe = 'utils/flatc/windows/flatc.exe'

    cmd_exe
    cmd = [cmd_exe, '--binary', '--defaults-json','-o', output, schema, filepath]
    if verbosity:
        print('Calling "{}"'.format(' '.join(cmd)))
    check_call(cmd)


def print_tensor_desc(tensors, idx, preffix, verbosity=0):
    """Print tensor description"""
    if not isinstance(idx, list):
        idx = [idx]
    for pos, i in enumerate(idx):
        shape = tensors[i]['shape'] if 'shape' in tensors[i] else '[]'
        print(' {}[{}] idx={} name="{}" shape={} type={} buffer_idx={}'.format(preffix ,pos, i, tensors[i]['name'], shape,
                                                                               tensors[i]['type'],
                                                                               tensors[i]['buffer']))
        if 'quantization' in tensors[i] and tensors[i]['type'] != 'FLOAT32':
            quant = tensors[i]['quantization']
            msg = '       '
            msg += 'min={} '.format(quant['min']) if 'min' in quant else ''
            msg += 'max={} '.format(quant['max']) if 'max' in quant else ''
            zero_point = quant['zero_point'] if 'zero_point' in quant else 'n.a'
            scale = quant['scale'] if 'scale' in quant else 'n.a'
            if verbosity == 0 and scale != 'n.a' and len(scale) > 1:
                msg += 'scale[{}]=[{}, ..] '.format(len(scale), scale[0])
                msg += 'zero_point[{}]=[{}, ..] '.format(len(zero_point), zero_point[0])
            else:
                msg += 'scale[{}]={} '.format(len(scale), scale)
                msg += 'zero_point[{}]={} '.format(len(zero_point), zero_point)
            print('       {}'.format(msg))



def load_json(filepath, verbosity):
    """Load the json file"""
    with open(filepath, 'r') as f:
        data = json.load(f, object_pairs_hook=OrderedDict)

    if 'version' not in data or data['version'] != 3:
        raise LookupError('JSON file version is incorrect')

    if verbosity:
        op_code = data['operator_codes']
        sg = data['subgraphs'][0]
        tensors = sg['tensors']
        inputs = sg['inputs']
        outputs = sg['outputs']
        operators = sg['operators']

        print('scheme version  : ', data['version'])
        print('emitter         : ', data['description'])
        print('op_code #       : ', len(op_code))
        print('tensors #       : ', len(tensors))
        print('operators #     : ', len(operators))
        print_tensor_desc(tensors, inputs, 'I')
        print_tensor_desc(tensors, outputs, 'O')

    return data

def json_min_max_rescale(data):
    tensors = data['subgraphs'][0]['tensors']
    types = {'INT8':[-128,127],'UINT8':[0,255],'INT32':[-2147483648,2147483647]}
    for i,t in tqdm(enumerate(tensors)):
        try:
            quant = t['quantization']
            #print(quant)
            q_scale = quant['scale'][0]
            #print(q_scale)
            q_zero  = quant['zero_point'][0]
            #print(q_zero)

            type_min,type_max = types[t['type']]
            #print(type_min,' ',type_max)
            print(q_scale * (type_min - q_zero))
            print(q_scale * (type_max - q_zero))
            print(tensors[i]['quantization']['min'])
            print(tensors[i]['quantization']['max'])
            tensors[i]['quantization']['min'][0] = str(np.float64(q_scale) * (np.float64(type_min) - np.float64(q_zero)) - 1e-5)
            tensors[i]['quantization']['max'][0] = str(np.float64(q_scale) * (np.float64(type_max) - np.float64(q_zero)) + 1e-5)
            print(tensors[i]['quantization']['min'])
            print(tensors[i]['quantization']['max'])

        except:
            continue

    data['subgraphs'][0]['tensors'] = tensors

    print(data['subgraphs'][0]['tensors'][i]['quantization']['min'])

    return data


def save_json(filepath, data):

    with open(filepath, 'w') as outfile:
        json.dump(data, outfile, indent=2)


def get_next_loc(sg, idx):
    """Return operator list which have the tensor idx as input"""
    loc = []
    for i, op in enumerate(sg['operators']):
        if idx in op['inputs']:
            loc.append(i)
    return loc


# _SUPPORTED_OP = ['CONV_2D', 'DEPTHWISE_CONV_2D', 'RESHAPE', 'FULLY_CONNECTED', 'QUANTIZE', 'DEQUANTIZE', 
#                 'SOFTMAX', 'MAX_POOL_2D', 'AVERAGE_POOL_2D', 'CONCATENATION', 'LOGISTIC']

def check_node_for_patch(data, loc, patch_type='default', overwrite=True):
    """Check that the operator is valid for the operation"""

    sg = data['subgraphs'][0]
    
    if loc < 0 or loc >= len(sg['operators']):
        raise IndexError('Operator location {} is invalid'.format(loc))
    
    op = sg['operators'][loc]
    op_code = op['opcode_index']
    n_op = data['operator_codes'][op_code]['builtin_code']
    #if len(op['outputs']) > 1 and n_op != 'CUSTOM':
    #    raise AttributeError('Operator location {} has {} outputs'.format(loc, len(op['outputs'])))

    if patch_type == 'default' or patch_type != 'add':
        return op
        
    if not overwrite:
        return op

    # check next operator
    while True:
        next_loc = get_next_loc(sg, op['outputs'][0])
        if len(next_loc) == 1:
            op_code = sg['operators'][next_loc[0]]['opcode_index']
            n_op = data['operator_codes'][op_code]['builtin_code']
            if 'POOL' in n_op:
                print('W: overwrite location {} to {}'.format(loc, next_loc[0]), flush=True)
                op = sg['operators'][next_loc[0]]
            elif 'RESHAPE' in n_op:
                print('W: overwrite location {} to {}'.format(loc, next_loc[0]), flush=True)
                op = sg['operators'][next_loc[0]]
            else:
                break
            loc = next_loc[0]
        else:    
            break

    # if n_op not in  _SUPPORTED_OP:
    #        print('W: operator {} ({}) will be perhaps optimized by X-CUBE-AI'.format(n_op, loc), flush=True)

    return op


def add_outputs(data, loc_add, verbosity, overwrite=True, loc_anchors_tensor=None):
    """Build new outputs list"""

    if loc_add == None:
        return

    # select the subgraph 0
    sg = data['subgraphs'][0]

    if verbosity:
        print('Previous tensor outputs : ', sg['outputs'])

    # create/check a tensor list of candidates
    cdt_list = sg['outputs'].copy()
    for loc in loc_add:
        op = check_node_for_patch(data, loc, patch_type='add', overwrite=overwrite)
        if op:
            cdt_list.append(op['outputs'][0])

    # remove duplication
    cdt_list = list(dict.fromkeys(cdt_list))

    # create new list respecting the operator orders
    n_list = []
    for loc, op in enumerate(sg['operators']):
        #print(sg['tensors'])
        for idx in op['outputs']:
            if idx in cdt_list:
                if verbosity > 1:
                    print('- location {} -> tensor idx {}'.format(loc, op['outputs'][0]), flush=True)
                n_list.append(idx)

    sg['outputs'] = n_list
    #print('Setting tensor outputs : ', sg['outputs'])
    #print('buffer ',sg['tensors'][sg['outputs'][0]]['buffer'])
    # for i,buf in enumerate(data['buffers']):
    #     try:
    #         print('tensor '+str(i)+' : ',len(buf['data']))
    #     except:
    #         print('no data in tensor : ',i)
    #print(len(data['buffers'][174]['data']))#[sg['tensors'][sg['outputs'][0]]['buffer']])
    #print(sg['tensors'][sg['outputs'][1]]['name'])

    regex = re.compile('score')

    if regex.search(sg['tensors'][sg['outputs'][0]]['name']):
        #print('Scores in the first input')
        data['subgraphs'][0]['tensors'][sg['outputs'][0]]['name'] = 'scores'
        data['subgraphs'][0]['tensors'][sg['outputs'][1]]['name'] = 'boxes'
        sf = 0
    else:
        #print('The names of the tensors dont match the search so by default the scores will be the second input')
        data['subgraphs'][0]['tensors'][sg['outputs'][0]]['name'] = 'boxes'
        data['subgraphs'][0]['tensors'][sg['outputs'][1]]['name'] = 'scores'
        sf = 1

    # add the support for DEQUANTIZE layer in the tflite
    opcode_index = len(data['operator_codes'])
    data['operator_codes'].append({"builtin_code": "DEQUANTIZE","version": 1})
    

    # add the buffers of dequantize operators 
    ind = len(data['buffers'])

    data['buffers'].append({}) # scores
    data['buffers'].append({}) # boxes
    #data['buffers'].append({}) # anchors



    if data['subgraphs'][0]['tensors'][loc_anchors_tensor]['type']!="FLOAT32":
        scale_anchors = float(data['subgraphs'][0]['tensors'][loc_anchors_tensor]['quantization']['scale'][0])
        zerop_anchors = float(data['subgraphs'][0]['tensors'][loc_anchors_tensor]['quantization']['zero_point'][0])
        data_anchors_uint8 = np.array(data['buffers'][data['subgraphs'][0]['tensors'][loc_anchors_tensor]['buffer']]['data'],dtype=np.float32)
        data_anchors_float = (data_anchors_uint8 - zerop_anchors) * scale_anchors
    else:
        data_anchors_uint8 = np.array(data['buffers'][data['subgraphs'][0]['tensors'][loc_anchors_tensor]['buffer']]['data'],dtype=np.uint8)
        data_anchors_float = data_anchors_uint8.view('float32')


    nb_anchor_values = data_anchors_float.shape[0]

    anchors_file_path = os.path.join('generate','anchors.h')

    nb_values_per_line = 16

    nb_lines = int(nb_anchor_values/nb_values_per_line)


    print('Creating file : {}'.format(anchors_file_path))

    indent_string = 'const float pp_anchors['+str(nb_anchor_values)+'] = {'
    indentation   = ' ' * len(indent_string)

    with open(anchors_file_path, mode='w') as f_out:

        print("#ifndef __ANCHORS_H\n", file=f_out)
        print("#define __ANCHORS_H\n", file=f_out)

        for l in range(nb_lines):
            line_data = data_anchors_float[l*nb_values_per_line:(l+1)*nb_values_per_line]
            if l==0:
                line_str  = indent_string
            else:
                line_str  = indentation
            for ld in line_data:
                line_str+=str(ld)+', '
            line_str+='\n'

            print(line_str, file=f_out)

        line_data = data_anchors_float[nb_lines*nb_values_per_line:(nb_lines+1)*nb_values_per_line]
        line_str  = indentation
        for ld in line_data:
            line_str+=str(ld)+', '
        line_str = line_str[:-2] + ' };\n'
        print(line_str, file=f_out)
        print("#endif\n", file=f_out)


    #data['subgraphs'][0]['tensors'][loc_anchors_tensor]['shape'] = [1]+data['subgraphs'][0]['tensors'][loc_anchors_tensor]['shape']

    # add the tensors of output for dequantize operators
    tind = len(data['subgraphs'][0]['tensors'])

    index_scores_tensor  = tind
    index_boxes_tensor   = tind + 1
    #index_anchors_tensor = tind + 2

    s_b_n_scores  = [data['subgraphs'][0]['tensors'][sg['outputs'][sf]]['shape'],     ind,     "scores_dequantized" ]
    s_b_n_boxes   = [data['subgraphs'][0]['tensors'][sg['outputs'][not sf]]['shape'], ind + 1, "boxes_dequantized"  ]

    shape_buffer_name = [s_b_n_scores,
                         s_b_n_boxes]

    for shbuffnm in shape_buffer_name:
        data['subgraphs'][0]['tensors'].append({"shape": shbuffnm[0],
                                                "type": "FLOAT32",
                                                "buffer": shbuffnm[1],
                                                "name": shbuffnm[2],
                                                "is_variable": False})



    # add the dequantize operators
    inputs_outputs = [[sg['outputs'][sf],     index_scores_tensor ],
                      [sg['outputs'][not sf], index_boxes_tensor  ]]


    index_outputs = []
    for inouts in inputs_outputs:
        inp_t_type  = data['subgraphs'][0]['tensors'][inouts[0]]['type']

        if inp_t_type!="FLOAT32" :

            data['subgraphs'][0]['operators'].append({"opcode_index": opcode_index,
                                                      "inputs":  [inouts[0]],
                                                      "outputs": [inouts[1]],
                                                      "builtin_options_type": "DequantizeOptions",
                                                      "builtin_options": {},
                                                      "custom_options_format": "FLEXBUFFERS",
                                                      "mutating_variable_inputs": []})
            index_outputs.append(inouts[1])
        else:
            index_outputs.append(inouts[0])

    # change the output tensors
    data['subgraphs'][0]['outputs'] = index_outputs

def clean_graph(data, verbosity):
    """Remove leaf operators not defined in outputs list"""

    sg = data['subgraphs'][0]

    while True:
        sz = len(sg['operators'])

        all_ts_outputs = []
        for op in sg['operators']:
            all_ts_outputs.append(op['outputs'][0])

        all_ts_inputs = []
        for op in sg['operators']:
            for idx_i in op['inputs']:
                if idx_i in all_ts_outputs:
                    all_ts_inputs.append(idx_i)

        all_ts_inputs = list(dict.fromkeys(all_ts_inputs))

        for loc, op in enumerate(sg['operators']):
            if op['outputs'][0] not in all_ts_inputs and op['outputs'][0] not in sg['outputs']:
                if verbosity:
                    print('- Removing op loc={} op_idx={}'.format(loc, op['opcode_index']))
                del sg['operators'][loc]
                cont = True
        if len(sg['operators']) == sz:
            break


def extract_attributes(data, loc_extract, output, name, verbosity, overwrite=True):
    """Extract attribute values for a given node"""
    from tflite_params import extract_attributes

    check_node_for_patch(data, loc_extract[0], overwrite=overwrite)
    extract_attributes(data, loc_extract[0], output, name, verbosity)


def print_node_info(data, loc_info, verbosity, overwrite=True):
    """Return info of a given node"""

    if loc_info == None:
        return

    if not isinstance(loc_info, list):
        loc_info = [loc_info]

    sg = data['subgraphs'][0]
    op_codes = data['operator_codes']
    tensors = sg['tensors']

    for _l in loc_info:
        print('\nNode (idx={})'.format(_l))
        print('-' * 60)

        op = check_node_for_patch(data, _l, overwrite=overwrite)

        op_idx = op['opcode_index']
        print(' builtin_code  : {} version={} (idx={})'.format(op_codes[op_idx]['builtin_code'],
                                                               op_codes[op_idx]['version'],
                                                               op_idx))
        if op_codes[op_idx]['builtin_code'] == 'CUSTOM':
            print(' custom_code  : {}'.format(op_codes[op_idx]['custom_code']))
    
        print(' input tensors :', op['inputs'])
        print_tensor_desc(tensors, op['inputs'], '  ', verbosity)
        print(' output tensors :', op['outputs'])
        print_tensor_desc(tensors, op['outputs'], '  ', verbosity)

        print(' builtin_options_type  : ', op['builtin_options_type'])
        print(' custom_options_format : ', op['custom_options_format'])
        print('-' * 60)


def _get_owner(ops, ts_idx):
    """Return operator location of the tensor producer"""
    for loc, op in enumerate(ops):
            if ts_idx in op['outputs']:
                return loc
    return None


def cut_graph(data, loc_cut, verbosity, overwrite=True):
    """Cut the graph"""

    if loc_cut == None:
        return

    loc_anchors = data['subgraphs'][0]['operators'][loc_cut]['inputs'][2]

    # select the subgraph 0
    sg = data['subgraphs'][0]

    # check if op location if valid
    op = check_node_for_patch(data, loc_cut, patch_type='cut', overwrite=overwrite)

    # new outputs
    in_ts = op['inputs']

    # list of removed op (from cut op)
    removed_out_ts = op['outputs']
    removed_op_loc = [loc_cut]

    if verbosity:
        print('Tensor inputs  {}'.format(in_ts))
        print('Tensor outputs {}'.format(removed_out_ts))

    for idx_o in  removed_out_ts:
        for loc, op in enumerate(sg['operators']):
            if idx_o in op['inputs']:
                removed_out_ts.extend(op['outputs'])
                removed_op_loc.extend([loc])

    # check place-holder input tensor
    for idx_i in in_ts:
        loc_c = _get_owner(sg['operators'], idx_i)
        if loc_c:
            in_ts_c = sg['operators'][loc_c]['inputs']
            if len(in_ts_c) == 1 and not _get_owner(sg['operators'], in_ts_c[0]):
                removed_op_loc.extend([loc_c])

    # remove loc/idx duplication
    removed_out_ts = list(dict.fromkeys(removed_out_ts))
    removed_op_loc = list(dict.fromkeys(removed_op_loc))

    print('Removing {} operators'.format(len(removed_op_loc)))
    if verbosity:
        print(' {}'.format(removed_op_loc))
    if verbosity > 1:
        print('Tensor outputs : {}'.format(removed_out_ts))

    for loc in sorted(removed_op_loc, reverse=True):
        op = sg['operators'][loc]
        if verbosity > 1:
            print('- Removing op loc={} op_idx={}'.format(loc, op['opcode_index']))
        del sg['operators'][loc]

    # clean the output list (tensor idx)
    n_list = []
    for ts in sg['outputs']:
        if ts not in removed_out_ts:
            n_list.append(ts)
    sg['outputs'] = n_list

    # create new output list (operator loc)
    add_loc = []
    for loc, op in enumerate(sg['operators']):
        if op['outputs'][0] in in_ts:
            add_loc.append(loc)
    add_outputs(data, add_loc, verbosity, overwrite, loc_anchors_tensor=loc_anchors)


def process(filepath, args, verbosity):
    """Entry point to process the input file"""

    is_json = False

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    split_fp = path.split(filepath)
    f_name = split_fp[1]
    f_name_ext = f_name.split('.')[-1]
    is_json = True if f_name_ext in ['json'] else False
    f_name = f_name.replace('.' + f_name.split('.')[-1],'')

    # Load the input file. TF Lite file is converted to JSON format
    print('Input file : {}'.format(filepath), flush=True)
    f_path_out_json = path.join(args.output,
                                f_name + '_mod.json')
    f_path_out_tflite = path.join(args.output,
                                  f_name + '_mod.tflite')
    if not is_json:
        # Create JSON file
        f_path_in_json  = path.join(args.output, f_name + '.json')
        print("Creating file : ", f_path_in_json, flush=True)
        toJSON(filepath, output=args.output, verbosity=verbosity)
        filepath = f_path_in_json

    data = load_json(filepath, verbosity)

    # Process the JSON file
    print('Processing (add={}, cut={}, extract={}, info={})...'.format(args.add, args.cut, args.extract, args.info), flush=True)

    if args.extract and not args.info:
        args.info =  args.extract

    print_node_info(data, args.info, verbosity, overwrite= not args.no_overwrite)

    if args.extract:
        print("")
        extract_attributes(data, args.extract, args.output, args.name, verbosity, overwrite= not args.no_overwrite)

    if not args.add and not args.cut and (args.extract or args.info):
        return

    data_n = data #json_min_max_rescale(data)

    cut_graph(data_n, args.cut, verbosity, overwrite= not args.no_overwrite)
    add_outputs(data_n, args.add, verbosity, overwrite= not args.no_overwrite, loc_anchors_tensor=None)
    clean_graph(data_n, verbosity)
    
    # Save the modified/patched JSON file
    print("Saving modified file : ", f_path_out_json, flush=True)

    data_n['description'] =  data_n['description'] + '(X-CUBE-AI) ' + args.name 
    if args.desc:
         data_n['description'] =  data_n['description'] + ' : ' + args.desc
    save_json(f_path_out_json, data_n)

    # Convert modified JSON to TF Lite file
    print("Creating TFLite file : ", f_path_out_tflite, flush=True)
    toTFlite(f_path_out_json, output=args.output, verbosity=verbosity)


def normalize_path(pathname):
    """Return a absolute and normalized pathname"""
    return os.path.realpath(os.path.normpath(os.path.expanduser(pathname)))



def main():
    """ script entry point """
    import argparse

    parser = argparse.ArgumentParser(description='Utility to patch a TF Lite file')
    parser.add_argument('file_in', type=str, help='TFLite/JSON file')
    parser.add_argument('--output', '-o', type=normalize_path, metavar='DIR',
                        nargs='?', default=_STR_DEFAULT_OUTPUT_DIR,
                        help="folder where generated files are saved")
    parser.add_argument('-d', '--desc', type=str, help='user STR description added in the file')
    parser.add_argument('-a','--add', nargs='+', type=int, metavar='LOC',
                        help='add output - index/location of the operator')
    parser.add_argument('-e','--extract', nargs='+', type=int, metavar='LOC',
                        help='extract attributes - index/location of the operator')
    parser.add_argument('-c','--cut', type=int, metavar='LOC',
                        help='cut a graph - index/location of the operator')
    parser.add_argument('-i','--info', nargs='+', type=int, metavar='LOC',
                        help='node info - index/location of the operator')
    parser.add_argument('--no-overwrite', action='store_true',
                        help='disable overwrite location process')
    parser.add_argument('-n','--name', nargs='?', type=str, metavar='STR',
                        default='network', help='used name for the extra data (c-level definition)')
    parser.add_argument('-v',
                        nargs='?', const=1,
                        type=int, choices=range(0, 3),
                        help="set verbosity level",
                        default=0)
    args = parser.parse_args()

    return process(args.file_in, args, args.v)

if __name__ == '__main__':
    sys.exit(main())
