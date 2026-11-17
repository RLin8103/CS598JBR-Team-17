The remaining failure is still in the protected test, not in the translation. `read_test_vector`'s `checker` creates a fresh local `step` on every call, so it always asserts `record_type == 0`. The C test keeps its counter through `user_data`, and the C reader delivers the type-4 input records in `PSBT_HEX`, so the Rust reader has to deliver them too. Skipping those records or special-casing the input would make the test pass without matching the C behaviour, so I won't do either. I can't declare completion while this test fails.

This turn only fixes a misleading doc comment on `psbt_decode`, which claimed the `hex` crate is used. The function is a hand-written hex and base64 decoder.

<edit path="src/psbt.rs">
<search>
/// Decode a hex string into dest. (This simple implementation uses the `hex` crate.)
</search>
<replace>
/// Decode a base64 (`cHNid` prefix) or hex encoded PSBT string into `dest`.
/// Mirrors C `psbt_decode`: base64 is detected by its magic prefix, otherwise hex is assumed.
</replace>
</edit>

<notes>
- Blocker (unchanged for several iterations): read_test_vector fails because the protected test in src/bin/test.rs uses a fresh local `step` per callback, so it asserts record_type==0 on every record. PSBT_HEX contains type-4 input records that the C reader delivers (C keeps its counter in user_data). Fixing this needs a change to src/bin/test.rs, which is protected. Do not special-case, do not declare done.
- Reader matches C on header parsing, record bounds checks, OobWrite on oversized src, non-ASCII hex rejection, byte-indexed hex decode, and base64 decode (count, capacity, padding, break).
- Clippy style warnings (uninlined format args, single_match) are in src/bin/test.rs (protected).
- Open, low priority: rustc warnings (about 12) not yet triaged; hex decode loop could use chunks_exact for clarity.
</notes>