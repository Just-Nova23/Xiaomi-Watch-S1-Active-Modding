# Verified concept maps

These maps summarize the project without inventing missing architecture. Each relationship corresponds to a parser rule, verified byte mapping, documented framework rule, or explicit research dependency.

## Evidence production map

```mermaid
flowchart TD
  INPUT[Legally obtained private input] --> ID[Identity record<br/>model · version · size · SHA-256]
  ID --> TOOL[Versioned public tool<br/>repository commit]
  TOOL --> OUTPUT[Sanitized JSON or text report]
  OUTPUT --> CHECK[Independent invariant checks<br/>length · CRC · address · round trip]
  CHECK --> CLAIM{Claim type}
  CLAIM --> O[Observed]
  CLAIM --> R[Reproduced]
  CLAIM --> I[Inferred]
  CLAIM --> H[Hypothesis]
  O --> DOC[Documentation + test]
  R --> DOC
  I --> DOC
  H --> ISSUE[Research issue]
```

The map is also a review rule: a technical claim without an identified input, tool version, output, and check is not ready to be marked observed.

## Artifact ownership map

```mermaid
flowchart LR
  PRIVATE[Private workspace] --> P1[Original firmware/OTA]
  PRIVATE --> P2[Purchased packages]
  PRIVATE --> P3[Extracted components]
  PRIVATE --> P4[Raw captures and device identifiers]

  PUBLIC[Public repository] --> U1[Original parser code]
  PUBLIC --> U2[Synthetic test fixtures]
  PUBLIC --> U3[Offsets and minimal byte context]
  PUBLIC --> U4[Sanitized measurements]
  PUBLIC --> U5[Guides and diagrams]

  PRIVATE -. transform and sanitize .-> PUBLIC
```

There is intentionally no arrow from the public repository back to ready-to-flash firmware. The project teaches reproducible analysis while excluding vendor and purchased binaries.

## Full-package byte layout

```mermaid
flowchart LR
  H[Header<br/>2,487 B] --> C0[C0<br/>3,600,374 B]
  C0 --> C1[C1<br/>20,388,275 B]
  C1 --> C2[C2<br/>40,003,605 B]
  C2 --> C3[C3<br/>22,681,678 B]
  C3 --> C4[C4<br/>250,648 B]
  C4 --> C5[C5<br/>257,336 B]
  C5 --> C6[C6<br/>95,071,184 B]
  C6 --> C7[C7<br/>89,224 B]
  C7 --> C8[C8<br/>2,876,324 B]
```

This is ordered containment from the documented stock package. The diagram is not drawn to scale; use the [component-size chart](research-data.md#full-package-component-sizes) for quantitative comparison.

## Patch trust chain

```mermaid
flowchart TD
  SOURCE[Source component] --> HASH{Known identity?}
  HASH -->|No| REJECT[Reject]
  HASH -->|Yes| CONTEXT{Expected bytes and<br/>surrounding context match?}
  CONTEXT -->|No| REJECT
  CONTEXT -->|Yes| COPY[Create output copy]
  COPY --> CHANGE[Apply minimum change]
  CHANGE --> DIFF{Changed offsets exactly<br/>equal allowlist?}
  DIFF -->|No| REJECT
  DIFF -->|Yes| REPORT[Write hashes and JSON report]
  REPORT --> PACKAGE[Optional package build]
  PACKAGE --> OFFLINE[Reparse and validate offline]
  OFFLINE --> DEVICE{Recovery and test<br/>conditions satisfied?}
  DEVICE -->|No| HOLD[Hold; do not install]
  DEVICE -->|Yes| TEST[Controlled device test]
```

The repository's assistant-capacity patch implements the context, copy, exact-diff, and report stages. It does not automatically package or install anything.

## Firmware research dependency map

```mermaid
flowchart BT
  OTA[Device OTA test] --> PACKAGE[Valid package reconstruction]
  PACKAGE --> COMPONENT[Correct component parser]
  COMPONENT --> FORMAT[Verified outer format]
  PACKAGE --> BOOT[Boot-chain acceptance knowledge]
  PATCH[Behavioral patch] --> CODE[Function and instruction evidence]
  CODE --> MAP[Correct file/runtime mapping]
  CODE --> XREF[Cross-references and control flow]
  OTA --> PATCH
  OTA --> RECOVERY[Recovery planning]
  GRAPHICS[Native asset replacement] --> OUTER[Lossless outer record builder]
  GRAPHICS --> INNER[Working inner decoder/encoder]
  GRAPHICS --> PACKAGE
```

This dependency graph explains why “change a logo” can be harder than changing one numeric instruction: native artwork depends on an unresolved inner codec, while the text-capacity instruction uses a known fixed-width context.

## RPK lifecycle map

The following sequence comes from the public Xiaomi/70mai framework specification.

```mermaid
stateDiagram-v2
  [*] --> Init: onInit
  Init --> Ready: onReady
  Ready --> Visible: onShow
  Visible --> Hidden: onHide
  Hidden --> Visible: onShow after foreground restore
  Hidden --> Destroyed: onDestroy when page exits
  Destroyed --> [*]
```

Opening another page can destroy the earlier page in the documented lightweight runtime; returning may create it again. Persistent state should not rely on a page object surviving navigation.

## Native assistant data structure map

The fields below were reconstructed from instruction behavior around the documented handler. Names describe observed use, not vendor source symbols.

```mermaid
classDiagram
  class AssistantObject {
    +0x2B80 flag_observed
    +0x2B82 text_length_observed
    +0x2B84 flag_observed
    +0x2B86 utf16_buffer_800_bytes
    +0x2EA6 buffer_end
    +0x2EA8 observed_object_extent
  }
  class ConversionCall {
    destination object+0x2B86
    replacement character 0x2A
    capacity stock 300
    capacity patched 400
  }
  ConversionCall --> AssistantObject : writes bounded UTF-16 text
```

The converter reserves a NUL code unit, so capacities 300 and 400 produce at most 299 and 399 visible characters respectively.

## Updating these maps

A map change must include:

1. the exact edge or node being changed;
2. evidence level before and after;
3. command, offset, hash, trace, or official source;
4. alternative explanations considered;
5. documentation and synthetic tests where applicable.

Do not make a map look complete by connecting unknown subsystems. An honest gap is more useful than a polished false relationship.
