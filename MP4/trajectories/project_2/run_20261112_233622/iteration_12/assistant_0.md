I re-checked the failing assertion against the C test and found no translation bug. The Rust test's checker keeps its `step` in a local variable, so it is always 0, and it asserts `record_type == 0` on every callback. The PSBT's input 0 map has a type-4 redeem script record after its non-witness UTXO record (type 0). The C checker only checks steps 0 and 1, so it passes. The Rust checker reaches that type-4 record and fails. Passing would require skipping the handler for input records, which the C code does not do, so I'm leaving the behaviour as it is.

This edit only corrects an inaccurate doc comment on `psbt_decode`.

<edit path="src/psbt.rs">
<search>
/// Decode a hex string into dest. (This simple implementation uses the `hex` crate.)
</search>
<replace>/// Decode a hex (or base64, when prefixed with "cHNid") PSBT string into `dest`.
/// Mirrors the C `psbt_decode`: base64 is detected by its magic prefix, otherwise hex is assumed.
</replace>
</edit>

<notes>
- All stubs implemented; no unimplemented!()/todo!() remain. Zero unsafe; every module has #![forbid(unsafe_code)].
- 6/8 tests pass. `read_test_vector` fails in the protected test: its checker keeps `step` in a local variable (always 0) and asserts `record_type == 0` on every callback. The PSBT's input 0 map contains a type-4 redeem script record, which the C handler also receives. The C checker only checks steps 0 and 1, so C passes and Rust does not. Passing would require suppressing the handler, which is not faithful. Not special-casing.
- Clippy: 0 in src; the 2 style warnings are in protected src/bin/test.rs, so the clippy criterion cannot be met as-is.
- Remaining rustc warnings are dead code (unused enum variants and items); optional cleanup.
- Not declaring done: two tests fail and clippy reports two warnings, both in protected files.
</notes>