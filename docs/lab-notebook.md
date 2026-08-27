# Reproducible lab notebook

A lab notebook prevents memory, filenames, and conclusions from drifting across long experiments. Keep a private notebook for sensitive paths and hashes; publish a sanitized version when it helps others reproduce the result.

## One experiment per entry

Use a stable identifier such as:

```text
EXP-2026-08-27-001-package-parse
EXP-2026-08-27-002-assistant-xref
```

Do not overwrite an old result after tools or assumptions change. Add a correction entry linking the earlier one.

## Complete template

```markdown
# Experiment ID and title

## Question
One sentence that can be answered by evidence.

## Safety boundary
- read-only / writes copy / package build / device test
- proprietary inputs remain outside repository: yes/no
- recovery prerequisite: not applicable / required / verified

## Environment
- date and timezone:
- operator:
- operating system:
- Python:
- repository commit:
- tool versions:

## Device
- model:
- firmware before:
- relevant mod/boot state:
- battery before:

## Inputs
| Name | Size | SHA-256 | Provenance |
|---|---:|---|---|

## Hypothesis

## Alternative explanations
1.

## Procedure
1. Exact command or action.

## Raw observations
- timestamps:
- offsets:
- byte context:
- return codes:
- logs:

## Derived values
- calculations:
- address mapping:
- grouped ranges:

## Result
- observed:
- reproduced:
- inferred:
- unknown:

## Validation
- repeated run:
- independent method:
- synthetic test:
- device result:

## Artifacts
- private:
- safe to publish:

## Next experiment
```

## Command capture

Copy commands exactly, including working directory and tool commit. A command without its input identity is incomplete.

Good:

```text
cwd: S1ActiveResearch/Xiaomi-Watch-S1-Active-Modding
commit: 0f455b64883b1bb11c08b0b3f9d1b8118d327aa5
input SHA-256: <full private hash>
command: python tools/thumb_xrefs.py ../generated/main.bin --text listening
exit code: 0
```

Weak:

```text
ran the scanner and found the function
```

## Byte excerpts

Publish only the minimum bytes necessary to describe interoperability or a patch. Include the starting offset and interpretation. Avoid long contiguous dumps.

```text
file offset 0x130350
before: 4f f4 96 72  ; mov.w r2,#300
after:  4f f4 c8 72  ; mov.w r2,#400
```

## Screenshot and video evidence

Record:

- exact build/package hash;
- start and end state;
- action performed;
- visible result;
- timestamp aligned with logs.

A video proves visible behavior but usually not internal causality. Pair it with a minimal binary diff or code path when claiming that a patch caused the result.

## Negative results

Document failures. A rejected package, unmatched context, or packet hypothesis that fails across assets prevents others from repeating the same dead end.

Use:

```markdown
### Negative result
Hypothesis: bytes 0..1 are width.
Test: compared 12 records with known visible dimensions.
Observation: value varied independently of width.
Conclusion: hypothesis rejected for payload version 2.
```

## Sanitization checklist

Before publishing:

- replace personal absolute paths;
- remove account IDs and Bluetooth addresses;
- remove tokens, cookies, keys, certificates, and `.env` values;
- do not attach firmware, APKs, RPKs, extracted assets, or purchased files;
- keep complete hashes only when they identify an input without exposing it;
- confirm screenshots contain no notifications or personal device names.

## Evidence review

Ask another contributor to reproduce the procedure using their own legally obtained input. Independent reproduction is stronger than repeating the same command on the same file.
