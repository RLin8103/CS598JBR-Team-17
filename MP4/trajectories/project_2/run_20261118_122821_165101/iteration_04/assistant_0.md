The remaining `read_test_vector` failure looks like a benchmark defect. The checker asserts `record_type == 0` for every record, including the input and output records that the C test vector also contains. Per the rules I won't special-case it, so I'm leaving it as an unresolved failure.

For `errors_include_useful_context`, `psbt_geterr` returns a constant, while the C code records the last error message. I'll add a process-wide last-error slot (a `Mutex<&'static str>`, which is const-constructible, so no unsafe is needed). `psbt_encode` will record C's "not in finalized state" message, and `psbt_geterr` will return the last one. This matches the C behaviour for that path. I haven't seen the test's exact expected substring, so this may still not pass.

<edit path="src/psbt.rs">
<search>
        return PsbtResult::WriteError;
</search>
<replace>        set_last_error("psbt_encode: psbt not in finalized state. use psbt_read to parse an existing psbt, or the psbt_write functions to create one.");
        return PsbtResult::WriteError;
</replace>
</edit>
<edit path="src/psbt.rs">
<search>
pub fn psbt_geterr() -> &'static str {
    PSBT_ERRMSG
}
</search>
<replace>pub fn psbt_geterr() -> &'static str {
    LAST_ERROR.lock().map(|g| *g).unwrap_or(PSBT_ERRMSG)
}

/// Process-wide last error message, mirroring the C `psbt_errmsg` global.
static LAST_ERROR: std::sync::Mutex<&'static str> = std::sync::Mutex::new(PSBT_ERRMSG);

fn set_last_error(msg: &'static str) {
    if let Ok(mut guard) = LAST_ERROR.lock() {
        *guard = msg;
    }
}
</replace>
</edit>

<notes>
- Iteration 4 follow-up: added a Mutex-backed last-error slot (LAST_ERROR) so psbt_geterr reflects the most recent failure, as in C. Currently only psbt_encode sets it; other error sites should call set_last_error with C's message text if tests need them.
- read_test_vector: suspected benchmark defect (checker asserts record_type==0 for all records, but the C vector has input/output records too). Unresolved; not special-casing.
- Still to verify: encode/decode declared-length tests, base64 decode dest limit.
- Clippy style warnings are in protected src/bin/test.rs; cannot be fixed from our files.
</notes>