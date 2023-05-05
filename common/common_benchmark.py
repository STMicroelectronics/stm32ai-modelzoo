# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import getpass
import json
import os
import sys
import shlex
from subprocess import Popen

import mlflow
from hydra.core.hydra_config import HydraConfig
from stm32ai_dc import (CliLibraryIde, CliLibrarySerie, CliParameters,
                     CloudBackend, Stm32Ai)
from stm32ai_dc.errors import BenchmarkServerError


def analyze_footprints(offline=True, cloud_results=None, inference_res=False):

    """ Print footprints after cube.ai benchmark. """

    if not inference_res:
        if offline:
            with open(os.path.join(HydraConfig.get().runtime.output_dir, 'stm32ai_files/network_report.json'), 'r') as f:
                m_data = json.load(f)

            m_ram = m_data["ram_size"][0] / 1024
            m_rom = m_data["rom_size"] / 1024
            macc = m_data["rom_n_macc"] / 1e6
        else:
            m_ram = cloud_results.ram_size / 1024
            m_rom = cloud_results.rom_size / 1024
            macc = cloud_results.macc / 1e6
        print("[INFO] : RAM Activations : {} (KiB)".format(m_ram))
        print("[INFO] : Flash weights : {} (KiB)".format(m_rom))
        print("[INFO] : MACCs : {} (M)".format(macc))
        mlflow.log_metric("Activations KiB", m_ram)
        mlflow.log_metric("weights KiB", m_rom)
        mlflow.log_metric("MACCs M", macc)
    else:
        activations_ram = cloud_results["ram_size"] / 1024
        runtime_ram = cloud_results["estimated_library_ram_size"] / 1024
        total_ram = activations_ram + runtime_ram
        weights_rom = cloud_results["rom_size"] / 1024
        code_rom = cloud_results["estimated_library_flash_size"] / 1024
        total_flash = weights_rom + code_rom
        macc = cloud_results["macc"] / 1e6
        cycles = cloud_results["cycles"]
        inference_time = cloud_results["duration_ms"]
        print("[INFO] : Total RAM : {} (KiB)".format(total_ram))
        print("[INFO] :     RAM Activations : {} (KiB)".format(activations_ram))
        print("[INFO] :     RAM Runtime : {} (KiB)".format(runtime_ram))
        print("[INFO] : Total Flash : {} (KiB)".format(total_flash))
        print("[INFO] :     Flash Weights  : {} (KiB)".format(weights_rom))
        print("[INFO] :     Estimated Flash Code : {} (KiB)".format(code_rom))
        print("[INFO] : MACCs : {} (M)".format(macc))
        print("[INFO] : Number of cycles : {} ".format(cycles))
        print("[INFO] : Inference Time : {} (ms)".format(inference_time))
        mlflow.log_metric("Total RAM KiB", total_ram)
        mlflow.log_metric("Activations KiB", activations_ram)
        mlflow.log_metric("Runtime KiB", runtime_ram)
        mlflow.log_metric("Total Flash KiB", total_flash)
        mlflow.log_metric("weights KiB", weights_rom)
        mlflow.log_metric("Estimated_Code KiB", code_rom)
        mlflow.log_metric("MACCs M", macc)
        mlflow.log_metric("cycles", cycles)
        mlflow.log_metric("inference_time ms", inference_time)


def get_model_name(cfg):

    strings = list(cfg['model']['model_type'].values())
    strings.append(str(cfg['model']['input_shape'][0]))
    strings.append(cfg['general']['project_name'])

    name = '_'.join([str(i) for i in strings])

    return name


def benchmark_model(cfg, model_path):

    """ Benchmark model using cube.ai locally. """

    stm32ai_output = os.path.join(HydraConfig.get().runtime.output_dir, "stm32ai_files")

    try:
        if not os.path.exists(stm32ai_output):
            os.system("mkdir {}".format(stm32ai_output))

        new_env = os.environ.copy()
        new_env.update({'STATS_TYPE': '_'.join(['stmai_modelzoo', get_model_name(cfg)])})
        command = "{} generate -m {} -v 0 --allocate-inputs --allocate-outputs --output {} --workspace {} --optimization {}".format(
            cfg.stm32ai.path_to_stm32ai, model_path, stm32ai_output, stm32ai_output, cfg.stm32ai.optimization)
        args = shlex.split(command, posix="win" not in sys.platform)
        stm32ai_subprocess = Popen(args, env=new_env)
        stm32ai_subprocess.wait()

        # Print footprints
        analyze_footprints()

    except Exception:
        raise TypeError(f"Received: stm32ai.path_to_stm32ai= {cfg.stm32ai.path_to_stm32ai}. Please specify a correct path to stm32ai!")


def get_credentials():

    """ Get user credentials. """
    if ("stmai_username" and "stmai_password") in os.environ:
        username = os.environ.get('stmai_username')
        password = os.environ.get('stmai_password')
    elif sys.stdin.isatty():
        username = input("Username: ")
        password = getpass.getpass("Password: ")
    else:
        username = sys.stdin.readline().rstrip()
        password = sys.stdin.readline().rstrip()
    return username, password


def Cloud_analyze(cfg, quantized_model_path):

    """ Use STM32Cube.AI STM32Cube.AI Developer Cloud Services to analyze model footprints """

    print("[INFO] : To create an account https://stm32ai-cs.st.com/home. Enter credentials:")
    login_success = 0
    username, password = get_credentials()
    for attempt in range(3):
        try:
            ai = Stm32Ai(CloudBackend(str(username), str(password), version="7.3.0"))
            login_success = 1
        except Exception as e:
            login_success = 0
            if type(e).__name__ == "LoginFailureException":
                if attempt < 2:
                    print("[ERROR] : Try logging again...")
                    username, password = get_credentials()

                else:
                    raise Exception(e)
    if login_success:
        optimization = str(cfg.stm32ai.optimization.lower())
        print("[INFO] : Successfully connected, starting to analyze the model footprints ...")

        # Benchmarking model using local file
        ai.upload_model(quantized_model_path)
        model_name = os.path.basename(quantized_model_path)
        res = ai.analyze(CliParameters(model=model_name, optimization=optimization, fromModel=get_model_name(cfg)))
        analyze_footprints(offline=False, cloud_results=res)

        ai.delete_model(model_name)

        return [username, password]
    else:
        return 0


def Cloud_benchmark(cfg, quantized_model_path, credentials, c_code=False):

    """ Use STM32Cube.AI Developer Cloud Services to benchmark the model on a board and generate C code. """

    stm32ai_output = os.path.join(HydraConfig.get().runtime.output_dir, "stm32ai_files")
    username, password = credentials
    try:
        ai = Stm32Ai(CloudBackend(str(username), str(password), version="7.3.0"))
        login_success = 1
    except Exception as e:
        login_success = 0
        if type(e).__name__ == "LoginFailureException":
            raise Exception(e)

    if login_success:
        cloud_results = {}

        # Benchmarking the model on board
        board_name = str(cfg.stm32ai.footprints_on_target)
        optimization = str(cfg.stm32ai.optimization.lower())
        boards = ai.get_benchmark_boards()
        board_names = [boards[i].name for i in range(len(boards))]

        # Upload model to STM32Cube.AI Developer Cloud Services
        ai.upload_model(quantized_model_path)
        model_name = os.path.basename(quantized_model_path)

        print("[INFO] : Successfully connected, starting the model validation on target ...")
        if len(board_names) != 0:
            if board_name in board_names:
                print("[INFO] : Starting the benchmark on target {}, other available boards  {}".format(board_name, board_names))
                # Benchmarking model using local file
                res_benchmark = ai.benchmark(CliParameters(model=model_name, optimization=optimization, fromModel=get_model_name(cfg)), board_name)
                cloud_results["duration_ms"] = res_benchmark.duration_ms
                cloud_results["cycles"] = res_benchmark.cycles

            else:
                raise BenchmarkServerError("Board {} not listed. Please select one of the available boards {}".format(board_name, board_names))
        else:
            raise BenchmarkServerError("No board detected remotely, can't start benchmark")

        # Get Libray/ code memory size
        try:
            res_validate = ai.validate(CliParameters(model=model_name, relocatable=True, fromModel=get_model_name(cfg)))
            cloud_results["ram_size"] = res_validate.ram_size
            cloud_results["estimated_library_ram_size"] = res_validate.estimated_library_ram_size
            cloud_results["rom_size"] = res_validate.rom_size
            cloud_results["estimated_library_flash_size"] = res_validate.estimated_library_flash_size
            cloud_results["macc"] = res_validate.macc

            analyze_footprints(offline=False, cloud_results=cloud_results, inference_res=True)

        except Exception as e:
            raise Exception(e)

        if c_code:
            # Generate model using local file
            try:
                print("[INFO] : Generating the model C code and retrieving STM32Cube.AI Lib from STM32Cube.AI Developer Cloud Services...")

                ai.generate(CliParameters(model=quantized_model_path, output=stm32ai_output, fromModel=get_model_name(cfg),
                                          includeLibraryForSerie=CliLibrarySerie(cfg.stm32ai.serie.upper()),
                                          includeLibraryForIde=CliLibraryIde(cfg.stm32ai.IDE.lower())))

            except Exception as e:
                raise Exception(e)

        ai.delete_model(model_name)
    else:
        return 0


def stm32ai_benchmark(cfg, model_path, c_code):

    """
    To benchmark model on Cloud or locally
    """

    if cfg.stm32ai.footprints_on_target:
        try:
            print("[INFO] : To create an account https://stm32ai-cs.st.com/home. Enter credentials:")
            credentials = get_credentials()
            output_benchmark = Cloud_benchmark(cfg, model_path, credentials, c_code)
            if output_benchmark == 0:
                raise Exception("Connection failed, using local STM32Cube.AI. Link to download https://www.st.com/en/embedded-software/x-cube-ai.html")

        except Exception as e:
            print("[FAIL] :", e)
            if type(e).__name__ == "BenchmarkFailure":
                try:
                    print("[INFO] : Cloud model analyze launched...")
                    # Benchmarking model using local file
                    ai = Stm32Ai(CloudBackend(str(credentials[0]), str(credentials[1]), version="7.3.0"))
                    res = ai.analyze(CliParameters(model=model_path))
                    analyze_footprints(offline=False, cloud_results=res)

                    if c_code:
                        # Generate model using local file
                        try:
                            print("[INFO] : Generating the model C code and retrieving STM32Cube.AI Lib from STM32Cube.AI Developer Cloud Services...")
                            stm32ai_output = os.path.join(HydraConfig.get().runtime.output_dir, "stm32ai_files")
                            ai.generate(CliParameters(model=model_path, output=stm32ai_output, fromModel=get_model_name(cfg),
                                                      includeLibraryForSerie=CliLibrarySerie(cfg.stm32ai.serie.upper()),
                                                      includeLibraryForIde=CliLibraryIde(cfg.stm32ai.IDE.lower())))

                        except Exception as e:
                            raise Exception(e)

                except Exception as e:
                    print("[FAIL] :", e)
                    print("[INFO] : Offline benchmark {} launched...".format(("and c code generation" if c_code else "")))
                    benchmark_model(cfg, model_path)
            else:
                print("[INFO] : Offline benchmark {} launched...".format(("and c code generation" if c_code else "")))
                benchmark_model(cfg, model_path)
    else:
        benchmark_model(cfg, model_path)
