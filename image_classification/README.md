# Image classification STM32 model zoo

Models are stored depending on the way they have been trained :
* `ST_pretrainedmodel_public_dataset` folder contains models trained by ST using public datasets
* `ST_pretrainedmodel_custom_dataset` folder contains models trained by ST using custom datasets
* `Public_pretrainedmodel_public_dataset` folder contains public models using public datasets

## List of available models families:

Following is the overview of all pretrained **image classification models** available for STM32 boards. Each model family links to its folder or README for downloads, usage, and performance metrics.


## TensorFlow Models

[Model performance analysis (TF)](./MODELS_ANALYSIS_TF.md) of these models can be used to select the model based on user's performance requirements. 

### EfficientNet
* [EfficientNet](./efficientnet/README.md)
* [EfficientNet v2](./efficientnetv2/README.md)

### FD MobileNet
* [FDMobileNet](./fdmobilenet/README.md)

### MobileNet
* [MobileNetv1](./mobilenetv1/README.md)
* [MobileNetv2](./mobilenetv2/README.md)

### ResNet
* [ResNet](./resnet/README.md)
* [ResNet50v2](./resnet50v2/README.md)

### SqueezeNet
* [SqueezeNetv1.1](./squeezenetv11/README.md)

### ST MNIST
* [ST MNISTv1](./st_mnistv1/README.md)


## PyTorch Models

[Model performance analysis (Pytorch)](./MODELS_ANALYSIS_TORCH.md) of these models can be used to select the model based on user's performance requirements. 

### ST ResNet
* [ST ResNet](./st_resnet_pt/README.md)

### FD MobileNet
* [FD MobileNet](./fdmobilenet_pt/README.md)

### MobileNet
* [MobileNetv1](./mobilenet_pt/README.md)

### MobileNet v2
* [MobileNetv2](./mobilenetv2_pt/README.md)

### MobileNet v4
* [MobileNetv4](./mobilenetv4_pt/README.md)

### PeleeNet v4
* [PeleeNet](./peleenet_pt/README.md)

### ResNet
* [ResNet18](./resnet18_pt/README.md)

### PreResNet
* [PreResNet18](./preresnet18_pt/README.md)

### DLA
* [DLA Torch](./dla_pt/README.md)

### HardNet
* [HardNet](./hardnet_pt/README.md)

### MNASNet
* [MNASNet](./mnasnet_pt/README.md)

### Proxyless NAS
* [ProxylessNAS](./proxylessnas_pt/README.md)

### SEMNASNet
* [SEMNASNet](./semnasnet_pt/README.md)

### ShuffleNet / SqNxt
* [ShuffleNetv2](./shufflenetv2_pt/README.md)

### ShuffleNext / SqNxt
* [SqueezeNext](./sqnxt_pt/README.md)

### SqueezeNet
* [SqueezeNet](./squeezenet_pt/README.md)

### DarkNet
* [DarkNet](./darknet_pt/README.md)

---

> **Note:** Some folders may contain multiple model variants (Float / Int8, different input resolutions, etc.). For detailed performance tables and ONNX links, refer to the individual README of each model family.

