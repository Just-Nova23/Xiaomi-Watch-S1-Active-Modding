# Research roadmap

This roadmap records research direction, not promised release dates.

## Working now

- inspect and validate Xiaomi `full` and compact `diff` packages;
- catalog native bitmap and GUI asset records;
- split and byte-perfectly rebuild the outer GUI packet stream;
- locate Thumb references and inspect fixed native constants;
- patch the verified native assistant capacity from 300 to 400 safely.

## Active research

- decode every `TSCFrameImage` packet field;
- export native animations to visible PNG frames;
- implement a byte-stable decoder and a compatible encoder;
- test whether full TSC6A or uncompressed frames can avoid Xiaomi delta coding;
- map more native assistant and watch-action instructions;
- document native application state and UI ownership.

## Later

- replace non-critical native artwork with a reversible device test;
- replace native assistant icons and animations with contributor-provided artwork;
- document boot artwork replacement only after a recovery path is proven;
- investigate a dynamically allocated answer buffer beyond 399 characters;
- build a public compatibility matrix for firmware variants.

## Explicitly not claimed

- a complete custom operating system independent of Xiaomi;
- a universal unbrick method;
- a safe public ready-to-flash image;
- complete understanding of every native application.
