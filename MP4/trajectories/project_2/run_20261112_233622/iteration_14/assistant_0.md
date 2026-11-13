The two remaining failures cannot be fixed without changing behaviour the C code has, so I'm not making another logic change.

- **`read_test_vector`**: the protected checker's `step` is a local that is always 0, so every callback must have `record_type == 0`. The C code also delivers the type-4 redeem script record from input 0 to its handler. C only checks steps 0 and 1, so it passes. Suppressing the record would be unfaithful, so I'm leaving it failing.
- **Clippy `style` (2 warnings)**: both are in the protected `src/bin/test.rs`, which I cannot edit.

This edit corrects a doc comment on `psbt_encode` that wrongly says only Hex is implemented. All four encodings are implemented.

<edit path="src/psbt.rs">
<search>
/// Encode the PSBT data into a destination buffer using the requested encoding.
/// (Only Hex encoding is implemented for simplicity.)
</search>
<replace>/// Encode the PSBT data into a destination buffer using the requested encoding.
/// Fails with `WriteError` unless the PSBT is finalized.
</replace>
</edit>

<notes>
- All stubs implemented; no unimplemented!()/todo!() remain. Zero unsafe; every module has #![forbid(unsafe_code)].
- 6/8 tests pass. `read_test_vector` fails in the protected test: its checker keeps `step` as a local (always 0) and asserts `record_type == 0` on every callback. The C handler also receives the type-4 redeem script record from input 0, and C's checker never checks it. Making Rust pass would mean suppressing a record the C code delivers, so I'm not doing it.
- Clippy: 0 in src; the 2 style warnings are in protected src/bin/test.rs and cannot be fixed from src/*.rs.
- Remaining rustc warnings are dead code (unused enum variants and items, some of them public interface items). Optional cleanup.
- Not declaring done: two tests fail and clippy reports two warnings, all in protected files.
</notes>