###################################################################################
#   Copyright (c) 2021 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
STM AI runner - AI Hw Driver - socket client

version: 0.1

The server is considered as a simple bridge/relay (blocking mode).
Server should be ready to manage the proto-buff messages (binary format), no
extra or specific messags is added.

- add timeout support for read/write operations

"""

import time as t
import socket

from .ai_runner import AiHwDriver
from .ai_runner import HwIOError


def socket_get_com_settings(desc):
    """
    Parse the desc parameter to retrieve the hostname and the port.
    Can be a "str" or directly an "int" if only the port is passed.

    Example:

        'localhost:10000'       ->  'localhost'  10000
        '10000'                 ->  'localhost'  10000
        ':10000                 ->  'localhost'  10000
        'localhost'             ->  'localhost'  10000
        ':localhost             ->  'localhost'  10000
        '127.0.0.1:10000'       ->  '127.0.0.1'  10000
        '127.0.0.1:'            ->  '127.0.0.1'  10000

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
    port_ = int(10000)
    msg_ = ''

    if desc is not None and isinstance(desc, int):
        return hostname_, int(desc), msg_

    if desc is None or not isinstance(desc, str):
        return hostname_, port_, msg_

    desc = desc.split(':')
    for _d in desc:
        if _d:
            try:
                _d = int(_d)
            except (ValueError, TypeError):
                hostname_ = _d
            else:
                port_ = _d

    try:
        socket.gethostbyname(hostname_) == hostname_
    except socket.gaierror as exc_:
        msg_ = 'Invalid hostname: {} ({})'.format(hostname_, str(exc_))
        hostname_ = None
        port_ = 0

    return (hostname_, port_, msg_)


class SocketHwDriver(AiHwDriver):
    """Low-level IO driver - Client socket"""

    def __init__(self):
        """Constructor"""
        self._hostname = None
        self._port = 0
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

    @staticmethod
    def test_socket_access(hostname, port):
        """
        Test if the server is active/alive

        Parameters
        ----------
        hostname
            name of the host or ip
        port
            port number

        Returns
        -------
        bool
            True is active
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((hostname, port))
        except (ConnectionRefusedError, InterruptedError):
            return False
        sock.close()
        return True

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
        self._hostname, self._port, msg_err = socket_get_com_settings(desc)
        if self._hostname is None:
            raise HwIOError(msg_err)

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

    def _read(self, size, timeout=0):
        """Read data from the connected device"""  # noqa: DAR101,DAR201,DAR401
        return self._hdl.recv(size)

    def _write(self, data, timeout=0):
        """Send data to the socket"""  # noqa: DAR101,DAR201,DAR401
        res = self._hdl.sendall(data)
        return len(data) if res is None else 0

    def short_desc(self, full: bool = True):
        """Report a human description of the connection state"""  # noqa: DAR101,DAR201,DAR401
        desc = 'SOCKET:' + str(self._hostname) + ':' + str(self._port)
        if full:
            desc += ':connected' if self.is_connected else ':not connected'
        return desc


if __name__ == '__main__':
    pass
