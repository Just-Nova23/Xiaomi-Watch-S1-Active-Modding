# Architecture overview

The S1 Active is not an Android or Wear OS watch. The analyzed firmware combines
an STM32-side main system and a BES-side Bluetooth/audio system, with resources
stored in separate OTA components.

```text
Phone / Mi Fitness
        │ Bluetooth OTA and assistant protocol
        ▼
BES image ─────────────── audio and transport
        │
        ▼
Main STM32 image ─────── native UI, application state, TouchGFX
        │
        ├── language resources
        ├── audio resources
        └── component 6 GUI asset archive
```

## Full-package component map

The current role names are descriptive, not vendor-provided symbols.

| Index | Current interpretation |
| ---: | --- |
| 0 | Main watch image with an `SFU1` header |
| 1 | Wrapped resource image; exact role unknown |
| 2 | Wrapped language/resource image |
| 3 | Audio resource container |
| 4 | STM32 bootloader or secondary image |
| 5 | Wrapped `BREAM PATCH` component |
| 6 | Native GUI asset archive |
| 7 | Calibration/configuration image |
| 8 | BES best1501 FreeRTOS image |

## Main-image mapping

For the analyzed `M2116W1` main component, embedded pointers consistently use:

```text
runtime_address = 0x08000000 + file_offset
```

Examples:

- file `0x130358` maps to runtime `0x08130358`;
- file `0x2eda06` maps to runtime `0x082eda06`.

Earlier experiments that treated the SFU1 header as unmapped produced incorrect
cross-references. Tools in this repository use the corrected mapping.

## Application types

Native system applications are compiled into the main image and use shared
firmware resources. Third-party RPK applications use Xiaomi's JavaScript quick
application framework and are installed separately. An RPK cannot automatically
access the privileges or internal C++ objects of a native system application.
