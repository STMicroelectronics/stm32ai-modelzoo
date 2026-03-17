---
title: Nanopb files generation
---

# Introduction

The COM protocol over serial link between the HOST and the STM32 aiValidation test
firmware is fully based on *Proto Buffer* (see **[[1]][PROTO_BUFF]**)
to handle and define the exchanged messages. A specific implementation for Embedded
Systems has been used for the STM32 support (see **[[2]][NANOPB]**).
  
This directory contents the source files (STM32 message definitions) to generate the
associated Python and embedded C API.

## History

+ 2.1: original version (X-CUBE-AI 4.x up to 6.0)
+ 2.2: minor update in msg desc (X-CUBE-AI 7.0) to retreive RT/ARM desc.


## References

[PROTO_BUFF]: https://developers.google.com/protocol-buffers/
[NANOPB]: https://github.com/nanopb/nanopb
[DOWNLOAD]: https://jpa.kapsi.fi/nanopb/download/

------------------------- -----------------------------------------------------  
[\[1\]][PROTO_BUFF]       [Protocol Buffers][PROTO_BUFF]

[\[2\]][NANOPB]           [Nanopb - Protocol Buffers for Embedded Systems][NANOPB]

[\[3\]][DOWNLOAD]         [Nanopb - downloads][DOWNLOAD]
------------------------- -----------------------------------------------------  

# Implementation considerations

- Currently the `0.3.9.1` version of the Proto Buffer compiler has been used.
  See **[[3]][DOWNLOAD]** to download a ready to use binary package.


## Dependencies

    pyserial>=3.4
    protobuf


# Generate the API files

Proto buffer compiler should be installed (see **[[3]][DOWNLOAD]**). The `Makefile` 
should be updated according the installation directory.

Generate the Python and C files

    make all

Install the generate files, `C_INSTALL_ROOT_DIR` should be also defined.

    make install

**Note** if a new version of Proto Buffer compiler is used, following files
should be also copied (from compiler package) to be able to build the
STM32 firmware.

    pb.h    (should be adapted: PB_FIELD_16BIT is defined)
    pb_common.h pb_common.c
    pb_decode.h pb_decode.c
    pb_encode.h pb_encode.c

