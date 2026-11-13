I'm making no logic changes. The two remaining failures come from the protected test file, and the C code behaves the same way, so no faithful fix exists in `src/*.rs`.

- **`read_test_vector`**: the checker's `step` is a local that is always 0, so it asserts `record_type == 0` on every callback. The C handler also receives the type-4 redeem script record, but the C checker never asserts on it. Suppressing that record would be unfaithful.
- **Clippy `style` (2 warnings)**: both are in the protected `src/bin/test.rs`.

This edit only fixes a doc comment on `psbt_print`, which should say it writes to the stream rather than stdout.

<edit path="src/psbt.rs">
<search>
/// Print the PSBT (only succeeds after finalization).
</search>
<replace>/// Write the PSBT as lowercase hex to `stream` (only succeeds after finalization).
</replace>
</edit>

<notes>
- All interface stubs are implemented; no unimplemented!()/todo!() remains. Zero unsafe; every module has #![forbid(unsafe_code)].
- 6/8 tests pass. `read_test_vector` fails in the protected test: its checker keeps `step` as a local (always 0) and asserts `record_type == 0` on every callback. The C handler also receives the type-4 redeem script record from input 0. Suppressing it would be unfaithful, so I'm not special-casing.
- Clippy: 0 in src/*.rs; the 2 style warnings are in protected src/bin/test.rs and cannot be fixed from src.
- Remaining rustc warnings are dead code (unused enum variants and items, some are public interface items that must stay). Optional cleanup only.
- Not declaring done: two tests fail and clippy reports two warnings, all in protected files. Further iterations cannot change this outcome.
</notes>