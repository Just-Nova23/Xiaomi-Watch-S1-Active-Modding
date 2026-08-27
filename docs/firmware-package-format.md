# Firmware package formats

Two outer formats are currently recognized: `full` and `diff`. Both store
multi-byte lengths and CRCs in big-endian form unless noted otherwise.

## Xiaomi CRC

Package CRC fields observed in this device use CRC-32/ISO-HDLC with an initial
value of `0xffffffff` and a final XOR of `0xffffffff`:

```python
(zlib.crc32(data, 0xFFFFFFFF) ^ 0xFFFFFFFF) & 0xFFFFFFFF
```

## `full` package

Important prefix fields:

| Offset | Size | Meaning |
| ---: | ---: | --- |
| `0x00` | 4 | ASCII `full` |
| `0x08` | 4 | Total component body size |
| `0x0c` | 4 | Target version bytes |
| `0x10` | 16 | NUL-padded model identifier |

The analyzed stock package contains nine components. Descriptor fields include
type, flag, reserved bytes, component size, and a 256-byte unknown/reserved
area. The CRC following one component is stored adjacent to the next descriptor;
the final component CRC and header CRC terminate the header.

Do not write a base version into offsets `0x04..0x07` of a stock `full` package.
Those bytes are not the same field used by `diff`. Doing so caused the watch to
reject an OTA with `OTA DIFF PTK OLD VERSION ERROR` before transfer.

## `diff` package

Important prefix fields:

| Offset | Size | Meaning |
| ---: | ---: | --- |
| `0x00` | 4 | ASCII `diff` |
| `0x04` | 4 | Required installed/base version |
| `0x08` | 4 | Component body size |
| `0x0c` | 4 | Target version |
| `0x10` | 16 | NUL-padded model identifier |

A known compact mod package uses a 597-byte header followed by bootloader and
main images. A generalized partial container uses a 53-byte prefix, one
270-byte descriptor per included component, a four-byte header CRC, then the
component bodies.

## SFU1 inner image

Component 0 begins with an `SFU1` header of `0x2000` bytes. Observed fields
include payload length, partial-firmware fields, repeated SHA-256 values, and a
64-byte signature candidate. Modified images can deliberately have a payload
digest that no longer matches the stock signed header; whether they boot depends
on the installed boot chain. Outer CRC validity alone does not establish that an
SFU1 image will run.
