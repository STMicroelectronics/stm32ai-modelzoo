/*
******************************************************************************
**

**  File        : LinkerScript.ld
**
**  Abstract    : Linker script for STM32H747XI Devices
**                2048KBytes FLASH and 1024KBytes RAM
**
**                Set heap size, stack size and stack location according
**                to application requirements.
**
**                Set memory bank area and size if external memory is used.
**
**  Target      : STMicroelectronics STM32
**
**  Distribution: The file is distributed as is, without any warranty
**                of any kind.
**
*****************************************************************************
** @attention
**
** <h2><center>&copy; COPYRIGHT(c) 2019 Ac6</center></h2>
**
** Redistribution and use in source and binary forms, with or without modification,
** are permitted provided that the following conditions are met:
**   1. Redistributions of source code must retain the above copyright notice,
**      this list of conditions and the following disclaimer.
**   2. Redistributions in binary form must reproduce the above copyright notice,
**      this list of conditions and the following disclaimer in the documentation
**      and/or other materials provided with the distribution.
**   3. Neither the name of Ac6 nor the names of its contributors
**      may be used to endorse or promote products derived from this software
**      without specific prior written permission.
**
** THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
** AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
** IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
** DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
** FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
** DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
** SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
** CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
** OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
** OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
**
*****************************************************************************
*/

/* Entry Point */
ENTRY(Reset_Handler)

/* Highest address of the user mode stack */
_estack = 0x24080000;    /* end of AXIRAM */
/* Generate a link error if heap and stack don't fit into RAM */
_Min_Heap_Size = 0x1000; /* required amount of heap  */
_Min_Stack_Size = 0x400; /* required amount of stack */

/* Specify the memory areas */
MEMORY
{
ITCMRAM (xrw)   : ORIGIN = 0x00000000, LENGTH = 64K
FLASH_BK1 (rx)  : ORIGIN = 0x08000000, LENGTH = 1024K
FLASH_BK2 (rx)  : ORIGIN = 0x08100000, LENGTH = 1024K
DTCMRAM (xrw)   : ORIGIN = 0x20000000, LENGTH = 128K
AXIRAM (xrw)    : ORIGIN = 0x24000000, LENGTH = 512K
SRAM123 (xrw)   : ORIGIN = 0x30000000, LENGTH = 288K
SRAM4   (xrw)   : ORIGIN = 0x38000000, LENGTH = 64K
BKPSRAM (xrw)   : ORIGIN = 0x38800000, LENGTH = 4K
QSPIFLASH (rx)  : ORIGIN = 0x90000000, LENGTH = 128M
SDRAM (xrw)     : ORIGIN = 0xD0000000, LENGTH = 32M
}

/* Define output sections */
SECTIONS
{
  /* The startup code for CM7 goes first into FLASH_BK1 */
  .isr_vector :
  {
    . = ALIGN(4);
    KEEP(*(.isr_vector)) /* Startup code */
    . = ALIGN(4);
  } >FLASH_BK1

   /* The startup code for CM4 goes into FLASH_BK2 */
  .isr_vector_m4 :
  {
    . = ALIGN(4);
    KEEP(*(.isr_vector_m4))
    . = ALIGN(4);
  } >FLASH_BK2

  /* The program code and other data goes into FLASH */
  .text :
  {
    . = ALIGN(4);
    *(.text)           /* .text sections (code) */
    *(.text*)          /* .text* sections (code) */
    *(.glue_7)         /* glue arm to thumb code */
    *(.glue_7t)        /* glue thumb to arm code */
    *(.eh_frame)

    KEEP (*(.init))
    KEEP (*(.fini))

    . = ALIGN(4);
    _etext = .;        /* define a global symbols at end of code */
  } >FLASH_BK1

  .qspi_section :
  {
    . = ALIGN(4);
    *(.ExternalFlashSection)
    . = ALIGN(4);
  } > QSPIFLASH

  .InternalFlashSection :
  {
    . = ALIGN(4);
    *(.InternalFlashSection)
    . = ALIGN(4);
  } >FLASH_BK2


  /* Constant data goes into FLASH_BK1 */
  .rodata :
  {
    . = ALIGN(4);
    *(.rodata)         /* .rodata sections (constants, strings, etc.) */
    *(.rodata*)        /* .rodata* sections (constants, strings, etc.) */
    . = ALIGN(4);
  } >FLASH_BK1

  .ARM.extab   : { *(.ARM.extab* .gnu.linkonce.armextab.*) } >FLASH_BK1
  .ARM : {
    __exidx_start = .;
    *(.ARM.exidx*)
    __exidx_end = .;
  } >FLASH_BK1

  .preinit_array     :
  {
    PROVIDE_HIDDEN (__preinit_array_start = .);
    KEEP (*(.preinit_array*))
    PROVIDE_HIDDEN (__preinit_array_end = .);
  } >FLASH_BK1
  .init_array :
  {
    PROVIDE_HIDDEN (__init_array_start = .);
    KEEP (*(SORT(.init_array.*)))
    KEEP (*(.init_array*))
    PROVIDE_HIDDEN (__init_array_end = .);
  } >FLASH_BK1
  .fini_array :
  {
    PROVIDE_HIDDEN (__fini_array_start = .);
    KEEP (*(SORT(.fini_array.*)))
    KEEP (*(.fini_array*))
    PROVIDE_HIDDEN (__fini_array_end = .);
  } >FLASH_BK1

  /* used by the startup to initialize data */
  _sidata = LOADADDR(.data);

  /* Initialized data sections goes into RAM, load LMA copy after code */
  .data : 
  {
    . = ALIGN(4);
    _sdata = .;        /* create a global symbol at data start */
    *(.data)           /* .data sections */
    *(.data*)          /* .data* sections */

    . = ALIGN(4);
    _edata = .;        /* define a global symbol at data end */

  } >AXIRAM AT> FLASH_BK1

  
  /* Uninitialized data section */
  . = ALIGN(4);
  .bss :
  {
    /* This is used by the startup in order to initialize the .bss secion */
    _sbss = .;         /* define a global symbol at bss start */
    __bss_start__ = _sbss;
    *(.bss)
    *(.bss*)
    *(COMMON)

    . = ALIGN(4);
    _ebss = .;         /* define a global symbol at bss end */
    __bss_end__ = _ebss;
    . = ALIGN(32);
    *(.CapturedImage_Buffer_AXIRAM)
    . = ALIGN(32);
    *(.RescaledImage_Buffer_AXIRAM)
  } >AXIRAM

  /* User_heap_stack section, used to check that there is enough RAM left */
  ._user_heap_stack :
  {
    . = ALIGN(8);
    PROVIDE ( end = . );
    PROVIDE ( _end = . );
    . = . + _Min_Heap_Size;
    . = . + _Min_Stack_Size;
    . = ALIGN(8);
    . = ALIGN(32);
    *(.NN_Activation_Buffer_DTCMRAM)
  } >DTCMRAM


 .axisram_section (NOLOAD):
  {
    . = ALIGN(32);
    *(.NN_Activation_Buffer_AXIRAM)
  } >AXIRAM
  
  .sram_section (NOLOAD):
  {
    . = ALIGN(32);
    *(.camera_line_buffer)
  } >SRAM123

  .sdram_section (NOLOAD):
  {
    . = ALIGN(32);
    *(.Lcd_Display)
    *(.Lcd_Display*)
    . = ALIGN(32);
    *(.NN_Activation_Buffer_SDRAM)
    . = ALIGN(32);
    *(.CapturedImage_Buffer_SDRAM)
    . = ALIGN(32);
    *(.RescaledImage_Buffer_SDRAM)
  } >SDRAM

  /* Remove information from the standard libraries */
  /DISCARD/ :
  {
    libc.a ( * )
    libm.a ( * )
    libgcc.a ( * )
  }

  .ARM.attributes 0 : { *(.ARM.attributes) }
}


