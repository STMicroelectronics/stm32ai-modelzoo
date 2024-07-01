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


class NetworkCInfoReader:
    """Helper class to read the generated <network>_c_graph.json"""

    def __init__(self, c_info_json_path: str, series: str):

        self._json_path = c_info_json_path
        self._dict = load_json_safe(self._json_path)

        # check JSON file version
        ver_ = self._dict['json_schema_version']
        if ver_ != '2.0':
            raise IOError(f'Network C graph JSON file version is invalid "{ver_}" instead "2.0"')

        self._parse(series.lower())

    def __getattr__(self, attr):
        try:
          return self._dict[attr]
        except:
          return self._dict['summary'][attr]

    def _parse(self, series: str):
        """Parse the json file"""  # noqa: DAR101,DAR201,DAR401

        # build ram info

        # No RAM and MACC info stored for now

        layers = []
        total_macc = 0
        for c_layer in self.graphs[0]['nodes']:
            # ram_in, ram_out = 0, 0
            # for tens in c_layer['inputs']:
            #     desc = _get_desc(tens)
            #     ram_in += desc.c_size
            #     ram_cont_min = max(ram_cont_min, desc.c_size)
            # for tens in c_layer['outputs']:
            #     desc = _get_desc(tens)
            #     ram_out += desc.c_size
            #     ram_cont_min = max(ram_cont_min, desc.c_size)
            # ram_no_overlay = ram_in + ram_out
            # ram_overlay = max(ram_in, ram_out)
            item = {
                'name': c_layer['name'],
                'm_id': c_layer['id'],
                'macc': c_layer['macc'],
                # 'ram': (ram_no_overlay, ram_overlay, ram_cont_min),
            }
            layers.append(item)
            total_macc = total_macc+c_layer['macc']

        weights_array = []
        for array in self.memory_pools:
            weights_array.append((array['id'], array['used_size_bytes']))

        activations_array = []
        for array in self.buffers:
            activations_array.append((array['id'], array['size_bytes']))

        self._dict['summary'] = {
            'c_name': self.environment['generated_model']['name'],
            'model_name': self.environment['tools'][0]['input_model']['name'],
            # 'model_fmt': self._dict.get('model_fmt', ''),
            'stm_ai_version': self.environment['tools'][0]['version'],
            'macc': total_macc,
            'weights': self.memory_footprint['weights'],
            'activations': self.memory_footprint['activations'],
            'io': self.memory_footprint['io'],
            # 'inputs_desc': [_get_desc(name, idx) for idx, name in enumerate(self.inputs)],
            # 'outputs_desc': [_get_desc(name, idx) for idx, name in enumerate(self.outputs)],
            'c_layers': layers,
            'weights_array': weights_array,
            'activations_array': activations_array,
            'series': self._dict.get('series', series),
            'type': self.environment['tools'][0]['input_model']['type'],
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
