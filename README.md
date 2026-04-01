# ST Object Detection

End-to-end YOLOv8-based object detection project for STM32N6 microcontrollers. This project automates the process of quantizing YOLOv8 models to INT8 format, converting them to TFLite, and deploying them to STM32N6 boards.


## Features

- **YOLOv8 Model Export**: Convert PyTorch models to ONNX, TFLite, and SavedModel formats
- **INT8 Quantization**: Reduce model size and increase inference speed with Post-Training Quantization (PTQ)
- **STM32N6 Deployment**: Deploy quantized models to STM32N6 microcontrollers
- **Pipeline Automation**: Run all steps with a single script
- **Configuration-Based**: Easy configuration with YAML files


## Hardware Prerequisites

Before starting, ensure you have the following hardware ready:

| Hardware | Details |
|----------|---------|
| **STM32N6570-DK** or **NUCLEO-N657X0-Q** | Target development board |
| **Camera module** | MB1854 (IMX335, included with DK), STEVAL-55G1MBI, or STEVAL-66GYMAI1 |
| **USB-C to USB-C cable** | Required for STLINK connection — USB-A to USB-C may not provide sufficient power |

> For full hardware setup instructions, boot mode configuration, debug console setup, and hardware troubleshooting, see [HARDWARE_GUIDE.md](HARDWARE_GUIDE.md).

---

## Installation

### Requirements

| Software | Description |
|----------|-------------|
| **Python 3.11+** | Project requires Python 3.11 or higher |
| **STM32CubeIDE** | Required for compiling and flashing STM32N6 projects. [Download](https://www.st.com/en/development-tools/stm32cubeide.html) |
| **ST Edge AI** | Required for model conversion and optimization. [Download](https://www.st.com/en/development-tools/stedgeai-core.html) |


### 1. Create Virtual Environment

```bash
cd stm32ai-n6-yolov8-objectdetection
python3.11 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Installed Packages (requirements.txt)

| Package | Version |
---------|---------|
| tensorflow | 2.15.1 |
| tf_keras | 2.15.1 |
| onnx | 1.15.0 |
| onnxruntime | 1.18.1 |



## Running

### Option 1: Run All Steps with Pipeline (Recommended)

> [!WARNING]
>
> Before running the pipeline:
> - STM32N6 board must be connected and ready for deployment
> - STM32CubeIDE and ST Edge AI paths must be configured in the system


Run all steps (export, quantization, deployment) with a single command:

```bash
python pipeline.py
```

The pipeline runs the following steps sequentially:
1. YOLOv8 model export (TFLite INT8)
2. TFLite quantization
3. STM32N6 deployment

> **Note**: If a step fails, the pipeline stops and does not proceed to the next steps.

---

### Option 2: Step-by-Step Manual Execution

#### Step 1: YOLOv8 Model Export

Convert the PyTorch model to TFLite INT8 format:

```bash
yolo export model=yolov8n.pt format=tflite imgsz=256 int8=True
```

Other format options:

```bash
# Export to ONNX format
yolo export model=yolov8n.pt format=onnx imgsz=256

# Export to TensorFlow SavedModel format
yolo export model=yolov8n.pt format=saved_model imgsz=256
```

#### Step 2: INT8 Quantization

```bash
cd yolov8_quantization
python tflite_quant.py --config-name user_config_quant.yaml
```

You can edit quantization settings in the `user_config_quant.yaml` file:

```yaml
model:
  model_name: yolov8n_256
  model_path: ../yolov8n_saved_model
  input_shape: [256, 256, 3]

quantization:
  quantizer: TFlite_converter
  quantization_type: PTQ
  quantization_input_type: uint8
  quantization_output_type: float
  granularity: per_tensor
  calibration_images_path: ../datasets/coco8/images/val
```

#### Step 3: STM32N6 Deployment

```bash
cd ../object_detection
python stm32ai_main.py --config-path ./config_file_examples/ --config-name deployment_n6_yolov8_config.yaml
```

After deployment is complete:
1. Open the `STM32N6/` folder with STM32CubeIDE
2. Build the project
3. Flash the binary to the STM32N6 board
4. Switch the board to **Boot from Flash** mode and power cycle

> For boot switch/jumper positions and board connection details, see [HARDWARE_GUIDE.md](HARDWARE_GUIDE.md).

## Project Structure

```
stm32ai-n6-yolov8-objectdetection/
├── pipeline.py                  # Main script that runs all steps
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
├── LICENSE.md                   # License information
├── SECURITY.md                  # Security policy
│
├── api/                         # API module
│   ├── api.py                   # API implementation
│   └── README.md                # API documentation
│
├── common/                      # Shared utilities and tools
│   ├── benchmarking/            # Benchmarking tools
│   ├── compression/             # Model compression utilities
│   ├── data_augmentation/       # Data augmentation tools
│   ├── deployment/              # Deployment utilities
│   ├── evaluation/              # Model evaluation tools
│   ├── model_utils/             # Model utilities
│   ├── onnx_utils/              # ONNX conversion utilities
│   ├── optimization/            # Optimization tools
│   ├── prediction/              # Prediction utilities
│   ├── quantization/            # Quantization tools
│   ├── stm32ai_dc/              # STM32AI Developer Cloud
│   ├── stm32ai_local/           # STM32AI Local tools
│   ├── stm_ai_runner/           # STM AI runner
│   ├── training/                # Training utilities
│   └── utils/                   # General utilities
│
├── object_detection/            # STM32 Model Zoo - Object Detection module
│   ├── stm32ai_main.py          # Main deployment script
│   ├── user_config.yaml         # TensorFlow configuration
│   ├── user_config_pt.yaml      # PyTorch configuration
│   ├── README.md                # Module documentation
│   ├── config_file_examples/    # TensorFlow example configs
│   ├── config_file_examples_pt/ # PyTorch example configs
│   ├── datasets/                # Datasets for training/validation
│   ├── docs/                    # Documentation
│   ├── pt/                      # PyTorch tools
│   └── tf/                      # TensorFlow tools
│
└── yolov8_quantization/         # YOLOv8 INT8 quantization tools
    ├── tflite_quant.py          # TFLite quantization script
    ├── user_config_quant.yaml   # Quantization configuration
    ├── README.md                # Quantization documentation
    ├── quantized_models/        # Quantized models (output)
    └── outputs/                 # Quantization outputs
```

## License

This project is licensed under the STMicroelectronics license. See `LICENSE.md` for details.

