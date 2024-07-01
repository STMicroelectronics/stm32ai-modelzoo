###################################################################################
#   Copyright (c) 2022 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
STM AI driver - Session definition
"""

import os
import logging
import shutil
from typing import Optional, List, Union
from mako.template import Template


from .utils import STMAICFileError, _LOGGER_NAME_
from .utils import STMAiMetrics, STMAiVersion, STMAiModelInfo
from .c_graph_loader import NetworkCGraphReader
from .stm_ai_tools import STMAiTools
from .board_config import STMAiBoardConfig
from .options import STMAiCompileOptions


# pylint: disable=invalid-name
logger = logging.getLogger(_LOGGER_NAME_)


class STMAiSession():
    """
    Object to handle a working session. Simple entry point to
    store the state and the outputs of the different operations.
    """

    def __init__(
            self,
            model_path: Union[str, List[str], None],
            tools: Union[STMAiTools, None] = None,
            session_name: Optional[str] = None,
            workspace_dir: Optional[str] = None
    ):
        """Create a working session"""

        self._model_path = None  # type: Union[str, List[str], None]
        if model_path:
            if isinstance(model_path, str):
                model_path = [model_path]
            for file_path in model_path:
                if not os.path.isfile(file_path):
                    raise STMAICFileError(f'"{file_path}" is not a regular file!')
            self._model_path = model_path
            if not session_name:
                session_name = os.path.split(model_path[0])[1].replace('.', '_')
            self._session_name = session_name
        else:
            self._session_name = 'none'
        if workspace_dir is None:
            self._workspace_path = os.path.join('.stmaic', self._session_name)
        else:
            self._workspace_path = workspace_dir

        self._cgraph = None  # type: Union[NetworkCGraphReader, None]
        self._tools = tools  # type: Union[STMAiTools, None]
        self._board_config = None  # type: Union[STMAiBoardConfig, None]
        self._options = None  # type: Union[STMAiCompileOptions, None]
        self._latency = 0.0  # type: float
        self._series = ''  # type: str

    @property
    def is_empty(self):
        """Indicate if a model file is registered or not"""
        return self._model_path is None

    @property
    def model_path(self):
        """Return the path of the model"""
        return self._model_path

    @property
    def name(self):
        """Return the name of the session"""
        return self._session_name

    @property
    def c_name(self):
        """Return c-name of the generated model"""
        if self._cgraph:
            return self._cgraph.summary['c_name']
        if self._options:
            return self._options.name
        return 'network'

    @property
    def series(self):
        """Return the series"""
        if self._board_config:
            return self._board_config.config.series
        return ''

    @property
    def options(self):
        """Return the options"""
        return self._options

    @property
    def tools(self):
        """Return the STM.AI tools"""
        return self._tools

    @property
    def board(self):
        """Return the board configuration"""
        return self._board_config

    @property
    def stm_ai_version(self):
        """Return the STM AI tools associated"""
        b_ver = t_ver = STMAiVersion(version="0.0.0")
        if self._board_config:
            b_ver = STMAiVersion(self._board_config.config.stm_ai_version)
        if self._tools:
            t_ver = STMAiVersion(self._tools.version)
        if t_ver == b_ver:
            return t_ver
        elif t_ver.is_valid() and b_ver.is_valid():
            logger.warning(f'Requested version for tools {t_ver} is not coherent with the board {b_ver}')
        return t_ver if t_ver.is_valid() else b_ver

    @property
    def workspace(self):
        """Return the worspace directory"""
        return self._workspace_path

    @property
    def generated_dir(self):
        """Return the directory where the files are generated"""
        return os.path.join(self._workspace_path, 'generated')

    @property
    def build_dir(self):
        """Return the build directory"""
        return os.path.join(self._workspace_path, 'build')

    @property
    def metrics(self):
        """Return the main metrics"""
        if self._cgraph:
            return self._cgraph.get_metrics(self._latency)
        return STMAiMetrics()

    @property
    def info(self):
        """Return main info"""
        if not self._cgraph:
            return STMAiModelInfo()
        c_info = self._cgraph.info()
        info = STMAiModelInfo(
            c_name=c_info['c_name'],
            name=c_info['model_name'],
            type=c_info['type'],
            format=c_info['model_fmt'],
            metrics=self.metrics,
            inputs=c_info['inputs_desc'],
            outputs=c_info['outputs_desc'],
            series=c_info['series'],
            stm_ai_version=c_info['stm_ai_version'],
        )
        return info

    @property
    def details(self):
        """Return a dict with details of the C-model"""
        if self._cgraph:
            info = self._cgraph.info()
            info['options'] = self.options
            info['board'] = self.board
            info['metrics'] = self.metrics._asdict()
            return info
        return {}

    def summary(self, pr_f=None):
        """Display a summary of the session"""
        info_ = self.info
        pr_f = pr_f if pr_f else print  # noqa:T202
        title = f'Session "{self.name}"'
        pr_f(f'\n{title}')
        pr_f('-' * len(title))
        pr_f(f' model name : "{info_.name}"')
        pr_f(f' model type : {info_.type} (fmt="{info_.format}")')
        pr_f(f' c-name     : {info_.c_name} (series="{info_.series}")')
        pr_f(f' metrics    : {str(self)}')
        options = self.options.used_options()
        options = options.replace('--dll', '').replace('--quiet', '').strip()
        pr_f(f' options    : {options}')
        pr_f(f' tools      : {self.tools}')

        def pr_f_io(tag, tensors):
            for tens in tensors:
                ext = ''
                if tens.quantization and '1_t' not in tens.c_type:
                    ext = ', s={:.06f}, zp={}'.format(tens.quantization['scales'][0],
                                                      tens.quantization['zero_points'][0])
                tag = f'{tag}.{tens.idx}'
                pr_f(f' {tag:8s}   : {tens.name}, {tens.shape}, {tens.c_type}{ext}')

        pr_f_io('input', info_.inputs)
        pr_f_io('output', info_.outputs)
        pr_f('')

    def clean_workspace(self):
        """Clean the workspace/temporary build-dir(s)"""

        inspector_dir = os.path.join(self.workspace, f'inspector_{self.c_name}')
        if os.path.isdir(inspector_dir):
            shutil.rmtree(inspector_dir, ignore_errors=True)

        if os.path.isdir(self.generated_dir):
            shutil.rmtree(self.generated_dir, ignore_errors=True)

        if os.path.isdir(self.build_dir):
            shutil.rmtree(self.build_dir, ignore_errors=True)

    def set_tools(self, tools: Union[STMAiTools, None] = None):
        """Set the STM AI tools"""
        self._tools = tools if tools is not None else STMAiTools()

    def set_options(self, options: Optional[Union[STMAiCompileOptions, None]] = None):
        """Set the Compile Options"""
        self._options = options

    def set_board(self, board_config: STMAiBoardConfig):
        """Set the board configuration"""
        self._board_config = board_config

    def set_c_graph(self, c_graph: NetworkCGraphReader):
        """Set the c_graph description"""
        self._cgraph = c_graph

    def c_graph(self):
        """Return the generated c_graph as a dict"""
        if self._cgraph:
            return self._cgraph
        return None

    def set_latency(self, value):
        """Store the measured latency (ms)"""
        self._latency = value

    def renderer_params(self):
        """Return a dict with the c-model parameters
           for renderer engine"""
        if not self._cgraph:
            return {}
        c_g = self._cgraph.info()
        render_params = {
            'name': c_g['c_name'],
            'inputs': [el._asdict() for el in c_g['inputs_desc']],
            'allocate_inputs': c_g['inputs_desc'][0].c_mem_pool != '',
            'outputs': [el._asdict() for el in c_g['outputs_desc']],
            'allocate_outputs': c_g['outputs_desc'][0].c_mem_pool != '',
            'activations': c_g['activations_array'],
        }
        return render_params

    def render(self, tpl_file: str, dst_file: str):
        """Apply the renderer engine to the template file"""

        render_params = self.renderer_params()
        if not render_params:
            return

        template = Template(filename=tpl_file)
        res = template.render(**render_params)

        with open(dst_file, 'w', newline='\n') as f:
            f.write(res)

    def results(self, mode='list', sep=' '):
        """Return results"""
        if self._cgraph and mode in ['csv', 'list']:
            metrics = self.metrics
            headers = ['session', *metrics._asdict().keys()]
            values = [self.name, *metrics._asdict().values()]
            if mode == 'csv':
                headers = sep.join(headers)
                values = sep.join([str(val) for val in values])
                return headers, values
            return headers, values
        return [], []

    def __str__(self):
        """Return a short summary"""
        if self._cgraph:
            return str(self._cgraph) + f' LATENCY={self._latency:.03f}'
        if self._model_path:
            return 'attached model files: {}'.format(', '.join(self._model_path))
        # Session is "empty", no model is attached
        return ''


def cmd_load(model_path: Union[str, List[str], None],
             tools: Union[STMAiTools, None] = None,
             session_name: Optional[str] = None,
             workspace_dir: Optional[str] = None) -> STMAiSession:
    """Create a working session associated to a model file.

    Parameters
    ----------
    model_path : str, list[str] (optional)
        The path or list of path for the model file.

    tools : STMAiTools (optional)
        Optional STM.AI tools used for the session

    session_name : str (optional)
        name of the session. If not defined, a name is
        created with the name of the provided file. This name will be
        used to create a specific directory into the workspace directory if
        no workspace_dir is defined.

    workspace_dir : str (optional)
        specific the path of the worspace directory. If not defined,
        `.stmaic` directory will be created in the ${PWD} directory.

    Returns
    -------
    STMAiSession
        created session

    """
    msg_ = f'loading model.. model_path="{model_path}"'
    logger.info(msg_)

    return STMAiSession(model_path, tools, session_name, workspace_dir)
