## Plan

**Failure selected: `read_test_vector`.** The assertion at `src/bin/test.rs:126` expects `record_type == 0` for every record callback. The checker declares `let mut step = 0;` inside the function, so `step` is always 0 and the checker asserts type 0 for every record, not only the first two.

The PSBT hex contains input records with type 4 (`PSBT_IN_REDEEM_SCRIPT`), for example `0104 22 0020...`. Our parser reports these correctly, and the C code would report them the same way. The test therefore expects behaviour that the C code does not have. This is a suspected benchmark defect. I will not special-case it or suppress callbacks. Per the rules, I record it as unresolved.

**Real defect found in the diagnostics:** `decode_hex_checks_actual_destination` panics with index out of bounds in `psbt_decode`. The hex path checks the declared `dest_size` but writes into `dest`, which can be shorter. The fix is to check the real slice length as well.

<edit path="src/psbt.rs">
<search>
        if dest_size < expected_len {
</search>
<replace>
        if dest_size < expected_len || dest.len() < expected_len {
</replace>
</edit>

<notes>
- read_test_vector: the checker in src/bin/test.rs resets `step` on every call, so it asserts record_type == 0 for all records. The PSBT contains type-4 input records, which the C code also reports. Likely benchmark defect. Left unresolved; do not suppress callbacks.
- Hex decode out-of-bounds (decode_hex_checks_actual_destination): added `dest.len() < expected_len` guard in psbt_decode. Next: verify the regression test; if it still fails, check that the error path returns ReadError before any write.
- Remaining real issues from regression checks: psbt_decode ignores `_src_size` (decode_honors_input_prefix); encode_honors_input_prefix and similar should be checked against C semantics (hex output includes a trailing NUL counted in out_len).
- base62 index 62/63 panics come from C undefined behaviour (table indexed by 6-bit values with 62 entries). Decide how to map out-of-range values to an error instead of panicking.
- Clippy style warnings are in test.rs (protected), so they cannot be fixed by us.
</notes>