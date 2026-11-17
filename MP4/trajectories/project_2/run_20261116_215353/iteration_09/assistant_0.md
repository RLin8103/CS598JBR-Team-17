The `read_test_vector` failure is in the test itself, not in the read logic. The `checker` in `src/bin/test.rs` declares `let mut step = 0;` inside the function, so it asserts `record_type == 0` for every record. A faithful reader must also deliver the type-4 redeem-script records (for example `0104 4752 21...` in `PSBT_HEX`), so this test cannot pass without special-casing. I won't do that, and I'm not declaring completion.

This turn I'm fixing a real panic I found in `psbt_decode`'s hex path. `src.chars().nth(i + 1).unwrap()` can panic on non-ASCII input, because the byte length and the char count differ. The C code rejects any non-hex byte with `PSBT_READ_ERROR`, so rejecting non-ASCII input up front matches the C behaviour.

<edit path="src/psbt.rs">
<search>
        for (i, c) in src.chars().enumerate() {
</search>
<replace>
        if !src.is_ascii() {
            return PsbtResult::ReadError;
        }
        for (i, c) in src.chars().enumerate() {
</replace>
</edit>

<notes>
- read_test_vector: test bug. The test's checker uses a fresh local `step`, so it asserts record_type==0 for every callback, but PSBT_HEX contains type-4 records. Not passable faithfully; do not special-case. Report it.
- Fixed: hex decode panicked on non-ASCII input (chars().nth unwrap). Now rejects non-ASCII with ReadError, as C does.
- Remaining review: psbt_read/read_record bounds look safe; base64 and encode buffers are size-checked.
- Not done: no `<done/>` while a test fails.
</notes>