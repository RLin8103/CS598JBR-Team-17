The `read_test_vector` failure is still caused by the protected test, not the reader. Its `checker` declares `let mut step = 0;` inside the callback, so it asserts `record_type == 0` on every record. The C test keeps its counter through `user_data`. The reader correctly delivers the second record in `PSBT_HEX`, which is a type-4 input record, so that assertion fails. Filtering that record out or special-casing the input would not match the C behaviour. I can't fix this from `src/*.rs`, so I'm not declaring completion.

This turn makes one behaviour-preserving cleanup: `hex_to_val` now uses `char::to_digit(16)`, which accepts exactly the ASCII hex digits the old code accepted.

<edit path="src/psbt.rs">
<search>
fn hex_to_val(c: char) -> u8 {
    if c.is_ascii_digit() {
        c as u8 - b'0'
    } else if ('a'..='f').contains(&c) {
        c as u8 - b'a' + 10
    } else if ('A'..='F').contains(&c) {
        c as u8 - b'A' + 10
    } else {
        0x80
    }
}
</search>
<replace>
/// Value of an ASCII hex digit, or 0x80 when `c` is not a hex digit.
fn hex_to_val(c: char) -> u8 {
    c.to_digit(16).map_or(0x80, |d| d as u8)
}
</replace>
</edit>

<notes>
- Blocker (unchanged for many iterations): read_test_vector fails because the protected test in src/bin/test.rs declares `let mut step = 0;` inside the callback, so it asserts record_type==0 on every record. The second record in PSBT_HEX is a type-4 input record, which the C reader also delivers (the C test keeps its counter in user_data). Fixing this needs a change to src/bin/test.rs, which I cannot edit. Do not special-case, do not declare done.
- Reader matches C on header parsing, record bounds checks, OobWrite on oversized src, non-ASCII hex rejection, hex decode, base64 decode, and base64/base62 encode.
- Clippy style warnings (uninlined format args, single_match) are in src/bin/test.rs (protected).
- Open, low priority: about 12 rustc warnings (dead code / unused items) not triaged; the hex decode loop could use chunks_exact.
- Next step if the test file is ever changed: rerun the suite and confirm 8/8.
</notes>