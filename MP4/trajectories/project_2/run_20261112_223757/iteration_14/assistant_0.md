The state has not changed, so I'm still not declaring done. Six of eight tests pass. `read_test_vector` is the only failure, and it cannot pass without special-casing the test data. The checker in `src/bin/test.rs` declares `step` inside the function, so it is 0 on every call, and its `0 =>` arm asserts `record_type == 0` for every record. The second record in `PSBT_HEX` is `PSBT_IN_REDEEM_SCRIPT` (type 4), so that assertion fails. The C checker shares one counter across calls and only checks the first two records.

I need a controller decision on one of these:
1. Accept `read_test_vector` as a test-spec defect and stop.
2. Permit a change to `src/bin/test.rs` (for example, sharing `step` across calls or checking only the first two records, as the C test does).

The edit below only documents the `tx.rs` parser. It makes no behavioural change.

<edit path="src/tx.rs">
<search>/// Walk a serialized transaction, emitting its inputs, outputs and the tx itself.</search>
<replace>/// Walk a serialized transaction (as in tx.c `psbt_btc_tx_parse`), emitting each
/// input, each output and finally the transaction itself. Fails on any truncation
/// or trailing bytes, like the C parser's `parsing fell short` check.</replace>
</edit>

<notes>
- Tests: 6/8 pass. read_test_vector is the only failure and cannot pass without special-casing. The checker in src/bin/test.rs resets `step` per call and asserts record_type == 0 for every record. PSBT_HEX has a type-4 record, which fails that assertion. The C checker shares its counter and never reaches it.
- Decision needed from the controller: accept as a test-spec defect, or permit editing the read-only test file. I will not special-case.
- Clippy: the 2 remaining style warnings are in src/bin/test.rs (read-only).
- psbt.rs: psbt_read counts inputs and outputs from the global unsigned tx via tx_io_counts, as psbt.c does. The handler is called for every record, as psbt.c does.
- cli.rs: decode, read (prints records), base62 encode, mirroring cli.c. Not a tested target.
- Unsafe: none. tx.rs has #![forbid(unsafe_code)].
- Remaining: rustc dead-code and unused warnings (about 11). I have not identified them without fresh compiler output.
</notes>