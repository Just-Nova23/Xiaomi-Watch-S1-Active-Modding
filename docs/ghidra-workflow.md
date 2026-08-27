# Ghidra and ARM Thumb workflow

This walkthrough creates a bounded Ghidra analysis for the extracted main component. It does not turn a raw binary into original source code, and auto-analysis output is not automatically correct.

## Install Ghidra safely

Use the [official NSA Ghidra repository and releases](https://github.com/NationalSecurityAgency/ghidra). The official installation notes require a compatible 64-bit JDK, extraction of the release archive, and launching `ghidraRun.bat` on Windows or `ghidraRun` on Linux. Read current security advisories before opening untrusted files.

## Prepare the input

1. Extract component 0 with `firmware_pkg.py`.
2. Verify its hash against the extraction report.
3. Copy it into a private working directory.
4. Record repository commit, package hash, component hash, size, model, and version.

For the documented build, the component size is `3,600,374` bytes and begins with an `SFU1` header.

## Create a project

1. Start Ghidra.
2. Choose **File → New Project**.
3. Select **Non-Shared Project** unless you have deliberately configured a secure team server.
4. Store the project outside this public Git repository.
5. Use a name that contains model and version, not a generic `firmware` name.

Example: `M2116W1_1.4.174_main_analysis`.

## Import as a raw binary

1. Choose **File → Import File**.
2. Select the extracted component.
3. When Ghidra reports raw binary, choose an ARM little-endian language compatible with Thumb analysis.
4. Do not guess a compiler specification as a fact; record the selection as an analysis setting.
5. Open **Options** or the memory map and establish the documented image base `0x08000000`.

The crucial mapping is:

```text
file 0x00000000 → runtime 0x08000000
file 0x0013024c → runtime 0x0813024c
```

Do not strip `0x2000` from file offsets when using this mapping.

## Treat the SFU1 header as data

The first `0x2000` bytes contain the observed `SFU1` header, digests, and signature candidate. Mark this region as data rather than disassembling it as Thumb instructions.

Suggested region note:

```text
0x08000000–0x08001fff: observed SFU1 header, not application code
```

The payload begins after that header in the documented component, but code and non-code data can still be mixed inside the payload.

## Run conservative auto-analysis

Enable basic reference, function, and ARM analysis, but expect false positives. Raw firmware lacks standard executable metadata, so Ghidra may:

- create functions in tables;
- miss Thumb entry points;
- apply the wrong function boundary;
- interpret UTF-16 or packed assets as instructions;
- propagate an incorrect type through many callers.

Do not bulk-rename hundreds of functions based on decompiler guesses.

## Use the repository locator first

Find a UTF-8 string and candidate cross-references:

```bash
python tools/thumb_xrefs.py \
  ../generated/stock-components/component-00-type-00.bin \
  --text "listening"
```

Or disassemble a verified window:

```bash
python tools/thumb_xrefs.py \
  ../generated/stock-components/component-00-type-00.bin \
  --disasm-offset 0x130240 \
  --bytes 0x100
```

The script uses Capstone in ARM Thumb little-endian mode. Capstone's [official Python tutorial](https://www.capstone-engine.org/lang_python.html) explains architecture/mode selection and why detailed operand information must be enabled explicitly.

## Navigate to an offset in Ghidra

Convert file offset to runtime address, then use **Go To**:

```text
0x08000000 + 0x0013024c = 0x0813024c
```

At the candidate address:

1. inspect bytes and instruction widths;
2. verify that branch targets land on plausible boundaries;
3. inspect incoming and outgoing references;
4. locate prologue and return behavior;
5. compare the same region in stock and modified components;
6. check whether the decompiler agrees with assembly, not the reverse.

## Follow a literal reference

Thumb code often loads a nearby literal using a PC-relative `ldr`. The effective literal address depends on the aligned program counter. The repository script calculates this and limits its search window to the reachable region.

Other addresses may be constructed with `movw` and `movt`. A textual search for a four-byte pointer alone will miss those pairs, so `thumb_xrefs.py` checks both strategies.

## Name evidence, not wishes

Good labels:

- `candidate_utf8_to_utf16_wrapper`;
- `assistant_text_handler_observed_0813024c`;
- `field_2b82_length_inferred`.

Weak labels:

- `send_to_screen` when only a string reference is known;
- `bluetooth_receive` without transport evidence;
- `alexa_main` for a function merely located near one Alexa string.

Add comments containing the evidence source and date.

## Verify the native assistant capacity region

The documented patch expects this context at file offset `0x130344`:

```text
4f f4 48 72 38 46 6a f1 b4 fe 2a 23
4f f4 96 72
39 46 70 68 c8 f0 b6 fa
```

The four bytes at `0x130350` decode as `mov.w r2, #300`. The guarded patch replaces them with the encoding for `mov.w r2, #400`; exactly one byte differs because of Thumb immediate encoding.

Before accepting the explanation, verify:

- the preceding call clears 800 bytes at the inline buffer;
- the destination object and field offsets remain consistent;
- the converter reserves a terminator;
- only the intended instruction changes;
- the context matches the documented build exactly.

## Export a reviewable finding

Include:

```markdown
## Location
- file offset:
- runtime address:
- component hash:

## Bytes
- context before:
- instruction before:
- instruction after:

## Cross-references
- callers:
- literals/strings:

## Interpretation
- observed:
- inferred:
- alternative explanation:

## Reproduction
- command:
- Ghidra language/base settings:
```

Do not upload a Ghidra project containing imported proprietary firmware. Share scripts, offsets, screenshots limited to necessary context, and synthetic fixtures.
