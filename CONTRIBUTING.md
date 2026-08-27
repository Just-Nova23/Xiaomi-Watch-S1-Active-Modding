# Contributing

Contributions are welcome from developers, reverse engineers, designers,
translators, testers, and technical writers.

This project is maintained from the personal GitHub profile of
[Just-Nova23](https://github.com/Just-Nova23).

## Good first contributions

- reproduce a documented parser result on your own legally obtained firmware;
- improve a guide or translate documentation;
- add tests built from synthetic data;
- identify a native function and provide address, bytes, disassembly, and a
  reproducible explanation;
- document an RPK API or working application pattern;
- analyze one `TSCFrameImage` packet without uploading its copyrighted payload.

## Evidence standard

Every technical claim should say which of these states it is in:

- **Verified on device** — observed on a real Xiaomi Watch S1 Active;
- **Verified offline** — reproduced from local binaries or generated fixtures;
- **Inferred** — supported by evidence but not yet proven;
- **Unknown** — deliberately not guessed.

Include model, firmware version, component index, file offset, runtime address,
original bytes, changed bytes, commands used, and the expected result whenever
they are relevant. Remove device identifiers and personal data.

## Never upload

- Xiaomi or third-party firmware images and OTA packages;
- modified or original Mi Fitness APKs;
- paid m0tral packages or other purchased files;
- private keys, keystores, certificates, API tokens, `.env` files;
- Bluetooth MAC addresses, account IDs, logs containing personal data;
- binaries copied from proprietary SDKs.

Small hexadecimal excerpts needed to describe a patch are acceptable when they
are limited to the minimum required for interoperability and review.

## Development workflow

1. Fork the repository and create a focused branch.
2. Keep firmware outside the repository; the `.gitignore` blocks common binary
   extensions as a second line of defense.
3. Run `python -m unittest discover -s tests -v`.
4. Run `python -m compileall -q tools tests`.
5. Update the relevant documentation when behavior changes.
6. Open a pull request explaining evidence, risk, and validation status.

Do not describe a patch as safe merely because it builds. Device verification
and a recovery plan are separate requirements.
