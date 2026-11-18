The crate still does not compile. `cli.rs` imports `psbt_encode` and `psbt_init`, which `psbt.rs` does not define, and `psbt.rs` is missing the write, print, finalize, encode and string-table functions from the interface. I am adding those, fixing the `dest` borrow error in `psbt_decode`, and aligning the enum declarations with the interface text.

Plan:
- Fix the `dest` reborrow in `psbt_decode` by computing the length before reslicing.
- Restore the interface enum layouts (multi-line, trailing commas).
- Append the write path (`reserve`/`close_records`/`write_record` with capacity checks), the state machine transitions copied from the C code, `psbt_init`, `psbt_print`, `psbt_finalize`, the encode functions, `psbt_geterr` (backed by the last-error store), and the `*_tostr` tables. `psbt_type_tostr` returns `UNKNOWN_GLOBAL_TYPE` for any global type other than 0, as the C code does.

Notes on the test suite: `read_test_vector` asserts `record_type == 0` for the redeem-script records, which the C test does not do. I am treating that as a benchmark defect and not working around it.

<edit path="src/psbt.rs">
<search>    let dest = &mut dest[..dest_size.min(dest.len())];</search>
<replace>    let dest_len = dest_size.min(dest.len());
    let dest = &mut dest[..dest_len];</replace>
</edit>
<edit path="src/psbt.rs">
<search>pub enum PsbtResult { Ok, CompactReadError, ReadError, WriteError, InvalidState, NotImplemented, OobWrite }</search>
<replace>pub enum PsbtResult {
    Ok,
    CompactReadError,
    ReadError,
    WriteError,
    InvalidState,
    NotImplemented,
    OobWrite,
}</replace>
</edit>
<edit path="src/psbt.rs">
<search>pub enum PsbtEncoding { Hex, Base64, Base62, Protobuf }</search>
<replace>pub enum PsbtEncoding {
    Hex,
    Base64,
    Base62,
    Protobuf,
}</replace>
</edit>
<edit path="src/psbt.rs">
<search>pub enum PsbtOutputType { RedeemScript = 0, WitnessScript = 1, Bip32Derivation = 2 }</search>
<replace>pub enum PsbtOutputType {
    RedeemScript = 0,
    WitnessScript = 1,
    Bip32Derivation = 2,
}</replace>
</edit>
<edit path="src/psbt.rs">
<search>pub enum PsbtScope { Global, Inputs, Outputs }</search>
<replace>pub enum PsbtScope {
    Global,
    Inputs,
    Outputs,
}</replace>
</edit>
<edit path="src/psbt.rs">
<search>pub enum PsbtState { Init = 2, Global, Inputs, InputsNew, Outputs, OutputsNew, Finalized }</search>
<replace>pub enum PsbtState {
    Init = 2,
    Global,
    Inputs,
    InputsNew,
    Outputs,
    OutputsNew,
    Finalized,
}</replace>
</edit>
<edit path="src/psbt.rs">
<search>pub enum PsbtElemType { Record, TxElem }</search>
<replace>pub enum PsbtElemType {
    Record,
    TxElem,
}</replace>
</edit>
<edit path="src/psbt.rs">
<search>pub enum PsbtTxElemType { TxIn, TxOut, Tx, WitnessItem }</search>
<replace>pub enum PsbtTxElemType {
    TxIn,
    TxOut,
    Tx,
    WitnessItem,
}</replace>
</edit>
<append path="src/psbt.rs">

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
</append>