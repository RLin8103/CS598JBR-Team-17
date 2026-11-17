The remaining failure comes from `src/bin/test.rs`, which I can't edit. The `checker` declares `let mut step = 0;` inside the callback, so `step` is 0 on every call. Each record is therefore asserted to have `record_type == 0`. The C test only checks the first two records, using a counter that persists across calls. A faithful `psbt_read` delivers every record, including the type-4 redeem script in the input map, so this assertion fails no matter how the parser is implemented. Special-casing the test data would violate the rules, so I'm leaving the parser's record delivery as it is.

The clippy `style` warnings in `src/bin/test.rs` are also outside my editable area, so they can't reach zero from my side.

I'll correct the misleading doc comment on `psbt_read` to describe what it actually does.

<edit path="src/psbt.rs">
<search>
/// For testing, we simulate reading by optionally calling the provided callback.
pub fn psbt_read(</search>
<replace>/// Parse a PSBT from `src`, invoking `elem_handler` once per record in document order.
/// Mirrors the C `psbt_read`: the input is copied into `psbt`, the state machine walks the
/// key/value maps, and the handler receives every record (including the global unsigned tx).
pub fn psbt_read(</replace>
</edit>

<notes>
- read_test_vector fails because test.rs `checker` resets `step` to 0 on every call and asserts record_type == 0 for ALL records. The C test only checks the first two. A faithful psbt_read delivers type-4 records, so this cannot pass without special-casing. Test file is protected; do not work around it.
- Clippy style warnings (uninlined_format_args, single_match) live in src/bin/test.rs and are also unfixable from src/*.rs.
- Library code is faithful to C for the header, record parsing, tx counting and encodings. Keep it; no further changes planned unless the controller changes the test.
- Next step if allowed: nothing in src/*.rs can make read_test_vector pass honestly.
</notes>