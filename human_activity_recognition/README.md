# Human Activity Recognition STM32 Model Zoo


## Directory components:
* [datasets](datasets/README.md) placeholder for the human activity recognition datasets.
* [deployment](deployment/README.md) contains the necessary files for the deployment service.
* [pretrained_models](pretrained_models/README.md) a collection of optimized pretrained models on different human activity datasets.
* [src](src/README.md) contains tools to train, evaluate, benchmark and quantize your model on your STM32 target.

## Quick & easy examples:
The `operation_mode` top-level attribute specifies the operations or the service you want to execute. This may be single operation or a set of chained operations.

You can refer to readme links below that provide typical examples of operation modes, and tutorials on specific services:

   - [training, chain_tb](./src/training/README.md)
   - [evaluation](./src/evaluation/README.md)
   - [benchmarking](./src/benchmarking/README.md)
   - [deployment](./deployment/README.md)

All .yaml configuration examples are located in [config_file_examples](./src/config_file_examples/) folder.

The different values of the `operation_mode` attribute and the corresponding operations are described in the table below. In the names of the chain modes, 't' stands for training, 'e' for evaluation, 'q' for quantization, 'b' for benchmark and 'd' for deployment on an STM32 board.

| operation_mode attribute | Operations |
|:---------------------------|:-----------|
| `training`| Train an HAR |
| `evaluation` | Evaluate the accuracy of a float model on a test or validation dataset|
| `benchmarking` | Benchmark a float model on an STM32 board |
| `deployment`   | Deploy a model on an STM32 board |
| `chain_tb`  | Sequentially: training, benchmarking of trained model |

