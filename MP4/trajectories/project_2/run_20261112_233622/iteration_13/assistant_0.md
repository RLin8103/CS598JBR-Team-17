I'm not changing the translation again. The controller has now sent the same two failures for several iterations, and I haven't found a faithful fix for either.

- **`read_test_vector`**: the protected checker keeps `step` in a local variable, so it is always 0 and asserts `record_type == 0` for every callback. The PSBT's input map contains a type-4 redeem script record, which the C handler also receives. Making this pass would mean suppressing the handler for input records, which the C code does not do.
- **Clippy `style` (2 warnings)**: both are in the protected `src/bin/test.rs`, so I can't fix them.

This edit corrects an inaccurate doc comment on `psbt_read`. It is the only change in this reply.

<edit path="src/psbt.rs">
<search>
/// For testing, we simulate reading by optionally calling the provided callback.
</search>
<replace>/// Parse a serialized PSBT from `src`, invoking `elem_handler` for every record
/// (mirrors the C `psbt_read`). Fails unless the PSBT ends in the finalized state.
</replace>
</edit>

<notes>
- All stubs implemented; no unimplemented!()/todo!() remain. Zero unsafe; every module has #![forbid(unsafe_code)].
- 6/8 tests pass. `read_test_vector` fails in the protected test: its checker keeps `step` as a local (always 0) and asserts `record_type == 0` on every callback. The PSBT's input map has a type-4 record, which the C handler also receives. Suppressing it would be unfaithful, so I'm not special-casing.
- Clippy: 0 in src; the 2 style warnings are in protected src/bin/test.rs.
- Remaining rustc warnings are dead code (unused enum variants and items). Optional cleanup.
- Not declaring done: two tests fail and clippy reports two warnings, all in protected files.
</notes>