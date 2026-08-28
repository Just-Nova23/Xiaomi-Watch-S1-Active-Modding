#!/usr/bin/env python3
"""Build and inspect Xiaomi ``TSCFrameImage`` files.

The native widget consumes an eight-byte little-endian header followed by
fixed-size NEMA TSC6A frames.  NEMA PixPresso can encode/decode the individual
headerless TSC6A frames; this module implements Xiaomi's surrounding file
format and validates every size before producing output.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile


HEADER = struct.Struct("<HHI")
NEMA_TSC6A_BITS_PER_PIXEL = 6


@dataclass(frozen=True)
class TSCFrameImage:
    width: int
    height: int
    frames: tuple[bytes, ...]

    @property
    def frame_size(self) -> int:
        return frame_size(self.width, self.height)

    def to_bytes(self) -> bytes:
        expected = self.frame_size
        for index, frame in enumerate(self.frames):
            if len(frame) != expected:
                raise ValueError(
                    f"frame {index} is {len(frame)} bytes; expected {expected}"
                )
        if not self.frames:
            raise ValueError("TSCFrameImage needs at least one frame")
        return HEADER.pack(self.width, self.height, len(self.frames)) + b"".join(
            self.frames
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "TSCFrameImage":
        if len(data) < HEADER.size:
            raise ValueError("truncated TSCFrameImage header")
        width, height, count = HEADER.unpack_from(data)
        expected = frame_size(width, height)
        body = data[HEADER.size :]
        if count == 0:
            raise ValueError("TSCFrameImage declares zero frames")
        if len(body) != count * expected:
            raise ValueError(
                f"TSCFrameImage body is {len(body)} bytes; "
                f"header requires {count * expected}"
            )
        frames = tuple(
            body[offset : offset + expected]
            for offset in range(0, len(body), expected)
        )
        return cls(width, height, frames)


def frame_size(width: int, height: int) -> int:
    if not 0 < width <= 0xFFFF or not 0 < height <= 0xFFFF:
        raise ValueError("width and height must fit unsigned 16-bit fields")
    if width % 4 or height % 4:
        raise ValueError("NEMA TSC6A dimensions must be multiples of four")
    bits = width * height * NEMA_TSC6A_BITS_PER_PIXEL
    if bits % 8:
        raise ValueError("TSC6A frame size is not byte-aligned")
    return bits // 8


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError(f"{path} is not a supported PNG")
    return struct.unpack(">II", data[16:24])


def _windows_path(path: Path) -> str:
    result = subprocess.run(
        ["wslpath", "-w", str(path.resolve())],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _run_pixpresso(
    executable: Path, source: Path, output_stem: Path, *, quality: str
) -> Path:
    image_format = "TSC6AHQ" if quality == "hq" else "TSC6AF"
    running_under_wsl = shutil.which("wslpath") is not None and executable.suffix.lower() == ".exe"
    if running_under_wsl:
        arguments = [
            _windows_path(executable),
            "-s",
            _windows_path(source),
            "-f",
            image_format,
            "-o",
            _windows_path(output_stem),
        ]
        command = ["cmd.exe", "/d", "/s", "/c", subprocess.list2cmdline(arguments)]
    else:
        command = [
            str(executable),
            "-s",
            str(source),
            "-f",
            image_format,
            "-o",
            str(output_stem),
        ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        message = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"PixPresso failed: {message}")

    candidates = (output_stem, Path(f"{output_stem}.tsc6a"))
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise RuntimeError("PixPresso succeeded but did not create a TSC6A output")


def encode_pngs(
    png_files: list[Path], pixpresso: Path, *, quality: str = "hq"
) -> TSCFrameImage:
    if not png_files:
        raise ValueError("at least one PNG frame is required")
    dimensions = [png_dimensions(path) for path in png_files]
    if any(item != dimensions[0] for item in dimensions[1:]):
        raise ValueError("all PNG frames must have identical dimensions")
    width, height = dimensions[0]
    expected = frame_size(width, height)
    frames: list[bytes] = []
    with tempfile.TemporaryDirectory(prefix="tsc-frame-image-") as directory:
        temporary = Path(directory)
        for index, source in enumerate(png_files):
            encoded = _run_pixpresso(
                pixpresso, source, temporary / f"frame-{index:04d}", quality=quality
            )
            frame = encoded.read_bytes()
            if len(frame) != expected:
                raise ValueError(
                    f"PixPresso frame {index} is {len(frame)} bytes; expected {expected}"
                )
            frames.append(frame)
    return TSCFrameImage(width, height, tuple(frames))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    inspect_parser = commands.add_parser("inspect", help="validate and describe a file")
    inspect_parser.add_argument("input", type=Path)

    extract_parser = commands.add_parser("extract", help="extract raw TSC6A frames")
    extract_parser.add_argument("input", type=Path)
    extract_parser.add_argument("output_dir", type=Path)

    pack_parser = commands.add_parser("pack", help="pack raw TSC6A frames")
    pack_parser.add_argument("width", type=int)
    pack_parser.add_argument("height", type=int)
    pack_parser.add_argument("output", type=Path)
    pack_parser.add_argument("frames", nargs="+", type=Path)

    encode_parser = commands.add_parser("encode", help="encode PNGs through PixPresso")
    encode_parser.add_argument("output", type=Path)
    encode_parser.add_argument("frames", nargs="+", type=Path)
    encode_parser.add_argument("--pixpresso", required=True, type=Path)
    encode_parser.add_argument("--quality", choices=("fast", "hq"), default="hq")

    args = parser.parse_args()
    if args.command == "inspect":
        image = TSCFrameImage.from_bytes(args.input.read_bytes())
        print(f"width={image.width}")
        print(f"height={image.height}")
        print(f"frames={len(image.frames)}")
        print(f"frame_size={image.frame_size}")
        return
    if args.command == "extract":
        image = TSCFrameImage.from_bytes(args.input.read_bytes())
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for index, frame in enumerate(image.frames):
            (args.output_dir / f"frame-{index:04d}.tsc6a").write_bytes(frame)
        return
    if args.command == "pack":
        image = TSCFrameImage(
            args.width, args.height, tuple(path.read_bytes() for path in args.frames)
        )
    else:
        image = encode_pngs(args.frames, args.pixpresso, quality=args.quality)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(image.to_bytes())


if __name__ == "__main__":
    main()
