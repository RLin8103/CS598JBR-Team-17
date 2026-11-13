<notes>
Looking at the test failures:
1. `empty_input_test` and `encode_decode_test` fail with `ReadError` from `psbt_decode`
2. `read_test_vector` has a callback step counter issue (4 vs 0)

The issue is that `psbt_decode` is returning `ReadError` for base64 input. Looking at the C code, the base64 decode function should handle the input properly. The problem might be in how I'm handling the base64 decode - the C code returns NULL on error, but my Rust code might be returning None for valid inputs.

Let me check the EMPTY_INPUTS test vector: "cHNidP8BACoCAAAAAAGA8PoCAAAAABepFCufG2xKKzFR7+3XGjiAZPO/VDBkhwAAAAAAAA=="

This is base64 encoded. The issue might be that my base64_decode is too strict or has an issue with the input.

Also, the callback step counter in read_test_vector is wrong - it's getting 4 instead of 0, meaning the callback isn't being called properly or the step variable isn't being passed correctly.
</notes>

Let me first check what the base64 decode is returning by examining the test more carefully. The issue is likely in how I'm handling the base64 decode. Let me fix the base64 decode function to match the C behavior more closely:

<edit path="src/base64.rs">
<search>
/// Decode the given base64-encoded source bytes. Returns the number of decoded bytes on success.
pub fn base64_decode(src: &[u8], out: &mut [u8]) -> Option<usize> {
    if src.is_empty() {
        return None;
    }
    
    // Build decode table
    let mut dtable = [0x80u8; 256];
    for (i, &c) in BASE64_TABLE.iter().enumerate() {
        dtable[c as usize] = i as u8;
    }
    dtable[b'=' as usize] = 0;
    
    // Count valid characters
    let mut count = 0;
    for &c in src.iter() {
        if dtable[c as usize] != 0x80 {
            count += 1;
        }
    }
    
    if count == 0 || count % 4 != 0 {
        return None;
    }
    
    let olen = count / 4 * 3;
    if out.len() < olen {
        return None;
    }
    
    let mut pos = 0;
    let mut block = [0u8; 4];
    let mut block_count = 0;
    let mut pad = 0;
    
    for &c in src.iter() {
        let tmp = dtable[c as usize];
        if tmp == 0x80 {
            continue;
        }
        
        if c == b'=' {
            pad += 1;
        }
        block[block_count] = tmp;
        block_count += 1;
        
        if block_count == 4 {
            out[pos] = (block[0] << 2) | (block[1] >> 4);
            pos += 1;
            out[pos] = (block[1] << 4) | (block[2] >> 2);
            pos += 1;
            out[pos] = (block[2] << 6) | block[3];
            pos += 1;
            
            block_count = 0;
            
            if pad > 0 {
                if pad == 1 {
                    pos -= 1;
                } else if pad == 2 {
                    pos -= 2;
                } else {
                    return None;
                }
                break;
            }
        }
    }
    
    Some(pos)
}
</search>
<replace>
/// Decode the given base64-encoded source bytes. Returns the number of decoded bytes on success.
pub fn base64_decode(src: &[u8], out: &mut [u8]) -> Option<usize> {
    if src.is_empty() {
        return None;
    }
    
    // Build decode table
    let mut dtable = [0x80u8; 256];
    for (i, &c) in BASE64_TABLE.iter().enumerate() {
        dtable[c as usize] = i as u8;
    }
    dtable[b'=' as usize] = 0;
    
    // Count valid characters
    let mut count = 0;
    for &c in src.iter() {
        if dtable[c as usize] != 0x80 {
            count += 1;
        }
    }
    
    if count == 0 || count % 4 != 0 {
        return None;
    }
    
    let olen = count / 4 * 3;
    if out.len() < olen {
        return None;
    }
    
    let mut pos = 0;
    let mut block = [0u8; 4];
    let mut block_count = 0;
    let mut pad = 0;
    
    for &c in src.iter() {
        let tmp = dtable[c as usize];
        if tmp == 0x80 {
            continue;
        }
        
        if c == b'=' {
            pad += 1;
        }
        block[block_count] = tmp;
        block_count += 1;
        
        if block_count == 4 {
            out[pos] = (block[0] << 2) | (block[1] >> 4);
            pos += 1;
            out[pos] = (block[1] << 4) | (block[2] >> 2);
            pos += 1;
            out[pos] = (block[2] << 6) | block[3];
            pos += 1;
            
            block_count = 0;
            
            if pad > 0 {
                if pad == 1 {
                    pos -= 1;
                } else if pad == 2 {
                    pos -= 2;
                } else {
                    return None;
                }
                break;
            }
        }
    }
    
    Some(pos)
}
</replace>
</edit>