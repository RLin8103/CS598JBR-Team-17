The two `ReadError` failures come from `psbt_read` ignoring its `_src_size` argument and using `src.len()` (2048 bytes in the tests) instead of the real PSBT length. The trailing zeros then parse as garbage. I'm fixing that, plus the clippy and warning cleanups.

<edit path="src/psbt.rs">
<search>
    _src_size: usize,
    psbt: &mut Psbt,
</search>
<replace>
    src_size: usize,
    psbt: &mut Psbt,
</replace>
</edit>
<edit path="src/psbt.rs">
<search>
    let src_size = src.len();
    
    // Set up state for parsing
</search>
<replace>
    // Only the first `src_size` bytes belong to the PSBT.
    let src = &src[..src_size.min(src.len())];
    let src_size = src.len();
    
    // Set up state for parsing
</replace>
</edit>
<edit path="src/psbt.rs">
<search>
    let mut end = src_size;
</search>
<replace>
    let end = src_size;
</replace>
</edit>
<edit path="src/psbt.rs">
<search>
    if c >= '0' && c <= '9' {</search>
<replace>    if ('0'..='9').contains(&c) {</replace>
</edit>
<edit path="src/psbt.rs">
<search>
    } else if c >= 'a' && c <= 'f' {</search>
<replace>    } else if ('a'..='f').contains(&c) {</replace>
</edit>
<edit path="src/psbt.rs">
<search>
    } else if c >= 'A' && c <= 'F' {</search>
<replace>    } else if ('A'..='F').contains(&c) {</replace>
</edit>
<edit path="src/psbt.rs">
<search>        let _ = write!(stream, "{:02x}", byte);</search>
<replace>        let _ = write!(stream, "{byte:02x}");</replace>
</edit>
<notes>
- Fixed: psbt_read now truncates src to the given src_size (the PSBT length), not the buffer length. This should fix empty_input_test and encode_decode_test.
- Open: read_test_vector's checker in src/bin/test.rs uses a local `step = 0` and asserts every record type is 0. A faithful psbt_read calls the handler for all records (including type 4 redeem scripts), so this test cannot pass without special-casing. Likely a test-spec defect. Leave it unless the controller says otherwise.
- Clippy: hex_to_val range checks and the write! format were converted. Still to check: the cli.rs stub, unused imports and the leftover `unimplemented!()` in psbt_btc_tx_parse (tx.rs), psbt_read's unused `records` path.
- TODO: replace remaining unimplemented in tx.rs (psbt_btc_tx_parse) and cli.rs main.
</notes>