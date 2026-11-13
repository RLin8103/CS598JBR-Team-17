This iteration makes one behaviour-preserving cleanup in `psbt_decode`. The hex path walked `chars()`, so a multi-byte UTF-8 character would shift the pairing, while the C code works on bytes. It now iterates over bytes. The `read_test_vector` failure is still the protected checker's `record_type == 0` assertion, so I'm not changing anything for it.

<edit path="src/psbt.rs">
<search>
        for (i, c) in src.chars().enumerate() {
</search>
<replace>        for (i, &c) in src.as_bytes().iter().enumerate() {
</replace>
</edit>
<edit path="src/psbt.rs">
<search>
                let c1 = c;
</search>
<replace>                let c1 = char::from(c);
</replace>
</edit>

<notes>
- All stubs implemented; no unimplemented!()/todo!() remain. Zero unsafe; every module has #![forbid(unsafe_code)].
- 6/8 tests pass. `read_test_vector` fails in the protected src/bin/test.rs: its checker asserts `record_type == 0` for every record (local `step` is always 0), but the PSBT has type-4 input records that the C handler also receives. No faithful fix exists; not special-casing.
- psbt_decode hex path now iterates bytes (matches C byte semantics for non-ASCII input).
- Clippy: 0 in src; the 2 style warnings are in protected test.rs, so the "clippy clean" criterion cannot be met as-is.
- Remaining rustc warnings are dead code (unused enum variants/items); optional cleanup, not in scored clippy categories.
- Recommendation: stop iterating. Further edits cannot change the protected test outcome.
</notes>