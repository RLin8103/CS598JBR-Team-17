The remaining `OobWrite` comes from `psbt_read` copying the whole 2048-byte input into `psbt.data` before truncating it, so `psbt_encode` sees the full buffer. The `ReadError` in `empty_input_test` comes from the input ending one separator early. The C reader treats bytes past the end of the zero-filled buffer as zero, and my bounds guard rejects that. I'm fixing both, plus the remaining clippy lint in `hex_to_val`.

<edit path="src/psbt.rs">
<search>    psbt.data.extend_from_slice(src);
    psbt.write_pos = 0;</search>
<replace>    psbt.data.extend_from_slice(&src[..src_size.min(src.len())]);
    psbt.write_pos = 0;</replace>
</edit>
<edit path="src/psbt.rs">
<search>                if psbt.write_pos >= src_size {
                    return PsbtResult::ReadError;
                }
</search>
<replace></replace>
</edit>
<edit path="src/psbt.rs">
<search>                if psbt.data[psbt.write_pos] == 0 {</search>
<replace>                // Bytes past the end of the input read as zero, as in the zeroed C buffer.
                if psbt.data.get(psbt.write_pos).copied().unwrap_or(0) == 0 {</replace>
</edit>
<edit path="src/psbt.rs">
<search>    if ('0'..='9').contains(&c) {</search>
<replace>    if c.is_ascii_digit() {</replace>
</edit>
<notes>
- Fixed: psbt_read copies only the first src_size bytes into psbt.data (encode length was wrong, causing OobWrite).
- Fixed: in the Global/Inputs/Outputs branch, bytes past the end read as 0 (C reads the zeroed buffer). The empty-input vector has its final output-set separator missing, so this is required.
- Open: read_test_vector asserts every record type is 0, but the second record is type 4. This is a test-spec defect; leave it.
- Clippy: remaining warnings are in src/bin/test.rs (not editable).
- cli.rs stub is not a tested target; leave it unless needed.
</notes>