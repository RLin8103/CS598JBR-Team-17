The remaining `read_test_vector` failure is still a test bug. Its `checker` uses a fresh local `step` that is always 0, so it asserts `record_type == 0` for every callback. `PSBT_HEX` contains type-4 input records, and the C reader must deliver them. The test can only pass by skipping records or special-casing, so I won't do either, and I'm not declaring completion.

This turn I'm adding a real C-behaviour check I had missed. `psbt_read` in C returns `PSBT_OOB_WRITE` when `src_size > tx->data_capacity`, and the Rust port ignored that. The existing tests all pass a size within capacity, so this doesn't change their results.

<edit path="src/psbt.rs">
<search>
    // Copy source data into psbt.data (up to src_size or src.len())
</search>
<replace>
    // C: reading more bytes than the psbt buffer can hold is an out-of-bounds write.
    if src_size > psbt.data_capacity {
        return PsbtResult::OobWrite;
    }

    // Copy source data into psbt.data (up to src_size or src.len())
</replace>
</edit>

<notes>
- read_test_vector: test bug. Its checker uses a fresh local `step`, so it asserts record_type==0 for every callback, but PSBT_HEX has type-4 input records that the C reader must deliver. Not passable without special-casing; do not special-case. Report it and do not declare done.
- Done: hex decode rejects non-ASCII (no panic). psbt_read now returns OobWrite when src_size > data_capacity, as C does.
- Known perf nit: hex decode uses chars().nth (quadratic); behaviour is correct.
- Clippy style warnings live in src/bin/test.rs (protected), so they cannot be cleared from our side.
</notes>