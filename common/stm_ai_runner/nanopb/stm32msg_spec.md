---
title: stm32 msg definition/specification
---

# Introduction

## Protocol overview

All requests are initiated by the HOST (master). A transaction is started by a given `reqMsg` (`CMD_XX`) message with a
specific `reqid`. The sequence of the exchanged messages are dependent of this command (answer/response from the STM32
should have always this `reqid`). A transaction is finished with a `reqMsg` message with the `state = S_IDLE/S_DONE/S_ERROR`

```proto
// Request/cmd message (HOST -> STM32)
message reqMsg {
	required uint32  reqid = 1;
	required EnumCmd cmd = 2 [default = CMD_SYS_INFO];
	required uint32  param = 3;
	required string  name = 4;
	required uint32  opt = 5;	
}
```

## Low-level PB message implementation

The LL COM protocol between the HOST and the STM32 is based on a "full-duplex" serial link interface. The main assumption and
constraint is that no HW flow control is available (case when only UART TX/RX pins are available with the ST-LINK VCP),
and STM32 side, zero-copy paradigm is considered in particular to exchange the data of the tensors. The port/adaptation of the
requested STM32 low-level COM functions should be also facilitated by the simple read/write functions in blocking mode.
To guarantee the exchanges and to avoid the overflows, extra messages (ack/sync) are generated allowing to suspend the transmitter
if the receiver is not ready to process more data.
Serialized messages are cut into packets of 32 bytes (`IO_[IN,OUT]_PACKET_SIZE`) with a header of 1 byte to indicate
the useful data. STM32 COM driver have a simple buffer of 32+1 bytes to handle the received packets (polling mode), when this
packet is consumed/de-serialzed by the embedded proto-buff stack (streaming mode), a sync (`IO_OUT_SYNC`) is sent, to
request the new data if necessary.

```
    [HOST]                                              [STM32]

    ...                                                 waiting msg state
    send_msg(X):
                                                        decode msg (stream mode)
            send packet0 ----------(packet0)---------->     read(33B)
                                                            de-serialize packet
        loop (packets[:-1])
                                                            until msg is not fully de-serialized
            wait sync   <--------- (sync) -------------        sent sync - write(sync)
            send packet -----------(packet) --------->         read(33B) 
                                                               de-serialize packet                            
```

Note that for the PB msg sent by the STM32 to HOST, the serialized msg is also cut into
packets of 32 bytes (32+1), but no `sync` is expected because the design consider that the HOST
as a sufficent low-level buffering capabality to store the received data w/o overflow. HOST side, the
`IO_HEADER_EOM_FLAG` flag in the header of the LL packet indicates that a full message has been accumulated and
it can be de-serialized. No proto-buff streaming mode is used by the HOST.  

### Send a PB message to STM32

`_send_request()/_send_ack()/_send_buffer()`

+ fill a PB mess and call `_write_delimited()` -> mess
+ check if the PB mess is fully initialized
+ serialize the PB mess (`mess.SerializeToString()`) and prefix it by the size in byte (PB write_delimited mode) -> buff
+ split the buffer by packet of 32 Bytes (`IO_OUT_PACKET_SIZE`) -> packs[]
+ send the first pack
+ if len(packs)>1, wait ack from STM32 (simple byte) before to send the next packet
    - no ack is expected for the last packet.

```
io_packet definition (see `_write_io_packet()`)
    size: IO_OUT_PACKET_SIZE + 1    // constant size: 32 (IO_OUT_PACKET_SIZE) + 1 = 33 bytes
    raw format:  <s><payload><pads> // first byte (s) indicates the size of data: pad size = IO_OUT_PACKET_SIZE - s   
```

This mechnism allows to control the flow between the HOST and the STM32. It guarantees that the current packet has been
received and consumed before to send the next. This is equivalent to have a INPUT buffer of 33 bytes.

```Python
    def _write_delimited(self, mess, timeout=5000):
        """Helper function to write a message prefixed with its size"""  # noqa: DAR101,DAR201,DAR401

        if not mess.IsInitialized():
            raise NotInitializedMsgError

        buff = mess.SerializeToString()
        _head = _VarintBytes(mess.ByteSize())

        buff = _head + buff

        packs = [buff[i:i + stm32msg.IO_OUT_PACKET_SIZE]
                 for i in range(0, len(buff), stm32msg.IO_OUT_PACKET_SIZE)]

        n_w = self._write_io_packet(packs[0])
        for pack in packs[1:]:
            if not self._waiting_io_ack(timeout):
                break
            n_w += self._write_io_packet(pack)

        return n_w

    def _write_io_packet(self, payload, delay=0):
        iob = bytearray(stm32msg.IO_OUT_PACKET_SIZE + 1)
        iob[0] = len(payload)
        for i, val in enumerate(payload):
            iob[i + 1] = val
        if not delay:
            _w = self._io_drv.write(iob)
        else:
            _w = 0
            for elem in iob:
                _w += self._io_drv.write(elem.to_bytes(1, 'big'))
                t.sleep(delay)
        return _w
```

### Receive PB message from STM32

```proto
// RESP message (STM32 to HOST)
message respMsg {
	required uint32 reqid = 1;
	required EnumState state = 2;
	oneof payload {
		syncMsg sync = 10;
		sysinfoMsg sinfo = 11;
		ackMsg ack = 12;
		logMsg log = 13;
		nodeMsg node = 14;

		aiNetworkInfoMsg ninfo = 20;
		aiRunReportMsg   report = 21; 
	}
}
```

```Python
def _waiting_answer(self, timeout=10000, msg_type=None, state=None)
def _waiting_msg(self, timeout, msg_type=None)
```

As to send a PB message, the driver (`_waiting_msg()`) expects to receive a serialized PB message by
io_packet of 33 bytes (`IO_IN_PACKET_SIZE + 1`).
No ack is sent to the STM32. The main assumption is that by construction the HOST is able to consume the incoming data w/o overflow.  
Last packet of the serialized PB message is defined by a specific bit: `last = p_buf[0] & stm32msg.IO_HEADER_EOM_FLAG`.
After the coherance of the serialized message is checked and desialized (see `_parse_and_check()`)

```Python
    def _waiting_msg(self, timeout, msg_type=None):
        """Helper function to receive a message"""  # noqa: DAR101,DAR201,DAR401
        buf = bytearray()

        packet_s = int(stm32msg.IO_IN_PACKET_SIZE + 1)
        if timeout == 0:
            t.sleep(0.2)

        start_time = t.monotonic()
        while True:
            p_buf = bytearray()
            while len(p_buf) < packet_s:
                io_buf = self._io_drv.read(packet_s - len(p_buf))
                if io_buf:
                    p_buf += io_buf
                else:
                    cum_time = t.monotonic() - start_time
                    if timeout and (cum_time > timeout / 1000):
                        raise TimeoutError(
                            'STM32 - read timeout {:.1f}ms/{}ms'.format(cum_time * 1000, timeout))
                    if timeout == 0:
                        return self._parse_and_check(buf, msg_type)
            last = p_buf[0] & stm32msg.IO_HEADER_EOM_FLAG
            # cbuf[0] = cbuf[0] & 0x7F & ~stm32msg.IO_HEADER_SIZE_MSK
            p_buf[0] &= 0x7F  # & ~stm32msg.IO_HEADER_SIZE_MSK)
            if last:
                buf += p_buf[1:1 + p_buf[0]]
                break
            buf += p_buf[1:packet_s]
        resp = self._parse_and_check(buf, msg_type)
        return resp
```

### Nano PB port

see `aiPbIO.c` file

```C++
pb_ostream_t pb_io_ostream(int fd)
{
  pb_ostream_t stream = {&write_callback, (void*)(intptr_t)fd, SIZE_MAX, 0};
  return stream;
}

pb_istream_t pb_io_istream(int fd)
{
  pb_istream_t stream = {&read_callback, (void*)(intptr_t)fd, SIZE_MAX};
  return stream;
}

int pb_io_stream_init(void)
{
  ioRawDisableLLWrite();
  return 0;
}
```


# CMD_XX

## CMD_SYNC

```proto
// Sub RESP message (STM32 to HOST)
message syncMsg {
	required uint32 version = 1;
	required uint32 capability = 4;
	required uint32 rtid = 5;
}
```

version: msg protocol version

rtid: runtime definition - 32b 4x8b
    b7..b0: runtime id          EnumAiRuntime
    b15..b8: api type id        EnumAiApiRuntime << AI_RT_API_POS
    b23..b16: tool-chain id     EnumTools << AI_TOOLS_POS
    b31..b24: reserved

capability: test capability - or-ed EnumCapability


```C
-> reqMsg(reqid=X, CMD_SYNC, name="", param=0, opt=0)
<- respMsg(reqid=X, state=S_IDLE, sync=(version=VER, capability=CAPS, rtid=RTID))
```

## CMD_SYS_INFO

```proto
// Sub RESP message (STM32 to HOST)
message sysinfoMsg {
	required uint32 devid = 1;
	required uint32 sclock = 2;
	required uint32 hclock = 3;
	required uint32 cache = 4;    // STM32 device dependent
}
```

```C
-> reqMsg(reqid=X, CMD_SYS_INFO, name="", param=0, opt=0)
<- respMsg(reqid=X, state=S_IDLE, sinfo=(...))
```