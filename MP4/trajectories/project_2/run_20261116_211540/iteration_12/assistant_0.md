I'm making one small robustness fix in `src/psbt.rs`. The base64 detection slices the `&str` at byte 5, which panics if the input has a multi-byte character there. Checking the bytes avoids that panic and keeps the same behaviour for valid input. This does not change the `read_test_vector` result, which still depends on the protected test.

<edit path="src/psbt.rs">
<search>    if &src[..b64_magic.len()] == b64_magic {</search>
<replace>    if src.as_bytes().starts_with(b64_magic.as_bytes()) {</replace>
</edit>

<notes>
- read_test_vector still fails. Cause: src/bin/test.rs `checker` resets `step` each call and asserts record_type == 0 for every record (record 3 is type 4). Fixing it needs a test-file change (counter in user_data, or check only the first two records). Protected, so not fixable from src/*.rs.
- Clippy style warnings (uninlined_format_args, single_match) are in src/bin/test.rs; protected.
- Library follows the C code for header, records, tx counting and encodings. Hex and base64 detection are byte-based, so no str slicing panics.
- Remaining work for a human or the controller: the test-file change above. Otherwise no further src/*.rs edits are expected to change results.
</notes>