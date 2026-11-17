The remaining `read_test_vector` failure is in the protected test, not the library. The `checker` declares `let mut step = 0;` inside the callback, so `step` is always 0 and every record must have type 0. The third record in the vector is an input record of type 4, so the assertion fails no matter how `psbt_read` is implemented. The C test only checks the first two records, because its counter lives in caller-owned memory. I won't special-case the test data.

This edit is a genuine cleanup in `src/psbt.rs`. The hex decoder calls `src.chars().nth(i + 1)` inside a loop, which is quadratic. Replacing it with a single pass over byte pairs gives identical output and removes the `unwrap`.

<edit path="src/psbt.rs">
<search>        let mut pos = 0;
        for (i, c) in src.chars().enumerate() {
            if i % 2 == 0 {
                let c1 = c;
                let c2 = src.chars().nth(i + 1).unwrap();
                
                let v1 = hex_to_val(c1);
                let v2 = hex_to_val(c2);
                
                if v1 == 0x80 || v2 == 0x80 {
                    return PsbtResult::ReadError;
                }
                
                dest[pos] = (v1 << 4) | v2;
                pos += 1;
            }
        }
        </search>
<replace>        for (pos, pair) in src.as_bytes().chunks_exact(2).enumerate() {
            let v1 = hex_to_val(char::from(pair[0]));
            let v2 = hex_to_val(char::from(pair[1]));

            if v1 == 0x80 || v2 == 0x80 {
                return PsbtResult::ReadError;
            }

            dest[pos] = (v1 << 4) | v2;
        }
        </replace>
</edit>

<notes>
- read_test_vector cannot pass honestly: test.rs `checker` keeps `step` at 0 and asserts record_type == 0 for every record; the third record in the vector is type 4. Test file is protected.
- Clippy style warnings (uninlined_format_args, single_match) are in src/bin/test.rs, outside my editable area.
- Library is otherwise faithful to C (header, records, tx counting, encodings). Hex decode now a single linear pass.
- No further changes planned unless the test changes.
</notes>