The `read_test_vector` failure is still in the protected test, not the reader. Its `checker` declares `let mut step = 0;` inside the callback, so it asserts `record_type == 0` on every record. The C test only checks the first two callbacks, using a counter kept in `user_data`. `PSBT_HEX` contains type-4 input records later on, which the C reader also delivers, so the Rust assertion fails there. Fixing this would require editing `src/bin/test.rs`, which is protected. I won't special-case the data, so I'm not declaring completion.

This turn makes one cosmetic edit. The comment in `psbt_read` was stale and misleading.

<edit path="src/psbt.rs">
<search>
    // Copy source data into psbt.data (up to src_size or src.len())
</search>
<replace>
    // Copy the first `src_size` bytes (or fewer, if `src` is shorter) into psbt.data.
</replace>
</edit>

<notes>
- Blocker (unchanged): read_test_vector fails because the protected test in src/bin/test.rs declares `let mut step = 0;` inside the callback, so every record is asserted to have record_type==0. The C test checks only callbacks 0 and 1 via a counter in user_data. PSBT_HEX has type-4 input records later on, which the reader correctly delivers. Fixing this needs a change to src/bin/test.rs (protected). Do not special-case, do not declare done.
- Review rounds 17-18: fixed the psbt_decode prefix panic (byte-level starts_with), clamped hex decode/encode destination checks to dest.len(). Reader, compactsize, base64/base62, tx parse and write paths reviewed against C with no further differences found.
- Clippy style warnings (uninlined format args, single_match) are in src/bin/test.rs (protected).
- Open, low priority: about 12 rustc warnings (dead code / unused items such as PsbtElemType and the TxElem variant) not triaged.
- If the test file is ever fixed, rerun the suite and confirm 8/8, then declare done.
</notes>