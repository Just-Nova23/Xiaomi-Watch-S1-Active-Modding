#!/usr/bin/env python3
"""Locate Thumb PC-relative references to strings or offsets in S1 Active firmware.

For the Xiaomi Watch S1 Active main component, runtime addresses observed in
embedded pointers map as ``0x08000000 + file_offset``.  The SFU1 header remains
part of that address space even though executable vectors/code begin later.
This helper keeps that verified mapping explicit and reports literal pools,
Thumb loads, and MOVW/MOVT address construction.
"""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_LITTLE_ENDIAN, CS_MODE_THUMB, Cs
from capstone.arm import (
    ARM_INS_MOVT,
    ARM_INS_MOVW,
    ARM_OP_IMM,
    ARM_OP_MEM,
    ARM_OP_REG,
    ARM_REG_PC,
)


def mapped_address(file_offset: int, image_offset: int, base: int) -> int:
    return base + file_offset - image_offset


def file_offset(address: int, image_offset: int, base: int) -> int:
    return image_offset + address - base


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--text")
    target.add_argument("--offset", type=lambda value: int(value, 0))
    target.add_argument("--immediate", type=lambda value: int(value, 0))
    target.add_argument("--disasm-offset", type=lambda value: int(value, 0))
    parser.add_argument("--image-offset", type=lambda value: int(value, 0), default=0)
    parser.add_argument("--base", type=lambda value: int(value, 0), default=0x08000000)
    parser.add_argument("--bytes", type=lambda value: int(value, 0), default=0x100)
    args = parser.parse_args()

    data = args.image.read_bytes()
    if args.text is not None:
        needle = args.text.encode("utf-8")
        targets = []
        cursor = 0
        while True:
            cursor = data.find(needle, cursor)
            if cursor < 0:
                break
            targets.append(cursor)
            cursor += 1
    else:
        targets = [args.offset]

    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)
    md.detail = True
    md.skipdata = True
    code = data[args.image_offset :]

    if args.disasm_offset is not None:
        start = args.disasm_offset
        address = mapped_address(start, args.image_offset, args.base)
        for instruction in md.disasm(data[start : start + args.bytes], address):
            if instruction.id == 0:
                print(f"0x{instruction.address:08x}: <data> {instruction.bytes.hex()}")
            else:
                print(
                    f"0x{instruction.address:08x}: {instruction.bytes.hex():<10} "
                    f"{instruction.mnemonic} {instruction.op_str}"
                )
        return

    if args.immediate is not None:
        for instruction in md.disasm(code, args.base):
            if instruction.id == 0:
                continue
            if not any(
                operand.type == ARM_OP_IMM and operand.imm == args.immediate
                for operand in instruction.operands
            ):
                continue
            offset = file_offset(instruction.address, args.image_offset, args.base)
            print(
                f"immediate=0x{args.immediate:x} file=0x{offset:x} "
                f"address=0x{instruction.address:08x}: "
                f"{instruction.mnemonic} {instruction.op_str}"
            )
        return

    for target_offset in targets:
        target_address = mapped_address(target_offset, args.image_offset, args.base)
        print(f"target file=0x{target_offset:x} address=0x{target_address:08x}")
        literals: list[tuple[int, int]] = []
        for pointer in (target_address, target_address | 1):
            encoded = struct.pack("<I", pointer)
            cursor = 0
            while True:
                cursor = data.find(encoded, cursor)
                if cursor < 0:
                    break
                literals.append((cursor, mapped_address(cursor, args.image_offset, args.base)))
                cursor += 1

        if not literals:
            print("  no literal pointers")
        else:
            literal_addresses = {address for _, address in literals}
            for literal_offset, literal_address in literals:
                print(f"  literal file=0x{literal_offset:x} address=0x{literal_address:08x}")

            for literal_offset, literal_address in literals:
                # A Thumb literal load can only reach a nearby, forward pool.
                # Restricting disassembly to that window makes this precise and
                # avoids decoding several megabytes for every pointer.
                start = max(args.image_offset, (literal_offset - 0x1004) & ~1)
                start_address = mapped_address(start, args.image_offset, args.base)
                for instruction in md.disasm(data[start:literal_offset], start_address):
                    if instruction.mnemonic != "ldr" or len(instruction.operands) < 2:
                        continue
                    operand = instruction.operands[1]
                    if operand.type != ARM_OP_MEM or operand.mem.base != ARM_REG_PC:
                        continue
                    loaded_from = ((instruction.address + 4) & ~3) + operand.mem.disp
                    if loaded_from != literal_address:
                        continue
                    offset = file_offset(instruction.address, args.image_offset, args.base)
                    print(
                        f"  xref file=0x{offset:x} address=0x{instruction.address:08x}: "
                        f"{instruction.mnemonic} {instruction.op_str}"
                    )

        if literals:
            continue

        # ARM/Thumb firmware often constructs addresses without a literal
        # pool by pairing MOVW (low half) and MOVT (high half).  Track a small
        # per-register window so string references emitted this way are not
        # missed.  Clear the candidate at control-flow boundaries to avoid
        # joining unrelated basic blocks.
        pending_movw: dict[int, tuple[int, int, str]] = {}
        for instruction in md.disasm(code, args.base):
            if instruction.id == 0:
                pending_movw.clear()
                continue
            operands = instruction.operands
            if (
                instruction.id == ARM_INS_MOVW
                and len(operands) == 2
                and operands[0].type == ARM_OP_REG
                and operands[1].type == ARM_OP_IMM
            ):
                pending_movw[operands[0].reg] = (
                    operands[1].imm & 0xFFFF,
                    instruction.address,
                    instruction.op_str,
                )
                continue
            if (
                instruction.id == ARM_INS_MOVT
                and len(operands) == 2
                and operands[0].type == ARM_OP_REG
                and operands[1].type == ARM_OP_IMM
                and operands[0].reg in pending_movw
            ):
                low, movw_address, movw_operands = pending_movw.pop(operands[0].reg)
                constructed = ((operands[1].imm & 0xFFFF) << 16) | low
                if constructed == target_address:
                    offset = file_offset(movw_address, args.image_offset, args.base)
                    print(
                        f"  movw/movt xref file=0x{offset:x} "
                        f"address=0x{movw_address:08x}: movw {movw_operands}; "
                        f"movt {instruction.op_str}"
                    )
            if instruction.group(1) or instruction.mnemonic in {"b", "bx", "bl", "blx", "pop"}:
                pending_movw.clear()


if __name__ == "__main__":
    main()
