# ST Object Detection

End-to-end YOLOv8-based object detection project for STM32N6 microcontrollers. This project automates the process of quantizing YOLOv8 models to INT8 format, converting them to TFLite, and deploying them to STM32N6 boards.

## Features

- **YOLOv8 Model Export**: Convert PyTorch models to ONNX, TFLite, and SavedModel formats
- **INT8 Quantization**: Reduce model size and increase inference speed with Post-Training Quantization (PTQ)
- **STM32N6 Deployment**: Deploy quantized models to STM32N6 microcontrollers
- **Pipeline Automation**: Run all steps with a single script
- **Configuration-Based**: Easy configuration with YAML files

## Installation

### Requirements

| Software | Description |
|----------|-------------|
| **Python 3.11+** | Project requires Python 3.11 or higher |
| **STM32CubeIDE** | Required for compiling and flashing STM32N6 projects. [Download](https://www.st.com/en/development-tools/stm32cubeide.html) |
| **ST Edge AI** | Required for model conversion and optimization. [Download](https://www.st.com/en/development-tools/stedgeai-core.html) |

### 1. Create Virtual Environment

```bash
cd st-objectdetection
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

| Category | Packages |
|----------|----------|
| Deep Learning | tensorflow==2.15.1, torch==2.10.0, keras==2.15.0 |
| YOLOv8 | ultralytics==8.4.21 |
| ONNX Tools | onnx==1.15.0, onnx2tf==1.28.8, onnxruntime==1.18.1 |
| TFLite | ai-edge-litert==1.3.0 |
| Config | hydra-core==1.3.2, omegaconf==2.3.0 |
| Data | numpy==1.26.4, opencv-python==4.13.0.92 |

## Running

### Option 1: Run All Steps with Pipeline (Recommended)

Run all steps (export, quantization, deployment) with a single command:

```bash
cd st-objectdetection
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
cd st-objectdetection
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
cd object_detection
python stm32ai_main.py --config-path ./config_file_examples/ --config-name deployment_n6_st_yoloxn_config.yaml
```

After deployment is complete:
1. Open the `STM32N6/` folder with STM32CubeIDE
2. Build the project
3. Flash the binary to the STM32N6 board

## Project Structure

```
st-objectdetection/
├── pipeline.py                # Main script that runs all steps
├── requirements.txt           # Python dependencies
├── yolov8n.pt                 # Original YOLOv8n PyTorch model
├── yolov8n.onnx               # Model in ONNX format
├── yolov8n_saved_model/       # TensorFlow SavedModel format
├── datasets/                  # Training and calibration datasets
│
├── object_detection/          # STM32 Model Zoo - Object Detection module
│   ├── stm32ai_main.py        # Main deployment script
│   ├── config_file_examples/  # Example configuration files
│   ├── tf/                    # TensorFlow tools
│   ├── pt/                    # PyTorch tools
│   └── docs/                  # Documentation
│
├── yolov8_quantization/       # YOLOv8 INT8 quantization tools
│   ├── tflite_quant.py        # TFLite quantization script
│   ├── user_config_quant.yaml # Quantization configuration
│   ├── quantized_models/      # Quantized models (output)
│   └── outputs/               # Quantization outputs
│
└── STM32N6/                   # STM32N6 deployment projects
    ├── Application/           # Application code
    ├── Model/                 # Model files
    ├── Binary/                # Compiled binary files
    └── Doc/                   # Documentation
```

## License

This project is licensed under the STMicroelectronics license. See `LICENSE.md` for details.

