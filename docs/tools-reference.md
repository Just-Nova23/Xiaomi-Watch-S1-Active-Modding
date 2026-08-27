# Tool reference

The scripts are intentionally small and inspectable. None communicates with the watch or starts a flash operation: they only read or transform local files.

## Common setup

Run commands from the repository root. Keep inputs outside the repository and save outputs under `generated/`, which Git ignores.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
mkdir -p generated
```

## `firmware_pkg.py`

Inspects a complete OTA package, validates lengths and CRCs, calculates SHA-256 hashes, and can extract components.

```bash
python tools/firmware_pkg.py /path/to/update.pkg
python tools/firmware_pkg.py /path/to/update.pkg \
  --extract-dir generated/components \
  --json-out generated/package-report.json
```

Extraction is not decryption and does not prove that a component is executable. Keep the JSON report with the input hash.

## `diff_pkg.py`

Inspects a differential package and reports the metadata required to associate it precisely with an earlier version.

```bash
python tools/diff_pkg.py /path/to/update-diff.pkg
```

## `build_partial_diff.py`

Rebuilds a research package while changing only selected components. This is an advanced tool: it does not bypass signatures and does not guarantee that a bootloader will accept its output.

```bash
python tools/build_partial_diff.py --help
```

## `asset_catalog.py`

Indexes records from the GUI component and produces a catalog containing paths, sizes, CRCs, and offsets.

```bash
python tools/asset_catalog.py /path/to/update.pkg \
  --extract-dir generated/gui-records \
  --json-out generated/assets.json
```

## `gui_animation.py`

Splits and losslessly rebuilds the packets of one GUI record. The inner packets remain opaque: the project does not call them “frames” until evidence supports that name.

```bash
python tools/gui_animation.py extract record.bin generated/record
python tools/gui_animation.py rebuild generated/record generated/rebuilt.bin
cmp record.bin generated/rebuilt.bin
```

A byte-identical comparison proves only that the outer container was preserved.

## `bitmap_catalog.py`

Searches for known bitmap signatures and structures, then prepares an inventory for comparative analysis.

```bash
python tools/bitmap_catalog.py component.bin --json-out generated/bitmaps.json
```

## `thumb_xrefs.py`

Uses Capstone to find strings, literal pointers, `MOVW/MOVT` pairs, and immediate values in ARM Thumb code.

```bash
python tools/thumb_xrefs.py main.bin --text "listening"
python tools/thumb_xrefs.py main.bin --offset 0x13024c
python tools/thumb_xrefs.py main.bin --disasm-offset 0x130240 --bytes 0x80
```

For the documented build, the defaults are `--image-offset 0` and `--base 0x08000000`. Do not reuse them on another build without verification.

## `patch_native_assistant_text_capacity.py`

Applies a version-specific patch protected by a context check. If the surrounding bytes do not match exactly, it exits rather than producing an apparently valid output.

```bash
python tools/patch_native_assistant_text_capacity.py \
  main-original.bin generated/main-patched.bin \
  --report generated/assistant-capacity.json
```

It is compatible only with the documented build. Read [Native assistant](native-assistant.md) before using it.

## Exit errors and diagnosis

- `ValueError`: the format, size, CRC, or expected context does not match;
- `FileNotFoundError`: the path is wrong or the component has not been extracted;
- no useful output: check `--help` and argument order;
- different output after a round trip: stop and preserve both hashes for investigation.
