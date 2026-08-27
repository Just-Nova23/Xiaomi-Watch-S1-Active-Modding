#!/usr/bin/env python3
"""Inspect and rebuild the compact Xiaomi Watch S1 Active ``diff`` OTA.

The format used by the m0tral S1 Active package is a 597-byte header followed
by bootloader and main-OS images.  Unknown/signature fields are preserved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zlib


HEADER_SIZE = 0x255
BOOT_SIZE_OFFSET = 0x3B
BOOT_CRC_OFFSET = 0x13F
MAIN_SIZE_OFFSET = 0x149
MAIN_CRC_OFFSET = 0x24D
HEADER_CRC_OFFSET = 0x251


def ota_crc(data: bytes) -> bytes:
    value = (zlib.crc32(data, 0xFFFFFFFF) ^ 0xFFFFFFFF) & 0xFFFFFFFF
    return value.to_bytes(4, "big")


def parse(raw: bytes) -> dict:
    if len(raw) < HEADER_SIZE or raw[:4] != b"diff":
        raise ValueError("not a supported Xiaomi diff package")
    body_size = int.from_bytes(raw[8:12], "big")
    if len(raw) != HEADER_SIZE + body_size:
        raise ValueError("declared body size does not match file")
    boot_size = int.from_bytes(raw[BOOT_SIZE_OFFSET:BOOT_SIZE_OFFSET + 4], "big")
    main_size = int.from_bytes(raw[MAIN_SIZE_OFFSET:MAIN_SIZE_OFFSET + 4], "big")
    if boot_size + main_size != body_size:
        raise ValueError("component sizes do not match body size")
    boot = raw[HEADER_SIZE:HEADER_SIZE + boot_size]
    main = raw[HEADER_SIZE + boot_size:]
    return {
        "header": raw[:HEADER_SIZE],
        "boot": boot,
        "main": main,
        "facts": {
            "model": raw[0x10:0x20].split(b"\0", 1)[0].decode("ascii", "replace"),
            "base_version": ".".join(str(x) for x in raw[4:8]),
            "target_version": ".".join(str(x) for x in raw[12:16]),
            "body_size": body_size,
            "boot_size": boot_size,
            "main_size": main_size,
            "boot_crc_valid": raw[BOOT_CRC_OFFSET:BOOT_CRC_OFFSET + 4] == ota_crc(boot),
            "main_crc_valid": raw[MAIN_CRC_OFFSET:MAIN_CRC_OFFSET + 4] == ota_crc(main),
            "header_crc_valid": raw[HEADER_CRC_OFFSET:HEADER_CRC_OFFSET + 4]
            == ota_crc(raw[:HEADER_CRC_OFFSET]),
            "sha256": hashlib.sha256(raw).hexdigest(),
        },
    }


def rebuild(
    template: bytes,
    boot: bytes,
    main: bytes,
    model: str | None = None,
    base_version: tuple[int, int, int, int] | None = None,
    target_version: tuple[int, int, int, int] | None = None,
) -> bytes:
    parsed = parse(template)
    header = bytearray(parsed["header"])
    body_size = len(boot) + len(main)
    header[8:12] = body_size.to_bytes(4, "big")
    header[BOOT_SIZE_OFFSET:BOOT_SIZE_OFFSET + 4] = len(boot).to_bytes(4, "big")
    header[MAIN_SIZE_OFFSET:MAIN_SIZE_OFFSET + 4] = len(main).to_bytes(4, "big")
    if model is not None:
        encoded_model = model.encode("ascii")
        if len(encoded_model) > 16:
            raise ValueError("model must fit in the 16-byte header field")
        header[0x10:0x20] = encoded_model.ljust(16, b"\0")
    if base_version is not None:
        header[4:8] = bytes(base_version)
    if target_version is not None:
        header[12:16] = bytes(target_version)
    header[BOOT_CRC_OFFSET:BOOT_CRC_OFFSET + 4] = ota_crc(boot)
    header[MAIN_CRC_OFFSET:MAIN_CRC_OFFSET + 4] = ota_crc(main)
    header[HEADER_CRC_OFFSET:HEADER_CRC_OFFSET + 4] = ota_crc(header[:HEADER_CRC_OFFSET])
    return bytes(header) + boot + main


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--boot", type=Path)
    parser.add_argument("--main", dest="main_image", type=Path)
    parser.add_argument("--model", help="16-byte OTA model/manufacturer identifier")
    parser.add_argument("--base-version", help="required installed version, for example 1.4.0.175")
    parser.add_argument("--target-version", help="target version, for example 1.4.0.176")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = args.package.read_bytes()
    if args.output:
        current = parse(raw)
        base_version = tuple(map(int, args.base_version.split("."))) if args.base_version else None
        target_version = tuple(map(int, args.target_version.split("."))) if args.target_version else None
        for name, version in (("base", base_version), ("target", target_version)):
            if version is not None and (len(version) != 4 or any(x < 0 or x > 255 for x in version)):
                raise ValueError(f"{name} version must contain four bytes")
        rebuilt = rebuild(
            raw,
            args.boot.read_bytes() if args.boot else current["boot"],
            args.main_image.read_bytes() if args.main_image else current["main"],
            args.model,
            base_version,
            target_version,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(rebuilt)
        raw = rebuilt
    facts = parse(raw)["facts"]
    rendered = json.dumps(facts, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        args.json_out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
