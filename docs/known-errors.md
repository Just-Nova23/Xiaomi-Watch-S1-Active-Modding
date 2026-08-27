# Known errors

## `OTA DIFF PTK OLD VERSION ERROR`

The differential package declares a base version different from the one accepted by the watch. This is not a battery error. Do not blindly edit the version number: content, metadata, and CRCs must all describe the same base.

## `system error` in the store

This is a generic companion-app message. It may involve the account, region, catalog, or server and does not prove a firmware fault. Capture Android logs at the same time and preserve any visible endpoint or error code.

## The assistant response is truncated

In the documented build, the converter receives a capacity of 300 UTF-16 code units and reserves the terminator, allowing at most 299 visible characters. The experimental patch raises the capacity to 400 and the maximum to 399 while remaining inside the existing 800-byte buffer. It is not an unlimited solution.

## Black screen in an RPK

Common causes include a JavaScript exception, unavailable API, missing resource, or off-screen layout. Begin with a minimal static page and add one feature at a time. Successful installation does not prove that every API is compatible.

## The parser rejects a file

This is intentional. Confirm that the input is the expected complete container rather than an extracted component, delta, or renamed archive.

## A GUI rebuild differs from the original

Do not use the output. Check the manifest, packet order, and hashes. The tool preserves the outer container but does not interpret or re-encode `TSCFrameImage`.
