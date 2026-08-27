#!/usr/bin/env python3
"""Catalog the individual GUI asset records in component 6 of an S1 Active package."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import zlib

from firmware_pkg import parse_package


ASSET_START = re.compile(
    rb"\x01\x00\x00\x00(?P<path_len>.)(?P<tag>.{4})(?P<path>nand/asset/[A-Za-z0-9_./-]+\.bin)"
)


def inspect_payload(payload: bytes) -> dict:
    if len(payload) < 8:
        return {"wrapped_payload_valid": False}
    declared_size = int.from_bytes(payload[:4], "big")
    stored_crc = payload[4:8]
    body = payload[8:]
    calculated_crc = (zlib.crc32(body, 0xFFFFFFFF) ^ 0xFFFFFFFF).to_bytes(4, "big")

    position = 0
    chunks: list[bytes] = []
    while position + 2 <= len(body):
        chunk_size = int.from_bytes(body[position : position + 2], "big")
        chunk_end = position + 2 + chunk_size
        if chunk_end > len(body):
            break
        chunks.append(body[position + 2 : chunk_end])
        position = chunk_end
    counts = Counter(hashlib.sha256(chunk).hexdigest() for chunk in chunks)
    return {
        "wrapped_payload_valid": declared_size == len(body) and stored_crc == calculated_crc,
        "declared_body_size": declared_size,
        "stored_body_crc32": stored_crc.hex(),
        "calculated_body_crc32": calculated_crc.hex(),
        "body_crc32_matches": stored_crc == calculated_crc,
        "length_prefixed_chunks": len(chunks),
        "chunks_cover_body": position == len(body),
        "unique_chunks": len(counts),
        "most_repeated_chunk_count": max(counts.values(), default=0),
    }


def catalog(package: Path, extract_dir: Path | None = None) -> dict:
    package_report = parse_package(package)
    component = package_report["components"][6]
    component_offset = component["offset"]
    component_size = component["size"]

    with package.open("rb") as handle:
        handle.seek(component_offset)
        data = handle.read(component_size)
    if len(data) != component_size:
        raise ValueError("unexpected end of GUI asset component")

    matches = list(ASSET_START.finditer(data))
    if not matches or matches[0].start() != 0:
        raise ValueError("GUI asset records were not found at the component start")

    if extract_dir:
        extract_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(data)
        record = data[start:end]
        path = match.group("path").decode("ascii")
        path_length = match.group("path_len")[0]
        if path_length != len(path):
            raise ValueError(f"path length mismatch for {path}")
        payload_version_offset = match.end()
        payload_version = data[payload_version_offset]
        payload_offset = payload_version_offset + 1
        payload = data[payload_offset:end]
        item = {
            "index": index,
            "path": path,
            "offset_in_component": start,
            "offset_in_component_hex": f"0x{start:08x}",
            "package_offset": component_offset + start,
            "package_offset_hex": f"0x{component_offset + start:08x}",
            "size": len(record),
            "size_hex": f"0x{len(record):08x}",
            "record_format_version": 1,
            "path_length": path_length,
            "record_tag_unknown": match.group("tag").hex(),
            "record_tag_algorithm": "CRC-32/ISO-HDLC with init=0, xorout=0 over the path, stored big-endian",
            "record_tag_matches": match.group("tag")
            == (zlib.crc32(match.group("path"), 0xFFFFFFFF) ^ 0xFFFFFFFF).to_bytes(4, "big"),
            "payload_format_version": payload_version,
            "payload_offset_in_component": payload_offset,
            "payload_size": len(payload),
            "payload_sha256": hashlib.sha256(payload).hexdigest(),
            "sha256": hashlib.sha256(record).hexdigest(),
            **inspect_payload(payload),
        }
        if extract_dir:
            output = extract_dir / f"{index:02d}-{Path(path).name}.record"
            output.write_bytes(record)
            item["extracted_file"] = output.name
        records.append(item)

    return {
        "input_file": package.name,
        "component_index": 6,
        "component_offset": component_offset,
        "component_size": component_size,
        "asset_count": len(records),
        "records_cover_entire_component": sum(item["size"] for item in records) == component_size,
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--extract-dir", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = catalog(args.package, args.extract_dir)
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        args.json_out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
