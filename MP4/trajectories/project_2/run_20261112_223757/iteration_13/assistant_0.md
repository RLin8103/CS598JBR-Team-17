I'm still not declaring done. The state is unchanged: 6 of 8 tests pass, and `read_test_vector` is the only failure. Nothing in the crate can make it pass without special-casing the test data, so this needs a controller decision. Either accept it as a test-spec defect, or allow a change to the read-only checker in `src/bin/test.rs`. Its `step` counter is local to each call, and its `0 =>` arm asserts `record_type == 0` for every record, including the type-4 redeem-script record.

This edit only corrects a misleading doc comment on `psbt_read`, which describes a "simulated" read. The function is a real parser.

<edit path="src/psbt.rs">
<search>/// For testing, we simulate reading by optionally calling the provided callback.</search>
<replace>/// Parse a PSBT from `src[..src_size]`, calling `elem_handler` for every record.</replace>
</edit>

<notes>
- Tests: 6/8 pass. read_test_vector is the only failure and cannot pass without special-casing. The checker in src/bin/test.rs resets `step` per call and asserts record_type == 0 for every record. PSBT_HEX has a type-4 record, which fails that assertion. The C checker shares its counter and never reaches it.
- Decision needed from the controller: accept as a test-spec defect, or permit editing the read-only test file. I will not special-case.
- Clippy: the 2 remaining style warnings are in src/bin/test.rs (read-only).
- psbt.rs: psbt_read counts inputs and outputs from the global unsigned tx via tx_io_counts, as psbt.c does. The handler is called for every record, as psbt.c does. The hex decoder indexes bytes directly.
- cli.rs: decode, read (prints records), base62 encode, mirroring cli.c. Not a tested target.
- Unsafe: none. tx.rs has #![forbid(unsafe_code)].
- Remaining: rustc dead-code and unused warnings only (about 11).
</notes>