# Contributing research

The project is maintained on [Just-Nova23's](https://github.com/Just-Nova23) personal profile, and welcomes reproducible results, corrections, and new tools.

## Useful ways to participate

- reproduce a parser result on another version;
- document offsets and hashes without uploading the binary;
- create synthetic fixtures for a format;
- compare two versions of the same region;
- improve translations, diagrams, and examples;
- investigate the `TSCFrameImage` payload;
- flag conclusions that are not sufficiently supported.

## Evidence levels

Use one of these labels in your pull request:

- **Observed:** directly acquired bytes, output, or behavior.
- **Reproduced:** independently observed at least twice.
- **Inferred:** an explanation consistent with several observations.
- **Hypothesis:** a useful direction that still needs verification.

## Experiment template

```markdown
## Objective

## Environment
- model:
- firmware version:
- operating system and Python version:

## Input
- descriptive name:
- SHA-256:

## Procedure
1.

## Observed result

## Expected result

## Shareable artifacts
- sanitized log:
- synthetic fixture:

## Uncertainties
```

## Prohibited data

Do not upload firmware, proprietary OTA packages, extracted apps, keys, certificates, tokens, dumps containing personal data, or purchased material. Read the [contribution policy](https://github.com/Just-Nova23/Xiaomi-Watch-S1-Active-Modding/blob/main/CONTRIBUTING.md) and [security policy](https://github.com/Just-Nova23/Xiaomi-Watch-S1-Active-Modding/blob/main/SECURITY.md).

## Pull requests

Keep each PR focused on one subject. Update documentation and tests in the same change. New parsers should preserve unproven fields as `unknown_*` rather than assigning speculative names.
