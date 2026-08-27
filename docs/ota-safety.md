# OTA safety and recovery

## Before any transfer

- charge the watch to at least 40%; 60% or more is preferable;
- keep the phone charged and disable aggressive battery saving for Mi Fitness;
- confirm the exact watch model, installed firmware, OTA model identifier, base
  version, target version, file size, MD5/SHA-256, and all outer CRCs;
- keep an independently verified stock package and recovery notes;
- test parsers and repackers without the watch first;
- change one behavior per experimental package.

## Validation levels

These are separate milestones:

1. package parses;
2. CRCs match;
3. Mi Fitness accepts the file;
4. Bluetooth transfer reaches 100%;
5. the watch validates and installs it;
6. the watch reboots and reconnects;
7. the changed behavior works;
8. unrelated critical behavior still works.

Never report level 3 or 4 as a successful firmware installation.

## If the watch remains on the Xiaomi logo

Do not repeatedly send more experimental packages. Keep it charged, allow a full
boot interval, try the documented hardware restart, and preserve phone/watch
pairing state and logs. Recovery options depend on which boot stage still runs;
there is currently no universal software unbrick procedure in this project.

## Avoid high-risk first tests

Do not begin with:

- bootloader logic;
- boot artwork or early boot resources;
- memory layout or object-size changes;
- power management and charging code;
- updates containing many unrelated modifications.

Prefer a non-critical native constant or secondary visual asset with a known
stock rollback path.
