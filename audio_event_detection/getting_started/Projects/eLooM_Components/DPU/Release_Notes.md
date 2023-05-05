---
pagetitle: Release Notes for Digital Processing Unit FW module
lang: en
header-includes: <link rel="icon" type="image/x-icon" href="_htmresc/favicon.png" />
---

::: {.row}
::: {.col-sm-12 .col-lg-4}

<center>
# Release Notes for <mark>Digital Processing Unit FW module</mark>
Copyright &copy; 2022  STMicroelectronics\
    
[![ST logo](_htmresc/st_logo_2020.png)](https://www.st.com){.logo}
</center>


# Purpose

The **Digital Processing Unit FW module** is an eLooM-based application-level FW module.

It implements an Abstract Data Processing Unit​, a Generic Processing Unit class​ that simplifies integration 
of the following Data processing libraries:

- Cube.AI
- FFT
- NanoEdge AI
- MFCC
- AiUSC

:::

::: {.col-sm-12 .col-lg-8}
# Update History

::: {.collapse}
<input type="checkbox" id="collapse-section4" checked aria-hidden="true">
<label for="collapse-section4" aria-hidden="true">v2.0.0 / 2-Dec-2022</label>
<div>	

## Main Changes

### Product update

- Compatibility break: complete code redesign
- New DPU interfaces, virtual tables and DataBuilder data format protocol
- Updated to DPU v2:
  - AiDPU (specialized in AI_HAR_DPU and AiUSC_DPU)
  - Dummy_DPU
  - FFT_DPU
  - MfccDPU
  - NeaiDPU
- Removed DPU v1 only libraries (not compatible with DPU v2):
  - AnomalyThreshold_DPU
  - Motion_DPU
- Moved CircularBuffer in EMData component
- Removed Process events, substituted by events available in EMData component 
- Code cleaning and typo fixed

</div>

:::

::: {.collapse}
<input type="checkbox" id="collapse-section3" aria-hidden="true">
<label for="collapse-section3" aria-hidden="true">v1.1.0 / 18-Mar-2022</label>
<div>	

## Main Changes

### Maintenance release and product update

- Added new libraries:
  - MFCC
  - AiUSC
- Updated NeaiDPU: aligned Classification part to latest NanoEdgeAI Studio
- Updated AiDPU: added SetSensitivity function and updated Init and Process
- Updated Release Notes and License

</div>

:::

::: {.collapse}
<input type="checkbox" id="collapse-section2"  aria-hidden="true">
<label for="collapse-section2" aria-hidden="true">v1.0.1 / 10-Dec-2021</label>
<div>	

## Main Changes

### Patch release

- NanoEdge AI Studio v3.x API break: 
  - Aligned NanoEdgeAI DPU to new APIs
  - Only anomaly detection use case is supported
  - Libraries generated from previous versions of NanoEdgeAI Studio are not compatible anymore
- Minor optimization in AiDPU.c

</div>

:::

::: {.collapse}
<input type="checkbox" id="collapse-section1" aria-hidden="true">
<label for="collapse-section1" aria-hidden="true">v1.0.0 / 6-Sep-2021</label>
<div>	

## Main Changes

### First official release

It contains specific implementations for the following signal processing units:

- Cube.AI
- Anomaly threshold
- FFT
- Motion Time Domain
- NanoEdge AI

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
