I'm not declaring done. The only failing test is `read_test_vector`, and I can't make it pass without special-casing test data.

**Why it fails:** the checker in `src/bin/test.rs` declares `let mut step = 0;` inside the function, so `step` is 0 on every call. Its `0 =>` arm asserts `record_type == 0` for every record. The record that fails has type 4 (`PSBT_IN_REDEEM_SCRIPT`). The C checker shares one counter across calls and only checks the first two records, so the Rust port is not the cause. `psbt_read` calls the handler for every record, as `psbt.c` does, and the parser output is correct for the other six tests.

Making this pass would require skipping the handler for some records or changing record types, which is special-casing. I've left the logic unchanged. The edit below only adds a comment documenting the handler call.

<edit path="src/psbt.rs">
<search>                    if let Some(ref mut handler) = elem_handler {</search>
<replace>                    // Like psbt.c, the handler sees every record. The test checker in
                    // src/bin/test.rs asserts type 0 for all records, which the type-4
                    // redeem-script record in PSBT_HEX violates (test-spec defect).
                    if let Some(ref mut handler) = elem_handler {</replace>
</edit>

<notes>
- Tests: 6/8 pass. read_test_vector is the only failure and cannot pass without special-casing. The test checker (src/bin/test.rs) resets `step` per call and asserts record_type == 0 for every record. PSBT_HEX contains a type-4 record, which fails that assertion. The C checker shares its counter and does not reach it. Needs a controller decision: accept as a test-spec defect, or permit editing the read-only test.
- Clippy: the 2 remaining style warnings are in src/bin/test.rs, which is read-only.
- psbt.rs: psbt_read counts inputs and outputs from the global unsigned tx (tx_io_counts), as psbt.c does. The hex decoder indexes bytes directly.
- cli.rs: decode, read (prints records), base62 encode, mirroring cli.c. Not a tested target.
- Unsafe: none. tx.rs has #![forbid(unsafe_code)].
- Remaining: rustc dead-code and unused warnings only.
</notes>