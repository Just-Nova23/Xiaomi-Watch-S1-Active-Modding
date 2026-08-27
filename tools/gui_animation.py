#!/usr/bin/env python3
"""Extract and rebuild Xiaomi GUI image-stream payloads.

The outer record and packet stream are understood. Packet boundaries are not
yet proven to be frame boundaries: Xiaomi uses the same container for animated
and non-animated GUI resources. The TSCFrameImage payload remains opaque, so
this tool deliberately preserves every packet byte-for-byte.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zlib


def crc32_xiaomi(data: bytes) -> bytes:
    return (zlib.crc32(data, 0xFFFFFFFF) ^ 0xFFFFFFFF).to_bytes(4, "big")


def split_record(record: bytes) -> tuple[bytes, int, list[bytes]]:
    if record[:4] != b"\x01\x00\x00\x00":
        raise ValueError("unsupported GUI record version")
    path_length = record[4]
    path_end = 9 + path_length
    path = record[9:path_end]
    if len(path) != path_length or not path.startswith(b"nand/asset/"):
        raise ValueError("invalid GUI record path")
    if record[5:9] != crc32_xiaomi(path):
        raise ValueError("GUI record path CRC mismatch")
    payload_version = record[path_end]
    payload = record[path_end + 1 :]
    if len(payload) < 8:
        raise ValueError("truncated GUI payload")
    body_size = int.from_bytes(payload[:4], "big")
    body = payload[8:]
    if body_size != len(body):
        raise ValueError("GUI animation body length mismatch")
    if payload[4:8] != crc32_xiaomi(body):
        raise ValueError("GUI animation body CRC mismatch")

    chunks: list[bytes] = []
    offset = 0
    while offset < len(body):
        if offset + 2 > len(body):
            raise ValueError("truncated GUI packet length")
        size = int.from_bytes(body[offset : offset + 2], "big")
        end = offset + 2 + size
        if end > len(body):
            raise ValueError("truncated GUI packet")
        chunks.append(body[offset + 2 : end])
        offset = end
    return path, payload_version, chunks


def build_record(path: bytes, payload_version: int, chunks: list[bytes]) -> bytes:
    if len(path) > 255:
        raise ValueError("GUI record path is too long")
    body_parts: list[bytes] = []
    for chunk in chunks:
        if len(chunk) > 0xFFFF:
            raise ValueError("GUI packet exceeds 16-bit length field")
        body_parts.extend((len(chunk).to_bytes(2, "big"), chunk))
    body = b"".join(body_parts)
    payload = len(body).to_bytes(4, "big") + crc32_xiaomi(body) + body
    return (
        b"\x01\x00\x00\x00"
        + bytes((len(path),))
        + crc32_xiaomi(path)
        + path
        + bytes((payload_version,))
        + payload
    )


def extract(record_file: Path, output_dir: Path) -> None:
    path, payload_version, chunks = split_record(record_file.read_bytes())
    output_dir.mkdir(parents=True, exist_ok=True)
    packets = []
    for index, chunk in enumerate(chunks):
        name = f"packet-{index:04d}.bin"
        (output_dir / name).write_bytes(chunk)
        packets.append(
            {
                "index": index,
                "file": name,
                "size": len(chunk),
                "sha256": hashlib.sha256(chunk).hexdigest(),
            }
        )
    manifest = {
        "path": path.decode("ascii"),
        "payload_version": payload_version,
        "packet_count": len(chunks),
        "packets": packets,
    }
    (output_dir / "animation.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def rebuild(input_dir: Path, output_file: Path) -> None:
    manifest = json.loads((input_dir / "animation.json").read_text(encoding="utf-8"))
    # Accept manifests produced by the earlier experimental extractor too.
    entries = manifest.get("packets", manifest.get("frames"))
    if entries is None:
        raise ValueError("manifest has neither packets nor legacy frames")
    chunks = [(input_dir / entry["file"]).read_bytes() for entry in entries]
    record = build_record(
        manifest["path"].encode("ascii"), manifest["payload_version"], chunks
    )
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_bytes(record)


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    extract_parser = subparsers.add_parser("extract")
    extract_parser.add_argument("record", type=Path)
    extract_parser.add_argument("output_dir", type=Path)
    rebuild_parser = subparsers.add_parser("rebuild")
    rebuild_parser.add_argument("input_dir", type=Path)
    rebuild_parser.add_argument("output_file", type=Path)
    args = parser.parse_args()
    if args.command == "extract":
        extract(args.record, args.output_dir)
    else:
        rebuild(args.input_dir, args.output_file)


if __name__ == "__main__":
    main()
