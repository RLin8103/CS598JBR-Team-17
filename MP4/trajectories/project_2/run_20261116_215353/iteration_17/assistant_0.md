This review pass found two real problems in `src/psbt.rs`. Both can panic where the C code returns an error:

1. `psbt_decode` slices `src[..5]` to detect the `cHNid` prefix. If the input contains multi-byte UTF-8 with a character boundary at byte 5, that slice panics. A byte-level prefix check fixes it.
2. The hex decode and hex encode paths check the size argument `dest_size`, but then index `dest`. If `dest.len()` is smaller than `dest_size`, they panic. Clamping the capacity to `dest.len()` makes them return an error instead.

The `read_test_vector` failure is still in the protected test (`step` is reset on every callback), so I am not declaring completion.

<edit path="src/psbt.rs">
<search>
    if &src[..b64_magic.len()] == b64_magic {
</search>
<replace>
    if src.as_bytes().starts_with(b64_magic.as_bytes()) {
</replace>
</edit>
<edit path="src/psbt.rs">
<search>
        if dest_size < expected_len {
</search>
<replace>
        if dest_size.min(dest.len()) < expected_len {
</replace>
</edit>
<edit path="src/psbt.rs">
<search>
            if dest_size < psbt_data.len() * 2 + 1 {
</search>
<replace>
            if dest_size.min(dest.len()) < psbt_data.len() * 2 + 1 {
</replace>
</edit>

<notes>
- Blocker (unchanged): read_test_vector fails because the protected test in src/bin/test.rs declares `let mut step = 0;` inside the callback, so it asserts record_type==0 on every record. The second record in PSBT_HEX is a type-4 input record, which the C reader also delivers (C keeps its counter in user_data). Fixing this needs a change to src/bin/test.rs, which I cannot edit. Do not special-case, do not declare done.
- Review round 17: fixed a panic in psbt_decode prefix check (non-char-boundary slice), and clamped hex decode/encode destination checks to dest.len() so dest indexing cannot panic.
- Reviewed and matching C: psbt_read header, record parsing and bounds, kvs/count logic, OobWrite on oversized src; compactsize read/write/length; base64/base62 encode and decode (count, capacity, padding); tx parse bounds and fell-short check; write_record and close_records capacity checks.
- Clippy style warnings (uninlined format args, single_match) are in src/bin/test.rs (protected).
- Open, low priority: about 12 rustc warnings (dead code / unused imports) not triaged.
</notes>