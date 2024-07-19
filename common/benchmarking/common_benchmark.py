# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
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
import subprocess
from subprocess import Popen
from typing import List, Union, Optional, Tuple, Dict
import mlflow
from hydra.core.hydra_config import HydraConfig
from stm32ai_dc import (CliLibraryIde, CliLibrarySerie, CliParameters, MpuParameters, MpuEngine,
                        CloudBackend, Stm32Ai)
from stm32ai_dc.errors import BenchmarkServerError

from omegaconf import DictConfig
from logs_utils import log_to_file
from models_utils import get_model_name_and_its_input_shape, get_model_name


def benchmark(cfg: DictConfig = None, model_path_to_benchmark: Optional[str] = None,
              credentials: list[str] = None, custom_objects: Dict = None) -> None:
    """
    Benchmark a model .

    Args:
        cfg (DictConfig): Configuration dictionary.
        model_path_to_benchmark (str, optional): model path to benchmark.
        credentials list[str]: User credentials used before to connect.
        custom_objects (Dict): custom objects attached to the model

    Returns:
        None
    """

    model_path = model_path_to_benchmark if model_path_to_benchmark else cfg.general.model_path
    model_name, input_shape = get_model_name_and_its_input_shape(model_path=model_path,
                                                                 custom_objects=custom_objects)
    output_dir = HydraConfig.get().runtime.output_dir
    stm32ai_output = output_dir + "/stm32ai_files"
    stm32ai_version = cfg.tools.stm32ai.version
    optimization = cfg.tools.stm32ai.optimization
    board = cfg.benchmarking.board
    path_to_stm32ai = cfg.tools.stm32ai.path_to_stm32ai
    #log the parameters in stm32ai_main.log
    log_to_file(cfg.output_dir, f'Stm32ai version : {stm32ai_version}')
    log_to_file(cfg.output_dir, f'Benchmarking board : {board}')
    get_model_name_output = get_model_name(model_type=str(model_name),
                                           input_shape=str(input_shape[0]),
                                           project_name=cfg.general.project_name)
    stm32ai_benchmark(footprints_on_target=board,
                      optimization=optimization,
                      stm32ai_version=stm32ai_version, model_path=model_path,
                      stm32ai_output=stm32ai_output, path_to_stm32ai=path_to_stm32ai,
                      get_model_name_output=get_model_name_output,on_cloud =cfg.tools.stm32ai.on_cloud,
                      credentials=credentials)


def analyze_footprints(offline: bool = True, results: dict = None, stm32ai_output: str = None,
                       inference_res: bool = False, target_mcu: bool = True) -> None:
    """Prints and logs footprints after the Cube.AI benchmark.

    Args:
        offline (bool, optional): Flag to indicate if the results are offline. Defaults to True.
        results (dict, optional): Dictionary containing the results of the benchmark. Defaults to None.
        inference_res (bool, optional): Flag to indicate if the results are for inference. Defaults to False.
        stm32ai_output (str, optional): Path to the output directory for the STM32. Defaults to "".
    """
    # Load results from file if offline
    output_dir = HydraConfig.get().runtime.output_dir
    if target_mcu:
        if offline:
            with open(os.path.join(stm32ai_output, 'network_report.json'), 'r') as f:
                results = json.load(f)
            # Extract footprint values
            if isinstance(results["ram_size"], list):
                activations_ram = round(int(results["ram_size"][0]) / 1024, 2) # for version <= 8.1.0
            else:
                activations_ram = round(int(results["ram_size"]) / 1024, 2) # for version >= 9.0.0
            weights_rom = round(int(results["rom_size"]) / 1024, 2)
            macc = round(int(results["rom_n_macc"]) / 1e6, 3)
            print("[INFO] : RAM Activations : {} (KiB)".format(activations_ram))
            print("[INFO] : Flash weights : {} (KiB)".format(weights_rom))
            print("[INFO] : MACCs : {} (M)".format(macc))
        else:
            activations_ram = round(int(results["ram_size"]) / 1024, 2)
            weights_rom = round(int(results["rom_size"]) / 1024, 2)
            macc = round(int(results["macc"]) / 1e6, 3)
            tools_version = results["report"]["tools_version"]
            # Check if inference results or tools version 8
            version_numbers = ["major", "minor", "micro"]
            version_strings = results["cli_version_str"]
            tools_version_str = ".".join(version_strings)
            if inference_res or int(tools_version_str[0]) >= 8:
                runtime_ram = round(results["estimated_library_ram_size"] / 1024, 2)
                total_ram = round(activations_ram + runtime_ram, 2)
                code_rom = round(results["estimated_library_flash_size"] / 1024, 2)
                total_flash = round(weights_rom + code_rom, 2)
                # Print and log total footprints
                print("[INFO] : Total RAM : {} (KiB)".format(total_ram))
                print("[INFO] :     RAM Activations : {} (KiB)".format(activations_ram))
                print("[INFO] :     RAM Runtime : {} (KiB)".format(runtime_ram))
                print("[INFO] : Total Flash : {} (KiB)".format(total_flash))
                print("[INFO] :     Flash Weights  : {} (KiB)".format(weights_rom))
                print("[INFO] :     Estimated Flash Code : {} (KiB)".format(code_rom))
                print("[INFO] : MACCs : {} (M)".format(macc))
                # Print and log inference results
                if inference_res:
                    internal_flash_usage = round(results["internal_flash_consumption"] / 1024,2)
                    external_flash_usage = round(results["external_flash_consumption"] / 1024, 2)
                    internal_ram_usage = round(results["internal_ram_consumption"] / 1024,2)
                    external_ram_usage = round(results["external_ram_consumption"] / 1024, 2)
                    if external_flash_usage > 0:
                        print("[INFO] : Internal Flash usage : {} (KiB)".format(internal_flash_usage))
                        print("[INFO] : External Flash usage : {} (KiB)".format(external_flash_usage))
                        mlflow.log_metric("Internal Flash usage", internal_flash_usage)
                        mlflow.log_metric("External Flash usage", external_flash_usage)
                        with open(os.path.join(output_dir, "stm32ai_main.log"), "a") as log_file:
                            log_file.write(f'Internal Flash usage : {internal_flash_usage} KiB\n' + f'External Flash usage : {external_flash_usage} KiB\n')
                    if external_ram_usage > 0:
                        print("[INFO] : Internal RAM usage : {} (KiB)".format(internal_ram_usage))
                        print("[INFO] : External RAM usage : {} (KiB)".format(external_ram_usage))
                        mlflow.log_metric("Internal RAM usage", internal_ram_usage)
                        mlflow.log_metric("External RAM usage", external_ram_usage)
                        with open(os.path.join(output_dir, "stm32ai_main.log"), "a") as log_file:
                            log_file.write(f'Internal RAM usage : {internal_ram_usage} KiB\n' + f'External RAM usage : {external_ram_usage} KiB\n')
                    cycles = round(results["cycles"] / 1e6, 3)
                    inference_time = round(results["duration_ms"], 2)
                    print("[INFO] : Number of cycles : {} (M) ".format(cycles))
                    print("[INFO] : Inference Time : {} (ms)".format(inference_time))
                    mlflow.log_metric("cycles", cycles)
                    mlflow.log_metric("inference_time ms", inference_time)
                    with open(os.path.join(output_dir, "stm32ai_main.log"), "a") as log_file:
                        log_file.write(f'Cycles : {cycles} M\n' + f'Inference_time : {inference_time} ms\n')

                mlflow.log_metric("Total RAM KiB", total_ram)
                mlflow.log_metric("RAM Runtime KiB", runtime_ram)
                mlflow.log_metric("Total Flash KiB", total_flash)
                mlflow.log_metric("Estimated Flash Code KiB", code_rom)
                with open(os.path.join(output_dir, "stm32ai_main.log"), "a") as log_file:
                    log_file.write(f'Total RAM : {total_ram} KiB\n' + f'RAM Runtime : {runtime_ram} KiB\n'+
                                f'Total Flash : {total_flash} KiB\n' +f'Estimated Flash Code : {code_rom} KiB\n' )

            # Print and log activation, weight, and MACC footprints if not inference results
            else:
                print("[INFO] : RAM Activations : {} (KiB)".format(activations_ram))
                print("[INFO] : Flash weights : {} (KiB)".format(weights_rom))
                print("[INFO] : MACCs : {} (M)".format(macc))
        mlflow.log_metric("RAM Activations KiB", activations_ram)
        mlflow.log_metric("Flash weights KiB", weights_rom)
        mlflow.log_metric("MACCs M", macc)
        with open(os.path.join(output_dir, "stm32ai_main.log"), "a") as log_file:
            log_file.write(f'RAM Activations : {activations_ram} KiB\n' + f'Flash weights : {weights_rom} KiB\n'+
                        f'MACCs : {macc} M\n')
    else :
        model_name=results["info"]["model_name"]
        model_size = round(int(results["info"]["model_size"]) / 1024, 2)
        peak_ram = round(results["ram_size"] / 1024, 2)
        peak_ram_MB =  round(peak_ram / 1024, 2)
        tools_version = results["info"]["tool_version"]
        version_numbers=["major", "minor", "micro"]
        version_strings = results["cli_version_str"]
        print("[INFO] : Model Name : {}".format(model_name))
        print("[INFO] : Tool version : {}".format(version_strings))
        print("[INFO] : Model Size : {} (KiB)".format(model_size))
        print("[INFO] : Peak Ram usage : {} (MiB)".format(peak_ram_MB))
        mlflow.log_metric("Model Size KiB", model_size)
        mlflow.log_metric("Peak Ram KiB", peak_ram)
        with open(os.path.join(output_dir, "stm32ai_main.log"), "a") as log_file:
            log_file.write(f'Model Name : {model_name} \n' + f'Tool version : {version_strings} \n'+ f'Model Size : {model_size} KiB \n' + f'Peak Ram usage : {peak_ram} KiB\n')
        if inference_res:
            inference_time = round(results["duration_ms"], 2)
            npu_percent = round(100*results["npu_percent"],2)
            gpu_percent = round(100*results["gpu_percent"],2)
            cpu_percent = round(100*results["cpu_percent"],2)
            print("[INFO] : Inference Time : {} (ms)".format(inference_time))
            print("[INFO] : Execution engine repartition : ")
            print("[INFO] :     NPU usage : {}".format(npu_percent))
            print("[INFO] :     GPU usage : {}".format(gpu_percent))
            print("[INFO] :     CPU usage : {}".format(cpu_percent))
            mlflow.log_metric("inference_time ms", inference_time)
            mlflow.log_metric("NPU usage", npu_percent)
            mlflow.log_metric("GPU usage", gpu_percent)
            mlflow.log_metric("CPU usage", cpu_percent)
            with open(os.path.join(output_dir, "stm32ai_main.log"), "a") as log_file:
                log_file.write(f'Inference_time : {inference_time} ms\n' + f'NPU usage : {npu_percent} %\n' + f'GPU usage : {gpu_percent} %\n' + f'CPU usage : {cpu_percent} %\n')


def benchmark_model(optimization: str = None, model_path: str = None, path_to_stm32ai: str = None,
                    stm32ai_output: str = None, stm32ai_version: str = None, get_model_name_output: str = None) -> \
        Optional[Exception]:
    """
    Benchmark model using STM32Cube.AI locally.

    Args:
        optimization (str): Optimization level.
        model_path (str): Path to the model file.
        path_to_stm32ai (str): Path to STM32Cube.AI.
        stm32ai_output (str): Path to output directory.
        stm32ai_version (str): STM32Cube.AI version.
        get_model_name_output (str): Model name output.

    Returns:
        Optional[Exception]: None if successful, otherwise the exception that occurred.
    """

    # Create output directory if it doesn't exist
    os.makedirs(stm32ai_output, exist_ok=True)

    print("[INFO] : Starting the model memory footprints estimation...")

    try:
        # Set environment variables for STM32Cube.AI
        new_env = os.environ.copy()
        new_env.update({'STATS_TYPE': '_'.join(['stmai_modelzoo', get_model_name_output])})

        # Check STM32Cube.AI version compatibility
        command = f"{path_to_stm32ai} --version"
        args = shlex.split(command, posix="win" not in sys.platform)
        line = Popen(args, env=new_env, stdout=subprocess.PIPE).communicate()[0].decode("utf-8")
        version_line = line.split('v')[-1].split('-')[0]
        if not version_line.endswith(stm32ai_version):
            print(
                f"[WARN] : STM32Cube.AI installed version {version_line} does not match the version specified in user_config.yaml file {stm32ai_version} !")
        print(f"[INFO] : STM32Cube.AI version {version_line} used.")

        # Run generate command locally
        command = f"{path_to_stm32ai} generate --target stm32 -m {model_path} -v 0 --allocate-inputs --allocate-outputs --output {stm32ai_output} --workspace {stm32ai_output} --optimization {optimization}"
        args = shlex.split(command, posix="win" not in sys.platform)
        subprocess.run(args, env=new_env, check=True)

    except subprocess.CalledProcessError as e:
        raise TypeError(
            f"Received: stm32ai.path_to_stm32ai={path_to_stm32ai}. Please specify a correct path to STM32Cube.AI!") from e

    return stm32ai_output


def get_credentials() -> tuple:
    """
    Get user credentials.

    Returns:
        tuple: Username and password.
    """

    # Check if credentials are set as environment variables
    if ("stmai_username" and "stmai_password") in os.environ:
        username = os.environ.get('stmai_username')
        password = os.environ.get('stmai_password')
        print('[INFO] : Found the saved credentials in environment variables! Logging in!' )
    # If running in a terminal, prompt the user for credentials
    elif sys.stdin.isatty():
        username = input("Username: ")
        password = getpass.getpass("Password: ")
    # If running in a non-interactive environment, read credentials from stdin
    else:
        username = sys.stdin.readline().rstrip()
        password = sys.stdin.readline().rstrip()

    return username, password


def cloud_connect(stm32ai_version: str = None, credentials: list[str] = None) -> Union[bool, Stm32Ai, list[str]]:
    """
    Connect to your STM32Cube.AI Developer Cloud account.

    Args:
        stm32ai_version (str): Version of the STM32Cube.AI backend to use.
        credentials list[str]: User credentials used before to connect.
    Returns:
        ai (class): Stm32Ai Class to establish connection with STM32Cube.AI Developer Cloud Services.
        login_success (bool): Flag to validate if login was done successfully.
        credentials list[str]: User credentials used before to connect.
    """

    print(
        "[INFO] : Establishing a connection to STM32Cube.AI Developer Cloud to launch the model benchmark on STM32 target...")
    if credentials:
        username, password = credentials
    else:
        print("[INFO] : To create an account, go to https://stm32ai-cs.st.com/home. Enter your credentials:")
        username, password = get_credentials()
        credentials = username, password

    login_success = False
    ai = None
    # Try to create the STM32Cube.AI instance up to 3 times
    for attempt in range(3):
        try:
            backend = CloudBackend(username, password, version=stm32ai_version)
            ai = Stm32Ai(backend)
            login_success = True
            break
        except Exception as e:
            if type(e).__name__ == "LoginFailureException":
                if attempt < 2:
                    print("[ERROR]: Login failed. Please try again.")
                    username, password = get_credentials()
                else:
                    print("[ERROR]: Failed to create STM32Cube.AI instance.")

    if login_success:
        print("[INFO] : Successfully connected!")
    else:
        print("[WARN] : Login failed!")
    return login_success, ai, credentials


def cloud_analyze(ai: Stm32Ai = None, model_path: str = None, optimization: str = None,
                  get_model_name_output: str = None) -> dict:
    """
    Use STM32Cube.AI Developer Cloud Services to analyze model footprints.

    Args:
        ai (class): Stm32Ai Class to establish connection with STM32Cube.AI Developer Cloud Services.
        model_path (str): Path to the quantized model file.
        optimization (str): Optimization level to use.
        get_model_name_output (str): Model name output.
    Returns:
        Dictionary of analyze results.
    """

    # Benchmark model using local file
    print("[INFO] : Starting the model memory footprints estimation...")
    optimization = optimization.lower()
    ai.upload_model(model_path)
    model_name = os.path.basename(model_path)
    res = ai.analyze(CliParameters(model=model_name, optimization=optimization, fromModel=get_model_name_output))

    # Store the analyzee results in a dictionary
    res_dict = {name: getattr(res, name) for name in dir(res) if not name.startswith("__")}

    return res_dict


def get_mpu_options(board_name: str = None) -> tuple:
    """
    Get MPU benchmark options depending on MPU board selected

    Returns:
        tuple: engine_used and num_cpu_cores.
    """

    #define configuration by MPU board
    STM32MP257F_EV1 = {
        "engine": MpuEngine.HW_ACCELERATOR,
        "cpu_cores": 2
    }

    STM32MP157F_DK2 = {
        "engine": MpuEngine.CPU,
        "cpu_cores": 2
    }

    STM32MP135F_DK = {
        "engine": MpuEngine.CPU,
        "cpu_cores": 1
    }

    #recover parameters based on board name:
    if board_name == "STM32MP257F-EV1":
        engine_used = STM32MP257F_EV1.get("engine")
        num_cpu_cores = STM32MP257F_EV1.get("cpu_cores")
    elif board_name == "STM32MP157F-DK2":
        engine_used = STM32MP157F_DK2.get("engine")
        num_cpu_cores = STM32MP157F_DK2.get("cpu_cores")
    elif board_name == "STM32MP135F-DK":
        engine_used = STM32MP135F_DK.get("engine")
        num_cpu_cores = STM32MP135F_DK.get("cpu_cores")
    else :
        engine_used = MpuEngine.CPU
        num_cpu_cores = 1

    return engine_used, num_cpu_cores


def cloud_benchmark(ai: Stm32Ai = None, model_path: str = None, board_name: str = None, optimization: str = None,
                    get_model_name_output: str = None) -> dict:
    """
    Use STM32Cube.AI Developer Cloud Services to benchmark the model on a board and generate C code.

    :param ai: Stm32Ai Class to establish connection with STM32Cube.AI Developer Cloud Services.
    :param model_path: Path to the quantized model file
    :param board_name: Name of the board to benchmark the model on
    :param optimization: Type of optimization to apply to the model
    :param get_model_name_output: Path to the output directory for the generated model name
    :return: Dictionary of benchmark results.
    """
    # Set up the STM32Cube.AI API client

    cloud_results = {}
    # Upload the model to STM32Cube.AI Developer Cloud Services
    ai.upload_model(model_path)
    model_name = os.path.basename(model_path)
    # Benchmark the model on the specified board
    boards = ai.get_benchmark_boards()
    board_names = [boards[i].name for i in range(len(boards))]
    if board_name not in board_names:
        raise ValueError(f"Board {board_name} not listed. Please select one of the available boards {board_names}")

    print(f"[INFO] : Starting the model benchmark on target {board_name}, other available boards {board_names}...")
    # Determine right parameters for MCU or MPU
    if "STM32MP" in board_name:
        engine, nbCores = get_mpu_options(board_name)
        stmai_params = MpuParameters(model=model_name, nbCores=nbCores, engine=engine)
    else:
        stmai_params = CliParameters(model=model_name, optimization=optimization, fromModel=get_model_name_output)
    res_benchmark = ai.benchmark(stmai_params,
                                board_name=board_name,
                                timeout=1500)

    # Store the benchmark results in a dictionary
    res_dict = {name: getattr(res_benchmark, name) for name in dir(res_benchmark) if not name.startswith("__")}
    return res_dict


def stm32ai_benchmark(footprints_on_target: str = False, optimization: str = None,
                      stm32ai_version: str = None, model_path: str = None,
                      stm32ai_output: str = None, path_to_stm32ai: str = None,
                      get_model_name_output: str = None, on_cloud: bool = False,
                      credentials: list[str] = None) -> None:
    """
    Benchmarks a model on Cloud or locally.

    Args:
    - footprints_on_target (str): Flag indicating the name of the board.
    - optimization (str): Optimization level to use.
    - stm32ai_version (str): Version of STM32Cube.AI to use.
    - model_path (str): Path to the model file.
    - stm32ai_output (str): Path to the output directory for the generated C code.
    - get_model_name_output (str): Path to the output directory for the generated model name.
    -  on_cloud(bool):Flag indicating whether to benchmark on cloud or not.
    - credentials list[str]: User credentials used before to connect.
    Returns:
    - None
    """

    # Initialise variables
    cloud_res = None
    offline = True
    inference_res = False

    # Determine which type of board is targeted
    board_name = str(footprints_on_target)
    if "STM32MP" in board_name:
        target_mcu = False
    else :
        target_mcu = True

    # If on cloud is True, benchmark the model on Cloud
    if on_cloud:

        # Connect to STM32Cube.AI Developer Cloud
        login_success, ai, _ = cloud_connect(stm32ai_version=stm32ai_version, credentials=credentials)

        if login_success:

            if not(target_mcu):
                if "STM32MP2" in board_name:
                    model_extension = os.path.splitext(model_path)[1]
                    model_name, input_shape = get_model_name_and_its_input_shape(model_path=model_path)
                    optimized_model_path = os.path.dirname(model_path) + "/"
                    if (model_extension == ".tflite" or model_extension == ".onnx"):
                        try:
                            ai.upload_model(model_path)
                            model = model_name + model_extension
                            res = ai.generate_nbg(model)
                            ai.download_model(res, optimized_model_path + res)
                            model_path=os.path.join(optimized_model_path,res)
                            model_name = model_name + ".nb"
                            rename_model_path=os.path.join(optimized_model_path,model_name)
                            os.rename(model_path, rename_model_path)
                            model_path = rename_model_path
                            print("[INFO] : Optimized Model Name:", model_name)
                            print("[INFO] : Optimization done ! Model available at :",optimized_model_path)

                        except Exception as e:
                            print(f"[FAIL] : Model optimization via Cloud failed : {e}.")
                            print("[INFO] : Use default model instead of optimized ...")

            try:
                # Benchmark the model inference time
                cloud_res = cloud_benchmark(ai=ai, model_path=model_path, board_name=board_name,
                                                optimization=optimization,
                                                get_model_name_output=get_model_name_output)

                inference_res = True
                offline = False
            except Exception as e:
                print(f"[FAIL] : Cloud Benchmark failed : {e}. Trying Cloud Analyze to get model memory footprints!")

                try:
                    # Analyze the model memory footprints
                    cloud_res = cloud_analyze(ai=ai, model_path=model_path, optimization=optimization,
                                            get_model_name_output=get_model_name_output)
                    offline = False

                except Exception as e:
                    if target_mcu :
                        print("[FAIL] : Cloud Analyze failed :", e)
                        print(
                            "[INFO] : Using the local download of STM32Cube.AI. Link to download https://www.st.com/en/embedded-software/x-cube-ai.html")
                        benchmark_model(
                            optimization=optimization, model_path=model_path, path_to_stm32ai=path_to_stm32ai,
                            stm32ai_output=stm32ai_output, stm32ai_version=stm32ai_version,
                            get_model_name_output=get_model_name_output)
                    else :
                        print("[FAIL] : Cloud Analyze failed :", e)
                        exit(1)
        else:
            if target_mcu :
                print(
                    "[INFO] : Using the local download of STM32Cube.AI. Link to download https://www.st.com/en/embedded-software/x-cube-ai.html")
                benchmark_model(
                    optimization=optimization, model_path=model_path, path_to_stm32ai=path_to_stm32ai,
                    stm32ai_output=stm32ai_output, stm32ai_version=stm32ai_version,
                    get_model_name_output=get_model_name_output)
            else :
                print("[FAIL] : Login to Developer cloud failed")
                exit(1)
    else:
        print(
            "[INFO] : Using the local download of STM32Cube.AI. Link to download https://www.st.com/en/embedded-software/x-cube-ai.html")
        benchmark_model(
            optimization=optimization, model_path=model_path, path_to_stm32ai=path_to_stm32ai,
            stm32ai_output=stm32ai_output, stm32ai_version=stm32ai_version,
            get_model_name_output=get_model_name_output)

    # Print footprints
    analyze_footprints(offline=offline, results=cloud_res, stm32ai_output=stm32ai_output, inference_res=inference_res, target_mcu=target_mcu)
