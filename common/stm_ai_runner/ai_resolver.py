###################################################################################
#   Copyright (c) 2021 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
Entry point to register a driver

Expected syntax for driver description/options for the connection

    [<domain>[:<option1>[:option2]]]

    domain:
        - None or 'serial' (default)
        - 'file' or valid file_path/directory
        - 'socket'

"""

import os


_DEFAULT_DOMAIN = 'serial'
_FILE_DOMAIN = 'file'
_APP_DOMAIN = 'app'
_LIB_DOMAIN = 'lib'
_SOCKET_DOMAIN = 'socket'
_ISPU_APP_DOMAIN = 'ispu-app'
_ISPU_TARGET_DOMAIN = 'serial-ispu'
_MPU_TARGET_DOMAIN = 'mpu'
_FVP_DOMAIN = 'fvp'


_SUPPORTED_EXEC_DOMAINS = (_DEFAULT_DOMAIN, _FILE_DOMAIN, _SOCKET_DOMAIN, _FVP_DOMAIN)


def is_valid_exec_domain(desc):
    """Indicates if the prefix is a valid domain"""  # noqa: DAR101,DAR201,DAR401
    first = desc.split(':')[0]
    return first in _SUPPORTED_EXEC_DOMAINS


def _default_resolver(domain, _):
    """Default resolver function"""  # noqa: DAR101,DAR201,DAR401
    if domain == _DEFAULT_DOMAIN or domain is None:
        return True
    return False


def _default_create(parent, desc):
    """Default create function"""  # noqa: DAR101,DAR201,DAR401
    from .serial_hw_drv import SerialHwDriver
    from .pb_mgr_drv import AiPbMsg

    return AiPbMsg(parent, SerialHwDriver()), desc


def _app_resolver(domain, desc):
    """App resolver function"""  # noqa: DAR101,DAR201,DAR401
    if domain == _APP_DOMAIN and desc is not None:
        from .x86_app_drv import X86AppDriver
        return X86AppDriver.is_valid(desc)
    return False


def _app_create(parent, desc):
    """App create function"""  # noqa: DAR101,DAR201,DAR401
    from .x86_app_drv import X86AppDriver
    return X86AppDriver(parent), desc


def _dll_resolver(domain, desc=None):
    """Default resolver function"""  # noqa: DAR101,DAR201,DAR401
    from .dll_mgr_drv import AiDllDriver

    if domain == _LIB_DOMAIN and desc is not None:
        res, _ = AiDllDriver.is_valid(desc)
        return res
    return False


def _dll_create(parent, desc):
    """Default create function"""  # noqa: DAR101,DAR201,DAR401
    from .dll_mgr_drv import AiDllDriver

    _, new_desc = AiDllDriver.is_valid(desc)

    return AiDllDriver(parent), new_desc


def _socket_resolver(domain, _):
    """Socket resolver function"""  # noqa: DAR101,DAR201,DAR401
    if domain == _SOCKET_DOMAIN:
        return True
    return False


def _socket_create(parent, desc):
    """Default create function"""  # noqa: DAR101,DAR201,DAR401
    from .socket_hw_drv import SocketHwDriver
    from .pb_mgr_drv import AiPbMsg

    return AiPbMsg(parent, SocketHwDriver()), desc


def _ispu_app_resolver(domain, desc):
    """ispu app resolver function"""  # noqa: DAR101,DAR201,DAR401
    if domain == _ISPU_APP_DOMAIN and desc is not None:
        from .ispu_app_drv import IspuAppDriver
        return IspuAppDriver.is_valid(desc)
    return False


def _ispu_app_create(parent, desc):
    """ispu app create function"""  # noqa: DAR101,DAR201,DAR401
    from .ispu_app_drv import IspuAppDriver
    return IspuAppDriver(parent), desc


def _ispu_target_resolver(domain, desc):
    """ispu target resolver function"""  # noqa: DAR101,DAR201,DAR401
    if domain == _ISPU_TARGET_DOMAIN and desc is not None:
        return True
    return False


def _ispu_target_create(parent, desc):
    """ispu target create function"""  # noqa: DAR101,DAR201,DAR401
    from .ispu_target_drv import IspuTargetDriver
    return IspuTargetDriver(parent), desc

def _mpu_target_resolver(domain, desc):
    """mpu target resolver function"""  # noqa: DAR101,DAR201,DAR401
    if domain == _MPU_TARGET_DOMAIN and desc is not None:
        return True
    return False

def _mpu_target_create(parent, desc):
    """mpu target create function"""  # noqa: DAR101,DAR201,DAR401
    from .mpu_target_drv import MpuTargetDriver
    return MpuTargetDriver(parent), desc

def _fvp_resolver(domain, _):
    """SVP resolver function"""  # noqa: DAR101,DAR201,DAR401
    if domain == _FVP_DOMAIN:
        return True
    return False


def _fvp_create(parent, desc):
    """Default create function"""  # noqa: DAR101,DAR201,DAR401
    from .fvp_hw_drv import FvpHwDriver
    from .pb_mgr_drv import AiPbMsg

    return AiPbMsg(parent, FvpHwDriver()), desc


_DRIVERS = {
    _DEFAULT_DOMAIN: (_default_resolver, _default_create),  # default
    _APP_DOMAIN: (_app_resolver, _app_create),
    _LIB_DOMAIN: (_dll_resolver, _dll_create),
    _SOCKET_DOMAIN: (_socket_resolver, _socket_create),
    _ISPU_APP_DOMAIN: (_ispu_app_resolver, _ispu_app_create),
    _ISPU_TARGET_DOMAIN: (_ispu_target_resolver, _ispu_target_create),
    _MPU_TARGET_DOMAIN: (_mpu_target_resolver, _mpu_target_create),
    _FVP_DOMAIN: (_fvp_resolver, _fvp_create),
}


def _fix_windows_paths(desc):

    split_ = desc.split(':')

    if len(split_) == 1:
        return split_

    # TODO: change delimiter to avoid confusion with Windows paths
    new_split = []
    split_idx = 0
    while split_idx < len(split_) - 1:
        token = split_[split_idx]
        if len(token) == 1 and token.lower() in "abcdefghijklmnopqrstuvwxyz":
            next_token = split_[split_idx + 1]
            if next_token[0] in ["\\", "/"]:
                token += f":{next_token}"
                split_idx += 1
        new_split.append(token)
        split_idx += 1
    return new_split


def ai_runner_resolver(parent, desc):
    """Return drv instance"""  # noqa: DAR101,DAR201,DAR401
    if desc is not None and isinstance(desc, str):
        desc = desc.strip()
        split_ = _fix_windows_paths(desc)

        nb_elem = len(split_)

        domain = None
        if nb_elem == 2 and split_[0] == 'app':
            domain = _APP_DOMAIN
            desc = desc[4:]
        elif nb_elem == 2 and split_[0] == 'ispu-app':
            domain = _ISPU_APP_DOMAIN
            desc = desc[9:]
        elif nb_elem == 2 and split_[0] == 'mpu':
            domain = _MPU_TARGET_DOMAIN
            desc = desc[4:]
        # only valid file or directory is passed
        elif os.path.isfile(desc) or os.path.isdir(desc) or os.path.isdir(os.path.dirname(desc)):
            domain = _LIB_DOMAIN
        # domain is considered
        elif nb_elem >= 1 and len(split_[0]) > 0:
            domain = split_[0].lower()
            desc = desc[len(domain + ':'):]
        # ':' is passed as first character
        elif len(split_[0]) == 0:
            domain = _DEFAULT_DOMAIN
            desc = desc[1:]

        for drv_ in _DRIVERS:
            if _DRIVERS[drv_][0](domain, desc):
                return _DRIVERS[drv_][1](parent, desc)
        err_msg_ = f'invalid/unsupported "{domain}:{desc}" descriptor'
        return None, err_msg_

    else:
        return _DRIVERS[_DEFAULT_DOMAIN][1](parent, desc)
