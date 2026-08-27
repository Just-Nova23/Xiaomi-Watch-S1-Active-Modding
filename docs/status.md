# Project status

Last reviewed: 27 August 2026.

## Compatibility baseline

| Item | Value | Confidence |
| --- | --- | --- |
| Device | Xiaomi Watch S1 Active | Verified on device |
| Model | `M2116W1` | Verified on device |
| Stock firmware | `1.4.174` | Verified on device |
| Stock OTA identifier | `midr.watch.k63a` | Verified offline |
| Compatible modified OTA identifier | `midr.mwtch.k63a` | Verified on device |
| Main component size | 3,600,374 bytes | Verified offline |
| Main runtime mapping | `0x08000000 + file_offset` | Verified from embedded pointers |
| Native bitmap records | 4,398 | Verified offline |

Identifiers must not be treated as interchangeable. Xiaomi's OTA path validates
the identifier and version bytes before component transfer.

## Capability matrix

| Capability | Status | Notes |
| --- | --- | --- |
| Parse stock `full` OTA | Working | Nine component descriptors recognized |
| Parse compact `diff` OTA | Working | Bootloader and main-image variant tested |
| Validate outer CRCs | Working | Xiaomi CRC variant implemented |
| Extract all full-package components | Working | No mutation required |
| Catalog component 6 GUI records | Working | Records cover the component exactly |
| Rebuild GUI outer record | Working | Byte-perfect with unchanged packets |
| Decode TSC6/TSC6A | Working with Ambiq PixPresso | Third-party SDK is not redistributed |
| Decode Xiaomi `TSCFrameImage` | In progress | Packet envelope known; frame payload unknown |
| Create arbitrary native artwork | Blocked | Requires `TSCFrameImage` encoder or loader bypass |
| Catalog TouchGFX bitmap metadata | Working | 4,398 entries at the known table |
| Native answer limit 299 → 399 | Verified on device | Uses existing 800-byte UTF-16 buffer |
| Native answer beyond 399 | Research required | Requires memory-layout changes |
| Ready-to-flash public firmware | Not provided | Vendor-derived binaries stay outside GitHub |

## Terminology

- **Verified on device**: observed on a real S1 Active after installation.
- **Verified offline**: reproduced from local binary analysis or generated data.
- **Inferred**: evidence exists, but a full round-trip or device test is missing.
- **Unknown**: the project intentionally does not guess.
