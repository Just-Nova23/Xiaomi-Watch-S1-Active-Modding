#!/usr/bin/env python3
"""Inspect and optionally split Xiaomi Watch S1 Active `full` packages.

The parser deliberately preserves unknown fields instead of assigning names that
have not yet been proven. It never modifies the input package.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zlib


COMPONENT_HINTS = {
    0: "main watch OS image with SFU1 header",
    1: "wrapped resource/image (unknown)",
    2: "wrapped resource/image (unknown)",
    3: "audio resource container",
    4: "STM32 bootloader/secondary image",
    5: "wrapped BREAM patch",
    6: "GUI asset container",
    7: "calibration/configuration image",
    8: "BES best1501 FreeRTOS image",
}


def digest_region(handle, offset: int, size: int, output: Path | None = None) -> dict:
    handle.seek(offset)
    remaining = size
    sha256 = hashlib.sha256()
    crc32 = 0
    crc32_init_zero = 0xFFFFFFFF
    first = b""
    last = b""
    writer = output.open("wb") if output else None
    try:
        while remaining:
            chunk = handle.read(min(1024 * 1024, remaining))
            if not chunk:
                raise ValueError("unexpected end of package")
            if not first:
                first = chunk[:16]
            last = (last + chunk)[-16:]
            sha256.update(chunk)
            crc32 = zlib.crc32(chunk, crc32)
            crc32_init_zero = zlib.crc32(chunk, crc32_init_zero)
            if writer:
                writer.write(chunk)
            remaining -= len(chunk)
    finally:
        if writer:
            writer.close()
    return {
        "sha256": sha256.hexdigest(),
        "standard_crc32": f"{crc32 & 0xFFFFFFFF:08x}",
        "crc32_init_zero": f"{(crc32_init_zero ^ 0xFFFFFFFF) & 0xFFFFFFFF:08x}",
        "first_16_bytes": first.hex(),
        "last_16_bytes": last.hex(),
    }


def inspect_sfu1(handle, offset: int, component_size: int) -> dict | None:
    handle.seek(offset)
    header = handle.read(0x2000)
    if header[:4] != b"SFU1" or len(header) != 0x2000:
        return None
    payload_size = int.from_bytes(header[8:12], "little")
    if payload_size + len(header) != component_size:
        raise ValueError("SFU1 payload length does not match component length")
    stored_digest = header[0x14:0x34]
    repeated_digest = header[0x34:0x54]
    handle.seek(offset + len(header))
    remaining = payload_size
    digest = hashlib.sha256()
    while remaining:
        chunk = handle.read(min(1024 * 1024, remaining))
        if not chunk:
            raise ValueError("unexpected end of SFU1 payload")
        digest.update(chunk)
        remaining -= len(chunk)
    calculated_digest = digest.digest()
    signature_candidate = header[0x80:0xC0]
    return {
        "format": "SFU1",
        "header_size": len(header),
        "protocol_version": int.from_bytes(header[4:6], "little"),
        "firmware_version": int.from_bytes(header[6:8], "little"),
        "payload_size": payload_size,
        "partial_firmware_offset": int.from_bytes(header[12:16], "little"),
        "partial_firmware_size": int.from_bytes(header[16:20], "little"),
        "stored_sha256": stored_digest.hex(),
        "repeated_sha256_matches": repeated_digest == stored_digest,
        "payload_sha256_matches": calculated_digest == stored_digest,
        "signed_header_sha256": hashlib.sha256(header[:0x80]).hexdigest(),
        "signature_scheme_hint": "ECDSA P-256, standard ST SBSFU layout",
        "signature_candidate_size": len(signature_candidate),
        "signature_candidate": signature_candidate.hex(),
        "signature_candidate_nonzero_bytes": sum(value != 0 for value in signature_candidate),
    }


def inspect_wrapped_component(handle, offset: int, component_size: int) -> dict | None:
    """Describe the 12-byte wrapper used by components marked with flag 1.

    The first two words deliberately remain unnamed: their meaning has not yet
    been established. The final word is known to be a big-endian payload size.
    """
    if component_size < 12:
        return None
    handle.seek(offset)
    wrapper = handle.read(12)
    payload_size = int.from_bytes(wrapper[8:12], "big")
    handle.seek(offset + 12)
    payload_prefix = handle.read(min(32, component_size - 12))
    result = {
        "format": "12-byte wrapped component",
        "wrapper_size": 12,
        "unknown_word_0": wrapper[0:4].hex(),
        "unknown_word_1": wrapper[4:8].hex(),
        "declared_payload_size": payload_size,
        "payload_size_matches": payload_size == component_size - 12,
        "payload_first_32_bytes": payload_prefix.hex(),
    }
    if len(payload_prefix) >= 16 and payload_prefix[4:16] == b"BREAM PATCH ":
        result["inner_marker"] = "BREAM PATCH"
    return result


def parse_package(package: Path, extract_dir: Path | None = None) -> dict:
    file_size = package.stat().st_size
    with package.open("rb") as handle:
        header = handle.read(0x1000)
        if header[:4] != b"full":
            raise ValueError("not a Xiaomi `full` package")

        body_size = int.from_bytes(header[8:12], "big")
        header_size = file_size - body_size
        if header_size <= 0 or header_size > len(header):
            raise ValueError("invalid body length in package header")

        raw_model = header[0x10:0x20].split(b"\0", 1)[0]
        version = ".".join(str(value) for value in header[0x0C:0x10])

        # Component zero uses a 13-byte descriptor. The remaining descriptors
        # use 14 bytes followed by a 256-byte reserved/signature area.
        descriptors = [
            {
                "leading_value_unknown": header[0x32:0x36].hex(),
                "type": header[0x36],
                "flag": header[0x37],
                "reserved": header[0x38:0x3B].hex(),
                "size": int.from_bytes(header[0x3B:0x3F], "big"),
                "signature_or_reserved": header[0x3F:0x13F],
            }
        ]
        for index in range(1, 9):
            start = 0x13F + (index - 1) * 0x10E
            descriptors.append(
                {
                    "previous_component_crc32": header[start : start + 4].hex(),
                    "type": header[start + 4],
                    "flag": header[start + 5],
                    "reserved": header[start + 6 : start + 10].hex(),
                    "size": int.from_bytes(header[start + 10 : start + 14], "big"),
                    "signature_or_reserved": header[start + 14 : start + 270],
                }
            )

        if sum(item["size"] for item in descriptors) != body_size:
            raise ValueError("component lengths do not match declared body length")

        if extract_dir:
            extract_dir.mkdir(parents=True, exist_ok=True)

        offset = header_size
        components = []
        for index, descriptor in enumerate(descriptors):
            output = extract_dir / f"component-{index:02d}-type-{descriptor['type']:02d}.bin" if extract_dir else None
            facts = digest_region(handle, offset, descriptor["size"], output)
            inner_format = inspect_sfu1(handle, offset, descriptor["size"])
            if inner_format is None and descriptor["flag"] == 1:
                inner_format = inspect_wrapped_component(handle, offset, descriptor["size"])
            signature = descriptor.pop("signature_or_reserved")
            stored_crc = (
                descriptors[index + 1]["previous_component_crc32"]
                if index + 1 < len(descriptors)
                else header[0x9AF:0x9B3].hex()
            )
            component = {
                "index": index,
                "type": descriptor["type"],
                "role_hint": COMPONENT_HINTS.get(index, "unknown"),
                "flag": descriptor["flag"],
                "reserved": descriptor["reserved"],
                "stored_crc32_after_component": stored_crc,
                "stored_crc32_matches": stored_crc == facts["crc32_init_zero"],
                "signature_area_nonzero_bytes": sum(value != 0 for value in signature),
                "offset": offset,
                "offset_hex": f"0x{offset:08x}",
                "size": descriptor["size"],
                "size_hex": f"0x{descriptor['size']:08x}",
                **facts,
            }
            if inner_format:
                component["inner_format"] = inner_format
            if output:
                component["extracted_file"] = output.name
            components.append(component)
            offset += descriptor["size"]

    return {
        "format": "Xiaomi full package (reverse-engineered subset)",
        "input_file": package.name,
        "file_size": file_size,
        "header_size": header_size,
        "body_size": body_size,
        "model": raw_model.decode("ascii", "replace"),
        "version": version,
        "component_count": len(components),
        "leading_value_unknown": descriptors[0]["leading_value_unknown"],
        "stored_header_crc32": header[0x9B3:0x9B7].hex(),
        "calculated_header_crc32": f"{(zlib.crc32(header[:header_size - 4], 0xFFFFFFFF) ^ 0xFFFFFFFF) & 0xFFFFFFFF:08x}",
        "header_crc32_matches": header[0x9B3:0x9B7].hex()
        == f"{(zlib.crc32(header[:header_size - 4], 0xFFFFFFFF) ^ 0xFFFFFFFF) & 0xFFFFFFFF:08x}",
        "components": components,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--extract-dir", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = parse_package(args.package, args.extract_dir)
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        args.json_out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
