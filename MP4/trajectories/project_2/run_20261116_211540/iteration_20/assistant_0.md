I'm stopping here rather than making another edit, because nothing in `src/*.rs` can make `read_test_vector` pass honestly.

The failing assertion is at `src/bin/test.rs:126`. The checker there resets `step` to 0 on every call and asserts `record_type == 0` for every record. The test vector's third record is an input record of type 4 (`PSBT_IN_REDEEM_SCRIPT`), and the C reference also delivers it to the handler. Any faithful `psbt_read` will fail that assertion. The only ways to get green are to special-case the test data or to stop delivering records, and both break the "implement the C behaviour" goal.

The two Clippy `style` warnings are also in `src/bin/test.rs` (`uninlined_format_args` at line 6, `single_match` at line 123), so they are outside my editable area as well.

Everything else is in place: the crate builds, 6 of 8 tests pass, the library mirrors the C code for the header, record parsing, transaction counting, encodings and the state machine, and there is no `unsafe` code.

To finish, the test file needs one of these changes (a human or the controller must make it):
- keep the step counter in `user_data` so it persists across calls, or
- check only the first two records, as the C `read_test_vector_checker` does.

With either change, the `read_test_vector` assertion should pass and the two Clippy warnings should be fixed by `print!("{byte:02x}")` and an `if let` in the test file.

<notes>
- read_test_vector fails only because src/bin/test.rs `checker` resets `step` to 0 on each call and asserts record_type == 0 for every record; record 3 is type 4. A faithful psbt_read cannot pass this without special-casing. Fix needs a test-file change (persist counter in user_data, or check only the first two records). src/bin/test.rs is protected.
- Clippy style warnings (uninlined_format_args line 6, single_match line 123) are in src/bin/test.rs; protected.
- Library follows C for header, records, tx counting, encodings, state machine. No unsafe code.
- Not declaring completion: tests and clippy are not clean until the test file changes.
- No further src/*.rs edits planned.
</notes>