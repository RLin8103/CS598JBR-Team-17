The remaining `read_test_vector` failure is not caused by the implementation. `PSBT_HEX` contains a type-4 input record (`0104 47 52 21 ...`, a redeem script). The C callback tracks `step` through `user_data`, but the Rust test's checker declares `let mut step = 0;` on every call, so it asserts `record_type == 0` for every record. Following C semantics, the handler must receive that type-4 record, so the test can't pass without special-casing. I'm leaving it alone.

The review did find two real divergences from the C code:
1. `psbt_read` never checks `src_size > data_capacity`, which C reports as `PSBT_OOB_WRITE`.
2. The hex decode path and the base64 prefix check slice `&str` by byte index and use `chars().nth()`. Non-ASCII input can panic at a char boundary or on `unwrap()`.

<edit path="src/psbt.rs">
<search>
    // Clear and prepare PSBT for reading</search>
<replace>    if src_size > psbt.data_capacity {
        return PsbtResult::OobWrite;
    }

    // Clear and prepare PSBT for reading</replace>
</edit>
<edit path="src/psbt.rs">
<search>    if &src[..b64_magic.len()] == b64_magic {</search>
<replace>    if src.as_bytes().starts_with(b64_magic.as_bytes()) {</replace>
</edit>
<edit path="src/psbt.rs">
<search>        for (i, c) in src.chars().enumerate() {</search>
<replace>        for (i, &c) in src.as_bytes().iter().enumerate() {</replace>
</edit>
<edit path="src/psbt.rs">
<search>                let c1 = c;</search>
<replace>                let c1 = c as char;</replace>
</edit>
<edit path="src/psbt.rs">
<search>                let c2 = src.chars().nth(i + 1).unwrap();</search>
<replace>                let c2 = src.as_bytes()[i + 1] as char;</replace>
</edit>
<notes>
- read_test_vector: NOT fixable faithfully. PSBT_HEX contains a type-4 input record, and the Rust test's checker resets a local `step`, so it asserts type 0 for every record. Handler semantics match C; leave as is.
- Review fixes applied: OOB check when src_size > capacity; hex decode and base64 prefix check work on bytes (no char-boundary panics).
- Remaining: clippy style warnings are in protected src/bin/test.rs only.
</notes>