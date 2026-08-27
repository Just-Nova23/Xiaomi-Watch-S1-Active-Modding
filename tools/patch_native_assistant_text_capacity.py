#!/usr/bin/env python3
"""Raise the native assistant single-answer UTF-16 capacity safely.

The S1 Active handler owns an 800-byte inline UTF-16 buffer (400 code units).
Stock passes 300 to the UTF-8 converter, which reserves one code unit for NUL
and therefore displays at most 299 characters.  This patch changes only that
immediate to 400, giving a maximum of 399 characters without crossing the
existing buffer boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


CAPACITY_INSTRUCTION_OFFSET = 0x130350
OLD_INSTRUCTION = bytes.fromhex("4ff49672")  # mov.w r2, #300
NEW_INSTRUCTION = bytes.fromhex("4ff4c872")  # mov.w r2, #400

# Surrounding instructions: memset(buffer, 0, 800), replacement='*', then the
# capacity immediate patched above.  Checking the full sequence prevents this
# script from modifying a different firmware build at a coincidental offset.
EXPECTED_CONTEXT_OFFSET = 0x130344
EXPECTED_CONTEXT = bytes.fromhex(
    "4ff4487238466af1b4fe2a23" "4ff49672" "39467068c8f0b6fa"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    original = args.input.read_bytes()
    actual_context = original[
        EXPECTED_CONTEXT_OFFSET : EXPECTED_CONTEXT_OFFSET + len(EXPECTED_CONTEXT)
    ]
    if actual_context != EXPECTED_CONTEXT:
        raise ValueError(
            "firmware context mismatch at 0x130344; refusing an unsafe patch"
        )
    if original.count(OLD_INSTRUCTION) < 1:
        raise ValueError("expected mov.w r2,#300 instruction not found")

    patched = bytearray(original)
    patched[
        CAPACITY_INSTRUCTION_OFFSET : CAPACITY_INSTRUCTION_OFFSET + 4
    ] = NEW_INSTRUCTION

    # Assert that this build changes exactly one byte (0x96 -> 0xc8).
    changed_offsets = [
        index for index, (old, new) in enumerate(zip(original, patched)) if old != new
    ]
    if changed_offsets != [CAPACITY_INSTRUCTION_OFFSET + 2]:
        raise AssertionError(f"unexpected changed offsets: {changed_offsets}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(patched)
    report = {
        "input": str(args.input),
        "output": str(args.output),
        "input_sha256": sha256(original),
        "output_sha256": sha256(patched),
        "instruction_offset": CAPACITY_INSTRUCTION_OFFSET,
        "old_instruction_hex": OLD_INSTRUCTION.hex(),
        "new_instruction_hex": NEW_INSTRUCTION.hex(),
        "changed_offsets": changed_offsets,
        "old_capacity": 300,
        "new_capacity": 400,
        "old_max_visible_characters": 299,
        "new_max_visible_characters": 399,
        "buffer_bytes": 800,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
