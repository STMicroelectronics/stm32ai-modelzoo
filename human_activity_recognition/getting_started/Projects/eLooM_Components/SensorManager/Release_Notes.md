---
pagetitle: Release Notes for SensorManager_threadx 
lang: en
header-includes: <link rel="icon" type="image/x-icon" href="_htmresc/favicon.png" />
---

::: {.row}
::: {.col-sm-12 .col-lg-4}

<center>
# Release Notes for <mark>SensorManager_threadx</mark>
Copyright &copy; 2022  STMicroelectronics\
    
[![ST logo](_htmresc/st_logo_2020.png)](https://www.st.com){.logo}
</center>


# Purpose

The **SensorManager_threadx** is an eLooM-based application-level FW component.

It retrieves sensor data and sets the sensors parameters.
It is implemented as an acquisition engine that:

- Orchestrates multiple tasks accesses to sensor bus data as follows:
  - One or more sensor for each task
  - Read/write requests via queue to handle concurrency on common buses
- Defines interfaces to avoid implementation dependencies 
- Dispatches events to notify when data ready

It contains specific implementations for the following sensor and peripheral tasks:

- IIS2DLPC
- IIS2ICLX
- IIS2MDC
- IIS3DWB
- ILPS22QS
- IMP23ABSU
- IMP34DT05 
- ISM330DHCX
- ISM330IS
- LIS2DU12
- LIS2MDL
- LPS22DF
- LSM6DSV16X
- MP23DB01HP
- STTS22H
- I2C
- SPI

:::

::: {.col-sm-12 .col-lg-8}
# Update History

::: {.collapse}
<input type="checkbox" id="collapse-section1" checked aria-hidden="true">
<label for="collapse-section1" aria-hidden="true">__v.2.0.0 / 2-Dec-22__</label>
<div>			

## Main Changes

### First official release

- Aligned threadx and FreeRTOS versions
- Removed SMUtilTask and the related UtilityDriver
- Removed Sensor events, substituted by events available in EMData component
- Removed EnvTask, substituted by independent tasks for HTS221 and LPS22HH sensors
- Redesigned Sensor and Bus interfaces
- Code cleaning and typo fixed


## Dependencies

- It works only with sensors drivers from X-CUBE-MEMS1 v9.4.0 and above

</div>
:::

:::
:::

<footer class="sticky">
::: {.columns}
::: {.column width="95%"}
For complete documentation,
visit: [www.st.com](http://www.st.com/STM32)
:::
::: {.column width="5%"}
<abbr title="Based on template cx566953 version 2.0">Info</abbr>
:::
:::
</footer>