# Reproducible reverse engineering

## Record facts, not conclusions alone

For each discovery, keep:

- device and firmware identity;
- SHA-256 of the input file;
- component index and size;
- file offset and mapped runtime address;
- raw bytes and disassembly;
- all references and callers examined;
- alternative explanations considered;
- offline and device tests performed.

## Correcting earlier work

Reverse engineering changes as evidence improves. Keep corrections explicit.
For example, early work treated the `0x2000` SFU1 header as unmapped and used an
incorrect code base. A broad embedded-pointer comparison later established the
main-component mapping `0x08000000 + file_offset`. Tools and documentation must
use the newer verified result.

## Patch design

Prefer modifications that:

- preserve component size and offsets;
- preserve surrounding instruction width;
- verify the original context before writing;
- change the smallest possible byte range;
- reject unknown firmware builds;
- emit hashes and a machine-readable report;
- can be compared against an unmodified input.

## Publication

Publish scripts, synthetic fixtures, offsets, minimal byte excerpts, and
reasoning. Do not publish copyrighted firmware or paid packages. A result that
cannot be shared as a binary can still be independently reproducible when the
tool accepts a contributor's own input.
