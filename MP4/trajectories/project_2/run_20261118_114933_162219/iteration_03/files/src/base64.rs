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
