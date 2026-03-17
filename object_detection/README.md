# Object Detection STM32 Model Zoo

## Directory Components:
* [config_file_examples](config_file_examples/): collection of YAML configuration file examples for Tensorflow.
* [config_file_examples_pt](config_file_examples_pt/): collection of YAML config file examples for Pytorch.
* [datasets](datasets/): scripts for dataset management and convertion. 
* [docs](docs/): contains all readmes and tutorials describing the allowed operation modes in Tensorflow or Pytorch and specific to the object detection use case.
* [tf](tf/): contains Tensorflow tools to train, evaluate, benchmark, quantize and deploy your model on your STM32 target.
* [pt](pt/): contains Pytorch tools to train, evaluate, benchmark, quantize and deploy your model on your STM32 target.

## Quick & easy examples:
The `operation_mode` top-level attribute specifies the operations or the service you want to execute. This may be a single operation or a set of chained operations.

You can refer to the README links below that provide typical examples of operation modes and tutorials on specific services:

- [training, chain_tqe (train + quantize + evaluate), chain_tqeb](docs/README_TRAINING.md) for Tensorflow 
- [training, chain_tqe (train + quantize + evaluate), chain_tqeb](docs/README_TRAINING_TORCH.md) for Pytorch
- [quantization, chain_eqe, chain_qb](docs/README_QUANTIZATION.md) for Tensorflow or Pytorch
- [quantization, chain_eqe, chain_qb](docs/README_QUANTIZATION_TOOL.md) for advanced quantization parameters (exclusively based on ONNX-runtime)
- [evaluation, chain_eqeb](docs/README_EVALUATION.md) for Tensorflow or Pytorch
- [benchmarking](docs/README_BENCHMARKING.md) for Tensorflow or Pytorch
- [prediction](docs/README_PREDICTION.md) for Tensorflow or Pytorch
- deployment, chain_qd ([STM32H7](docs/README_DEPLOYMENT_STM32H7.md), [STM32N6](docs/README_DEPLOYMENT_STM32N6.md), [STM32MPU](docs/README_DEPLOYMENT_MPU.md))

The different values of the `operation_mode` attribute and the corresponding operations are described in the table below. In the names of the chain modes, 't' stands for training, 'e' for evaluation, 'q' for quantization, 'b' for benchmarking, and 'd' for deployment on an STM32 board.

| operation_mode attribute | Operations |
|:---------------------------|:-----------|
| `training`| Train a model from the variety of object detection models in the model zoo **(BYOD)** or your own model with the same model type **(BYOM)** |
| `evaluation` | Evaluate the accuracy of a float or quantized model on a test or validation dataset|
| `quantization` | Quantize a float model |
| `prediction`   | Predict the classes some images belong to using a float or quantized model |
| `benchmarking` | Benchmark a float or quantized model on an STM32 board |
| `deployment`   | Deploy a model on an STM32 board |
| `chain_tqeb`  | Sequentially: training, quantization of trained model, evaluation of quantized model, benchmarking of quantized model |
| `chain_tqe`    | Sequentially: training, quantization of trained model, evaluation of quantized model |
| `chain_eqe`    | Sequentially: evaluation of a float model,  quantization, evaluation of the quantized model |
| `chain_qb`     | Sequentially: quantization of a float model, benchmarking of quantized model |
| `chain_eqeb`   | Sequentially: evaluation of a float model,  quantization, evaluation of quantized model, benchmarking of quantized model |
| `chain_qd`     | Sequentially: quantization of a float model, deployment of quantized model |

The list of the available models in [STM32 model zoo](https://github.com/STMicroelectronics/stm32ai-modelzoo/) can be found in [Pytorch models](./docs/README_MODELS_TORCH.md) or in [Tensorflow models](./docs/README_MODELS.md) readmes.

## You don't know where to start? You feel lost?
Don't forget to follow our tuto below for a quick ramp up : 
* [How can I use my own dataset?](./docs/tuto/how_to_use_my_own_object_detection_dataset.md)
* [How can I fine tune a pretrained model on my own dataset?](./docs/tuto/how_to_finetune_a_model_zoo_model_on_my_own_dataset.md)
* [How can I check the accuracy after quantization of my model?](./docs/tuto/how_to_compare_the_accuracy_after_quantization_of_my_model.md)
* [How can I quickly check the performance of my model using the dev cloud?](./docs/tuto/how_to_quickly_benchmark_the_performances_of_a_model.md)
* [How can I quantize, evaluate and deploy an Ultralytics Yolov8 model?](./docs/tuto/How_to_deploy_yolov8_yolov5_object_detection.md)
* [How can I evaluate my model on STM32N6 target?](./docs/tuto/how_to_evaluate_my_model_on_stm32n6_target.md)

Remember that you have minimalistic YAML files available in [config_file_examples](config_file_examples/) for Tensorflow and in [config_file_examples_pt](config_file_examples_pt/) for Pytorch to play with specific services, and that all pre-trained models in the [STM32 model zoo](https://github.com/STMicroelectronics/stm32ai-modelzoo/) are provided with their configuration YAML file used to generate them. These are very good starting points to start playing with!