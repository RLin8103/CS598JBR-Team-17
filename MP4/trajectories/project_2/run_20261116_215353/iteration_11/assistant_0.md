The remaining `read_test_vector` failure is still the test's fault, not the reader's. Its `checker` uses a fresh local `step` that is always 0, so it asserts `record_type == 0` on every callback, while `PSBT_HEX` contains type-4 input records that the C reader must deliver. I won't skip records or special-case the input, so I'm not declaring completion.

This turn I'm removing the quadratic `chars().nth(i + 1)` lookup in hex decode. The input is already checked to be ASCII and of even length, so byte indexing is safe and gives the same result.

<edit path="src/psbt.rs">
<search>
                let c2 = src.chars().nth(i + 1).unwrap();
</search>
<replace>
                let c2 = src.as_bytes()[i + 1] as char;
</replace>
</edit>

<notes>
- read_test_vector: test bug. Its checker uses a fresh local `step`, so it asserts record_type==0 for every callback, but PSBT_HEX has type-4 input records that the C reader must deliver. Not passable without special-casing. Do not special-case. Do not declare done.
- Done: hex decode rejects non-ASCII (no panic). Hex decode now indexes bytes instead of chars().nth (linear, same result). psbt_read returns OobWrite when src_size > data_capacity, as C does.
- Clippy style warnings are in src/bin/test.rs (protected), so they cannot be cleared from our side.
- Next (if continuing): review base64 decode for C parity on short/padded input.
</notes>