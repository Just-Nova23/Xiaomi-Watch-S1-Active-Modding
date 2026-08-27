#!/usr/bin/env python3
"""Build a compact post-m0tral OTA from selected full-package components.

The Xiaomi ``diff`` container is a 0x35-byte prefix, followed by one 0x10e
descriptor per component and a four-byte header CRC.  Component descriptors
are copied from a known-good full package so type, flags and reserved fields
remain exact; only size and CRC are recalculated.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import zlib

from firmware_pkg import parse_package


PREFIX_SIZE = 0x35
DESCRIPTOR_SIZE = 0x10E


def ota_crc(data: bytes) -> bytes:
    value = (zlib.crc32(data, 0xFFFFFFFF) ^ 0xFFFFFFFF) & 0xFFFFFFFF
    return value.to_bytes(4, "big")


def full_descriptor(header: bytes, index: int) -> bytes:
    if index == 0:
        # The first full descriptor starts at 0x35.  Earlier inspection code
        # treated its first byte as part of the prefix; the 0x10e-byte layout
        # is in fact identical for every component.
        start = PREFIX_SIZE
    else:
        start = 0x143 + (index - 1) * DESCRIPTOR_SIZE
    return header[start : start + DESCRIPTOR_SIZE]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template-diff", type=Path, required=True)
    parser.add_argument("--full-package", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-version", required=True)
    parser.add_argument("--target-version", required=True)
    parser.add_argument("--component", action="append", default=[], metavar="INDEX=FILE")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    components: list[tuple[int, bytes]] = []
    for value in args.component:
        raw_index, separator, raw_path = value.partition("=")
        if not separator:
            parser.error("--component must use INDEX=FILE")
        components.append((int(raw_index), Path(raw_path).read_bytes()))
    if not components:
        parser.error("at least one --component is required")

    full_report = parse_package(args.full_package)
    full_raw = args.full_package.read_bytes()
    full_header = full_raw[: full_report["header_size"]]
    template = args.template_diff.read_bytes()
    if template[:4] != b"diff":
        raise ValueError("template is not a diff OTA")

    prefix = bytearray(template[:PREFIX_SIZE])
    body_size = sum(len(data) for _, data in components)
    prefix[8:12] = body_size.to_bytes(4, "big")
    prefix[0x34] = len(components)

    model = args.model.encode("ascii")
    if len(model) > 16:
        raise ValueError("model exceeds the 16-byte header field")
    prefix[0x10:0x20] = model.ljust(16, b"\0")

    for offset, version in ((4, args.base_version), (12, args.target_version)):
        values = tuple(map(int, version.split(".")))
        if len(values) != 4 or any(value < 0 or value > 255 for value in values):
            raise ValueError("versions must contain four byte values")
        prefix[offset : offset + 4] = bytes(values)

    descriptors = bytearray()
    facts = []
    for index, data in components:
        descriptor = bytearray(full_descriptor(full_header, index))
        if len(descriptor) != DESCRIPTOR_SIZE:
            raise ValueError(f"missing descriptor for component {index}")
        descriptor[6:10] = len(data).to_bytes(4, "big")
        descriptor[-4:] = ota_crc(data)
        descriptors.extend(descriptor)
        facts.append({
            "index": index,
            "type": descriptor[0],
            "flag": descriptor[1],
            "size": len(data),
            "crc": descriptor[-4:].hex(),
        })

    header_without_crc = bytes(prefix) + bytes(descriptors)
    result = header_without_crc + ota_crc(header_without_crc) + b"".join(
        data for _, data in components
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(result)

    report = {
        "model": args.model,
        "base_version": args.base_version,
        "target_version": args.target_version,
        "header_size": len(header_without_crc) + 4,
        "body_size": body_size,
        "component_count": len(components),
        "header_crc": result[len(header_without_crc) : len(header_without_crc) + 4].hex(),
        "components": facts,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.json_out:
        args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
