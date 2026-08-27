# Xiaomi Watch S1 Active Modding

An open research and modification project maintained by [Just-Nova23](https://github.com/Just-Nova23) for the Xiaomi Watch S1 Active (`M2116W1`). Its goal is to document the platform, study native behavior, and make careful, reproducible experimentation possible.

The project currently covers:

- Xiaomi `full` and `diff` OTA container inspection;
- component extraction, CRC validation, and conservative rebuilding;
- the native TouchGFX bitmap database and GUI asset archive;
- the partially understood `TSCFrameImage` animation format;
- native assistant message handling and its verified text-buffer limit;
- third-party RPK application structure and development notes;
- a safety-first workflow that never requires committing vendor firmware.

## Current verified result

On firmware derived from Xiaomi `1.4.174` with the compatible m0tral bootloader patch, the native assistant caption handler was traced to a fixed 800-byte UTF-16 buffer. The stock conversion capacity is 300 code units, producing at most 299 visible characters. A one-byte instruction patch can raise the capacity to 400, producing at most 399 visible characters without crossing the existing buffer boundary.

This repository does **not** distribute Xiaomi firmware, m0tral packages, modified Mi Fitness APKs, signing material, API keys, or ready-to-flash OTA packages. Bring firmware obtained legally from your own device or an official source.

## Start here

- [Complete documentation website](https://just-nova23.github.io/Xiaomi-Watch-S1-Active-Modding/)
- [Safe research setup](docs/getting-started.md)
- [Current research status](docs/status.md)
- [Architecture overview](docs/architecture.md)
- [Tool reference](docs/tools-reference.md)
- [Native apps](docs/native-apps.md) and [RPK apps](docs/rpk-apps.md)
- [Graphics and TSCFrameImage](docs/graphics-tscframeimage.md)
- [OTA safety](docs/ota-safety.md) and [recovery](docs/recovery.md)
- [How to contribute](CONTRIBUTING.md)

## Repository layout

```text
docs/       Guides, specifications, research results, and safety notes
tools/      Small inspection and reconstruction tools
tests/      Tests built exclusively from synthetic data
```

## Important warning

Firmware modification can permanently disable a watch. A successful package build or Bluetooth transfer does not prove that the installed image is valid. Read [OTA safety](docs/ota-safety.md) before changing anything.

## Legal and project boundaries

This is an independent interoperability and research project. Xiaomi, Alexa, Amazon, TouchGFX, Ambiq, Nema, PixPresso, and m0tral are names or technologies belonging to their respective owners. See [DISCLAIMER.md](DISCLAIMER.md).
