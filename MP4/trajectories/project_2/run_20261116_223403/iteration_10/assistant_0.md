No further divergences from the C code turned up in this review round, so I'm not making any edits.

The one remaining test failure is `read_test_vector`. `PSBT_HEX` contains a type-4 input record, and the test's checker declares `let mut step = 0;` on every call, so it asserts `record_type == 0` for every record. Following the C semantics, the handler has to receive that record. Making the test pass would mean suppressing or altering callbacks for particular records, which is special-casing, so I'm leaving it as is.

The earlier review fixes hold up on re-reading: the `src_size > data_capacity` check, and byte-based hex decoding with no `&str` char-boundary slicing. Every index in `psbt_read` and `read_record` is guarded by a length check, and the remaining clippy style warnings are in the protected `src/bin/test.rs`.

<done/>

<notes>
- read_test_vector fails only because the protected test's checker resets a local `step` and asserts record_type 0 for every record. PSBT_HEX has a type-4 input record, which C also passes to the handler. Not fixable without special-casing; leave as is.
- Review complete: src_size/capacity check, byte-based hex decode and base64 prefix check, bounds guards in psbt_read/read_record verified.
- Only remaining clippy style warnings are in protected src/bin/test.rs.
</notes>