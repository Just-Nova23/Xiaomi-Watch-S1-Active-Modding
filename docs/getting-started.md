# Safe research setup

This guide prepares an offline workspace. It does not flash a watch.

## Requirements

- Python 3.11 or newer;
- Git;
- optional: Capstone for `thumb_xrefs.py`;
- optional: Ghidra, Rizin, or another ARM Thumb disassembler;
- firmware obtained legally by the researcher.

Keep firmware outside the repository:

```text
watch-research/
├── project/          cloned Git repository
└── private-firmware/ files that must never be committed
```

## Clone and test

```bash
git clone https://github.com/Just-Nova23/Xiaomi-Watch-S1-Active-Modding.git
cd Xiaomi-Watch-S1-Active-Modding
python -m unittest discover -s tests -v
python -m compileall -q tools tests
```

## Inspect a full package

```bash
python tools/firmware_pkg.py \
  ../private-firmware/stock.pkg \
  --extract-dir ../private-firmware/components \
  --json-out ../private-firmware/package-report.json
```

Review these fields before trusting the result:

- package model and version;
- declared body size and calculated file size;
- component sizes and offsets;
- header and component CRC matches;
- SFU1 payload length and digest state.

## Catalog GUI assets

```bash
python tools/asset_catalog.py \
  ../private-firmware/stock.pkg \
  --extract-dir ../private-firmware/gui-records \
  --json-out ../private-firmware/gui-assets.json
```

## Rules for reproducible notes

Record hashes rather than uploading firmware:

```bash
sha256sum ../private-firmware/stock.pkg
```

For every patch, record the component index, exact file offset, original bytes,
replacement bytes, reason, expected behavior, and validation state.
