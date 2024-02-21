# README.MD

In this FW Package, the modules listed below are not directly accessible as they are subject to some restrictive license terms requiring user's approval via a "click thru" procedure.They have to be downloaded from the [www.st.com](https://www.st.com/content/st_com/en.html) website.

## __X-CUBE-AI tool installation__

[X-CUBE-AI](https://www.st.com/en/embedded-software/x-cube-ai.html) is an STM32Cube Expansion Package, which is part of the STM32Cube.AI ecosystem. It extends STM32CubeMX capabilities with automatic conversion of pretrained artificial intelligence algorithms, including neural network and classical machine learning models. It integrates also a generated optimized library into the user's project.

This software is tested with [X-CUBE-AI](https://www.st.com/en/embedded-software/x-cube-ai.html) `v8.0.1`. It is advised that the user uses the same version to avoid any potential compatibility issues.

The pack can be installed through [STM32CubeMX](https://www.st.com/content/st_com/en/products/development-tools/software-development-tools/stm32-software-development-tools/stm32-configurators-and-code-generators/stm32cubemx.html) through the  *STM32CubeExpansion* pack mechanism.

### __Installation of the X-CUBE-AI runtime__

Please copy

```bash
<X_CUBE_AI-directory-path>
  \- Middlewares/ST/AI/Inc/*.h
```

into the middleware project directory `'<install-dir>/Middleware/STM32_AI_Library/Inc'`

and

```bash
<X_CUBE_AI-directory-path>
  \- Middlewares/ST/AI/Lib/NetworkRuntime800_CM33_GCC.a
```

into the middleware project directory `'<install-dir>/Middleware/STM32_AI_Library/Lib'`
