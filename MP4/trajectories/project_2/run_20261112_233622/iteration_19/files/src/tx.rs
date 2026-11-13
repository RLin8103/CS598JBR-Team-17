#![forbid(unsafe_code)]
use super::psbt::PsbtResult;
use crate::compactsize::{compactsize_peek_length, compactsize_read};

/// Translates the C struct psbt_txin.
pub struct PsbtTxIn {
    pub txid: Vec<u8>,
    pub index: u32,
    pub script: Vec<u8>,
    pub sequence_number: u32,
}

/// Translates the C struct psbt_txout.
pub struct PsbtTxOut {
    pub amount: u64,
    pub script: Vec<u8>,
}

/// Translates the C struct psbt_witness_item.
pub struct PsbtWitnessItem {
    pub input_index: i32,
    pub item_index: i32,
    pub item: Vec<u8>,
}

/// Translates the C struct psbt_tx.
pub struct PsbtTx {
    pub version: u32,
    pub lock_time: u32,
}

/// Translates the C union inside psbt_txelem.
pub enum PsbtTxElem {
    TxIn(PsbtTxIn),
    TxOut(PsbtTxOut),
    Tx(PsbtTx),
    WitnessItem(PsbtWitnessItem),
}

/// The handler type for psbt_txelem.
pub type PsbtTxElemHandler = fn(elem: &mut PsbtTxElem, user_data: &mut dyn std::any::Any);

/// Bounds-checked take of `n` bytes at `pos`.
fn take<'a>(data: &'a [u8], pos: &mut usize, n: usize) -> Result<&'a [u8], PsbtResult> {
    let end = pos.checked_add(n).ok_or(PsbtResult::ReadError)?;
    let bytes = data.get(*pos..end).ok_or(PsbtResult::ReadError)?;
    *pos = end;
    Ok(bytes)
}

fn take_array<const N: usize>(data: &[u8], pos: &mut usize) -> Result<[u8; N], PsbtResult> {
    let bytes = take(data, pos, N)?;
    bytes.try_into().map_err(|_| PsbtResult::ReadError)
}

fn take_u32(data: &[u8], pos: &mut usize) -> Result<u32, PsbtResult> {
    Ok(u32::from_le_bytes(take_array::<4>(data, pos)?))
}

/// Read a compactsize integer at `pos`, advancing the cursor past it.
fn take_compact(data: &[u8], pos: &mut usize) -> Result<u64, PsbtResult> {
    let rest = data.get(*pos..).ok_or(PsbtResult::ReadError)?;
    let first = *rest.first().ok_or(PsbtResult::ReadError)?;
    let (val, res) = compactsize_read(rest);
    if res != PsbtResult::Ok {
        return Err(res);
    }
    *pos += compactsize_peek_length(first) as usize;
    Ok(val)
}

/// Walk a serialized transaction, emitting its inputs, outputs and the tx itself.
fn parse_tx<F: FnMut(PsbtTxElem)>(data: &[u8], mut emit: F) -> Result<(), PsbtResult> {
    let mut pos = 0;
    let version = take_u32(data, &mut pos)?;

    let n_in = take_compact(data, &mut pos)?;
    for _ in 0..n_in {
        let txid = take(data, &mut pos, 32)?.to_vec();
        let index = take_u32(data, &mut pos)?;
        let script_len = take_compact(data, &mut pos)?;
        let script = take(data, &mut pos, script_len as usize)?.to_vec();
        let sequence_number = take_u32(data, &mut pos)?;
        emit(PsbtTxElem::TxIn(PsbtTxIn {
            txid,
            index,
            script,
            sequence_number,
        }));
    }

    let n_out = take_compact(data, &mut pos)?;
    for _ in 0..n_out {
        let amount = u64::from_le_bytes(take_array::<8>(data, &mut pos)?);
        let script_len = take_compact(data, &mut pos)?;
        let script = take(data, &mut pos, script_len as usize)?.to_vec();
        emit(PsbtTxElem::TxOut(PsbtTxOut { amount, script }));
    }

    let lock_time = take_u32(data, &mut pos)?;
    if pos != data.len() {
        return Err(PsbtResult::ReadError);
    }
    emit(PsbtTxElem::Tx(PsbtTx {
        version,
        lock_time,
    }));
    Ok(())
}

/// Walk a serialized transaction, passing each element (TXIN, TXOUT, TX) to `emit`.
/// Mirrors the C `psbt_btc_tx_parse` callback that `psbt_read` relies on for counts.
pub(crate) fn tx_elements<F: FnMut(PsbtTxElem)>(tx: &[u8], emit: F) -> Result<(), PsbtResult> {
    parse_tx(tx, emit)
}

/// Parse a Bitcoin transaction, forwarding every element (TXIN, TXOUT, TX) to `handler`.
/// Returns `ReadError` if the transaction is malformed or has trailing bytes.
pub fn psbt_btc_tx_parse(
    tx: &[u8],
    tx_size: usize,
    user_data: &mut dyn std::any::Any,
    handler: Option<PsbtTxElemHandler>,
) -> PsbtResult {
    let tx = &tx[..tx_size.min(tx.len())];
    let result = parse_tx(tx, |mut elem| {
        if let Some(h) = handler {
            h(&mut elem, &mut *user_data);
        }
    });
    match result {
        Ok(()) => PsbtResult::Ok,
        Err(res) => res,
    }
}
