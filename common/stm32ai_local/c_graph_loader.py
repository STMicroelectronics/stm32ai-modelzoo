###################################################################################
#   Copyright (c) 2022 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
STM AI driver - C graph loader
"""
import logging

from .utils import load_json_safe, STMAiMetrics, STMAiTensorInfo, STMAiVersion, _LOGGER_NAME_

logger = logging.getLogger(_LOGGER_NAME_)


class NetworkCGraphReader:
    """Helper class to read the generated <network>_c_graph.json"""

    def __init__(self, c_graph_json_path: str, series: str):

        self._json_path = c_graph_json_path
        self._dict = load_json_safe(self._json_path)

        # check JSON file version
        ver_ = self._dict['version']
        if ver_ != '1.2':
            raise IOError(f'Network C graph JSON file version is invalid "{ver_}" instead "1.2"')

        self._parse(series.lower())

    def __getattr__(self, attr):
        return self._dict[attr]

    def _parse(self, series: str):
        """Parse the json file"""  # noqa: DAR101,DAR201,DAR401

        # build the IO descriptors

        def _get_desc(name_, idx=-1):
            desc = {}
            desc['name'] = name_[:-len('_output')]
            for c_array in self.c_arrays:
                for tens in c_array['tensors']:
                    if tens['name'] == name_:
                        desc['shape'] = tuple(tens['shape'])
                        if 'items' in c_array:
                            desc['size'] = c_array['n_items']
                        else:
                            desc['size'] = c_array['size']
                        desc['c_type'] = c_array['c_type']
                        desc['c_size'] = c_array['c_size_in_byte']
                        desc['c_mem_pool'] = c_array['c_mem_pool']
                        if 'scale' in c_array:
                            desc['q_parm'] = {
                                'scales': c_array['scale'],
                                'zero_points': c_array['zeropoint']
                            }
                        else:
                            desc['q_parm'] = {}
                        break
                if 'shape' in desc:
                    break
            if not desc:
                raise IOError(f'Unable to build the description for "{name_}"')
            info = STMAiTensorInfo(
                name=desc['name'],
                idx=idx,
                size=desc['size'],
                shape=desc['shape'],
                c_size=desc['c_size'],
                c_type=desc['c_type'],
                c_mem_pool=desc['c_mem_pool'],
                quantization=desc['q_parm']
            )
            return info

        # build ram info

        layers = []
        ram_cont_min = 0
        for c_layer in self.c_layers:
            ram_in, ram_out = 0, 0
            for tens in c_layer['tensors']['inputs']:
                desc = _get_desc(tens)
                ram_in += desc.c_size
                ram_cont_min = max(ram_cont_min, desc.c_size)
            for tens in c_layer['tensors']['outputs']:
                desc = _get_desc(tens)
                ram_out += desc.c_size
                ram_cont_min = max(ram_cont_min, desc.c_size)
            ram_no_overlay = ram_in + ram_out
            ram_overlay = max(ram_in, ram_out)
            item = {
                'name': c_layer['name'],
                'm_id': c_layer['m_id'],
                'macc': c_layer['macc'],
                'rom': c_layer['rom'],
                'ram': (ram_no_overlay, ram_overlay, ram_cont_min),
            }
            if 'op_by_type' in c_layer:
                item['op'] = c_layer['op_by_type']
            layers.append(item)

        weights_array = []
        for array in self.weights.values():
            weights_array.append((array['pool_id'], array['pool_size']))

        activations_array = []
        for array in self.activations.values():
            activations_array.append((array['pool_id'], array['pool_size']))

        self._dict['summary'] = {
            'c_name': self.c_name,
            'model_name': self.model_name,
            'model_fmt': self._dict.get('model_fmt', ''),
            'stm_ai_version': STMAiVersion(self.stm_ai_version),
            'macc': self.macc,
            'weights': self.memory_footprint['weights'],
            'activations': self.memory_footprint['activations'],
            'io': self.memory_footprint['io'],
            'inputs_desc': [_get_desc(name, idx) for idx, name in enumerate(self.inputs)],
            'outputs_desc': [_get_desc(name, idx) for idx, name in enumerate(self.outputs)],
            'c_layers': layers,
            'weights_array': weights_array,
            'activations_array': activations_array,
            'series': self._dict.get('series', series),
            'type': self._dict.get('type', ''),
        }

        memory_footprint = self._dict.get('memory_footprint', None)
        if memory_footprint and 'stm32' in memory_footprint['series']:
            rt_layout = {
                'detailed': memory_footprint,
                'rt_ram': memory_footprint['kernel_ram'],
                'rt_flash': memory_footprint['kernel_flash']
            }
            self._dict['summary']['rt_layout'] = rt_layout
            self._dict['summary']['series'] = memory_footprint['series']
            if memory_footprint['series'] != series:
                logger.warning('"series" value is not coherent.. %s != %s', series,
                               memory_footprint['series'])

    def info(self):
        """Return a dict with the main data"""
        results = self._dict['summary']
        return results

    def add_rt_layout(self, desc, series):
        """Update summary with runtime memory footprint"""

        val_ = desc['filtered']
        rt_flash = val_['text'] + val_['rodata'] + val_['data']
        rt_flash -= self._dict['summary']['weights']
        rt_layout = {
            'detailed': desc,
            'rt_ram': val_['data'] + val_['bss'],
            'rt_flash': rt_flash,
        }
        self._dict['summary']['rt_layout'] = rt_layout
        self._dict['summary']['series'] = series

    def get_metrics(self, latency: float = 0.0):
        """Return namedtuple with the main metrcis"""
        weights_ = self.summary['weights']
        act_ = self.summary['activations']
        io_ = tuple(self.summary['io'])
        rt_ram, rt_flash = 0, 0
        if 'rt_layout' in self._dict['summary']:
            rt_ram = self._dict['summary']['rt_layout']['rt_ram']
            rt_flash = self._dict['summary']['rt_layout']['rt_flash']
        return STMAiMetrics(act_, io_, weights_, self.macc, rt_ram, rt_flash, latency)

    def __str__(self):
        """Return a summary of the uploaded file"""  # noqa: DAR101,DAR201,DAR401

        metrics = self.get_metrics()
        io_ = ':'.join([f'{v:,}' for v in metrics.io])

        msg_ = f'RAM={metrics.ram:,} IO={io_} WEIGHTS={metrics.weights:,} MACC={metrics.macc:,}'
        if 'rt_layout' in self._dict['summary']:
            msg_ += f' RT_RAM={metrics.rt_ram:,} RT_FLASH={metrics.rt_flash:,}'
        return msg_
