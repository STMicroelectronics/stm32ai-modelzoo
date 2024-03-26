# Image classification STM32 model zoo


## Directory components:
* [datasets](datasets/README.md) placeholder for the image classification datasets.
* [deployment](deployment/README.md) contains the necessary files for the deployment service.
* [pretrained_models](pretrained_models/README.md) a collection of optimized pretrained models on different image classification datasets.
* [src](src/README.md) contains tools to train, evaluate, benchmark and quantize your model on your STM32 target.

## Quick & easy examples:
The `operation_mode` top-level attribute specifies the operations or the service you want to execute. This may be single operation or a set of chained operations.

You can refer to readme links below that provide typical examples of operation modes, and tutorials on specific services:

   - [training, chain_tqe (train + quantize + evaluate), chain_tbqeb](./src/training/README.md)
   - [quantization, chain_eqe, chain_qb](./src/quantization/README.md)
   - [evaluation, chain_eqeb](./src/evaluation/README.md)
   - [benchmarking](./src/benchmarking/README.md)
   - [prediction](./src/prediction/README.md)
   - [deployment, chain_qd](./deployment/README.md)

All .yaml configuration examples are located in [config_file_examples](./src/config_file_examples/) folder.

The different values of the `operation_mode` attribute and the corresponding operations are described in the table below. In the names of the chain modes, 't' stands for training, 'e' for evaluation, 'q' for quantization, 'b' for benchmark and 'd' for deployment on an STM32 board.

| operation_mode attribute | Operations |
|:---------------------------|:-----------|
| `training`| Train a model from the variety of classification models in the model zoo **(BYOD)** or your own model **(BYOM)** |
| `evaluation` | Evaluate the accuracy of a float or quantized model on a test or validation dataset|
| `quantization` | Quantize a float model |
| `prediction`   | Predict the classes some images belong to using a float or quantized model |
| `benchmarking` | Benchmark a float or quantized model on an STM32 board |
| `deployment`   | Deploy a model on an STM32 board |
| `chain_tbqeb`  | Sequentially: training, benchmarking of trained model, quantization of trained model, evaluation of quantized model, benchmarking of quantized model |
| `chain_tqe`    | Sequentially: training, quantization of trained model, evaluation of quantized model |
| `chain_eqe`    | Sequentially: evaluation of a float model,  quantization, evaluation of the quantized model |
| `chain_qb`     | Sequentially: quantization of a float model, benchmarking of quantized model |
| `chain_eqeb`   | Sequentially: evaluation of a float model,  quantization, evaluation of quantized model, benchmarking of quantized model |
| `chain_qd`     | Sequentially: quantization of a float model, deployment of quantized model |

