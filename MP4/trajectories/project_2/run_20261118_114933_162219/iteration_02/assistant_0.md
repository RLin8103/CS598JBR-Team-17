## Plan

**Failure selected: `read_test_vector`.** I'm keeping my earlier diagnosis. The checker at `src/bin/test.rs:126` asserts `record_type == 0` for every record because `step` is reset on each call. The PSBT contains type-4 input records, which the C code also reports. This is a suspected benchmark defect. I won't special-case it or suppress callbacks, so it stays unresolved.

**Real defect to fix: base62 panics.** `BASE62_TABLE` has 62 entries, but the encoder indexes it with 6-bit values (0..63). Indices 62 and 63 panic. In C this is undefined behaviour. The safe mapping is to return `None` (encode failure) instead of panicking. I'm also consolidating the base64 and base62 encoders into one helper that uses checked table lookups. The decoder stays the same.

<file path="src/base64.rs">
const BASE64_TABLE: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
const BASE62_TABLE: &[u8; 62] = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

/// Checked table lookup. Indices outside the alphabet yield `None` instead of panicking.
fn sym(table: &[u8], idx: u8) -> Option<u8> {
    table.get(usize::from(idx)).copied()
}

/// Shared encoder for the 4-character-per-3-byte schemes (RFC 1341 layout).
/// Returns the number of symbols written, excluding the NUL terminator.
fn encode_with(src: &[u8], out: &mut [u8], table: &[u8]) -> Option<usize> {
    let olen = src.len() * 4 / 3 + 4;
    if olen + 1 > out.len() {
        return None;
    }

    let mut symbols: Vec<u8> = Vec::with_capacity(olen);
    for chunk in src.chunks(3) {
        let b0 = chunk[0];
        let b1 = chunk.get(1).copied().unwrap_or(0);
        let b2 = chunk.get(2).copied().unwrap_or(0);
        let idx = [
            b0 >> 2,
            ((b0 & 0x03) << 4) | (b1 >> 4),
            ((b1 & 0x0f) << 2) | (b2 >> 6),
            b2 & 0x3f,
        ];
        // Significant characters: one byte -> 2, two bytes -> 3, three bytes -> 4.
        let significant = chunk.len() + 1;
        for (k, &v) in idx.iter().enumerate() {
            if k < significant {
                symbols.push(sym(table, v)?);
            } else {
                symbols.push(b'=');
            }
        }
    }

    let len = symbols.len();
    out.get_mut(..len)?.copy_from_slice(&symbols);
    *out.get_mut(len)? = 0;
    Some(len)
}

/// Encode the given source bytes into base62. Returns the number of written bytes on success.
pub fn base62_encode(src: &[u8], out: &mut [u8]) -> Option<usize> {
    encode_with(src, out, BASE62_TABLE)
}

/// Encode the given source bytes into base64. Returns the number of written bytes on success.
pub fn base64_encode(src: &[u8], out: &mut [u8]) -> Option<usize> {
    encode_with(src, out, BASE64_TABLE)
}

/// Decode the given base64-encoded source bytes. Returns the number of decoded bytes on success.
pub fn base64_decode(src: &[u8], out: &mut [u8]) -> Option<usize> {
    if src.is_empty() {
        return None;
    }

    // Build decode table
    let mut dtable = [0x80u8; 256];
    for (i, &c) in BASE64_TABLE.iter().enumerate() {
        dtable[usize::from(c)] = i as u8;
    }
    dtable[usize::from(b'=')] = 0;

    // Count valid characters
    let count = src
        .iter()
        .filter(|&&c| dtable[usize::from(c)] != 0x80)
        .count();

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

    for &c in src {
        let tmp = dtable[usize::from(c)];
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
</file>

<notes>
- read_test_vector: unresolved suspected benchmark defect. The checker resets `step` per call, so it asserts record_type == 0 for every record, but the PSBT has type-4 input records that the C code also reports. Do not suppress callbacks.
- Fixed in this iteration: base62 panics (indices 62/63 from a 6-bit value into a 62-entry table). Now checked via `sym()`, which returns None (encode failure) instead of panicking. This matches the C UB-free interpretation as closely as possible.
- Hex decode out-of-bounds: fixed earlier with a `dest.len()` guard; regression `decode_hex_checks_actual_destination` now passes.
- Still open (extra regression checks, not in the provided tests): psbt_decode ignores `_src_size` (decode_honors_input_prefix); encode_honors_input_prefix expects the trailing NUL not to be counted or written the way C does; psbt_encode_raw hex path writes out of bounds when dest.len() < 2n+1 (encode_hex_checks_actual_destination); errors_include_useful_context expects psbt_geterr to return context, but it returns a constant; multi-map callback indices. Next iteration should address the hex-encode dest.len() guard and psbt_geterr if budget allows.
- Clippy style warnings (uninlined_format_args, single_match) come from the protected src/bin/test.rs, so they cannot be fixed here.
</notes>