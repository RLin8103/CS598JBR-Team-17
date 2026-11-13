I'll analyze the failing tests and implement the necessary fixes. Let me first understand the issues:

1. `empty_input_test` - `psbt_decode` returns `ReadError` instead of `Ok`
2. `read_test_vector` - The callback step counter is wrong (4 vs 0)
3. `encode_decode_test` - `psbt_decode` returns `ReadError` instead of `Ok`

Looking at the C code, I see the issue: the `psbt_decode` function needs to handle base64 decoding properly. The test uses `EMPTY_INPUTS` which starts with "cHNid" (base64 magic), but my implementation might have issues.

Let me fix the `psbt_decode` function and related issues:

<edit path="src/psbt.rs">
<search>
/// Decode a hex string into dest. (This simple implementation uses the `hex` crate.)
pub fn psbt_decode(
    src: &str,
    _src_size: usize,
    dest: &mut [u8],
    dest_size: usize,
    psbt_len: &mut usize,
) -> PsbtResult {
    let b64_magic = "cHNid";
    
    if src.len() < b64_magic.len() {
        return PsbtResult::ReadError;
    }
    
    if &src[..b64_magic.len()] == b64_magic {
        // Base64 decode
        let src_bytes = src.as_bytes();
        match base64_decode(src_bytes, dest) {
            Some(len) => {
                *psbt_len = len;
                PsbtResult::Ok
            }
            None => PsbtResult::ReadError,
        }
    } else {
        // Hex decode
        if src.len() % 2 != 0 {
            return PsbtResult::ReadError;
        }
        
        let expected_len = src.len() / 2;
        if dest_size < expected_len {
            return PsbtResult::ReadError;
        }
        
        let mut pos = 0;
        for i in (0..src.len()).step_by(2) {
            let c1 = src.chars().nth(i).unwrap();
            let c2 = src.chars().nth(i + 1).unwrap();
            
            let v1 = hex_to_val(c1);
            let v2 = hex_to_val(c2);
            
            if v1 == 0x80 || v2 == 0x80 {
                return PsbtResult::ReadError;
            }
            
            dest[pos] = (v1 << 4) | v2;
            pos += 1;
        }
        
        *psbt_len = expected_len;
        PsbtResult::Ok
    }
}
</search>
<replace>
/// Decode a hex string into dest. (This simple implementation uses the `hex` crate.)
pub fn psbt_decode(
    src: &str,
    _src_size: usize,
    dest: &mut [u8],
    dest_size: usize,
    psbt_len: &mut usize,
) -> PsbtResult {
    let b64_magic = "cHNid";
    
    if src.len() < b64_magic.len() {
        return PsbtResult::ReadError;
    }
    
    if &src[..b64_magic.len()] == b64_magic {
        // Base64 decode
        let src_bytes = src.as_bytes();
        match base64_decode(src_bytes, dest) {
            Some(len) => {
                *psbt_len = len;
                PsbtResult::Ok
            }
            None => PsbtResult::ReadError,
        }
    } else {
        // Hex decode
        if src.len() % 2 != 0 {
            return PsbtResult::ReadError;
        }
        
        let expected_len = src.len() / 2;
        if dest_size < expected_len {
            return PsbtResult::ReadError;
        }
        
        let mut pos = 0;
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
        
        *psbt_len = expected_len;
        PsbtResult::Ok
    }
}
</replace>
</edit>