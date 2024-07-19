# Pose estimation STM32 model zoo

## Directory Components:
* [datasets](datasets/README.md) placeholder for the pose estimation datasets.
* [deployment](./deployment/README_MPU.md) contains the necessary files for the deployment service.
* [pretrained_models ](pretrained_models/README.md) a collection of optimized pretrained models for different pose estimation use cases.
* [src](src/README.md) contains tools to evaluate, benchmark and quantize your model on your STM32 target.

## Quick & easy examples:
The `operation_mode` top-level attribute specifies the operations or the service you want to execute. This may be single operation or a set of chained operations.

You can refer to readme links below that provide typical examples of operation modes, and tutorials on specific services:

   - [quantization, chain_eqe, chain_qb](./src/quantization/README.md)
   - [evaluation, chain_eqeb](./src/evaluation/README.md)
   - [benchmarking](./src/benchmarking/README.md)
   - [prediction](./src/prediction/README.md)
   - [deployment, chain_qd](./deployment/README_MPU.md)

All .yaml configuration examples are located in [config_file_examples](./src/config_file_examples/) folder.

The different values of the `operation_mode` attribute and the corresponding operations are described in the table below. In the names of the chain modes, 'e' stands for evaluation, 'q' for quantization, 'b' for benchmark and 'd' for deployment on an STM32 board.

| operation_mode attribute | Operations |
|:---------------------------|:-----------|
| `evaluation` | Evaluate the accuracy of a float or quantized model on a test or validation dataset|
| `quantization` | Quantize a float model |
| `prediction`   | Predict the classes some images belong to using a float or quantized model |
| `benchmarking` | Benchmark a float or quantized model on an STM32 board |
| `deployment`   | Deploy a model on an STM32 board |
| `chain_eqe`    | Sequentially: evaluation of a float model,  quantization, evaluation of the quantized model |
| `chain_qb`     | Sequentially: quantization of a float model, benchmarking of quantized model |
| `chain_eqeb`   | Sequentially: evaluation of a float model,  quantization, evaluation of quantized model, benchmarking of quantized model |
| `chain_qd`     | Sequentially: quantization of a float model, deployment of quantized model |
