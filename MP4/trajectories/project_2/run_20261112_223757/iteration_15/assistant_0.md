The state is unchanged: 6 of 8 tests pass, and `read_test_vector` is the only failure. I can't make it pass without special-casing. Its checker (`src/bin/test.rs`) asserts `record_type == 0` for every record, and the second record in `PSBT_HEX` is a type-4 redeem script. The C checker never reaches that assertion because it shares one counter and checks only the first two records. I need a controller decision: accept this as a test-spec defect, or allow a change to the read-only checker, for example sharing `step` across calls.

This edit corrects an inaccurate doc comment on `psbt_decode`. It claims the function uses the `hex` crate, which it doesn't. There is no behaviour change.

<edit path="src/psbt.rs">
<search>/// Decode a hex string into dest. (This simple implementation uses the `hex` crate.)</search>
<replace>/// Decode a PSBT string into `dest`. Strings starting with the base64 magic `cHNid`
/// are base64-decoded; anything else is parsed as hex, as in psbt.c `psbt_decode`.</replace>
</edit>

<notes>
- Tests: 6/8 pass. read_test_vector is the only failure and cannot pass without special-casing. The checker in src/bin/test.rs resets `step` per call and asserts record_type == 0 for every record. PSBT_HEX has a type-4 record, which fails that assertion. The C checker shares its counter and never reaches it.
- Decision needed from the controller: accept as a test-spec defect, or permit editing the read-only test file. I will not special-case.
- Clippy: the 2 remaining style warnings are in src/bin/test.rs (read-only).
- psbt.rs: psbt_read counts inputs and outputs from the global unsigned tx via tx_io_counts, as psbt.c does. The handler is called for every record, as psbt.c does.
- cli.rs: decode, read (prints records), base62 encode, mirroring cli.c. Not a tested target.
- Unsafe: none. tx.rs has #![forbid(unsafe_code)].
- Remaining: about 11 rustc dead-code and unused warnings. I still need fresh compiler output to locate them.
</notes>