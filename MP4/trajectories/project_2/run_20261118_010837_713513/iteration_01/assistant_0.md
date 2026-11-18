The crate is still far from passing, and the failing tests point to three root causes. Most of the read, encode and decode paths deviate from the C code, and the base62 path panics on table lookups it cannot represent. I am starting the rewrite with `base64.rs` and `tx.rs`, plus the first half of `psbt.rs`. The second half follows next turn.

Plan:
- `base64.rs`: rewrite with checked table lookups. Base62 lookups at index 62 or 63 fail instead of panicking, and destination limits are enforced.
- `tx.rs`: expose `parse_tx` to the crate so `psbt_read` can forward transaction elements in order. Remove the now-unused counter helper.
- `psbt.rs` (part 1 of 2): exact interface types, a last-error store so `psbt_geterr` returns real messages, a C-faithful `psbt_read` (`kvs` counts map index, not record index, and transaction elements are forwarded before the unsigned-tx record), and `psbt_decode` honouring `src_size` and `dest_size`. The remaining functions follow in an `<append>` block.

Benchmark note: `read_test_vector` cannot pass as written. Its checker resets `step` on every call and asserts `record_type == 0` for every record, but the PSBT contains type-4 redeem-script records. I am treating this as a test defect and will not special-case it.

<file path="src/base64.rs">
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
</file>

<edit path="src/tx.rs">
<search>
fn parse_tx<F: FnMut(PsbtTxElem)>(data: &[u8], mut emit: F) -> Result<(), PsbtResult> {
</search>
<replace>
pub(crate) fn parse_tx<F: FnMut(PsbtTxElem)>(data: &[u8], mut emit: F) -> Result<(), PsbtResult> {
</replace>
</edit>

<edit path="src/tx.rs">
<search>
/// Count (inputs, outputs) of a serialized transaction.
pub(crate) fn tx_io_counts(tx: &[u8]) -> Result<(usize, usize), PsbtResult> {
    let mut counts = (0usize, 0usize);
    parse_tx(tx, |elem| match elem {
        PsbtTxElem::TxIn(_) => counts.0 += 1,
        PsbtTxElem::TxOut(_) => counts.1 += 1,
        _ => {}
    })?;
    Ok(counts)
}
</search>
<replace></replace>
</edit>

<file path="src/psbt.rs">
#![forbid(unsafe_code)]
use crate::base64::{base62_encode, base64_decode, base64_encode};
use crate::compactsize::{
    compactsize_length, compactsize_peek_length, compactsize_read, compactsize_write,
};
use crate::tx::*;
use std::fmt;
use std::sync::{Mutex, PoisonError};

// Common constant from common.h
pub const MAX_SERIALIZE_SIZE: u32 = 0x02000000;

/// Last error message, the Rust counterpart of the C global `psbt_errmsg`.
static LAST_ERR: Mutex<&'static str> = Mutex::new("psbt error");

fn set_err(msg: &'static str) {
    *LAST_ERR.lock().unwrap_or_else(PoisonError::into_inner) = msg;
}

fn read_err<T>(msg: &'static str) -> Result<T, PsbtResult> {
    set_err(msg);
    Err(PsbtResult::ReadError)
}

// --- Enum definitions ---
#[derive(Debug, PartialEq, Eq)]
pub enum PsbtResult { Ok, CompactReadError, ReadError, WriteError, InvalidState, NotImplemented, OobWrite }

impl fmt::Display for PsbtResult {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{self:?}")
    }
}

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtGlobalType {
    UnsignedTx = 0,
}

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtEncoding { Hex, Base64, Base62, Protobuf }

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtInputType {
    NonWitnessUtxo = 0,
    WitnessUtxo = 1,
    PartialSig = 2,
    SighashType = 3,
    RedeemScript = 4,
    WitnessScript = 5,
    Bip32Derivation = 6,
    FinalScriptSig = 7,
    FinalScriptWitness = 8,
}

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtOutputType { RedeemScript = 0, WitnessScript = 1, Bip32Derivation = 2 }

#[derive(Debug, PartialEq, Eq, Clone)]
pub enum PsbtScope { Global, Inputs, Outputs }

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtState { Init = 2, Global, Inputs, InputsNew, Outputs, OutputsNew, Finalized }

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtElemType { Record, TxElem }

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtTxElemType { TxIn, TxOut, Tx, WitnessItem }

// --- Struct definitions ---
/// Translates the C struct psbt.
/// (Here we use a Vec<u8> to hold the PSBT data and a write position index.)
pub struct Psbt {
    pub state: PsbtState,
    pub data: Vec<u8>,
    pub write_pos: usize,
    pub data_capacity: usize,
    // For simulation purposes we keep a list of records.
    pub records: Vec<PsbtRecord>,
}

impl Psbt {
    pub fn new(capacity: usize) -> Self {
        Self {
            state: PsbtState::Init,
            data: Vec::with_capacity(capacity),
            write_pos: 0,
            data_capacity: capacity,
            records: Vec::new(),
        }
    }
}

/// Translates the C struct psbt_record.
pub struct PsbtRecord {
    /// (The C field "type" is renamed to avoid conflict with the Rust keyword.)
    pub record_type: u8,
    pub key: Vec<u8>,
    pub val: Vec<u8>,
    pub scope: PsbtScope,
}

/// Translates the C union (record/txelem) in psbt_elem into an enum.
pub enum PsbtElem {
    Record { index: i32, record: PsbtRecord },
    TxElem { index: i32, txelem: PsbtTxElem },
}

/// The C typedef for a handler function.
pub type PsbtElemHandler = fn(elem: &mut PsbtElem, user_data: &mut dyn std::any::Any);

// External constants
pub const PSBT_MAGIC: [u8; 4] = [0x70, 0x73, 0x62, 0x74]; // "psbt"
pub static PSBT_ERRMSG: &str = "psbt error";

/// Return the number of bytes stored in the PSBT.
pub fn psbt_size(tx: &Psbt) -> usize {
    tx.data.len()
}

/// Read a compactsize at `*pos`, advancing the cursor past it.
fn read_compact(data: &[u8], pos: &mut usize) -> Result<u64, PsbtResult> {
    let rest = data.get(*pos..).ok_or(PsbtResult::ReadError)?;
    let first = *rest.first().ok_or(PsbtResult::ReadError)?;
    let (val, res) = compactsize_read(rest);
    if res != PsbtResult::Ok {
        set_err("compactsize_read: non-canonical or truncated compactsize");
        return Err(res);
    }
    *pos += compactsize_peek_length(first) as usize;
    Ok(val)
}

/// Take `len` bytes at `*pos`, advancing the cursor past them.
fn read_bytes<'a>(data: &'a [u8], pos: &mut usize, len: u64) -> Result<&'a [u8], PsbtResult> {
    let end = usize::try_from(len)
        .ok()
        .and_then(|n| pos.checked_add(n))
        .filter(|&e| e <= data.len());
    let Some(end) = end else {
        set_err("psbt_read: record size too large");
        return Err(PsbtResult::ReadError);
    };
    let bytes = data.get(*pos..end).ok_or(PsbtResult::ReadError)?;
    *pos = end;
    Ok(bytes)
}

fn byte_at(data: &[u8], pos: usize) -> Result<u8, PsbtResult> {
    match data.get(pos) {
        Some(&b) => Ok(b),
        None => read_err("psbt_read: unexpected end of psbt data"),
    }
}

/// Read one key/value record at `*pos` (C psbt_read_record).
fn read_record(data: &[u8], pos: &mut usize, scope: PsbtScope) -> Result<PsbtRecord, PsbtResult> {
    let key_with_type = read_compact(data, pos)?;
    let key_bytes = read_bytes(data, pos, key_with_type)?;
    let Some((&record_type, key)) = key_bytes.split_first() else {
        return read_err("psbt_read: zero-length key");
    };
    let val_len = read_compact(data, pos)?;
    let val = read_bytes(data, pos, val_len)?;
    Ok(PsbtRecord {
        record_type,
        key: key.to_vec(),
        val: val.to_vec(),
        scope,
    })
}

/// Walk the embedded transaction, forwarding every element to the handler
/// and counting inputs and outputs (C tx_counter).
fn forward_tx(
    tx: &[u8],
    index: i32,
    handler: Option<PsbtElemHandler>,
    user_data: &mut dyn std::any::Any,
) -> Result<(usize, usize), PsbtResult> {
    let mut counts = (0usize, 0usize);
    parse_tx(tx, |txelem| {
        match txelem {
            PsbtTxElem::TxIn(_) => counts.0 += 1,
            PsbtTxElem::TxOut(_) => counts.1 += 1,
            _ => {}
        }
        if let Some(h) = handler {
            let mut elem = PsbtElem::TxElem { index, txelem };
            h(&mut elem, user_data);
        }
    })?;
    Ok(counts)
}

/// Parse the PSBT body after the buffer has been loaded (C psbt_read loop).
fn read_body(
    psbt: &mut Psbt,
    data: &[u8],
    elem_handler: Option<PsbtElemHandler>,
    user_data: &mut dyn std::any::Any,
) -> Result<(), PsbtResult> {
    let end = data.len();
    let mut pos = 0usize;
    let mut kvs = 0usize;
    // (inputs, outputs) announced by the global unsigned transaction.
    let mut counts = (0usize, 0usize);

    while psbt.state != PsbtState::Finalized && pos <= end {
        match psbt.state {
            PsbtState::Init => {
                if data.get(pos..pos + 4) != Some(PSBT_MAGIC.as_slice()) {
                    return read_err("psbt_read: invalid magic header");
                }
                pos += 4;
                if byte_at(data, pos)? != 0xff {
                    return read_err("psbt_read: no 0xff found after magic");
                }
                pos += 1;
                psbt.state = PsbtState::Global;
            }
            PsbtState::Global | PsbtState::Inputs | PsbtState::Outputs => {
                if byte_at(data, pos)? == 0 {
                    match psbt.state {
                        PsbtState::Global => psbt.state = PsbtState::InputsNew,
                        PsbtState::Inputs => {
                            kvs += 1;
                            psbt.state = if kvs >= counts.0 {
                                kvs = 0;
                                PsbtState::OutputsNew
                            } else {
                                PsbtState::InputsNew
                            };
                        }
                        PsbtState::Outputs => {
                            kvs += 1;
                            psbt.state = if kvs >= counts.1 {
                                PsbtState::Finalized
                            } else {
                                PsbtState::OutputsNew
                            };
                        }
                        _ => {}
                    }
                } else {
                    let scope = match psbt.state {
                        PsbtState::Inputs => PsbtScope::Inputs,
                        PsbtState::Outputs => PsbtScope::Outputs,
                        _ => PsbtScope::Global,
                    };
                    let rec = read_record(data, &mut pos, scope)?;
                    if psbt.state == PsbtState::Global
                        && rec.record_type == PsbtGlobalType::UnsignedTx as u8
                    {
                        counts = forward_tx(&rec.val, kvs as i32, elem_handler, user_data)?;
                    }
                    let mut elem = PsbtElem::Record {
                        index: kvs as i32,
                        record: rec,
                    };
                    if let Some(handler) = elem_handler {
                        handler(&mut elem, user_data);
                    }
                    if let PsbtElem::Record { record, .. } = elem {
                        psbt.records.push(record);
                    }
                }
            }
            PsbtState::InputsNew | PsbtState::OutputsNew => {
                if byte_at(data, pos)? != 0 {
                    return read_err("psbt_read: expected null byte between record sets");
                }
                pos += 1;
                psbt.state = if psbt.state == PsbtState::InputsNew {
                    PsbtState::Inputs
                } else {
                    PsbtState::Outputs
                };
            }
            PsbtState::Finalized => break,
        }
    }

    if psbt.state != PsbtState::Finalized {
        set_err("psbt_read: invalid psbt");
        return Err(PsbtResult::InvalidState);
    }
    if byte_at(data, pos)? != 0 {
        return read_err("psbt_read: expected null byte at end of psbt");
    }
    psbt.write_pos = pos + 1;
    Ok(())
}

/// For testing, we simulate reading by optionally calling the provided callback.
pub fn psbt_read(
    src: &[u8],
    src_size: usize,
    psbt: &mut Psbt,
    elem_handler: Option<PsbtElemHandler>,
    user_data: &mut dyn std::any::Any,
) -> PsbtResult {
    if psbt.state != PsbtState::Init {
        set_err("psbt_read: psbt not initialized, use psbt_init first");
        return PsbtResult::InvalidState;
    }
    if src_size > psbt.data_capacity {
        set_err("psbt_read: read buffer is larger than psbt capacity");
        return PsbtResult::OobWrite;
    }
    let Some(data) = src.get(..src_size) else {
        set_err("psbt_read: length larger than backing slice");
        return PsbtResult::ReadError;
    };
    psbt.data = data.to_vec();
    psbt.data_capacity = src_size;
    psbt.records.clear();
    psbt.write_pos = 0;

    match read_body(psbt, data, elem_handler, user_data) {
        Ok(()) => PsbtResult::Ok,
        Err(res) => res,
    }
}

fn hex_val(c: u8) -> Option<u8> {
    match c {
        b'0'..=b'9' => Some(c - b'0'),
        b'a'..=b'f' => Some(c - b'a' + 10),
        b'A'..=b'F' => Some(c - b'A' + 10),
        _ => None,
    }
}

fn hex_decode(src: &[u8], dest: &mut [u8], psbt_len: &mut usize) -> PsbtResult {
    if src.len() % 2 != 0 {
        set_err("psbt_decode: invalid hex string");
        return PsbtResult::ReadError;
    }
    let n = src.len() / 2;
    if dest.len() < n {
        set_err("psbt_decode: dest_size must be at least half the size of src_size");
        return PsbtResult::ReadError;
    }
    for (out, pair) in dest.iter_mut().zip(src.chunks_exact(2)) {
        match (hex_val(pair[0]), hex_val(pair[1])) {
            (Some(hi), Some(lo)) => *out = (hi << 4) | lo,
            _ => {
                set_err("psbt_decode: invalid hex string");
                return PsbtResult::ReadError;
            }
        }
    }
    *psbt_len = n;
    PsbtResult::Ok
}

/// Decode a hex or base64 PSBT string into dest.
pub fn psbt_decode(
    src: &str,
    _src_size: usize,
    dest: &mut [u8],
    dest_size: usize,
    psbt_len: &mut usize,
) -> PsbtResult {
    let Some(bytes) = src.as_bytes().get(.._src_size) else {
        set_err("psbt_decode: source length larger than source string");
        return PsbtResult::ReadError;
    };
    if bytes.len() < 5 {
        set_err("psbt_decode: psbt too small");
        return PsbtResult::ReadError;
    }
    let dest = &mut dest[..dest_size.min(dest.len())];
    if bytes.starts_with(b"cHNid") {
        return match base64_decode(bytes, dest) {
            Some(n) => {
                *psbt_len = n;
                PsbtResult::Ok
            }
            None => {
                set_err("psbt_decode: base64 decode failure");
                PsbtResult::ReadError
            }
        };
    }
    hex_decode(bytes, dest, psbt_len)
}
</file>