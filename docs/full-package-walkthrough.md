# Full-package walkthrough

This tutorial inspects one legally obtained `full` package without changing it. It explains every command, expected output, and stop condition.

## Before you begin

You need:

- a package you are legally allowed to inspect;
- its original filename or download context;
- the watch model and installed/target version if known;
- the repository environment from [Windows and Linux setup](windows-setup.md).

Do not assume a file is a full package because its extension is `.pkg`. The first four bytes must identify the format.

## Step 1: preserve identity

Calculate a SHA-256 hash before extraction.

PowerShell:

```powershell
Get-FileHash "..\private-inputs\stock.pkg" -Algorithm SHA256
```

Linux/WSL:

```bash
sha256sum ../private-inputs/stock.pkg
```

Record the complete 64-character hash, byte size, acquisition date, model, and reported version. SHA-256 identifies the bytes; it does not establish legality, authenticity, or compatibility.

## Step 2: inspect without extraction

```bash
python tools/firmware_pkg.py \
  ../private-inputs/stock.pkg \
  --json-out ../generated/stock-package-report.json
```

The tool:

1. reads the file size;
2. checks the `full` magic;
3. derives header size from declared body length;
4. parses nine descriptors;
5. confirms that component lengths equal the body length;
6. hashes every component and validates stored CRCs;
7. inspects known inner wrappers;
8. emits a JSON report.

It does not modify the package.

## Step 3: check the report identity

Open `stock-package-report.json` in a text editor. Start at the top:

```json
{
  "format": "Xiaomi full package (reverse-engineered subset)",
  "file_size": 185221135,
  "header_size": 2487,
  "body_size": 185218648,
  "model": "M2116W1"
}
```

The snippet shows the important shape of the documented stock report; additional keys are omitted here. Your file should be treated as a different build if any identity field differs.

Check the invariant:

```text
header_size + body_size = file_size
2,487 + 185,218,648 = 185,221,135
```

If it fails, stop. Do not repair lengths by hand before understanding the discrepancy.

## Step 4: inspect component descriptors

Each report entry contains:

- component index and observed type;
- inferred role hint;
- file offset and size in decimal and hexadecimal;
- SHA-256;
- stored and calculated CRC state;
- first and last bytes;
- any recognized inner format.

For stock `1.4.174`, exact component sizes are listed under [Research data and charts](research-data.md#full-package-component-sizes). Compare all nine, not only component 0.

Stop if:

- the component count is not nine;
- sizes do not add up;
- any CRC fails;
- model is not the expected `M2116W1`;
- an expected wrapper is absent;
- the report comes from a different hash than the file you intend to study.

## Step 5: inspect the SFU1 layer

Component 0 begins with a `0x2000`-byte `SFU1` header in the documented package. The parser checks:

- magic;
- header size assumption;
- declared payload size;
- component size relationship;
- stored and repeated SHA-256 fields;
- calculated payload SHA-256;
- a 64-byte signature candidate.

Three different statements must remain separate:

1. **Outer CRC matches:** the OTA container region is internally consistent.
2. **SFU1 payload digest matches:** the inner payload matches the digest stored in its header.
3. **Boot chain accepts it:** only a controlled device test can establish this, and acceptance may depend on signatures, installed bootloader, rollback policy, and base version.

A valid outer CRC does not imply a bootable image.

## Step 6: extract components

Only after the report passes basic checks:

```bash
python tools/firmware_pkg.py \
  ../private-inputs/stock.pkg \
  --extract-dir ../generated/stock-components \
  --json-out ../generated/stock-package-report.json
```

The output names include component index and type. Immediately hash the extracted directory and keep it read-only when practical.

Linux/WSL example:

```bash
sha256sum ../generated/stock-components/* > ../notes/stock-component-hashes.txt
```

PowerShell example:

```powershell
Get-ChildItem "..\generated\stock-components" -File |
  Get-FileHash -Algorithm SHA256 |
  Format-Table Path, Hash
```

## Step 7: verify extraction offsets

An extracted component should equal the exact source slice described by `offset` and `size`. The parser calculates hashes while streaming the source region, so the report hash and extracted-file hash should match.

If they do not:

1. preserve both files;
2. confirm the report and extraction came from the same command/input;
3. check disk errors and path confusion;
4. do not continue to patching.

## Step 8: write a reproducible result

Record:

```markdown
## Input identity
- model: M2116W1
- claimed version: 1.4.174
- file size: 185221135
- SHA-256: <complete local hash>

## Parser
- repository commit: <git rev-parse HEAD>
- Python: <python --version>
- command: <exact command>

## Result
- header/body invariant: pass/fail
- component count: 9
- component CRCs: 9/9 pass
- SFU1 payload digest: pass/fail
- differences from public matrix: none/list

## Evidence level
- observed/reproduced/inferred/hypothesis
```

Do not paste personal directories, account data, Bluetooth identifiers, firmware payloads, or purchased files into a public issue.

## Next steps

- To compare another package: [Firmware comparison](firmware-comparison.md).
- To inspect component 6: [GUI asset laboratory](gui-asset-lab.md).
- To inspect main-image code: [Ghidra and ARM workflow](ghidra-workflow.md).
- To understand package fields: [Firmware package formats](firmware-package-format.md).
