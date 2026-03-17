#
# Makefile to generate the proto interface files
#  Python and Embedded C (nanopb) version
#

###################################################################################
#   Copyright (c) 2021 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################

NANOPB_DIR ?= "c:\tools\nanopb\generator-bin"
C_INSTALL_ROOT_DIR ?= "D:\dev\stm.ai\new_root\targets\common\EmbedNets\stm32\Nucleo-App\Middlewares\ST\Application\Validation"


PROTOC = $(NANOPB_DIR)/protoc

TARGET_PY = stm32msg_pb2.py
TARGET_C  = stm32msg.pb.c stm32msg.pb.h

PROTO_SRC  = stm32msg.proto
PROTO_DEPS = $(PROTO_SRC) stm32msg.options

PY_INSTALL_DIR ?= ..
C_INSTALL_DIR ?= Src
H_INSTALL_DIR ?= Inc

O  ?= ./build

PY_OBJS = $(addprefix $(O)/, $(TARGET_PY))
C_OBJS  = $(addprefix $(O)/, $(TARGET_C))

#
# Targets
#
.PHONY: all install clean FORCE

.DEFAULT_GOAL := all

all: $(PY_OBJS) $(C_OBJS)

$(PY_OBJS): $(PROTO_DEPS)
	@mkdir -p $(@D)
	$(PROTOC) --python_out=$(O) $(PROTO_SRC)

$(C_OBJS): $(PROTO_DEPS)
	@mkdir -p $(@D)
	$(PROTOC) --nanopb_out=$(O) $(PROTO_SRC)

install: $(PY_OBJS) $(C_OBJS)
ifneq ($(strip $(C_INSTALL_ROOT_DIR)),)
	@echo Install generated files
	@cp $(O)/*.c $(C_INSTALL_ROOT_DIR)/$(C_INSTALL_DIR)
	@cp $(O)/*.h $(C_INSTALL_ROOT_DIR)/$(H_INSTALL_DIR)
	@cp $(O)/*.py $(PY_INSTALL_DIR)
else
	$(info C_INSTALL_ROOT_DIR should be defined)
endif

clean:
	${q}rm -rf $(O)

FORCE: ;
