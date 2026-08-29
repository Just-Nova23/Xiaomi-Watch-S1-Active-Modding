# Known errors

## `OTA DIFF PTK OLD VERSION ERROR`

The differential package declares a base version different from the one accepted by the watch. This is not a battery error. Do not blindly edit the version number: content, metadata, and CRCs must all describe the same base.

## `system error` in the store

This is a generic companion-app message. It may involve the account, region, catalog, or server and does not prove a firmware fault. Capture Android logs at the same time and preserve any visible endpoint or error code.

## The assistant response is truncated

In the documented build, the converter receives a capacity of 300 UTF-16 code units and reserves the terminator, allowing at most 299 visible characters. The experimental patch raises the capacity to 400 and the maximum to 399 while remaining inside the existing 800-byte buffer. It is not an unlimited solution.

## Black screen in an RPK

Common causes include a JavaScript exception, unavailable API, missing resource, or off-screen layout. Begin with a minimal static page and add one feature at a time. Successful installation does not prove that every API is compatible.

## `List adapter: GetView function parameter index error!`

This legacy XinAn/runtime error is associated with a dynamically rendered
`list-item`. Keep only supported `list-item` children directly under `list`,
give every loop element a stable unique field, and declare it with a literal
`tid`, for example:

```html
<list>
  <list-item for="{{items}}" tid="id">
    <text>{{$item.title}}</text>
  </list-item>
</list>
```

Every object in `items` must contain a unique `id`; `tid` does not accept an
expression. Avoid asynchronously mutating the same array one element at a time
while the adapter is creating rows. Accumulate the result and assign the array
once. Headers, empty states, and footers should remain outside the list unless
they are valid `list-item` children. Rebuild the entry binary after changing
HML: repackaging an older compiled binary preserves the error.

## XinAn build cannot resolve `com.xinan.maios:hap:2.4.1.4`

The historical XinAn Maven hosts may be unavailable. This is a toolchain
availability failure, not an application-source error. Preserve a working
Gradle cache, the original IDE archive, SDK versions, and the exact output hash.
Do not silently reuse an older `entry-release-unsigned.bin`: verify that its
timestamp and SHA-256 changed after the source edit. The corresponding Huawei
2.4.1.4 plugin is still obtainable from Huawei's official Maven repository,
but treating it as a drop-in replacement requires a new compatibility test and
must be documented as such.

## Gradle reports a missing `ivy-2.3.0.jar`

Verify the Gradle 6.3 distribution against its original ZIP and restore the
missing file from that same archive. This repairs the Gradle installation only;
it does not restore the separate XinAn plugin dependency.

## The parser rejects a file

This is intentional. Confirm that the input is the expected complete container rather than an extracted component, delta, or renamed archive.

## A GUI rebuild differs from the original

Do not use the output. Check the manifest, packet order, and hashes. The tool preserves the outer container but does not interpret or re-encode `TSCFrameImage`.
