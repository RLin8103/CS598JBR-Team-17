This iteration makes no logic change. The last edit (forwarding transaction elements to the handler) has not been compiled yet, and the controller feedback shows no compile errors. I'm only updating the `psbt_read` doc comment so it mentions the transaction-element callbacks.

The remaining failure is in the protected `src/bin/test.rs`. Its checker keeps `step` as a local that is always 0, so it asserts `record_type == 0` on the type-4 input record that the C handler also receives. I'm not special-casing that.

<edit path="src/psbt.rs">
<search>
/// Parse a serialized PSBT from `src`, invoking `elem_handler` for every record
/// (mirrors the C `psbt_read`). Fails unless the PSBT ends in the finalized state.
</search>
<replace>/// Parse a serialized PSBT from `src`, invoking `elem_handler` for every record
/// and for every transaction element (TXIN/TXOUT/TX) of the global unsigned tx
/// (mirrors the C `psbt_read` with its `tx_counter` forwarding). Fails unless the
/// PSBT ends in the finalized state.
</replace>
</edit>

<notes>
- All interface stubs implemented; no unimplemented!()/todo!() remains. Zero unsafe; every module has #![forbid(unsafe_code)].
- psbt_read forwards TXIN/TXOUT/TX elements to the handler as PsbtElem::TxElem and derives counts from the same parse (tx_elements in tx.rs). Compile status of that change is still unconfirmed by the controller output; check build first if it fails.
- 6/8 tests pass. read_test_vector fails in the protected test: its checker keeps `step` as a local (always 0) and asserts record_type == 0 on every Record callback. The C handler also receives the type-4 input record, so no faithful fix exists. Not special-casing.
- Clippy: 0 in src/*.rs; the 2 style warnings are in protected src/bin/test.rs.
- Not declaring done: two tests fail and clippy reports two warnings, all in protected files.
</notes>