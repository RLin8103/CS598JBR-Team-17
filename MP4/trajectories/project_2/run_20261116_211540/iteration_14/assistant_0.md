I can't make `read_test_vector` pass from the editable files. The test's `checker` resets `step` to 0 on every call and asserts `record_type == 0` for every record. The vector contains type-4 input records, so a faithful `psbt_read` will always trip that assertion. I am not going to special-case the test data or alter behaviour to satisfy a test that contradicts the C reference, and `src/bin/test.rs` is protected.

No source edit is made in this reply. The library already mirrors the C code for the header, record parsing, transaction counting and the encoders, and it contains no unsafe code.

<notes>
- read_test_vector fails because src/bin/test.rs `checker` resets `step` to 0 on each call and asserts record_type == 0 for every record. The vector's third record is type 4, so a faithful psbt_read cannot pass. Fixing this needs a test-file change (keep the counter in user_data, or check only the first two records). src/bin/test.rs is protected.
- Clippy style warnings (uninlined_format_args, single_match) are in src/bin/test.rs; protected.
- Library is faithful to C for header, records, tx counting and encodings. No unsafe code.
- No further src/*.rs edits will change test results. Awaiting a decision on the test file.
</notes>