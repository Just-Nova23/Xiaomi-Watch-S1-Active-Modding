# Native graphics and TSCFrameImage

`TSCFrameImage` is now understood well enough to build, validate, extract, and
round-trip its files. It is important not to confuse this native widget format
with the separate variable-length packet codec used by assets such as
`guiimage_anim_logo.bin` and the assistant animations.

## Verified file format

A `TSCFrameImage` NAND file is:

```text
offset  size  encoding  meaning
0x00    2     u16 LE    width in pixels
0x02    2     u16 LE    height in pixels
0x04    4     u32 LE    frame count
0x08    ...   bytes     consecutive headerless NEMA TSC6A frames
```

Each frame has exactly:

```text
width * height * 6 / 8 bytes
```

Width and height must be multiples of four because NEMA TSC6A operates on 4×4
blocks. Raw TSC6A has no magic, dimensions, frame count, or timing metadata.

| Dimensions | One frame |
| ---: | ---: |
| 4×4 | 12 bytes |
| 60×60 | 2,700 bytes |
| 352×352 | 92,928 bytes |

## Firmware evidence

The result comes from executable behavior, not only from matching file sizes.
In Xiaomi `1.4.174`:

1. the string `/nand/asset/%s` is referenced by the function at file offset
   `0x1a5730`;
2. that function opens names such as `guiimage_en_p1.bin`, reads eight bytes,
   and passes the two halfwords and one word to the image widget;
3. the widget setup routine is at file offset `0x1f2a9e` in this load region;
4. its frame-offset routine multiplies width and height, then computes
   `(width * height * 3) >> 2`, exactly six bits per pixel;
5. its draw path passes `0x17` to the Nema GPU API; ST's public Nema headers
   define `0x17` as `NEMA_TSC6A`;
6. frame `n` is read at `8 + n * frame_size`.

The code and related string/data region use the verified local relation
`runtime = file_offset + 0x08060000`. This does **not** establish one universal
base for every region in the SFU image. Derive mappings from pointers or load
metadata in the exact region being studied.

## Encode PNG frames

The repository implements Xiaomi's complete framing and uses Nema PixPresso for
the patented TSC6A texture layer:

```bash
python tools/tsc_frame_image.py encode \
  generated/example.tscframe \
  artwork/frame-000.png artwork/frame-001.png \
  --pixpresso /path/to/nema_pixpresso \
  --quality hq
```

The encoder rejects mixed dimensions, non-4×4-aligned dimensions, empty frame
sets, and any PixPresso result whose byte count is not exact.

If frames are already encoded as raw `.tsc6a`:

```bash
python tools/tsc_frame_image.py pack \
  60 60 generated/example.tscframe \
  generated/frame-0000.tsc6a generated/frame-0001.tsc6a
```

## Inspect and extract

```bash
python tools/tsc_frame_image.py inspect generated/example.tscframe
python tools/tsc_frame_image.py extract \
  generated/example.tscframe generated/raw-frames
```

To render an extracted frame with PixPresso, provide its external dimensions:

```bash
nema_pixpresso \
  -s generated/raw-frames/frame-0000.tsc6a \
  -sw 60 -sh 60 -f PNG \
  -o generated/frame-0000.png
```

## Put the file in the GUI archive

The file stored on NAND is wrapped by a generic component-6 record. These are
separate layers:

```text
component 6
└── generic nand/asset record
    ├── record/path metadata
    ├── body length and CRC
    └── TSCFrameImage NAND file
        ├── width, height, frame count
        └── raw TSC6A frames
```

Build a record without copying proprietary input bytes:

```bash
python tools/gui_asset_record.py build \
  nand/asset/guiimage_en_p1.bin \
  generated/example.tscframe \
  generated/guiimage_en_p1.record
```

Append only to a private, extracted component:

```bash
python tools/gui_asset_record.py append \
  private/component-06.bin \
  generated/guiimage_en_p1.record \
  generated/component-06-with-example.bin
```

The command refuses duplicate NAND paths. Package rebuilding and device testing
remain separate operations with the gates in [OTA safety](ota-safety.md).

## What remains unknown

This result does not decode every native image asset. The 40 stock component-6
records include another family whose bodies are variable-length packets ending
in `11 00 00`. Examples include the boot logo, Alexa/Luna listen and think
animations, loading animations, and an A8 left arrow. Their inner full-frame,
delta, timing, and reuse opcodes are still under investigation.

| Asset | Record size | Packets | Unique packets |
| --- | ---: | ---: | ---: |
| `guiimage_anim_logo.bin` | 173,471 bytes | 379 | 208 |
| `guiimage_anim_alexa_listen.bin` | 31,473 bytes | 18 | 18 |
| `guiimage_anim_alexa_think.bin` | 107,032 bytes | 57 | 57 |

Do not feed those packets to `tsc_frame_image.py`, and do not place a raw
PixPresso stream where that variable-length codec is expected.

## Reproducibility standard

A `TSCFrameImage` result is considered verified when all of these succeed:

1. PNG → PixPresso TSC6A;
2. exact frame-size validation;
3. Xiaomi header build;
4. parser round trip;
5. raw frame extraction;
6. PixPresso TSC6A → PNG with the original dimensions;
7. generic asset-record CRC validation;
8. package/component CRC validation;
9. non-critical on-device test with a compatible recovery path.
