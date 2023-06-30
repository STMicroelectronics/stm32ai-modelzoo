---
pagetitle: Release Notes for eLooM_threadx
lang: en
header-includes: <link rel="icon" type="image/x-icon" href="_htmresc/favicon.png" />
---

::: {.row}
::: {.col-sm-12 .col-lg-4}

<center>
# Release Notes for <mark>eLooM_threadx</mark>
Copyright &copy; 2022 STMicroelectronics\
    
[![ST logo](_htmresc/st_logo_2020.png)](https://www.st.com){.logo}
</center>


# Purpose

<center>
[![eLooM logo](_htmresc/eLooM_logo.png)]{.logo}
</center>

**eLooM** is an **e**mbedded **L**ight **o**bject **o**riented fra**M**ework for STM32 application. 
This version has been developed based on **threadx**.
It is:

 - a well structured design pattern to model low power embedded application.
 - a framework providing the infrastructure to build your embedded applications.
 - a way to make firmware modular and easy to reuse.

The framework provides the following features:

 - System Initialization
 - Tasks management
 - Power Mode management
 - 2nd Bootloader ready
 - Error management
 - Debug log

:::

::: {.col-sm-12 .col-lg-8}
# Update History

::: {.collapse}
<input type="checkbox" id="collapse-section1" checked aria-hidden="true">
<label for="collapse-section1" aria-hidden="true">v3.1.0 / 2-Dec-22</label>
<div>

## Main Changes

### First official release

 - Aligned threadx and FreeRTOS versions
 - Removed SourceObservable events, substituted by events available in EMData component 
 - Added SysTimestamp service and related drivers
 - Implemented sysmem service to allow use the preferred allocator
 - Code cleaning and typo fixed

</div>

:::
:::
:::


<footer class="sticky">
::: {.columns}
::: {.column width="95%"}
For complete documentation on **STM32**
microcontrollers please visit: [www.st.com](https://www.st.com/en/microcontrollers-microprocessors.html)
:::
::: {.column width="5%"}
<abbr title="Based on template cx566953 version 2.0">Info</abbr>
:::
:::
</footer>
