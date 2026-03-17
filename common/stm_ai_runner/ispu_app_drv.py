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
import os
from shutil import which
import subprocess
import sys

from .ai_runner import AiRunnerError, AiRunner
from .app_drv import AppDriver
from functools import reduce
import re


class IspuAppDriver(AppDriver):
    """
    Class to handle ispu application
    """

    def __init__(self, parent):
        self.gprof_dump_file = None
        self.time_tag = None
        self.time_tag_number = None
        self.clock = 5000
        self.compiler = None

        super(IspuAppDriver, self).__init__(parent)

    def _get_device_info(self):
        """
        Create the dictionary with device info

        Returns
        -------
        dict
            A dictionary with device info
        """
        info_device = dict()
        info_device['desc'] = 'xstsim ISPU simulator'
        info_device['dev_type'] = 'SIMULATOR'
        return info_device

    def _clean(self):
        """
        Clean simulation files
        """
        files = ['sim-0000.prof.c0.callgrind', 'sim-0000.prof.c0.cycles.tmp', 'sim-0000.prof.c0.gprof.cycles',
                 'sim-0000.prof.c0.info', 'sim-0000.stats.raw']
        for file in files:
            if os.path.exists(file):
                os.remove(file)

    def connect(self, desc=None, **kwargs):
        """
        Connect to application and configure app for gprof dump if specified

        Parameters
        ----------
        desc: str
            The application
        kwargs
            The other arguments
        """
        """
        --gprof: hidden dev option for performance profiling purposes
        """

        self.gprof_dump_file = kwargs['context'].get_option('validate.gprof')
        self.time_tag = kwargs['context'].get_option('validate.time-tag')
        self.time_tag_number = kwargs['context'].get_option('validate.time-tag-number')
        self.compiler = kwargs['context'].get_option('target.compiler')

        if self.time_tag == 'th_signal':
            raise AssertionError("This is the private name tag the whole inference: choose another name")

        super().connect(desc, **kwargs)

    def gprof_dump(self):
        """
        Utility to dump gprof statistics during model validation with stredl simulator
        """
        if self.compiler == 'reisc-gcc':
            gprof_cmd = 'reisc-gprof'
        elif self.compiler == 'stred-gcc':
            gprof_cmd = 'stred-gprof'
        else:
            raise AiRunnerError('Unknown compiler ' + self.compiler)

        gprof_exe = which(gprof_cmd)
        if not os.path.exists(gprof_exe):
            raise AiRunnerError(gprof_cmd + ' not found')

        gprof_app_args = [gprof_exe, self._app, 'sim-0000.prof.c0.gprof.cycles']
        gprof_output = subprocess.run(gprof_app_args, check=False, capture_output=True, text=True)
        gprof_output = gprof_output.stdout.splitlines()

        with open(self.gprof_dump_file, 'w') as cf:
            for line in gprof_output:
                cf.write(line + "\n")

    def get_optional_time_tags(self):
        """
        Get optional time tags list
        """
        l = []
        if self.time_tag is not None:
            if self.time_tag_number <= 0:
                l.append(self.time_tag + '_start')
                l.append(self.time_tag + '_stop')
            else:
                for i in range(self.time_tag_number):
                    l.append(self.time_tag + '_{0}_start'.format(i))
                    l.append(self.time_tag + '_{0}_stop'.format(i))
        return l

    def get_time_tags(self):
        """
        Get time tags list
        """
        # These tags delimit the whole inference
        return ['th_signal_start', 'th_signal_stop'] + self.get_optional_time_tags()

    def write_sim_config(self, profiling_file_name, sample):
        """
        Write xtsim configurations

        Parameters
        ----------
        profiling_file_name: name of the configuration file
        """
        time_tags = self.get_time_tags()
        assert 'th_signal_start' in time_tags and 'th_signal_stop' in time_tags

        with open(profiling_file_name, 'w') as fp:
            s = 'symbol(_.c0.target_exec, "{0}")'
            cfg_dump = str([s.format(tag) for tag in time_tags]).replace('\'', '')
            if sys.platform == 'win32':
                app_name = self._app.replace('\\', '\\\\')
            else:
                app_name = self._app
            fp.write('verbosity              "high"\n')
            fp.write('dump_stats             "raw"\n')
            fp.write('accuracy               "functional"\n')
            fp.write(f'var target_exec       "{app_name}"\n')
            fp.write('\n')
            fp.write('[c0]\n')
            fp.write('type    "ReISC-L"\n')
            fp.write('target_exec            _.target_exec\n\n')
            fp.write(f'target_args           ["{sample}"]\n\n')
            fp.write('[c0.profiler]\n')
            fp.write('metrics                ["cycles"]\n')
            fp.write('dump_at                {0}\n'.format(cfg_dump))
            fp.write('tmp_dump               "text"')

    def get_exec_time(self, start, stop):
        return (stop - start) / self.clock

    def get_region_exec_times(self, trace_file):
        """
        Compute exec times for all the tagged critical regions assuming time tags start/stop convention

        Parameters
        ----------
        trace output file

        Returns
        -------
        return dict[k] = v where (k, v) (time_tag, [times]). [times] is used as a stack
        """

        def _assert_proper_tags(cond):
            if not cond:
                raise AssertionError('Time tags  start/stop should be placed in order')

        d = dict()
        # skip to legend
        for line in trace_file:
            if line == 'Legend:\n':
                break
        for line in trace_file:
            if re.match('[ \t]*\[[0-9]+\]', line):
                flag = line.split()[12].split('_')[-1]
                if flag == 'start':
                    region = line.split()[12][:-6]
                    if region not in d:
                        d[region] = []
                    _assert_proper_tags(len(d[region]) == 0 or d[region][-1] > 0)
                    # push cycles dump
                    d[region].append(int(line.split()[6]))
                    # push start flag (to verify stop after start assertion)
                    d[region].append(0)

                elif flag == 'stop':
                    region = line.split()[12][:-5]
                    # a stop tag should always be preceeded by its start dual
                    _assert_proper_tags(d[region].pop() == 0)
                    start = d[region].pop()
                    stop = int(line.split()[6])
                    d[region].append(self.get_exec_time(start, stop))
        return d

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
        AiRunnerError
            If xstsim is not found
        AssertionError
            If the output return code is not 0
        """

        xstsim = which('xstsim')
        if xstsim is None:
            raise AiRunnerError('xstsim not found')

        profiling_file_name = os.path.join(os.getcwd(), 'profiling.xst')
        self.write_sim_config(profiling_file_name, sample)

        self._clean()

        lite_app_args = [xstsim, '--config-file=' + profiling_file_name]
        self._logger.info('Executing %s', ' '.join(lite_app_args))
        output = subprocess.run(lite_app_args, check=False, capture_output=True, text=True)
        sys.stdout.flush()

        if output.returncode:
            stderr = output.stderr
            for line in output.stdout.splitlines():
                self._logger.error(line)
            # For memory overlap, the error message is printed on stderr
            for line in stderr.splitlines():
                self._logger.error(line)
            raise AssertionError('Error in running validation application')
        output = output.stdout.splitlines()

        if sample != 0:
            trace_file_name = 'sim-0000.prof.c0.cycles.tmp'
            self._logger.debug('Opening %s', trace_file_name)

            with open(trace_file_name) as fp:
                time_dict = self.get_region_exec_times(fp)

            regions = []
            for k, v in time_dict.items():
                if k == 'th_signal':
                    elapsed_time = v[0]
                else:
                    regions.append((k, max(v), sum(v)))

            regions.sort(key=lambda el: el[0])
            for el in regions:
                self._logger.info('-' * 20)
                self._logger.info('Critical region {0} executed in {1} ms (max time)'.format(el[0], el[1]))
                self._logger.info('Critical region {0} cumulated execution time: {1} ms'.format(el[0], el[2]))
                self._logger.info('-' * 20)
            self._logger.debug('Net elapsed time is %s', str(elapsed_time))
        else:
            elapsed_time = None

        if self.gprof_dump_file is not None:
            self.gprof_dump()

        self._clean()
        self._logger.debug('Elapsed time is %s', str(elapsed_time))
        return output, elapsed_time

    @property
    def capabilities(self):
        """
        Return list with the capabilities

        Returns
        -------
        list
            List of capabilities
        """
        return [AiRunner.Caps.IO_ONLY]

    def short_desc(self):
        """
        Return human readable description

        Returns
        -------
        str
            Human readable description
        """
        return 'ISPU app' + ' (' + self._app + ')'
