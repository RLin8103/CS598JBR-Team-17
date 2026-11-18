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
pub enum PsbtResult {
    Ok,
    CompactReadError,
    ReadError,
    WriteError,
    InvalidState,
    NotImplemented,
    OobWrite,
}

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
pub enum PsbtEncoding {
    Hex,
    Base64,
    Base62,
    Protobuf,
}

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
pub enum PsbtOutputType {
    RedeemScript = 0,
    WitnessScript = 1,
    Bip32Derivation = 2,
}

#[derive(Debug, PartialEq, Eq, Clone)]
pub enum PsbtScope {
    Global,
    Inputs,
    Outputs,
}

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtState {
    Init = 2,
    Global,
    Inputs,
    InputsNew,
    Outputs,
    OutputsNew,
    Finalized,
}

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtElemType {
    Record,
    TxElem,
}

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtTxElemType {
    TxIn,
    TxOut,
    Tx,
    WitnessItem,
}

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
    let dest_len = dest_size.min(dest.len());
    let dest = &mut dest[..dest_len];
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
/// Return the last error message.
pub fn psbt_geterr() -> &'static str {
    *LAST_ERR.lock().unwrap_or_else(PoisonError::into_inner)
}

/// Convert a PSBT state to a human-readable string.
pub fn psbt_state_tostr(state: PsbtState) -> &'static str {
    match state {
        PsbtState::Init => "INIT",
        PsbtState::Global => "GLOBAL",
        PsbtState::Inputs => "INPUTS",
        PsbtState::InputsNew => "INPUTS_NEW",
        PsbtState::Outputs => "OUTPUTS",
        PsbtState::OutputsNew => "OUTPUTS_NEW",
        PsbtState::Finalized => "FINALIZED",
    }
}

/// Return a string for a record type and scope.
pub fn psbt_type_tostr(record_type: u8, scope: PsbtScope) -> &'static str {
    match scope {
        PsbtScope::Global => match record_type {
            0 => psbt_global_type_tostr(PsbtGlobalType::UnsignedTx),
            _ => "UNKNOWN_GLOBAL_TYPE",
        },
        PsbtScope::Inputs => match record_type {
            0 => psbt_input_type_tostr(PsbtInputType::NonWitnessUtxo),
            1 => psbt_input_type_tostr(PsbtInputType::WitnessUtxo),
            2 => psbt_input_type_tostr(PsbtInputType::PartialSig),
            3 => psbt_input_type_tostr(PsbtInputType::SighashType),
            4 => psbt_input_type_tostr(PsbtInputType::RedeemScript),
            5 => psbt_input_type_tostr(PsbtInputType::WitnessScript),
            6 => psbt_input_type_tostr(PsbtInputType::Bip32Derivation),
            7 => psbt_input_type_tostr(PsbtInputType::FinalScriptSig),
            8 => psbt_input_type_tostr(PsbtInputType::FinalScriptWitness),
            _ => "UNKNOWN_INPUT_TYPE",
        },
        PsbtScope::Outputs => match record_type {
            0 => psbt_output_type_tostr(PsbtOutputType::RedeemScript),
            1 => psbt_output_type_tostr(PsbtOutputType::WitnessScript),
            2 => psbt_output_type_tostr(PsbtOutputType::Bip32Derivation),
            _ => "UNKNOWN_OUTPUT_TYPE",
        },
    }
}

/// Return a string for a psbt_txelem type.
pub fn psbt_txelem_type_tostr(txelem_type: PsbtTxElemType) -> &'static str {
    match txelem_type {
        PsbtTxElemType::Tx => "TX",
        PsbtTxElemType::TxIn => "TXIN",
        PsbtTxElemType::TxOut => "TXOUT",
        PsbtTxElemType::WitnessItem => "WITNESS_ITEM",
    }
}

pub fn psbt_global_type_tostr(gt: PsbtGlobalType) -> &'static str {
    match gt {
        PsbtGlobalType::UnsignedTx => "GLOBAL_UNSIGNED_TX",
    }
}

pub fn psbt_output_type_tostr(ot: PsbtOutputType) -> &'static str {
    match ot {
        PsbtOutputType::RedeemScript => "OUT_REDEEM_SCRIPT",
        PsbtOutputType::WitnessScript => "OUT_WITNESS_SCRIPT",
        PsbtOutputType::Bip32Derivation => "OUT_BIP32_DERIVATION",
    }
}

pub fn psbt_input_type_tostr(it: PsbtInputType) -> &'static str {
    match it {
        PsbtInputType::NonWitnessUtxo => "IN_NON_WITNESS_UTXO",
        PsbtInputType::WitnessUtxo => "IN_WITNESS_UTXO",
        PsbtInputType::PartialSig => "IN_PARTIAL_SIG",
        PsbtInputType::SighashType => "IN_SIGHASH_TYPE",
        PsbtInputType::RedeemScript => "IN_REDEEM_SCRIPT",
        PsbtInputType::WitnessScript => "IN_WITNESS_SCRIPT",
        PsbtInputType::Bip32Derivation => "IN_BIP32_DERIVATION",
        PsbtInputType::FinalScriptSig => "IN_FINAL_SCRIPTSIG",
        PsbtInputType::FinalScriptWitness => "IN_FINAL_SCRIPTWITNESS",
    }
}

/// Fail with OobWrite unless `extra` more bytes fit in the capacity.
fn reserve(psbt: &Psbt, extra: usize) -> Result<(), PsbtResult> {
    if psbt.data.len() + extra > psbt.data_capacity {
        set_err("write out of bounds");
        return Err(PsbtResult::OobWrite);
    }
    Ok(())
}

fn write_header(psbt: &mut Psbt) -> Result<(), PsbtResult> {
    reserve(psbt, PSBT_MAGIC.len() + 1)?;
    psbt.data.extend_from_slice(&PSBT_MAGIC);
    psbt.data.push(0xff);
    psbt.write_pos = psbt.data.len();
    psbt.state = PsbtState::Global;
    Ok(())
}

fn close_records(psbt: &mut Psbt) -> Result<(), PsbtResult> {
    reserve(psbt, 1)?;
    psbt.data.push(0);
    psbt.write_pos = psbt.data.len();
    Ok(())
}

/// Serialize a compactsize value into its wire bytes.
fn compact_bytes(v: u64) -> Vec<u8> {
    let mut buf = vec![0u8; compactsize_length(v) as usize];
    compactsize_write(&mut buf, v);
    buf
}

/// Append one key/value record (C psbt_write_record).
fn write_record(psbt: &mut Psbt, rec: &PsbtRecord) -> PsbtResult {
    let key_len_bytes = compact_bytes(rec.key.len() as u64 + 1);
    let val_len_bytes = compact_bytes(rec.val.len() as u64);
    let total = key_len_bytes.len() + 1 + rec.key.len() + val_len_bytes.len() + rec.val.len();
    if let Err(res) = reserve(psbt, total) {
        return res;
    }
    psbt.data.extend_from_slice(&key_len_bytes);
    psbt.data.push(rec.record_type);
    psbt.data.extend_from_slice(&rec.key);
    psbt.data.extend_from_slice(&val_len_bytes);
    psbt.data.extend_from_slice(&rec.val);
    psbt.write_pos = psbt.data.len();
    PsbtResult::Ok
}

/// Write a global record into the PSBT.
pub fn psbt_write_global_record(psbt: &mut Psbt, rec: &PsbtRecord) -> PsbtResult {
    if psbt.state == PsbtState::Init {
        if let Err(res) = write_header(psbt) {
            return res;
        }
    } else if psbt.state != PsbtState::Global {
        set_err("psbt_write_global_record: only valid after psbt_init and before input records");
        return PsbtResult::InvalidState;
    }
    write_record(psbt, rec)
}

/// Write an input record into the PSBT.
pub fn psbt_write_input_record(psbt: &mut Psbt, rec: &PsbtRecord) -> PsbtResult {
    if psbt.state == PsbtState::Global {
        if let Err(res) = close_records(psbt) {
            return res;
        }
        psbt.state = PsbtState::Inputs;
    } else if psbt.state != PsbtState::Inputs && psbt.state != PsbtState::InputsNew {
        set_err("psbt_write_input_record: write global records first");
        return PsbtResult::InvalidState;
    }
    write_record(psbt, rec)
}

/// Write an output record into the PSBT.
pub fn psbt_write_output_record(psbt: &mut Psbt, rec: &PsbtRecord) -> PsbtResult {
    if psbt.state == PsbtState::Inputs {
        if let Err(res) = close_records(psbt) {
            return res;
        }
        psbt.state = PsbtState::Outputs;
    } else if psbt.state != PsbtState::Outputs && psbt.state != PsbtState::OutputsNew {
        set_err("psbt_write_output_record: write input records first");
        return PsbtResult::InvalidState;
    }
    write_record(psbt, rec)
}

/// Create a new input record set.
pub fn psbt_new_input_record_set(_psbt: &mut Psbt) -> PsbtResult {
    match _psbt.state {
        PsbtState::Global | PsbtState::InputsNew | PsbtState::Inputs => {
            if let Err(res) = close_records(_psbt) {
                return res;
            }
            _psbt.state = PsbtState::InputsNew;
            PsbtResult::Ok
        }
        _ => {
            set_err("psbt_new_input_record_set: called in an invalid state");
            PsbtResult::InvalidState
        }
    }
}

/// Create a new output record set.
pub fn psbt_new_output_record_set(psbt: &mut Psbt) -> PsbtResult {
    match psbt.state {
        PsbtState::Inputs | PsbtState::InputsNew | PsbtState::OutputsNew | PsbtState::Outputs => {
            if let Err(res) = close_records(psbt) {
                return res;
            }
            psbt.state = PsbtState::OutputsNew;
            PsbtResult::Ok
        }
        _ => {
            set_err("psbt_new_output_record_set: this can only be called after writing input records");
            PsbtResult::InvalidState
        }
    }
}

/// Initialize a PSBT using the given destination buffer.
pub fn psbt_init(psbt: &mut Psbt, _dest: &mut [u8], dest_size: usize) -> PsbtResult {
    psbt.data.clear();
    psbt.data_capacity = dest_size;
    psbt.write_pos = 0;
    psbt.state = PsbtState::Init;
    psbt.records.clear();
    PsbtResult::Ok
}

/// Print the PSBT (only succeeds after finalization).
pub fn psbt_print(psbt: &Psbt, stream: &mut dyn std::io::Write) -> PsbtResult {
    if psbt.state != PsbtState::Finalized {
        set_err("psbt_print: transaction is not finished");
        return PsbtResult::InvalidState;
    }
    for byte in &psbt.data {
        if write!(stream, "{byte:02x}").is_err() {
            return PsbtResult::WriteError;
        }
    }
    if writeln!(stream).is_err() {
        return PsbtResult::WriteError;
    }
    PsbtResult::Ok
}

/// Finalize the PSBT.
pub fn psbt_finalize(psbt: &mut Psbt) -> PsbtResult {
    if psbt.state != PsbtState::OutputsNew && psbt.state != PsbtState::Outputs {
        set_err("psbt_finalize: no output records found");
        return PsbtResult::InvalidState;
    }
    if let Err(res) = close_records(psbt) {
        return res;
    }
    psbt.state = PsbtState::Finalized;
    PsbtResult::Ok
}

fn hex_char(val: u8) -> u8 {
    if val < 10 {
        b'0' + val
    } else {
        b'a' + val - 10
    }
}

/// Encode raw PSBT data into dest using the requested encoding.
pub fn psbt_encode_raw(
    psbt_data: &[u8],
    _psbt_len: usize,
    encoding: PsbtEncoding,
    dest: &mut [u8],
    dest_size: usize,
    out_len: &mut usize,
) -> PsbtResult {
    let dest_len = dest_size.min(dest.len());
    let dest = &mut dest[..dest_len];
    match encoding {
        PsbtEncoding::Hex => {
            let hex: Vec<u8> = psbt_data
                .iter()
                .flat_map(|&b| [hex_char(b >> 4), hex_char(b & 0x0f)])
                .chain(std::iter::once(0))
                .collect();
            if hex.len() > dest.len() {
                set_err("psbt_encode: destination too small");
                return PsbtResult::OobWrite;
            }
            dest[..hex.len()].copy_from_slice(&hex);
            *out_len = psbt_data.len() * 2 + 1;
            PsbtResult::Ok
        }
        PsbtEncoding::Base64 => match base64_encode(psbt_data, dest) {
            Some(len) => {
                *out_len = len;
                PsbtResult::Ok
            }
            None => {
                set_err("psbt_encode: base64 encode failure");
                PsbtResult::WriteError
            }
        },
        PsbtEncoding::Base62 => match base62_encode(psbt_data, dest) {
            Some(len) => {
                *out_len = len;
                PsbtResult::Ok
            }
            None => {
                set_err("psbt_encode: base62 encode failure");
                PsbtResult::WriteError
            }
        },
        PsbtEncoding::Protobuf => PsbtResult::NotImplemented,
    }
}

/// Encode the PSBT data into a destination buffer using the requested encoding.
pub fn psbt_encode(
    psbt: &Psbt,
    encoding: PsbtEncoding,
    dest: &mut [u8],
    dest_size: usize,
    out_len: &mut usize,
) -> PsbtResult {
    if psbt.state != PsbtState::Finalized {
        set_err("psbt_encode: psbt not in finalized state");
        return PsbtResult::WriteError;
    }
    psbt_encode_raw(&psbt.data, psbt_size(psbt), encoding, dest, dest_size, out_len)
}
