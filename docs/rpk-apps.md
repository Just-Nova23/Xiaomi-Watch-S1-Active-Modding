# RPK application development

Third-party applications use Xiaomi's JavaScript quick application framework.
They are separate from native firmware applications and are the safest path for
new watch experiences.

## Typical package contents

Working S1 Active applications commonly contain:

```text
app.js
manifest.json
manifest-watch.json
Common/logo.png
pages or feature directories
entry-release-unsigned.bin
```

The source UI uses JavaScript, HTML-like templates, and CSS. Image components and
frame animations accept PNG/JPG resources. The platform compiler creates the RPK
and its compiled entry binary.

## RPK versus native firmware

| RPK application | Native application |
| --- | --- |
| Installed and removed through Mi Fitness | Compiled into system firmware |
| PNG/JPG source assets | Shared native GUI archive |
| Sandboxed JavaScript APIs | C/C++ system privileges |
| Lower device risk | OTA/boot risk |
| Best for new applications | Best for modifying existing system behavior |

An RPK cannot assume access to microphone streaming, Bluetooth internals, or
system actions merely because a built-in application has those capabilities.
Phone assistance may be required, and available APIs differ by firmware.

## Safe development loop

1. Start from a minimal page and one ordinary PNG icon.
2. Build with the Xiaomi Watch IDE/toolchain available to you.
3. Install through the same Mi Fitness route used for known working RPKs.
4. Verify launch, back gesture, physical buttons, suspend/resume, and uninstall.
5. Add one capability at a time and record the API/firmware requirement.

Do not include third-party sample RPK binaries in this repository. Document
their public source URL or describe the structure instead.
