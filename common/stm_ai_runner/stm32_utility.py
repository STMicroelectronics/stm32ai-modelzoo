###################################################################################
#   Copyright (c) 2021 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
STM AI runner - STM32 helper functions
"""

# todo - push the STM32 flags/definition in an interface file (TBD) to share them
#        with the C-code.

#  format(32b)    31..24: STM32 series
#                 23..17: spare
#                 16:     FPU is enabled or not
#                 15..12: spare
#                 11:     H7/F7:D$ is enabled
#                 10:     H7/F7:I$ is enabled             F4/L4: ART DCen
#                 9:      F7: ART enabled                 F4/L4: ART ICen   L5: ICACHE
#                 8:      F4/L4/F7:ART Prefetch enabled
#                 7..0:   ART number of cycles (latency)
#

from binascii import hexlify


_STM32_SERIES_F4 = 1
_STM32_SERIES_F7 = 2
_STM32_SERIES_H7 = 3
_STM32_SERIES_L5 = 4
_STM32_SERIES_L4 = 1
_STM32_SERIES_U5 = 4
_STM32_SERIES_N6 = 5
_STELLAR_SERIES_E  = 3
_STELLAR_SERIES_PG =  6


def _is_series(fmt, series):
    return (fmt >> 24) == series


def stm32_id_to_str(dev_id):
    """Helper function to return a Human readable device ID description"""  # noqa: DAR101,DAR201,DAR401

    switcher = {  # (see BZ119679)
        0x439: 'STM32F301',
        0x432: 'STM32F37x',
        0x422: 'STM32F30xB/C',
        0x438: 'STM32F30x/F33x',
        0x446: 'STM32F303D/E',

        0x419: 'STM32F4x7',
        0x434: 'STM32F469',
        0x423: 'STM32F401xB/C',
        0x431: 'STM32F411xC/E',
        0x441: 'STM32F412',
        0x421: 'STM32F446',
        0x413: 'STM32F4x',
        0x458: 'STM32F410',
        0x463: 'STM32F413',
        0x433: 'STM32F401xD/E',

        0x435: 'STM32L43xxx',
        0x461: 'STM32L49xxx',
        0x462: 'STM32L45xxx',
        0x464: 'STM32L4x2',
        0x415: 'STM32L4x6xx',
        0x470: 'STM32L4R/S',
        0x471: 'STM32L4Q',

        0x472: "STM32L5[5,6]2xx",

        0x451: "STM32F76x/F77x",
        0x449: 'STM32F746',
        0x452: 'STM32F72x/F73x',

        0x483: 'STM32H7[2,3]x',
        0x450: 'STM32H743/53/50xx and STM32H745/55/47/57xx',
        0x480: 'STM32H7A/7B',
        0x485: 'STM32H7[R,]Sxx',
        0x47B: "STM32H7Pxxx",

        0x484: 'STM32H5x',
        0x474: 'STM32H503',

        0x460: 'STM32G07x/8x',
        0x467: 'STM32G0B1/C1',
        0x466: 'STM32G031/41',
        0x456: 'STM32G051/61',

        0x469: 'STM32G474',
        0x468: 'STM32G454',
        0x479: 'STM32G491',

        0x444: 'STM32F03x',
        0x445: 'STM32F04x',
        0x440: 'STM32F03x/F05x',
        0x448: 'STM32F07x',
        0x442: 'STM32F091',

        0x457: 'STM32L0x1',
        0x425: 'STM32L0x2',
        0x417: 'STM32L0x3',
        0x447: 'STM32L0x5',

        0x482: 'STM32U575/585',

        0x494: 'STM32WB1',
        0x495: 'STM32WBxx',

        0x497: 'STM32WLx',

        0x500: 'STM32MP1',
        0x486: 'STM32N6xx',
        0x499: 'STM32V8xx',
        0x42a: 'STM32U3xx',

        0x155: 'Corstone SSE-300 FVP',

        0x2511: 'SR5E1',
        0x2643: 'SR6P3',
        0x2646: 'SR6P6',
        0x2647: 'SR6P7',
        0x2633: 'SR6G3',
        0x2636: 'SR6G6',
        0x2637: 'SR6G7',
        0x2A47: 'SR6P7G7',
        0x2663: 'SR6P3E',
    }
    desc_ = f'0x{dev_id:X} - '
    desc_ += switcher.get(dev_id, 'UNKNOW')
    return desc_


def stm32_attr_config(cache):
    """Return human desc fpu/cache config  # noqa: DAR101,DAR201,DAR401
        see FW c-file aiTestUtility.c
    """

    def _fpu(cache_):
        if cache_ & (1 << 16):
            return ['fpu']
        return ['no_fpu']

    def _lat(cache_):
        if (cache_ >> 24) > 0 and not _is_series(cache, _STM32_SERIES_L5) and not _is_series(cache, _STM32_SERIES_N6):
            return ['art_lat={}'.format(cache_ & 0xFF)]
        return []

    def _art_f4(cache_):
        attr = []
        if cache_ & 1 << 8:
            attr.append('art_prefetch')
        if cache_ & 1 << 9:
            attr.append('art_icache')
        if cache_ & 1 << 10:
            attr.append('art_dcache')
        return attr

    def _icache_l5(cache_):
        return ['icache'] if cache_ & 1 << 9 else []

    def _core_f7h7(cache_):
        attr = []
        if cache_ & 1 << 10:
            attr.append('core_icache')
        if cache_ & 1 << 11:
            attr.append('core_dcache')
        return attr

    def _art_f7(cache_):
        attr = []
        if cache_ & 1 << 8:
            attr.append('art_prefetch')
        if cache_ & 1 << 9:
            attr.append('art_en')
        return attr

    def _extra_n6(cache_):
        attr = []
        if cache_ & 0x1:
            attr.append('npu_cache')
        return attr

    desc = _fpu(cache)
    desc.extend(_lat(cache))

    if _is_series(cache, _STM32_SERIES_F4) or _is_series(cache, _STM32_SERIES_L4):
        attr = _art_f4(cache)
        desc.extend(attr)

    if _is_series(cache, _STM32_SERIES_F7) or _is_series(cache, _STM32_SERIES_H7)\
            or _is_series(cache, _STM32_SERIES_N6) or _is_series(cache, _STELLAR_SERIES_E)\
            or _is_series(cache, _STELLAR_SERIES_PG):
        attr = _core_f7h7(cache)
        desc.extend(attr)

    if _is_series(cache, _STM32_SERIES_F7):
        attr = _art_f7(cache)
        desc.extend(attr)

    if _is_series(cache, _STM32_SERIES_L5):
        attr = _icache_l5(cache)
        desc.extend(attr)

    if _is_series(cache, _STM32_SERIES_N6):
        attr = _extra_n6(cache)
        if attr:
            desc.extend(attr)

    return desc


def bsdchecksum(data):
    """Computing BSD 16b checksum"""  # noqa: DAR101,DAR201,DAR401
    # see https://en.wikipedia.org/wiki/BSD_checksum
    if not isinstance(data, (bytes, bytearray)):
        msg = 'bsdchecksum() - Invalid data type: {} instead \'bytes,bytearray\''.format(type(data))
        raise TypeError(msg)
    checksum = 0
    for char in data:
        checksum = (checksum >> 1) + ((checksum & 1) << 15)
        checksum += char
        checksum &= 0xffff
    return checksum


def _decode_ihex_record(line, count):
    """Decode Intel HEX record format"""  # noqa: DAR101,DAR201,DAR401
    dec = {}
    line = line.rstrip('\r\n')
    if line[0] == ':':
        # Record format - Intel Hex format: ":llaaaatt[dd...]cc"
        #
        #   ll    number of data (dd)
        #   aaaa  offset
        #   tt    type
        #       00 - data record
        #       01 - end-of-file record
        #       02 - extended segment address record
        #       04 - extended linear address record     @ = dd << 16 | aa
        #       05 - start linear address record
        #   dd    data
        #   cc    checksum
        #
        bin_ = bytearray.fromhex(line[1:])
        ll_, aaaa_, tt_ = bin_[0], bin_[1:3], bin_[3:4]
        dd_ = bin_[4:4 + ll_]
        # cc = bin[-1]
        if tt_ == b'\x05':  # Start linear address
            dec['start_addr'] = int(hexlify(dd_), 16) << 16 + int(hexlify(aaaa_), 16)
        elif tt_ == b'\x04':  # Extended Linear Address Records (HEX386)
            dec['addr'] = int(hexlify(dd_), 16) << 16 + int(hexlify(aaaa_), 16)
        elif tt_ == b'\x02':  # Extended Segment Address Records (HEX86)
            dec['addr'] = int(hexlify(dd_), 16) << 4 + int(hexlify(aaaa_), 16)
        elif tt_ == b'\x00':  # data record
            # dec['data'] = dd_[::-1]
            dec['data'] = dd_
            dec['offset'] = int(hexlify(aaaa_), 16)
        elif tt_ == b'\x01':
            dec['eof'] = True
        else:
            msg_ = 'Invalid Intel HEX record type - line={}'.format(count)
            raise ValueError(msg_)
    return dec


def dump_ihex_file(filepath, fill_with_zeros=True):
    """Decode Intel HEX file"""  # noqa: DAR101,DAR201,DAR401
    segments = []
    count = 0
    # fill_with_zeros = True
    with open(filepath) as file_:
        for line in file_:
            count += 1
            line = line.strip()
            if line[0] != ':':
                msg_ = 'Invalid Intel HEX file - {}:{}'.format(count, filepath)
                raise ValueError(msg_)
            dec = _decode_ihex_record(line, count)
            if 'addr' in dec:
                segment = {
                    'addr': dec['addr'],
                    'data': bytearray()
                }
                lba = segment['addr']  # LBA
                next_off = 0
                segments.append(segment)
            elif 'data' in dec:
                if next_off != dec['offset']:
                    if fill_with_zeros:
                        segments[-1]['data'] += bytearray(dec['offset'] - len(segments[-1]['data']))
                    else:
                        segment = {
                            'addr': lba + dec['offset'],
                            'data': bytearray()
                        }
                        segments.append(segment)
                segments[-1]['data'] += dec['data']
                next_off = dec['offset'] + len(dec['data'])
        file_.close()
    return segments
