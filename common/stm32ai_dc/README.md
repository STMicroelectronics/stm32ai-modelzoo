# STM32AI Python interface
STM32AI Python Interface is a Python implementation of the REST APIs dedicated to [STM32Cube.AI Developer Cloud](https://stedgeai-dc.st.com/home). 

With this package, you will be able to:
- Log in to [STM32Cube.AI Developer Cloud](https://stedgeai-dc.st.com/home) using your MyST Account
- Upload your own Keras, TFLite and ONNX Model
- Analyze your model with our tool in order to know memory footprint, model complexity and more
- Benchmark your model directly in real STM32 targets to get real performance (inference time, memory footprint...)
- Generate C Code from your model


# Before you start

You will need to have a MyST account in order to use this service. If not, please register in [st.com](https://www.st.com/content/st_com/en.html) website.

# Requirements
- Python >= 3.7

# Getting Started

Install Python package required
```sh
pip install -r requirements.txt
```

Export your MyST username and passwords 

```sh
export STM32AI_USERNAME="dupont@example.com"    # Address mail used for your MyST Account
export STM32AI_PASSWORD="password"              # Your password
```

# Arguments Interface

Arguments supported for CLI calls are available in [./stm32ai_dc/types.py](https://github.com/STMicroelectronics/stm32ai-modelzoo_services/blob/75947f8946c144e0fdd341c189d327bcc187db22/common/stm32ai_dc/types.py#L77)


# Troubleshooting

You might have issues if you are working behind a corporate proxy. To fix your issues, please try the following:

## I need to set a proxy setting

```sh
export http_proxy="http://username:password@proxy_addr:proxy_port"
export https_proxy="http://username:password@proxy_addr:proxy_port"
```

## Connection Reset / Connection error on HTTPS Requests

These issues might be due to proxy configuration which requires to set a certificate.
In order to skip this error, you can try the following:

```sh
export NO_SSL_VERIFY="1"
```

# Example

Examples are available in `./stm32ai_dc_examples/` folder