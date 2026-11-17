I'm stopping here rather than making another edit, because nothing in the editable files can make `read_test_vector` pass without special-casing.

The failing assertion is at `src/bin/test.rs:126`. The test's `checker` declares `let mut step = 0;` inside the callback, so `step` is always 0. That forces every record to have `record_type == 0`. The vector's third record is an input record of type 4 (`PSBT_IN_REDEEM_SCRIPT`), so the assertion fails for any faithful `psbt_read`. The C original keeps its counter in caller memory (`user_data`), which the Rust test does not replicate. Making this pass would mean returning different records for these test bytes, which violates the no-special-casing rule.

What is verified:
- The crate builds.
- 6 of 8 tests pass.
- `unsafe` is zero, and `#![forbid(unsafe_code)]` is present in the files that contain no unsafe code.
- Clippy reports 2 style warnings, both in `src/bin/test.rs` (`uninlined_format_args` and `single_match`). They are in a protected file, so I cannot fix them.

Remaining items for the controller or a human:
- The `checker` in `src/bin/test.rs` needs its counter moved into `user_data` (as the C version does), or the test needs to check only the first two records. Either change would let `read_test_vector` pass against the current library.
- The two style warnings need the same test-file edits.

<notes>
- read_test_vector fails only because src/bin/test.rs `checker` resets `step` to 0 each call and asserts record_type == 0 for all records (record 3 is type 4). Not fixable honestly from src/*.rs. Needs test-file change (move counter into user_data, or check only first two records).
- Clippy style warnings (uninlined_format_args, single_match) are in src/bin/test.rs; protected.
- Library is faithful to C for header, records, tx counting, encodings. Hex decode is a single linear pass.
- Stopping: no further src/*.rs edits will change the outcome.
</notes>