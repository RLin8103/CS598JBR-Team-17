The remaining failure is in the test itself, and I can't make it pass without special-casing the test data, so I'm not declaring done.

**Why `read_test_vector` can't pass:** the checker in `src/bin/test.rs` declares `let mut step = 0;` inside the function, so `step` is 0 on every call. The `0 =>` arm then asserts `record_type == 0` for every record it sees. The C checker shares one `step` across calls, so it only asserts for the first two records and never reaches the type-4 redeem script record. The Rust port calls the handler for every record, as `psbt.c` does, so the third record (type 4) trips the assertion. Making it pass would mean skipping the handler or changing record types for this input, which is special-casing. The other 6 tests pass, and the parser matches the C control flow.

Below is a small cleanup in `psbt_read` (removing a redundant `end` binding). It doesn't change behaviour.

<edit path="src/psbt.rs">
<search>    let end = src_size;
    let mut kvs: usize = 0;</search>
<replace>    let mut kvs: usize = 0;</replace>
</edit>
<edit path="src/psbt.rs">
<search>    while psbt.state != PsbtState::Finalized && psbt.write_pos <= end {</search>
<replace>    while psbt.state != PsbtState::Finalized && psbt.write_pos <= src_size {</replace>
</edit>

<notes>
- Tests: 6/8 pass. The only failure is read_test_vector, which is unsatisfiable without special-casing. Its checker (src/bin/test.rs) uses a fresh `step = 0` per call, so it asserts record_type == 0 for every record. The C checker shares `step` and only asserts for the first two records. The third record (PSBT_IN_REDEEM_SCRIPT, type 4) fails the Rust assertion. The handler is called for every record, as in psbt.c. Not special-cased.
- Clippy: the 2 remaining style warnings are in src/bin/test.rs, which I may not edit.
- psbt.rs: psbt_read parses the global unsigned tx via tx_io_counts to drive input/output set counts, as in psbt.c.
- cli.rs: decode -> read (prints records) -> base62 encode, mirroring cli.c. Not a tested target.
- Unsafe: none; tx.rs has #![forbid(unsafe_code)].
- Remaining: rustc warnings only. Needs the controller to decide whether read_test_vector is accepted as a test-spec defect.
</notes>