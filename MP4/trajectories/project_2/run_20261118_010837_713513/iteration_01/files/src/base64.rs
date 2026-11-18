#![forbid(unsafe_code)]
const BASE64_TABLE: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
const BASE62_TABLE: &[u8; 62] = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

/// Shared encoder mirroring the C `base_encode`. A table index outside the
/// table (the C code reads the NUL terminator or past it) is reported as failure.
fn base_encode(src: &[u8], out: &mut [u8], table: &[u8]) -> Option<usize> {
    // 4 output bytes per 3-byte block, plus the nul terminator.
    let olen = src.len() * 4 / 3 + 4 + 1;
    if olen > out.len() {
        return None;
    }
    let sym = |v: u8| table.get(usize::from(v)).copied();
    let mut enc = Vec::with_capacity(olen);
    let mut chunks = src.chunks_exact(3);
    for c in &mut chunks {
        let (a, b, d) = (c[0], c[1], c[2]);
        enc.push(sym(a >> 2)?);
        enc.push(sym(((a & 0x03) << 4) | (b >> 4))?);
        enc.push(sym(((b & 0x0f) << 2) | (d >> 6))?);
        enc.push(sym(d & 0x3f)?);
    }
    match *chunks.remainder() {
        [a] => {
            enc.push(sym(a >> 2)?);
            enc.push(sym((a & 0x03) << 4)?);
            enc.extend_from_slice(b"==");
        }
        [a, b] => {
            enc.push(sym(a >> 2)?);
            enc.push(sym(((a & 0x03) << 4) | (b >> 4))?);
            enc.push(sym((b & 0x0f) << 2)?);
            enc.push(b'=');
        }
        _ => {}
    }
    let n = enc.len();
    out[..n].copy_from_slice(&enc);
    out[n] = 0;
    Some(n)
}

/// Encode the given source bytes into base62. Returns the number of written bytes on success.
pub fn base62_encode(src: &[u8], out: &mut [u8]) -> Option<usize> {
    base_encode(src, out, BASE62_TABLE)
}

/// Encode the given source bytes into base64. Returns the number of written bytes on success.
pub fn base64_encode(src: &[u8], out: &mut [u8]) -> Option<usize> {
    base_encode(src, out, BASE64_TABLE)
}

/// Decode the given base64-encoded source bytes. Returns the number of decoded bytes on success.
pub fn base64_decode(src: &[u8], out: &mut [u8]) -> Option<usize> {
    let mut dtable = [0x80u8; 256];
    for (i, &c) in BASE64_TABLE.iter().enumerate() {
        dtable[usize::from(c)] = i as u8;
    }
    dtable[usize::from(b'=')] = 0;

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

    let mut pos = 0usize;
    let mut block = [0u8; 4];
    let mut n = 0usize;
    let mut pad = 0usize;
    for &c in src {
        let tmp = dtable[usize::from(c)];
        if tmp == 0x80 {
            continue;
        }
        if c == b'=' {
            pad += 1;
        }
        block[n] = tmp;
        n += 1;
        if n == 4 {
            out[pos] = (block[0] << 2) | (block[1] >> 4);
            out[pos + 1] = (block[1] << 4) | (block[2] >> 2);
            out[pos + 2] = (block[2] << 6) | block[3];
            pos += 3;
            n = 0;
            if pad > 0 {
                match pad {
                    1 => pos -= 1,
                    2 => pos -= 2,
                    _ => return None,
                }
                break;
            }
        }
    }
    Some(pos)
}
