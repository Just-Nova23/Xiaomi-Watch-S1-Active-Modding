#!/usr/bin/env python3
"""Catalog the native TouchGFX bitmap database in the S1 Active main image."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import struct


ENTRY_SIZE = 20
DEFAULT_TABLE_OFFSET = 0x2F4DF4
VIRTUAL_BITMAP_BASE = 0x60000000


def parse_entry(data: bytes, offset: int, bitmap_id: int) -> dict:
    pointer, extra, width, height, solid_x, solid_y, packed_width, packed_height = (
        struct.unpack_from("<IIHHHHHH", data, offset)
    )
    expected_pointer = VIRTUAL_BITMAP_BASE + bitmap_id
    if pointer != expected_pointer:
        raise ValueError(
            f"bitmap {bitmap_id}: expected pointer 0x{expected_pointer:08x}, "
            f"got 0x{pointer:08x}"
        )
    format_hi = packed_width >> 13
    format_lo = packed_height >> 13
    return {
        "id": bitmap_id,
        "table_offset": offset,
        "virtual_pointer": f"0x{pointer:08x}",
        "extra_pointer": f"0x{extra:08x}",
        "width": width,
        "height": height,
        "solid_rect": {
            "x": solid_x,
            "y": solid_y,
            "width": packed_width & 0x1FFF,
            "height": packed_height & 0x1FFF,
        },
        "format": (format_hi << 3) | format_lo,
    }


def catalog(image: Path, table_offset: int) -> dict:
    data = image.read_bytes()
    entries = []
    bitmap_id = 0
    while table_offset + (bitmap_id + 1) * ENTRY_SIZE <= len(data):
        offset = table_offset + bitmap_id * ENTRY_SIZE
        pointer = struct.unpack_from("<I", data, offset)[0]
        if pointer != VIRTUAL_BITMAP_BASE + bitmap_id:
            break
        entries.append(parse_entry(data, offset, bitmap_id))
        bitmap_id += 1
    if not entries:
        raise ValueError("no TouchGFX bitmap records found at requested offset")
    formats = Counter(item["format"] for item in entries)
    return {
        "input_file": image.name,
        "table_offset": table_offset,
        "entry_size": ENTRY_SIZE,
        "bitmap_count": len(entries),
        "table_end": table_offset + len(entries) * ENTRY_SIZE,
        "format_counts": {str(key): value for key, value in sorted(formats.items())},
        "entries": entries,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument(
        "--table-offset",
        type=lambda value: int(value, 0),
        default=DEFAULT_TABLE_OFFSET,
    )
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(catalog(args.image, args.table_offset), indent=2) + "\n"
    if args.json_out:
        args.json_out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
