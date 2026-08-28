# Native system apps

Preinstalled applications are not equivalent to RPK apps. Their UI, strings, and logic can live in the main component and GUI container, while audio, Bluetooth, and peripheral services may depend on other components.

## Meaning of “native app”

In this project, it means a feature compiled and distributed with the firmware. No separate, reinstallable archive has been identified for every system app.

## Where to look

| Element | Likely area | Method |
|---|---|---|
| logic and event handling | main component | strings, cross-references, Thumb disassembly |
| images and animations | GUI component 6 | record catalog and visual comparison |
| audio and prompts | audio resource component | signatures, indexes, version comparison |
| phone connectivity | firmware and companion app | Android logs, traffic, and Bluetooth state |
| independent apps | RPK packages | manifest, JavaScript, and web resources |

## Analysis workflow

1. Reproduce the state on the device and record the exact action.
2. Search visible strings in the firmware.
3. Connect the string, handler, and graphics records using verifiable references.
4. Compare stock and modified files built from the same base version.
5. Change one item in a copy and inspect the diff.

## Current limits

There is no general system for rebuilding every native app. `TSCFrameImage`
files can now be authored, but static bitmap databases and variable-packet
logo/assistant animations use other formats. Specific cases can be documented
and patched; a universal visual editor cannot yet be promised.

## Native and RPK compared

| Property | Native | RPK |
|---|---|---|
| distribution | firmware | installable package |
| privileges | potentially system-level | APIs exposed by the runtime |
| images | native GUI format | usually PNG/JPG |
| modification risk | high; can affect boot or OTA | more isolated and uninstallable |
| microphone/services | possible when implemented by the system | depends on public APIs |

For UI prototypes, RPK is the lower-risk starting point. Deep changes require firmware research and a real recovery path.
