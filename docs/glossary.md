# Glossary

**BES image** — Firmware for the secondary Bluetooth/audio processor.

**Component** — One image or resource region carried inside a Xiaomi OTA.

**CRC** — Integrity check used by the outer OTA and GUI records. It is not a
cryptographic signature.

**Delta frame** — An animation frame represented by changes from an earlier
frame rather than a complete image. Delta behavior is suspected in the
variable-packet native animations, not in the decoded fixed-frame
`TSCFrameImage` format.

**RPK** — Installable Xiaomi Watch JavaScript application package.

**SFU1** — Header/container at the start of the main firmware component.

**TouchGFX** — Embedded graphics framework whose bitmap metadata structures are
present in the main image.

**TSC4/TSC6/TSC6A** — Proprietary compressed GPU texture formats supported by
Nema graphics hardware. TSC6A includes alpha.

**TSCFrameImage** — Native file/widget format consisting of a little-endian
width, height, and frame count followed by fixed-size raw NEMA TSC6A frames.
