I'm stopping here rather than making another no-op edit. The remaining failure is not a library bug.

`read_test_vector` in `src/bin/test.rs` has a checker that resets `step` to 0 on every call and asserts `record_type == 0` for every record. The vector's third record is a type-4 input record (`PSBT_IN_REDEEM_SCRIPT`), and the C reference would deliver it to the handler too, so no faithful `psbt_read` can satisfy that assertion. Making it pass would mean special-casing the input or changing the library's record semantics away from the C code, and I won't do that.

The library is otherwise in the state the C code defines: header parsing, record parsing with the C checks, transaction counting, hex/base64/base62 encodings, and the state machine all follow `psbt.c`. There is no `unsafe` code, and no interface signatures have changed.

The two outstanding items both need a decision outside `src/*.rs`:
1. `src/bin/test.rs` needs its checker fixed. Either keep the step counter in `user_data` so it persists across calls, or check only the first two records as the C test does.
2. The two clippy `style` warnings (`uninlined_format_args` at line 6 and `single_match` at line 123) are also in `src/bin/test.rs`.

Once the test file is corrected, the rest of the suite already passes and I expect `read_test_vector` to pass too. I'm not declaring completion, because the test suite and clippy are not clean yet.

<notes>
- read_test_vector fails only because src/bin/test.rs `checker` resets `step` to 0 each call and asserts record_type == 0 for all records; record 3 is type 4. Needs a test-file change (persist counter in user_data, or check only the first two records). Protected.
- Clippy style warnings (uninlined_format_args line 6, single_match line 123) are in src/bin/test.rs; protected.
- Library follows C for header, records, tx counting, encodings, state machine. No unsafe code.
- No further src/*.rs edits expected to change results. Awaiting test-file decision.
</notes>