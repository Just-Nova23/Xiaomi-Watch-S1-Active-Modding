# Native assistant research

The [text-capacity chart](research-data.md#native-assistant-text-capacity) shows the measured stock and patched limits against the existing buffer.

The stock assistant path transports phone-produced instructions to a native
watch UI. The phone-side serializer, BES-side decoder, and Bluetooth framing all
preserve strings longer than 300 characters. The observed truncation occurs in
the main firmware's UTF-8 to UTF-16 conversion.

## Verified handler

The relevant handler starts near runtime `0x0813024c`. For instruction/message
type `8`, it clears an 800-byte inline buffer and then passes capacity `300` to
the converter at runtime `0x081f88c8`:

```text
08130344  mov.w r2, #800      ; memset size in bytes
08130348  mov   r0, r7
0813034a  bl    memset
0813034e  movs  r3, #42       ; replacement character '*'
08130350  mov.w r2, #300      ; UTF-16 capacity
08130354  mov   r1, r7
08130356  ldr   r0, [r6, #4]  ; UTF-8 source
08130358  bl    0x081f88c8    ; UTF-8 -> UTF-16
```

The converter reserves one code unit for a NUL terminator. Capacity 300 therefore
produces at most 299 visible UTF-16 code units.

## Object layout

Observed fields relative to the containing object:

| Offset | Meaning |
| ---: | --- |
| `+0x2b80` | State flag |
| `+0x2b82` | Converted/displayed length |
| `+0x2b84` | Additional flag |
| `+0x2b86` | Start of 800-byte inline text buffer |

The object size is `0x2ea8` bytes. The text buffer ends immediately before the
object boundary; it cannot safely hold more than 400 UTF-16 code units.

## Conservative capacity patch

At component file offset `0x130350`:

```text
old instruction bytes: 4f f4 96 72   ; mov.w r2, #300
new instruction bytes: 4f f4 c8 72   ; mov.w r2, #400
```

Only byte `0x130352` changes. The safe maximum becomes 399 visible code units.
Setting a larger immediate would write beyond the object and is not a valid way
to remove the limit.

Going beyond 399 in one response requires either enlarging every dependent object
layout or allocating a separate dynamic buffer and redirecting all producers and
consumers. That work is not complete.
