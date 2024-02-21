# STMicroelectronics – STM32 Dev. Cloud Examples

This folder provides a collection of examples that you can use in order to get started with STM32Cube.AI Developer Cloud Python Interface.

You will retrieve multiples files in order to [analyze](analyze_model_with_cloud.py), [validate](validate_model_with_cloud.py), [generate code](generate_model_with_cloud.py), [benchmark your model to STM32 Benchmark Farm](benchmark_model_with_cloud.py) or simply [connect](connect_to_cloud.py).


## Available examples

* [Connect to STM32Cube.AI Developer Cloud](connect_to_cloud.py)
* [Analyze a model](analyze_model_with_cloud.py)
* [Validate a model](validate_model_with_cloud.py)
* [Generate associated C code](generate_model_with_cloud.py)
* [Benchmark my model to STM32 Benchmark Farm](benchmark_model_with_cloud.py) 

### [Connect to STM32Cube.AI Developer Cloud](connect_to_cloud.py)

Connect to STM32Cube.AI Dev. Cloud script describes how you shall configure your environment variables in order to use our service. It includes env. getters, and a request to get your user informations

### [Analyze](analyze_model_with_cloud.py)

Analyze script allows to get informations about a given model, such as weights, activations size, flash and ram constraints including library size.

### [Validate](validate_model_with_cloud.py)

Validate script permits to get the same informations as analyze, but includes metrics to compare the accuracy of generated C model and original model (from a numerical standpoint). Both models are loaded with the same input tensors (with fixed random inputs or custom dataset)

### [Generate](generate_model_with_cloud.py)

Generate script permits to get the same informations as analyze, but generates STM32CubeAI Library and C Code associated to an input model.

### [Benchmark to STM32 Benchmark Farm](benchmark_model_with_cloud.py)

Benchmark script permits to get informations about a given model associated to a true board, and gives total inference time associated to a model. 

## Before you start

- Create, if not already done, an account by connecting to [STM32Cube.AI Developer Cloud](https://stm32ai-cs.st.com/home) to be able to use the service. 
- Install all the necessary python packages listed in [requirement file](../../../requirements.txt)   
```sh
    pip install -r ./requirements.txt
```
- Once you have logged in to your MyST account, add your username and password in env. variables
```sh
    export STM32AI_USERNAME="dupont@example.com"
    export STM32AI_PASSWORD="password"
```
- When getting started with one example, kindly replace "`mobilenet_v1_0.25_96.h5`" by the path of your own model. 
