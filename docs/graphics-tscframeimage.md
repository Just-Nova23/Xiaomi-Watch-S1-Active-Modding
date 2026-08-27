# Native graphics and TSCFrameImage

The [native GUI record chart](research-data.md#selected-native-gui-records) compares exact sizes and packet counts for three verified assistant assets.

## What is known

Component 6 is a concatenation of native GUI asset records. Each observed record
contains:

```text
record version (4 bytes)
path length (1 byte)
path CRC (4 bytes)
ASCII path such as nand/asset/guiimage_anim_logo.bin
payload version (1 byte)
payload body length (4 bytes)
payload body CRC (4 bytes)
repeated: packet length (2 bytes) + packet data
```

The outer record parser and builder are implemented in `tools/gui_animation.py`.
Unmodified packets rebuild byte-for-byte.

Examples from stock `1.4.174`:

| Asset | Record size | Packets |
| --- | ---: | ---: |
| `guiimage_anim_logo.bin` | 26,739 bytes | 20 |
| `guiimage_anim_alexa_listen.bin` | 31,473 bytes | 18 |
| `guiimage_anim_alexa_think.bin` | 107,032 bytes | 57 |
| `guiimage_anim_xiaoai_transition.bin` | 682,484 bytes | 167 |

The main image contains the class/name string `TSCFrameImage`. Packet boundaries
are proven; their exact relationship to frames is not yet proven.

## Compression layers

Ambiq Nema PixPresso can convert PNG artwork to GPU texture formats such as TSC4,
TSC6, and TSC6A. TSC6A retains alpha and produced a correct standalone texture in
offline tests. Xiaomi's native asset, however, adds its own `TSCFrameImage`
framing or delta layer. Raw PixPresso output is not a drop-in replacement.

RPK applications are different: their source packages use ordinary PNG/JPG
assets and do not require contributors to author `TSCFrameImage` data.

## Encoder completion plan

1. Locate every code reference to `TSCFrameImage` in the main image.
2. Translate the packet reader into a small host-side decoder.
3. Export known native assets to individual TSC textures and then PNG files.
4. Identify full-frame, repeated-frame, and delta-frame packet types.
5. Test whether the loader accepts independent full TSC6A frames; this may avoid
   implementing delta compression initially.
6. Implement the inverse packet builder.
7. Prove an original asset can be decoded and rebuilt with identical rendering.
8. Replace a non-critical asset before any boot or assistant artwork.

## Contribution target

A useful graphics contribution includes packet hex limited to the relevant
header, inferred field names, comparison against at least two different assets,
and a script/test using synthetic data. Do not upload extracted asset payloads.
