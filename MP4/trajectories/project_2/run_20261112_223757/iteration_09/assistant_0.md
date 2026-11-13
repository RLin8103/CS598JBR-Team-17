The remaining failure is the test's `read_test_vector` checker, which I can't satisfy faithfully. It starts `step` at 0 on every call and asserts `record_type == 0` for every record. The third record in the PSBT is `PSBT_IN_REDEEM_SCRIPT` (type 4), so the assertion fails there. The C handler is called for every record, and so is the Rust one, so the parser is correct and I won't special-case the test. I'm also making a small cleanup in `psbt_read` (removing the stray blank lines in the Global/Inputs/Outputs branch).

<edit path="src/psbt.rs">
<search>            PsbtState::Global | PsbtState::Inputs | PsbtState::Outputs => {

                
                // Bytes past the end</search>
<replace>            PsbtState::Global | PsbtState::Inputs | PsbtState::Outputs => {
                // Bytes past the end</replace>
</edit>
<notes>
- Tests: 6/8 pass. The only failure is read_test_vector. Its checker (src/bin/test.rs) starts `step` at 0 on every call and asserts record_type == 0 for every record. The third record in PSBT_HEX is PSBT_IN_REDEEM_SCRIPT (type 4), so the assertion fails. The C handler is called for every record, as in psbt.c. Fixing this would mean special-casing test data, so it is a test-spec defect. Not special-cased.
- Clippy: the 2 remaining style warnings are in src/bin/test.rs (not editable).
- psbt.rs: psbt_read parses the global unsigned tx via tx.rs (tx_io_counts) to drive input/output set counts, as in psbt.c.
- cli.rs: decode -> read (prints records) -> base62 encode, mirroring cli.c. Not a tested target.
- Unsafe: none in any file; tx.rs has #![forbid(unsafe_code)].
- Remaining: rustc dead-code/unused warnings only. No logic TODOs.
</notes>

<done/>