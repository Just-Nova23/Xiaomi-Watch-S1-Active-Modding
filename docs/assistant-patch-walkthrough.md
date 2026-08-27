# Native assistant capacity patch walkthrough

This page explains the verified text-capacity patch from observation to offline output. It is specific to the documented main component and is not a universal firmware patch.

## Problem statement

The native assistant display truncates long responses. Static analysis found an inline UTF-16 buffer of 800 bytes and a conversion call receiving capacity 300. Because the converter reserves one UTF-16 code unit for the NUL terminator, stock displays at most 299 code units in one response.

## Evidence chain

```mermaid
flowchart LR
  UI[Observed truncated text] --> STR[Locate assistant strings]
  STR --> XREF[Trace Thumb cross-references]
  XREF --> HANDLER[Handler region 0x0813024c]
  HANDLER --> CLEAR[800-byte buffer clear]
  CLEAR --> CALL[UTF-8 to UTF-16 conversion]
  CALL --> IMM[mov.w r2,#300 at file 0x130350]
  IMM --> BOUND[Existing buffer allows capacity 400]
  BOUND --> PATCH[Guarded one-byte difference]
  PATCH --> TEST[399 visible characters observed]
```

The final device result supports the chain, but the offline checks are what make the change reviewable.

## Object layout reconstructed from use

| Relative offset | Observed use |
|---:|---|
| `+0x2b80` | state/validity flag |
| `+0x2b82` | text length field |
| `+0x2b84` | second state flag |
| `+0x2b86` | start of inline UTF-16 buffer |
| `+0x2ea8` | observed object extent |

The buffer region from `0x2b86` spans 800 bytes in the analyzed code path. This yields 400 two-byte UTF-16 code units.

## Instruction change

```text
file offset:     0x00130350
runtime address: 0x08130350
before:          4f f4 96 72  → mov.w r2, #300
after:           4f f4 c8 72  → mov.w r2, #400
changed byte:    file offset 0x00130352, 0x96 → 0xc8
```

The instruction is four bytes wide, but Thumb immediate encoding means this value change alters one stored byte.

## Step 1: verify the source identity

Use the report produced during package extraction. Confirm model, base version, component size, and complete SHA-256. Do not use a file renamed from an unknown mod.

## Step 2: inspect the region

```bash
python tools/thumb_xrefs.py ../generated/main-original.bin \
  --disasm-offset 0x130340 \
  --bytes 0x40
```

Confirm the expected conversion setup and instruction boundary. If Capstone output differs, stop.

## Step 3: run the guarded patch

```bash
python tools/patch_native_assistant_text_capacity.py \
  ../generated/main-original.bin \
  ../generated/main-capacity-400.bin \
  --report ../generated/assistant-capacity-report.json
```

The script checks the complete expected context beginning at file offset `0x130344`. A mismatch raises an error before it writes a valid patched output.

## Step 4: review the report

Confirm:

- input and output SHA-256 differ;
- instruction offset is `0x130350`;
- old/new instruction bytes match the documented values;
- changed offsets contains only `0x130352`;
- old/new capacities are 300 and 400;
- buffer size remains 800 bytes.

## Step 5: independently compare bytes

```python
from pathlib import Path

a = Path("../generated/main-original.bin").read_bytes()
b = Path("../generated/main-capacity-400.bin").read_bytes()
changes = [i for i, pair in enumerate(zip(a, b)) if pair[0] != pair[1]]
print(changes)
```

Expected output:

```text
[1246034]
```

`1246034` decimal is `0x130352`.

Also verify equal lengths:

```python
print(len(a), len(b), len(a) == len(b))
```

## Step 6: understand what is not changed

The patch does not:

- allocate a new buffer;
- paginate a response;
- remove protocol-side limits;
- change the phone-side model response;
- guarantee that every Unicode sequence occupies one visible glyph;
- support other firmware versions automatically;
- build or flash an OTA.

UTF-16 code units and user-perceived characters are not always one-to-one. Emoji and some characters may consume surrogate pairs, so 399 code units can represent fewer than 399 visible glyphs.

## Why not exceed 400

Passing 401 would allow the converter to write beyond the observed 800-byte region if it interprets capacity in UTF-16 code units. Without redesigning the object, allocation, and all consumers, that risks corrupting adjacent memory.

## Toward a dynamic solution

A larger or unlimited response requires more than changing an immediate:

1. identify allocation and object lifetime;
2. find every reader of buffer, length, and flags;
3. determine UI text widget limits and scrolling behavior;
4. replace inline storage with a bounded external allocation or paging model;
5. update destructor/reset paths;
6. test out-of-memory and malformed UTF-8 cases;
7. preserve protocol and UI timing.

Until those dependencies are mapped, 400 is the maximum justified by the existing buffer evidence.
