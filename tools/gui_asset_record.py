#!/usr/bin/env python3
"""Build or append generic ``nand/asset/*.bin`` records.

The OTA archive wrapper is independent from the file stored on NAND.  This
tool wraps an arbitrary NAND-file body with Xiaomi's path tag, body length and
body CRC.  It is suitable for TSCFrameImage files as well as other asset types.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import zlib


ASSET_START = re.compile(
    rb"\x01\x00\x00\x00(?P<path_len>.)(?P<tag>.{4})"
    rb"(?P<path>nand/asset/[A-Za-z0-9_./-]+\.bin)"
)


def crc32_xiaomi(data: bytes) -> bytes:
    return (zlib.crc32(data, 0xFFFFFFFF) ^ 0xFFFFFFFF).to_bytes(4, "big")


def build_record(path: bytes, body: bytes, payload_version: int = 2) -> bytes:
    if not path.startswith(b"nand/asset/") or not path.endswith(b".bin"):
        raise ValueError("asset path must be nand/asset/*.bin")
    if len(path) > 0xFF:
        raise ValueError("asset path exceeds its one-byte length field")
    if not 0 <= payload_version <= 0xFF:
        raise ValueError("payload version must fit one byte")
    payload = len(body).to_bytes(4, "big") + crc32_xiaomi(body) + body
    return (
        b"\x01\x00\x00\x00"
        + bytes((len(path),))
        + crc32_xiaomi(path)
        + path
        + bytes((payload_version,))
        + payload
    )


def append_record(component: bytes, record: bytes) -> bytes:
    match = ASSET_START.match(record)
    if not match or match.group("path_len")[0] != len(match.group("path")):
        raise ValueError("invalid asset record")
    new_path = match.group("path")
    existing = [item.group("path") for item in ASSET_START.finditer(component)]
    if new_path in existing:
        raise ValueError(f"component already contains {new_path.decode('ascii')}")
    if not existing or not ASSET_START.match(component):
        raise ValueError("input does not look like a GUI asset component")
    return component + record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    build_parser = commands.add_parser("build")
    build_parser.add_argument("path", help="NAND path, for example nand/asset/custom.bin")
    build_parser.add_argument("body", type=Path)
    build_parser.add_argument("output", type=Path)
    build_parser.add_argument("--payload-version", type=int, default=2)

    append_parser = commands.add_parser("append")
    append_parser.add_argument("component", type=Path)
    append_parser.add_argument("record", type=Path)
    append_parser.add_argument("output", type=Path)

    args = parser.parse_args()
    if args.command == "build":
        output = build_record(
            args.path.encode("ascii"), args.body.read_bytes(), args.payload_version
        )
    else:
        output = append_record(args.component.read_bytes(), args.record.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output)


if __name__ == "__main__":
    main()
