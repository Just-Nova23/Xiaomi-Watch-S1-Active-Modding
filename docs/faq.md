# Frequently asked questions

## Can I install custom apps?

Yes, the runtime supports compatible RPK packages. Their capabilities depend on exposed APIs and do not equal native-app privileges.

## Can I recover the source code of every native app?

No. The firmware contains compiled code and resources, not the original source project. Parts of the behavior can be reconstructed through static analysis and version comparison.

## Can I replace logos and animations?

The GUI asset container is partly understood, but there is no complete verified `TSCFrameImage` encoder yet. Replacing bytes without correct encoding can break the UI or boot process.

## Why is there no ready-made firmware download?

For licensing, safety, and compatibility reasons. The repository publishes original tools, documentation, and synthetic tests, not proprietary material or flashable images.

## Does the text patch remove every limit?

No. It uses the full existing buffer and raises the observed safe maximum from 299 to 399 visible characters. A dynamic limit requires a broader architectural change.

## Is this project affiliated with Xiaomi or 70mai?

No. It is independent research maintained by Just-Nova23.

## Can a factory reset recover a brick?

Not necessarily. A reset may repair user data or pairing, but it is not a guaranteed recovery method for firmware that cannot boot.
