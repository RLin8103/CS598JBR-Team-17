The `read_test_vector` failure is still caused by the protected test, not the reader. Its `checker` declares `let mut step = 0;` inside the callback, so it always asserts `record_type == 0`. The C test keeps a counter across calls through `user_data`. Matching the C behaviour means the reader must deliver the type-4 input records, which makes the Rust assertion fail. Skipping those records or special-casing the input would be wrong, so I'm not declaring completion. The fix belongs in `src/bin/test.rs`, which I can't edit.

This turn is a cosmetic reorder in `psbt_decode`: the ASCII check now runs before the buffer is touched. Behaviour is unchanged.

<edit path="src/psbt.rs">
<search>
        let mut pos = 0;
        if !src.is_ascii() {
            return PsbtResult::ReadError;
        }
</search>
<replace>
        if !src.is_ascii() {
            return PsbtResult::ReadError;
        }
        let mut pos = 0;
</replace>
</edit>

<notes>
- read_test_vector: blocked by the protected test. Its checker uses a fresh local `step` (always 0), so it asserts record_type==0 on every callback, but PSBT_HEX contains type-4 input records that the C reader delivers (the C test keeps a counter via user_data). Needs a fix in src/bin/test.rs. Do not special-case. Do not declare done.
- Reader matches C on header, record parsing, bounds checks, OobWrite on oversized src, non-ASCII hex rejection, byte-indexed hex decode.
- base64_decode reviewed against C: count, capacity, padding and break logic agree.
- Clippy style warnings are in src/bin/test.rs (protected).
- Open: rustc warnings (12) not yet triaged; the hex decode loop could be rewritten with chunks_exact for clarity.
</notes>