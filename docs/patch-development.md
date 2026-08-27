# Patch development

A publishable patch should be small, reproducible, and refuse to operate on the wrong file.

## Recommended cycle

```text
observation → hypothesis → static evidence → synthetic fixture → patch a copy
→ byte-for-byte diff → guarded package → test with recovery available
```

## Safety contract

Every patch should:

1. check the model, version, and preferably SHA-256;
2. verify both the original bytes and a wider context;
3. write to a new file;
4. list every changed offset;
5. produce a JSON report;
6. fail if even one unexpected byte changes;
7. never start an OTA or flash automatically.

## Single change

The documented assistant patch changes one byte in a `mov.w` immediate. This does not make it absolutely safe, but it makes cause and effect measurable.

## Tests without proprietary firmware

The included tests generate synthetic bytes containing the same minimum context. This makes the validation logic public without distributing original firmware.

```bash
python -m unittest discover -s tests -v
```

## Patch manifest

A report should contain at least:

```json
{
  "model": "M2116W1",
  "base_version": "1.4.174",
  "input_sha256": "…",
  "output_sha256": "…",
  "changed_offsets": [1246034],
  "verification": "context matched"
}
```

Do not publish an invented or shortened hash as an operational identifier. If a real hash cannot be shared, explain exactly how users should calculate it.

## Stop conditions

Stop if the context differs, the diff contains unexpected changes, the battery is low, the base version is different, or no verified recovery procedure exists.
