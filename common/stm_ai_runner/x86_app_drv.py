###################################################################################
#   Copyright (c) 2022 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
X86 driver to manage the App (generated for the lite validation)
"""
import platform
import subprocess
import time

from .app_drv import AppDriver


class X86AppDriver(AppDriver):
    """
    Class to handle x86 application
    """

    def _run_application(self, sample):
        """
        Run the wrapped application

        Parameters
        ----------
        sample: int
            The sample index to be evaluated (0 for inspection)

        Returns
        -------
        The output of subprocess.run and the elapsed time

        Raises
        ------
        AssertionError
            If the application return non-zero value
        """
        lite_app_args = [self._app, str(sample)]
        start_time = time.perf_counter()
        output = subprocess.run(lite_app_args, check=False, capture_output=True, text=True)
        if output.returncode:
            for line in output.stdout.splitlines():
                self._logger.error(line)
            raise AssertionError('Error in running validation application')
        elapsed_time = (time.perf_counter() - start_time) * 1000.0
        output = output.stdout.splitlines()
        self._logger.debug('Elapsed time is %s', str(elapsed_time))
        return output, elapsed_time

    def _get_device_info(self):
        """
        Create the dictionary with device info

        Returns
        -------
        dict
            A dictionary with device info
        """
        info_device = dict()
        info_device['desc'] = '{} {} ({})'.format(platform.machine(), platform.processor(), platform.system())
        info_device['dev_type'] = 'HOST'
        return info_device

    def short_desc(self):
        """
        Return human readable description

        Returns
        -------
        str
            Human readable description
        """
        return 'X86 app' + ' (' + self._app + ')'
