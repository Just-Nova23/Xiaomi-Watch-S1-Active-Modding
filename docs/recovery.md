# Recovery and failure handling

There is currently no public, verified procedure guaranteed to recover every S1 Active brick. This page reduces risk; it does not remove it.

## Before any OTA

- keep both watch and phone comfortably above the minimum battery threshold;
- use a stable Bluetooth connection and disable phone battery restrictions;
- verify the model and exact base version;
- check files and hashes;
- retain a legally obtained original firmware copy;
- change only one component at a time;
- capture logs and note the start time.

## Classify the problem

| Symptom | First cautious action |
|---|---|
| frozen UI but notifications still arrive | wait, document, then try a normal reboot |
| logo remains after an update | do not repeat OTA blindly; preserve logs and version details |
| companion app cannot see the watch | check Bluetooth pairing and account state before repeated resets |
| `OLD VERSION` error | the delta does not match the base; do not force it |
| progress appears frozen | determine whether progress is real or merely stale before interrupting |

## What not to do

- do not send the same package repeatedly hoping for a different result;
- do not change firmware, companion app, and pairing at the same time;
- do not use packages for similar-looking models;
- do not delete logs or original inputs;
- do not present a factory reset as a universal firmware recovery method.

## Useful failure report

Open an issue containing the model, version before and after, package SHA-256 without attaching it, progress percentage, complete error message, timeline, and observable device state. Remove personal identifiers and full Bluetooth details.
