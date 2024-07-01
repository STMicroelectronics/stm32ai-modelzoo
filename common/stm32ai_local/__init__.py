###################################################################################
#   Copyright (c) 2021 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
STMAIC - STM AI driver
"""

import logging
import os


from .__version__ import __author__, __copyright__, __license__, __version__

from .utils import set_log_level, STMAiVersion, STMAIC_LOGGER_NAME, STMAIC_DEBUG_ENV  # noqa:F401
from .stm_ai_tools import STMAiTools  # noqa:F401
from .stm32_tools import STM32_TOOLS as STM32Tools  # noqa:F401
from .stm32_tools import get_stm32_board_interfaces  # noqa:F401

from .options import STMAiCompileOptions
from .board_config import STMAiBoardConfig
from .utils import STMAICException, get_logger  # noqa:F401

from .session import cmd_load as load  # noqa:F401
from .compile import cmd_compile as compile  # pylint: disable=redefined-builtin
from .build import cmd_build as build
from .run import cmd_run as run


set_log_level(logging.DEBUG if os.environ.get(STMAIC_DEBUG_ENV, None) else logging.WARNING)


__all__ = (
    "__author__",
    "__copyright__",
    "__license__",
    "__version__",
    "STMAiVersion",
    "STMAiTools",
    "STMAiBoardConfig",
    "STMAiCompileOptions",
    "STMAIC_LOGGER_NAME",
    "STMAICException",
    "get_logger",
    "load",
    "compile",
    "build",
    "run"
)
