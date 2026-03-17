###################################################################################
#   Copyright (c) 2021 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
AI Hw Driver - fvp/Corstone client

version: 0.1

The client is considered as a simple bridge/relay (blocking mode).
FVP platfom should be ready to manage the proto-buff messages (binary format), no
extra or specific messags is added.

- add timeout support for read/write operations

"""

import time as t
import socket

import iris.debug

from .ai_runner import AiHwDriver
from .ai_runner import HwIOError


def fvp_get_com_settings(desc):
    """
    Parse the desc parameter to retrieve the hostname and the port.
    Can be a "str" or directly an "int" if only the port is passed.

    Example:

        'localhost:10000'       ->  'localhost'  10000
        '10000'                 ->  'localhost'  10000
        ':10000                 ->  'localhost'  10000
        'localhost'             ->  'localhost'  5000
        ':localhost             ->  'localhost'  10000
        '127.0.0.1:10000'       ->  '127.0.0.1'  10000
        '127.0.0.1:'            ->  '127.0.0.1'  5000

    Parameters
    ----------
    desc
        str with the description of the hostname/port

    Returns
    -------
    tuple
        3-tuple with the hostname, port and err msg.
        None hostname is returned if the hostname is invalid.

    """
    # default values
    hostname_ = 'localhost'  # 127.0.0.1
    port_ = int(5000)
    iris_port_ = int(7100)
    msg_ = ''

    if desc is not None and isinstance(desc, int):
        return hostname_, int(desc), msg_

    if desc is None or not isinstance(desc, str):
        return hostname_, port_, msg_

    if 'kill-on-exist' in desc:
        desc = desc.replace('kill-on-exist', '')

    desc = desc.split(':')
    port_set = False
    for _d in desc:
        if _d:
            try:
                _d = int(_d)
            except (ValueError, TypeError):
                hostname_ = _d
            else:
                if not port_set:
                    port_ = _d
                    port_set = True
                else:
                    iris_port_ = _d

    try:
        socket.gethostbyname(hostname_) == hostname_
    except socket.gaierror as exc_:
        msg_ = 'Invalid hostname: {} ({})'.format(hostname_, str(exc_))
        hostname_ = None
        port_ = 0

    return (hostname_, port_, iris_port_, msg_)


class FvpHwDriver(AiHwDriver):
    """Low-level IO driver - Client socket"""

    def __init__(self):
        """Constructor"""
        self._hostname = None
        self._port = 0
        self._iris_model = None
        self._iris_cpu = None
        self._kill_on_exist = False
        super().__init__()

    def get_config(self):
        """"
        Return a dict with used configuration

        Returns
        -------
        dict
            specific dictionary with the used configuration
        """
        return {
            'hostname': self._hostname,
            'port': self._port
        }

    def _connect(self, desc=None, **kwargs):
        """
        Create and connect a client socket (family=AF_INET, type=SOCK_STREAM)..

        Parameters
        ----------
        desc
            str with the hostname/port description
        kwargs
            arbitrary keyworded parameters

        Returns
        -------
        bool
            True if connection is created and valid. False indicates
            un-valid run-time

        Raises
        ------
        HwIOError
            invalid hostname/port or the connection has been refused
        """
        self._hostname, self._port, self._iris_port, msg_err = fvp_get_com_settings(desc)
        if self._hostname is None:
            raise HwIOError(msg_err)

        self._iris_model = iris.debug.NetworkModel(host="localhost", port=self._iris_port)
        self._iris_cpu = self._iris_model.get_cpus()[0]
        self._kill_on_exist = 'kill-on-exist' in desc

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        n_retry = 4
        while n_retry:
            try:
                sock.connect((self._hostname, self._port))
            except (ConnectionRefusedError, InterruptedError) as exc_:
                n_retry -= 1
                if not n_retry:
                    raise HwIOError('{}'.format(exc_))
            else:
                break
        t.sleep(0.2)

        self._hdl = sock
        if hasattr(self._parent, 'is_alive') and self._parent.is_alive():
            self._hdl = sock
        else:
            self._disconnect()

        return self.is_connected

    def _disconnect(self):
        """Close the connection"""  # noqa: DAR101,DAR201,DAR401
        if self._hdl is not None:
            self._hdl.close()
        self._hdl = None
        if self._iris_model:
            self._logger.debug('Release the FVP model (kill-on-exist:{})'.format(self._kill_on_exist))
            if self._kill_on_exist:
                self._iris_model.release(True)

    def _read(self, size, timeout=0):
        """Read data from the connected device"""  # noqa: DAR101,DAR201,DAR401
        res = self._hdl.recv(size)
        return res

    def _write(self, data, timeout=0):
        """Send data to the socket"""  # noqa: DAR101,DAR201,DAR401
        res = None
        for elem in data:
            self._hdl.sendall(elem.to_bytes(1, 'big'))
            self._hdl.recv(1)
        return len(data) if res is None else 0

    def _write_memory(self, target_add, data, timeout=0):
        """write memory"""  # noqa: DAR101,DAR201,DAR401
        if data is None and self._iris_cpu:
            # service is available
            return 1
        self._logger.info('direct memory write {} / {}'.format(hex(target_add), len(data)))
        # Split large writes
        _chunckWriteMax = 1228800  # maximum size seen as correcly written in one call
        _currPos = 0
        while (len(data) - _currPos) > 0:
            try:
                _size = min(len(data) - _currPos, _chunckWriteMax)
                self._logger.info('---> direct memory write {} / {} {}'.format(
                    hex(target_add + _currPos),
                    len(bytearray(data[_currPos:_currPos + _size])),
                    _size))
                self._iris_cpu.write_memory(target_add + _currPos,
                                            bytearray(data[_currPos:_currPos + _size]),
                                            size=1,
                                            count=len(data[_currPos:_currPos + _size]))
                _currPos += _size
            except Exception as err:
                self._logger.info(f"Exception during write {err} {len(data[_currPos:_currPos+_size])}"
                                  f"bytes @ {hex(target_add+_currPos)}")
                raise HwIOError(err)

        return len(data)

    def short_desc(self, full: bool = True):
        """Report a human description of the connection state"""  # noqa: DAR101,DAR201,DAR401
        desc = 'FVP:' + str(self._hostname) + ':' + str(self._port)
        if full:
            desc += ':connected' if self.is_connected else ':not connected'
        return desc


if __name__ == '__main__':
    pass
