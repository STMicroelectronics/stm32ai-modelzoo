###################################################################################
#   Copyright (c) 2024 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
Generic interpreter (experimental)
"""

import logging
import os
from pathlib import Path
from typing import List, Optional, Any, NamedTuple, Union, Dict
from enum import Enum
from abc import ABC, abstractmethod

import numpy as np


from .ai_runner import AiRunner, AiRunnerSession, AiTensorDesc, AiTensorType
from .utils import get_logger


class AiRuntimeType(Enum):
    """AiRuntime type"""
    TARGET = 0
    SIMULATOR = 1
    HOST = 2

    def __repr__(self):
        """."""  # noqa: DAR201
        return self.name

    def __str__(self):
        """."""  # noqa: DAR201
        return self.name


class AiDeviceDesc(NamedTuple):
    """Class to describe the device"""
    device: str = ''
    desc: str = ''
    id: str = ''
    system: str = ''
    attrs: Dict = {}


class AiRuntimeDesc(NamedTuple):
    """Class to describe the AI Runtime"""
    rt_type: AiRuntimeType = AiRuntimeType.HOST
    name: str = ''
    protocol: str = ''
    capabilities: List[Any] = []
    device: Optional[AiDeviceDesc] = None
    rt_lib_desc: str = ''
    rt_lib_version: str = ''


class AiRunnerInterpreterBase(ABC):
    """Base model interpreter"""

    def __init__(self, model_path: Union[Path, str], logger: logging.Logger):
        """Create a model interpreter"""  # noqa: DAR101,DAR201,DAR401
        self._name: str = ''
        self._model: Union[Path, str] = model_path
        self._inputs: List[AiTensorDesc] = []
        self._outputs: List[AiTensorDesc] = []
        self._interpreter: Optional[Any] = None
        self._logger = logger

    @property
    def is_valid(self) -> bool:
        """Indicate if the interpreter is ready/valid"""
        # noqa: DAR101,DAR201,DAR401
        return self._interpreter is not None

    @property
    def name(self) -> str:
        """Name of the model"""
        return self._name

    @abstractmethod
    def _get_inputs(self) -> List[AiTensorDesc]:
        pass

    @abstractmethod
    def _get_outputs(self) -> List[AiTensorDesc]:
        pass

    @abstractmethod
    def _invoke(self, inputs: Union[np.ndarray, List[np.ndarray]]) -> List[np.ndarray]:
        pass

    @abstractmethod
    def _reset(self) -> bool:
        pass

    @abstractmethod
    def _desc(self) -> str:
        pass

    def get_inputs(self) -> List[AiTensorDesc]:
        """Return input descriptions"""  # noqa: DAR101,DAR201,DAR401
        if not self.is_valid:
            return []
        return self._get_inputs()

    def get_outputs(self) -> List[AiTensorDesc]:
        """Return input descriptions"""  # noqa: DAR101,DAR201,DAR401
        if not self.is_valid:
            return []
        return self._get_outputs()

    def invoke(self, inputs: Union[np.ndarray, List[np.ndarray]]) -> List[np.ndarray]:
        """Invoke the interpreter"""  # noqa: DAR101,DAR201,DAR401
        if not self.is_valid:
            return []
        return self._invoke(inputs)

    def reset(self) -> bool:
        """Reset the interpreter"""  # noqa: DAR101,DAR201,DAR401
        if not self.is_valid:
            return False
        return self._reset()

    def __str__(self):
        """Return short description of the instance"""  # noqa: DAR101,DAR201,DAR401
        return self._desc()


class AiRunnerInterpreterTFlite(AiRunnerInterpreterBase):
    """Interpreter for TFlite file"""

    def __init__(self, model_path: Union[Path, str], logger: logging.Logger, **kwargs):
        """Create an instance of the TFlite interpreter"""  # noqa: DAR101,DAR201,DAR401

        model_path = str(model_path)
        super(AiRunnerInterpreterTFlite, self).__init__(model_path, logger)
        self._mode: str = kwargs.pop('mode', '')
        self._short_desc: str = ''
        self._name = Path(self._model).stem

        self._logger.debug("-> Loading '%s' file (mode=%s)...",
                           self._model, self._mode)

        try:
            import warnings  # import_outside_toplevel: ignore
            warnings.filterwarnings("ignore")
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            logging.getLogger("tensorflow").setLevel(logging.ERROR)
            import tensorflow as tf
        except (ImportError, ModuleNotFoundError) as exc_:
            msg_ = "tensorflow module is not installed, please install it"
            self._logger.warning(msg_)
            exc_.msg = exc_.msg + f'\n {msg_}'
            raise  # re-raise current exception

        self._short_desc = f'tf.lite.Interpreter(v{tf.__version__}): model_path={self._model}'

        if self._mode and 'no-kref' in self._mode:
            exp_resolve_type = tf.lite.experimental.OpResolverType.AUTO
        else:
            exp_resolve_type = tf.lite.experimental.OpResolverType.BUILTIN_REF

        interp_ = tf.lite.Interpreter(model_path=self._model,
                                      experimental_op_resolver_type=exp_resolve_type)

        interp_.allocate_tensors()
        self._inputs_raw = interp_.get_input_details()
        self._outputs_raw = interp_.get_output_details()
        self._interpreter: tf.lite.Interpreter = interp_

        self._logger.debug(str(self))
        for idx, io_desc_ in enumerate(self.get_inputs()):
            self._logger.debug(f'IO.{idx:02d}: {io_desc_}')
        for idx, io_desc_ in enumerate(self.get_outputs()):
            self._logger.debug(f'IO.{idx:02d}: {io_desc_}')

        self._logger.debug(f"<- done - {self._name}")

    def _get_inputs(self) -> List[AiTensorDesc]:
        """Return input descriptors"""  # noqa: DAR101,DAR201,DAR401
        descs_ = []
        for desc_ in self._inputs_raw:
            if len(desc_['quantization_parameters']['scales']):
                scale = [np.float32(v) for v in desc_['quantization_parameters']['scales']]
                zp = [np.int32(v) for v in desc_['quantization_parameters']['zero_points']]
            else:
                scale, zp = [np.float32(0.0)], [np.int32(0)]
            item = AiTensorDesc(
                iotype=AiTensorType.INPUT,
                name=desc_['name'],
                shape=tuple(desc_['shape']),
                dtype=desc_['dtype'],
                scale=scale,
                zero_point=zp,
            )
            descs_.append(item)
        return descs_

    def _get_outputs(self) -> List[AiTensorDesc]:
        """Return input descriptors"""  # noqa: DAR101,DAR201,DAR401
        descs_ = []
        for desc_ in self._outputs_raw:
            if len(desc_['quantization_parameters']['scales']):
                scale = [np.float32(v) for v in desc_['quantization_parameters']['scales']]
                zp = [np.int32(v) for v in desc_['quantization_parameters']['zero_points']]
            else:
                scale, zp = [np.float32(0.0)], [np.int32(0)]
            item = AiTensorDesc(
                iotype=AiTensorType.OUTPUT,
                name=desc_['name'],
                shape=tuple(desc_['shape']),
                dtype=desc_['dtype'],
                scale=scale,
                zero_point=zp,
            )
            descs_.append(item)
        return descs_

    def _invoke(self, inputs: Union[np.ndarray, List[np.ndarray]]) -> List[np.ndarray]:
        """Perform the inference"""  # noqa: DAR101,DAR201,DAR401
        if len(inputs) != len(self._inputs_raw):
            return []

        results_ = []
        for desc_, din_ in zip(self._inputs_raw, inputs):
            self._interpreter.set_tensor(desc_['index'], din_)
        self._interpreter.invoke()
        for desc_ in self._outputs_raw:
            results_.append(self._interpreter.get_tensor(desc_['index']))

        return results_

    def _reset(self):
        """Reset the state of the interpreter"""  # noqa: DAR101,DAR201,DAR401
        self._interpreter.reset_all_variables()

    def _desc(self) -> str:
        """Return shordt description of the instance"""  # noqa: DAR101,DAR201,DAR401
        return self._short_desc


class AiRunnerInterpreterStAi(AiRunnerInterpreterBase):
    """Interpreter for ST.AI runtime"""

    def __init__(self, model_path: Union[AiRunner, AiRunnerSession, Path, str],
                 logger: logging.Logger, **kwargs):
        """Create/Use an instance of AiRunner"""  # noqa: DAR101,DAR201,DAR401
        super(AiRunnerInterpreterStAi, self).__init__('', logger)
        self._name = kwargs.pop('name', 'network')

        self._logger.debug("-> Loading '%s'..", model_path)

        ai_runner_: Union[AiRunner, AiRunnerSession]
        model_: Optional[str]
        if isinstance(model_path, (Path, str)):
            model_ = str(model_path)
            ai_runner_ = AiRunner(logger=logger)
            ai_runner_.connect(model_)
        else:
            ai_runner_ = model_path
            model_ = ai_runner_.name

        self._model = str(model_)
        msg_ = '<unconnected>'
        if ai_runner_.is_connected:
            self._interpreter: Union[AiRunner, AiRunnerSession] = ai_runner_
            msg_ = str(ai_runner_)

        self._logger.debug("is connected %s", ai_runner_.is_connected)
        self._short_desc = f'AiRunner(v{AiRunner.version()}): {msg_}'
        self._logger.debug("<- done")

    def _get_inputs(self) -> List[AiTensorDesc]:
        """Return input descriptors"""  # noqa: DAR101,DAR201,DAR401
        return self._interpreter.get_inputs()

    def _get_outputs(self) -> List[AiTensorDesc]:
        """Return input descriptors"""  # noqa: DAR101,DAR201,DAR401
        return self._interpreter.get_outputs()

    def _invoke(self, inputs: Union[np.ndarray, List[np.ndarray]]) -> List[np.ndarray]:
        """Perform the inference"""  # noqa: DAR101,DAR201,DAR401
        if len(inputs) != len(self._interpreter.get_inputs()):
            return []
        results_, _ = self._interpreter.invoke(inputs, mode=AiRunner.Mode.IO_ONLY)
        return results_

    def _reset(self):
        """Reset the state of the interpreter"""  # noqa: DAR101,DAR201,DAR401
        return True

    def _desc(self) -> str:
        """Return shordt description of the instance"""  # noqa: DAR101,DAR201,DAR401
        return self._short_desc


class AiRunnerInterpreter():
    """Generic interpreter"""

    def __init__(self, model_path: Union[AiRunner, AiRunnerSession, Path, str], **kwargs):
        """Create a model interpreter"""  # noqa: DAR101,DAR201,DAR401
        logger_: Optional[logging.Logger] = kwargs.pop('logger', None)
        debug_: bool = kwargs.pop('debug', False)
        verbosity_: bool = kwargs.pop('verbosity', False)
        self._interp: AiRunnerInterpreterBase

        if logger_ is None:
            lvl_ = logging.DEBUG if debug_ else logging.INFO if verbosity_ else logging.WARNING
            logger_ = get_logger(name=self.__class__.__name__, level=lvl_)

        if isinstance(model_path, (str, Path)):
            if os.path.isfile(Path(model_path)):
                _, ext = os.path.splitext(Path(model_path))
                if 'tflite' in ext:
                    self._interp = AiRunnerInterpreterTFlite(model_path,
                                                             logger=logger_, **kwargs)
            else:
                self._interp = AiRunnerInterpreterStAi(model_path,
                                                       logger=logger_, **kwargs)
        elif isinstance(model_path, (AiRunner, AiRunnerSession)):
            self._interp = AiRunnerInterpreterStAi(model_path,
                                                   logger=logger_, **kwargs)
        else:
            self._interp = None

    @property
    def is_valid(self):
        """Indicate if the interpreter is valid/ready"""
        # noqa: DAR101,DAR201,DAR401
        return self._interp is not None

    def get_inputs(self) -> List[AiTensorDesc]:
        """Return input descriptions"""  # noqa: DAR101,DAR201,DAR401
        if not self.is_valid:
            return []
        return self._interp.get_inputs()

    def get_outputs(self) -> List[AiTensorDesc]:
        """Return input descriptions"""  # noqa: DAR101,DAR201,DAR401
        if not self.is_valid:
            return []
        return self._interp.get_outputs()

    def invoke(self, inputs: Union[np.ndarray, List[np.ndarray]]) -> List[np.ndarray]:
        """Invoke the interpreter"""  # noqa: DAR101,DAR201,DAR401
        if not self.is_valid:
            return []
        return self._interp.invoke(inputs)

    def reset(self) -> bool:
        """Reset the interpreter"""  # noqa: DAR101,DAR201,DAR401
        if not self.is_valid:
            return False
        return self._interp.reset()

    def __str__(self):
        """Return short description of the instance"""  # noqa: DAR101,DAR201,DAR401
        if not self.is_valid:
            return '<undefined>'
        return str(self._interp)
