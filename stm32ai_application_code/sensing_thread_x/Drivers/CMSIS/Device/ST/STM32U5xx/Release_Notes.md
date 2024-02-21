---
pagetitle: Release Notes for STM32U5xx CMSIS
lang: en
header-includes: <link rel="icon" type="image/x-icon" href="_htmresc/favicon.png" />
---

::: {.row}
::: {.col-sm-12 .col-lg-4}

<center>
# Release Notes for <mark>\ STM32U5xx CMSIS </mark>
Copyright &copy; 2021\ STMicroelectronics\
    
[![ST logo](_htmresc/st_logo_2020.png)](https://www.st.com){.logo}
</center>

:::

::: {.col-sm-12 .col-lg-8}

# __Update History__

::: {.collapse}
<input type="checkbox" id="collapse-section3" checked aria-hidden="true">
<label for="collapse-section3" checked aria-hidden="true">__V1.1.0 /  16-February-2022__</label>
<div>

## Main Changes 

- **CMSIS Device** Maintenance Release version of bits and registers definition aligned with RM0456 (STM32U5 reference manual)
  - Add the support of STM32U595xx, STM32U5A5xx, STM32U599xx and STM32U5A9xx devices
  - Define XSPI_TypeDef as alias to OCTOSPI_TypeDef and HSPI_TypeDef
  - Define XSPIM_TypeDef as alias to OCTOSPIM_TypeDef
  - Update XSPI bit definition to alias OCTOSPI and HSPI bits
  - Add OPAMP12_COMMON_NS, OPAMP12_COMMON_S, OPAMP12_COMMON, OPAMP12_COMMON_BASE defines
  - Update OPAMP_Common_TypeDef to align with reference manual
  - Add the SRAM4 memory definition in all STM32CubeIDE flashloader files
  - Update the flash size define to support:
     - STM32U575/STM32U585: 2Mbytes flash devices
	 - STM32U595/STM32U5A5/STM32U599/STM32U5A9: 4Mbytes flash devices
  - Rename PVD_AVD_IRQHandler to PVD_PVM_IRQHandler in all start-up files
  - Rename RCC_AHB2RSTR1_ADC1RST to RCC_AHB2RSTR1_ADC12RST
  - Rename RCC_AHB2ENR1_ADC1EN to RCC_AHB2ENR1_ADC12EN
  - Rename RCC_AHB2SMENR1_ADC1SMEN to RCC_AHB2SMENR1_ADC12SMEN
  - Rename RCC_CCIPR1_CLK48MSEL to RCC_CCIPR1_ICLKSEL
  - Rename RCC_SECCFGR_CLK48MSEC to RCC_SECCFGR_ICLKSEC
  - Add TIM3 and TIM4 are missing in IS_TIM_32B_COUNTER_INSTANCE macro definition

</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section2" aria-hidden="true">
<label for="collapse-section2" checked aria-hidden="true">__V1.0.1 /  01-October-2021__</label>
<div>

## Main Changes 

- Rename OTG_FS_BASE_NS to USB_OTG_FS_BASE_NS define
- Rename OTG_FS_BASE_S to USB_OTG_FS_BASE_S define
- Add LSI_STARTUP_TIME define
- Fix wrong IRQn name in partition_stm32u5xx.h


</div>
:::


::: {.collapse}
<input type="checkbox" id="collapse-section1" aria-hidden="true">
<label for="collapse-section1" checked aria-hidden="true">__V1.0.0 /  28-June-2021__</label>
<div>

## Main Changes 

- First official release version of bits and registers definition aligned with RM0456 (STM32U5 reference manual)


</div>
:::

:::
:::

<footer class="sticky">
For complete documentation on STM32 Microcontrollers </mark> ,
visit: [[www.st.com/stm32](http://www.st.com/stm32)]{style="font-color: blue;"}
</footer>
