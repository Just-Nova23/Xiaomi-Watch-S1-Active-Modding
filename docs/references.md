# Resource library

This library prioritizes primary documentation, official tool repositories, and clearly identified community work. A source explains its own platform; it does not automatically prove how Xiaomi integrated that technology into this watch.

## Xiaomi/70mai watch application framework

### Essential

- [Development tools](https://xiaomiwatch.70mai.com.cn/en/%E5%BC%80%E5%8F%91%E5%B7%A5%E5%85%B7/) — Windows IDE setup, project creation, build command, signing setup, and RPK output location.
- [Framework specifications](https://xiaomiwatch.70mai.com.cn/en/%E6%A1%86%E6%9E%B6%E8%AF%B4%E6%98%8E/) — file organization, page routes, resource paths, supported syntax, lifecycle, i18n, and media formats.
- [API reference](https://xiaomiwatch.70mai.com.cn/en/%E6%8E%A5%E5%8F%A3/) — system modules, synchronous/asynchronous behavior, callbacks, parameters, and error codes.
- [Component reference](https://xiaomiwatch.70mai.com.cn/%E7%BB%84%E4%BB%B6/) — UI elements, touch/swipe events, images, inputs, lists, and animation components. Some sections are available only on the Chinese-language site.

### How to use these sources

Use them for RPK app behavior. They support claims such as:

- the homepage route is `pages/index/index`;
- application logic lives in `app.js`;
- page lifecycle includes `onInit`, `onReady`, `onShow`, `onHide`, and `onDestroy`;
- ordinary application resources can use PNG/JPEG/BMP under documented API versions;
- system functions are imported through modules such as `@system.app`.

They do **not** document Xiaomi's variable-packet logo/assistant codec, private
assistant privileges, firmware signing chain, or internal inter-processor
transport. The `TSCFrameImage` wrapper itself was reconstructed from firmware
code and public Nema format constants.

## Python and project isolation

- [Python `venv`](https://docs.python.org/3/library/venv.html) — official virtual-environment creation and activation behavior.
- [Python `hashlib`](https://docs.python.org/3/library/hashlib.html) — SHA-256 and other secure hash APIs.
- [Python `zlib`](https://docs.python.org/3/library/zlib.html) — CRC32 implementation used by the package tools.
- [Python `struct`](https://docs.python.org/3/library/struct.html) — explicit byte order and binary field conversion.
- [Python `argparse`](https://docs.python.org/3/library/argparse.html) — command-line parsing used by repository scripts.
- [Python `unittest`](https://docs.python.org/3/library/unittest.html) — synthetic regression tests.

Read binary fields with explicit endianness. A host machine's native byte order should never silently decide package interpretation.

## Git and GitHub

- [Installing Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) — official Git book installation chapter.
- [Git object integrity](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects) — useful background for repository hashes, which are different from firmware SHA-256 identity.
- [GitHub encrypted secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions) — credentials belong in protected settings, never committed files.
- [GitHub Pages](https://docs.github.com/en/pages) — hosting and deployment documentation for this guide.
- [GitHub security advisories](https://docs.github.com/en/code-security/security-advisories) — responsible disclosure workflow for repository tooling issues.

This repository intentionally rejects firmware, packages, keys, and common signing-file extensions in CI.

## Ghidra

- [Official NSA Ghidra repository](https://github.com/NationalSecurityAgency/ghidra) — releases, installation requirements, source, security advisories, and documentation.
- [Ghidra releases](https://github.com/NationalSecurityAgency/ghidra/releases) — obtain official prebuilt archives; do not confuse source archives with release builds.
- [Ghidra beginner guide](https://github.com/NationalSecurityAgency/ghidra/blob/master/GhidraDocs/GhidraClass/Beginner/Introduction_to_Ghidra_Student_Guide.html) — official project training material.
- [Ghidra security advisories](https://github.com/NationalSecurityAgency/ghidra/security/advisories) — check before opening unknown binaries.

For this project, raw-binary import settings and the verified base mapping matter more than decompiler prettiness. See [Ghidra and ARM workflow](ghidra-workflow.md).

## Capstone

- [Capstone official site](https://www.capstone-engine.org/) — project overview and releases.
- [Python tutorial](https://www.capstone-engine.org/lang_python.html) — architecture/mode setup, instruction iteration, detailed operands, and semantic groups.
- [Capstone source repository](https://github.com/capstone-engine/capstone) — code, issues, and version history.

`thumb_xrefs.py` enables detailed ARM operands because literal loads and `MOVW/MOVT` construction cannot be found reliably from mnemonic text alone.

## Rizin

- [Rizin official documentation](https://book.rizin.re/) — command-line analysis concepts and commands.
- [Rizin source repository](https://github.com/rizinorg/rizin) — releases and implementation.
- [Cutter](https://github.com/rizinorg/cutter) — graphical interface built around Rizin.

Rizin and Ghidra are alternative analysis environments. Agreement between independent decoders can strengthen an instruction interpretation, but both can share the same wrong base address if configured identically.

## ARM architecture

- [Arm developer documentation](https://developer.arm.com/documentation) — authoritative architecture manuals and instruction references.
- [Arm Architecture Reference Manual for A-profile architecture](https://developer.arm.com/documentation/ddi0487/latest/) — useful for general instruction semantics; choose the correct profile for the analyzed core.
- [CMSIS documentation](https://arm-software.github.io/CMSIS_6/latest/Core/index.html) — Cortex-M software interface and core concepts.

Do not infer the exact MCU or core revision solely from an instruction that exists in several ARM profiles. Device-specific identification requires independent evidence.

## STM32 secure boot and firmware update

- [ST X-CUBE-SBSFU user manual UM2262](https://www.st.com/resource/en/user_manual/um2262-getting-started-with-the-xcubesbsfu-stm32cube-expansion-package-stmicroelectronics.pdf) — secure boot/update concepts, image authentication, and update flow.
- [X-CUBE-SBSFU data brief](https://www.st.com/resource/en/data_brief/x-cube-sbsfu.pdf) — official package scope and supported STM32 context.

The observed `SFU1` header resembles an SBSFU layout and includes digest/signature-related regions. The ST documents provide format and security context; they do not prove that Xiaomi uses an unmodified reference implementation or identical keys/policies.

## TouchGFX

- [Graphics engine](https://support.touchgfx.com/docs/basic-concepts/graphics-engine) — retained-mode scene model, event collection, scene updates, and rendering loop.
- [Code structure](https://support.touchgfx.com/docs/development/ui-development/software-architecture/code-structure) — generated and user-code boundaries in standard TouchGFX projects.
- [Image widget](https://support.touchgfx.com/docs/development/ui-development/ui-components/images/image) — bitmap association, sizing, alpha, visibility, and performance.
- [Image formats](https://support.touchgfx.com/docs/development/ui-development/touchgfx-engine-features/image-formats) — supported framebuffer and bitmap formats.
- [Image compression](https://support.touchgfx.com/docs/development/ui-development/touchgfx-engine-features/image-compression) — official lossless-compression support and version context.
- [Widgets and containers](https://support.touchgfx.com/docs/development/ui-development/working-with-touchgfx/widgets-and-containers) — UI hierarchy concepts.
- [SVG support](https://support.touchgfx.com/docs/development/ui-development/touchgfx-engine-features/svg) — supported and unsupported vector features in recent TouchGFX versions.

The watch firmware contains TouchGFX-related structures and a bitmap database, but the component-6 animated asset layer is not fully explained by standard TouchGFX documentation.

## Ambiq and texture compression

- [Ambiq Apollo4 Display Kit / Nema GUI Builder guide](https://ambiq.com/wp-content/uploads/2022/04/Apollo4-Display-Kit-NEMA-GUI-Builder-UsersGuide.pdf) — Nema graphics tooling and embedded display workflow.
- [Ambiq Apollo4 Family SDK User's Guide](https://ambiq.com/wp-content/uploads/2022/10/Apollo4-Family-SDK-Users-Guide.pdf) — official SDK context for NemaGFX initialization, memory pools, synchronization, and GPU operation.
- [ST X-CUBE-IMAGE-PROCESSING Nema header](https://github.com/STMicroelectronics/x-cube-image-processing/blob/main/Middleware/NemaGFX/include/nema_graphics.h) — primary source for `NEMA_TSC4 = 0x12`, `NEMA_TSC6 = 0x16`, and `NEMA_TSC6A = 0x17`.
- [ST PixPresso starting guide](https://github.com/STMicroelectronics/x-cube-image-processing/blob/main/Middleware/NemaGFX/doc/Pixpresso_Starting_Guide.pdf) — official command-line formats, fixed rates, and dimension requirements.
- [Think Silicon fixed-rate block-compression patent](https://patents.google.com/patent/US9640149B2/en) — block layout and codec background; patents are specifications, not redistribution licenses.
- [AmbiqSuite TSC framebuffer example](https://github.com/amir1387aht/AmbiqSuite_R4.5.0/tree/main/boards/apollo4b_evb_disp_shield/examples/graphics/nemagfx_tsc_fb) — public raw TSC sample arrays with dimensions supplied by consumer code.

PixPresso and Nema tooling encode the headerless fixed-size texture layer. A
complete Xiaomi `TSCFrameImage` file additionally needs its verified eight-byte
width, height, and frame-count header.

## Documentation diagrams

- [Material for MkDocs diagrams](https://squidfunk.github.io/mkdocs-material/reference/diagrams/) — official Mermaid integration, supported diagram types, instant navigation, and theme behavior.
- [Mermaid flowcharts](https://mermaid.js.org/syntax/flowchart.html) — official syntax and edge semantics.
- [Mermaid sequence diagrams](https://mermaid.js.org/syntax/sequenceDiagram.html) — actor/message timeline syntax.
- [Mermaid state diagrams](https://mermaid.js.org/syntax/stateDiagram.html) — lifecycle/state modeling.

Project diagrams must still be evidence-backed. Rendering a relationship beautifully does not make it true.

## Community research

- [m0tral/UnpackMiColorFace](https://github.com/m0tral/UnpackMiColorFace/) — community tool for Xiaomi watch-face investigation.

Community projects can provide valuable leads, but check license, supported model, version, and reproducibility. Paid or extracted binaries must not be copied into this repository.

## Source evaluation checklist

Before adding a technical reference, ask:

1. Is it the original vendor/project documentation?
2. Which version or date does it describe?
3. Does it describe RPK apps, standard TouchGFX, STM32 SBSFU, or this exact watch integration?
4. Which claim does it support directly?
5. Which part remains an inference?
6. Can another contributor access it without purchasing or redistributing protected material?

When a source conflicts with device evidence, preserve both and document the scope difference rather than silently choosing the more convenient statement.
