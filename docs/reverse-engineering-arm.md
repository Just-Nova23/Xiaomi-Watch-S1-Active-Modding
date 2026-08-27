# ARM Thumb reverse engineering

This page explains the method used on the main component. It is not a complete assembly course and does not authorize flashing an output.

## 1. Establish the address mapping

In the verified build, file offset `x` maps to this runtime address:

```text
runtime = 0x08000000 + x
file    = runtime - 0x08000000
```

For example, file offset `0x0013024c` becomes `0x0813024c`. This relationship was checked against embedded pointers and consistent references; it must not be assumed for other components.

## 2. Find a string

```bash
python tools/thumb_xrefs.py main.bin --text "listening"
```

The tool finds the string, little-endian pointers to its address, and instructions that load those pointers. A result is a starting point, not proof of a function's final purpose.

## 3. Reconstruct control flow

For each reference:

1. disassemble a narrow window;
2. identify the prologue, epilogue, and calls;
3. observe registers and object fields;
4. find uses of the same function in nearby paths;
5. record observations separately from hypotheses.

## 4. Recognize false positives

ARM Thumb firmware can mix data and instructions. A linear disassembler may interpret a table as code. Useful signals include consistent alignment, valid branch targets, multiple callers, and stable stack use.

## 5. Prepare a minimal patch

A robust patch records:

- source-file hash;
- file offset and runtime address;
- original and replacement bytes;
- disassembly before and after;
- verified surrounding context;
- the exact list of changed offsets;
- model and version constraints;
- offline tests and a recovery plan.

Do not patch a function merely because it contains UI text: a string may be shared by several states.

## Recommended tools

- `thumb_xrefs.py` for reproducible searches;
- Ghidra for functions, cross-references, and annotations;
- `xxd` or a hex editor for the final comparison;
- `sha256sum` to identify every artifact.

Ghidra annotations are not self-contained evidence. Always export verifiable offsets and bytes.
