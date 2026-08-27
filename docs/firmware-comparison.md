# Firmware comparison workflow

A useful comparison answers **what changed, where, and under which base assumptions**. A global “files differ” result is not enough, while blindly listing millions of changed offsets is usually noise.

## Define the comparison

Before running a tool, write one sentence:

> Compare stock M2116W1 version A with candidate version B to identify changed components and isolate the smallest code or resource regions.

Do not compare files from different models or unknown provenance and then attribute every difference to one feature.

## Step 1: identify both packages independently

```bash
python tools/firmware_pkg.py ../private-inputs/a.pkg \
  --extract-dir ../generated/a-components \
  --json-out ../generated/a-report.json

python tools/firmware_pkg.py ../private-inputs/b.pkg \
  --extract-dir ../generated/b-components \
  --json-out ../generated/b-report.json
```

Confirm separately:

- SHA-256 and file size;
- model identifier;
- declared version;
- component count and sizes;
- CRC and inner digest state.

If package B is a compact `diff`, inspect it with `diff_pkg.py` instead of forcing the full-package parser.

## Step 2: compare metadata first

Use a structured JSON diff tool or a short local script. Focus on:

| Field | Why it matters |
|---|---|
| format magic | determines the parser and version semantics |
| base version | required for differential-package acceptance |
| target version | identifies the intended result, not necessarily content identity |
| model | prevents cross-model conclusions |
| descriptor index/type/flag | defines component interpretation and wrapper handling |
| size | detects insertion, deletion, or replacement |
| SHA-256 | detects any byte difference |
| CRC status | distinguishes consistent packaging from damaged/rebuilt data |

Metadata differences can explain an OTA rejection before executable code is even read.

## Step 3: produce a component matrix

```markdown
| Index | A size/hash | B size/hash | State |
|---:|---|---|---|
| 0 | … | … | changed |
| 1 | … | … | identical |
```

Classify each component as:

- identical size and hash;
- same size, changed content;
- changed size;
- missing or newly introduced;
- not comparable because package structure differs.

## Step 4: calculate changed ranges

For equal-sized components, group adjacent changed bytes into ranges. The following read-only example prints range starts and lengths without writing either input:

```python
from pathlib import Path

a = Path("../generated/a-components/component-00-type-00.bin").read_bytes()
b = Path("../generated/b-components/component-00-type-00.bin").read_bytes()

if len(a) != len(b):
    raise SystemExit("sizes differ; normalize the comparison first")

start = None
for offset, (left, right) in enumerate(zip(a, b)):
    changed = left != right
    if changed and start is None:
        start = offset
    if not changed and start is not None:
        print(f"0x{start:08x} length={offset-start}")
        start = None
if start is not None:
    print(f"0x{start:08x} length={len(a)-start}")
```

Keep this as an analysis snippet; do not commit the input or generated binary output.

## Step 5: interpret by layer

For component 0, separate at least:

```text
0x00000000 .. 0x00001fff  SFU1 header
0x00002000 .. end         payload in the documented build
```

A digest or signature-field difference is not automatically an application-code change. Conversely, one changed instruction inside the payload may alter behavior even when component size stays constant.

For component 6, compare record catalogs by path, size, packet count, and hash. Do not compare only global offsets: changing one record size shifts every later record.

## Step 6: map code offsets to runtime addresses

For the documented main image:

```text
runtime = 0x08000000 + file offset
```

Use:

```bash
python tools/thumb_xrefs.py main-b.bin \
  --disasm-offset 0x130340 \
  --bytes 0x60
```

Inspect the same window in both files. Record instruction boundaries, not merely hexadecimal differences.

## Step 7: avoid causal overclaiming

Suppose a mod changes 200 ranges and enables tap-to-wake. The comparison proves those ranges differ; it does not prove which range implements tap-to-wake. Stronger evidence requires one or more of:

- a unique string or configuration reference;
- code reaching the relevant input/power handler;
- a minimal isolated patch;
- controlled A/B device behavior;
- independent reproduction on another build.

## Comparison report template

```markdown
# Comparison: A → B

## Identity
| | A | B |
|---|---|---|
| model | | |
| version | | |
| SHA-256 | | |
| package format | | |

## Component summary

## Changed ranges

## Interpreted changes
- Observed:
- Inferred:
- Unknown:

## Commands

## Device evidence

## Alternative explanations
```

## Stop conditions

Stop and re-identify inputs when a model differs, a parser reports failed CRCs, a package was already modified by an unknown tool, component sizes cannot be aligned, or a report cannot be traced to its exact input hash.
