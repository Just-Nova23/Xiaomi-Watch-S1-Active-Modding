# Xiaomi Watch S1 Active Modding

An open, reproducible guide maintained by [Just-Nova23](https://github.com/Just-Nova23) for understanding the **Xiaomi Watch S1 Active M2116W1** firmware, building analysis tools, and experimenting with verifiable modifications.

!!! warning "This is not a ready-to-install firmware"
    The project does not distribute Xiaomi firmware, modified firmware, APKs, commercial RPKs, keys, or signatures. The tools operate only on copies legally obtained by the user. An incorrect modification can make the watch unusable.

## Where to begin

| If you want to… | Read… |
|---|---|
| choose the correct route for your goal | [Learning path](learning-path.md) |
| prepare Windows, WSL, or Linux from zero | [Windows and Linux setup](windows-setup.md) |
| understand the project with no prior knowledge | [Getting started](getting-started.md) |
| see what has actually been verified | [Research status](status.md) |
| understand the firmware components | [Architecture](architecture.md) |
| inspect only evidence-backed diagrams | [Verified concept maps](concept-maps.md) |
| inspect a package without changing it | [Package formats](firmware-package-format.md) and [Tools](tools-reference.md) |
| follow a complete package inspection | [Full-package walkthrough](full-package-walkthrough.md) |
| compare two versions or mods | [Firmware comparison](firmware-comparison.md) |
| analyze native code in Ghidra | [Ghidra and ARM workflow](ghidra-workflow.md) |
| study built-in system apps | [Native apps](native-apps.md) |
| study installable apps | [RPK apps](rpk-apps.md) |
| build an installable app from zero | [RPK tutorial](rpk-tutorial.md) |
| understand graphics and animations | [Graphics and TSCFrameImage](graphics-tscframeimage.md) |
| reproduce GUI-container experiments | [Native GUI asset laboratory](gui-asset-lab.md) |
| develop a guarded patch | [Patch development](patch-development.md) |
| reproduce the verified text-capacity patch | [Assistant patch walkthrough](assistant-patch-walkthrough.md) |
| inspect measured firmware data as charts | [Research data and charts](research-data.md) |
| keep experiments reproducible | [Lab notebook](lab-notebook.md) |
| find official specifications and tools | [Resource library](references.md) |
| contribute new evidence | [Contributing research](contributing-research.md) |

## Principles

1. **Evidence before conclusions.** Every fact should have an offset, hash, output, or reproducible procedure.
2. **Read before write.** Analyze a copy; do not begin with a device test.
3. **One change at a time.** A minimal patch is easier to verify and reverse.
4. **No proprietary material.** The repository contains documentation, original code, and synthetic fixtures.
5. **Explicit uncertainty.** “Observed,” “inferred,” and “hypothesized” do not mean the same thing.

## Main results

- identified the `full` OTA container and the differential-package model;
- mapped the nine components in the observed package;
- verified `runtime address = 0x08000000 + file offset` for the main component;
- located the native assistant response limit and built a guarded patch from 299 to 399 visible characters;
- decoded the outer GUI asset container, while the inner `TSCFrameImage` codec remains an active research target.

Always check the [compatibility matrix](status.md) before using a tool.
