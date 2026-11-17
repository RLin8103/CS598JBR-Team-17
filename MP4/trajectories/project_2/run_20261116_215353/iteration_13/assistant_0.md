The `read_test_vector` failure is still caused by the protected test, not the reader. Its `checker` declares `let mut step = 0;` inside the callback, so `step` is always 0 and the test asserts `record_type == 0` on every record. The first record the reader delivers is the global type-0 record, which passes. A later input record has type 4, which the reader must deliver to match the C behaviour, so the assertion at `src/bin/test.rs:126` fails. Making the reader skip type-4 records or special-casing the input would be wrong, so I'm not declaring completion.

The C test keeps a counter across calls through `user_data`. The Rust test would need the same, for example `user_data.downcast_mut::<usize>()`, to pass faithfully. Since `src/bin/test.rs` is read-only for me, this needs a change on your side.

This turn is a small clippy-clean cleanup in `psbt_read`. It replaces the `ref mut` binding with a plain one, which has no behavioural effect.

<edit path="src/psbt.rs">
<search>
                    if let Some(ref mut handler) = elem_handler {
</search>
<replace>
                    if let Some(handler) = elem_handler {
</replace>
</edit>

<notes>
- read_test_vector: blocked by the protected test. Its checker uses a fresh local `step` (always 0), so it asserts record_type==0 on every callback, but PSBT_HEX contains type-4 input records that the C reader delivers (the C test keeps a counter via user_data). Needs a fix in src/bin/test.rs. Do not special-case. Do not declare done.
- Reader matches C on header, record parsing, bounds checks, OobWrite on oversized src, non-ASCII hex rejection, byte-indexed hex decode.
- Clippy style warnings are in src/bin/test.rs (protected).
- Open: base64 decode parity on short/padded input not yet reviewed.
</notes>