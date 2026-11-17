The only change I can make safely in `src/psbt.rs` is removing a redundant state check after the loop. The state is already `Finalized` at that point, so behaviour is identical. This does not affect `read_test_vector`, which still cannot pass without changing the protected test.

<edit path="src/psbt.rs">
<search>    if psbt.state == PsbtState::Finalized && psbt.write_pos < actual_size && psbt.data[psbt.write_pos] != 0 {</search>
<replace>    if psbt.write_pos < actual_size && psbt.data[psbt.write_pos] != 0 {</replace>
</edit>

<notes>
- read_test_vector fails because src/bin/test.rs `checker` resets `step` to 0 on every call and asserts record_type == 0 for all records. Record 3 is type 4, so any faithful psbt_read fails. Only a test-file change fixes it (counter in user_data, or check only the first two records). src/bin/test.rs is protected.
- Clippy style warnings (uninlined_format_args, single_match) are in src/bin/test.rs; protected.
- Library follows the C code for header, records, tx counting, encodings. No unsafe code.
- No further src/*.rs changes are expected to change test results. Needs a human or controller decision on the test file.
</notes>