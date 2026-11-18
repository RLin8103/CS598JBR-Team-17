The previous edit failed because `tx_io_counts` was not visible to `psbt.rs`. I'll rewrite `tx.rs` so it exposes a crate-visible `tx_elements` that returns every transaction element, and have `psbt_read` emit those `TxElem` callbacks before the unsigned-tx record. That also fixes the `transaction_callbacks_precede_unsigned_record` ordering. The `mut` on `elem_handler` becomes unnecessary, so I'm dropping it too.

<file path="src/tx.rs">
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

/// Parse a serialized transaction into its elements (inputs, outputs, tx), in C callback order.
pub(crate) fn tx_elements(tx: &[u8]) -> Result<Vec<PsbtTxElem>, PsbtResult> {
    let mut out = Vec::new();
    parse_tx(tx, |e| out.push(e))?;
    Ok(out)
}

/// Parse a Bitcoin transaction, forwarding every element to `handler`.
pub fn psbt_btc_tx_parse(
    tx: &[u8],
    tx_size: usize,
    user_data: &mut dyn std::any::Any,
    handler: Option<PsbtTxElemHandler>,
) -> PsbtResult {
    let tx = &tx[..tx_size.min(tx.len())];
    let result = parse_tx(tx, |mut elem| {
        if let Some(h) = handler {
            h(&mut elem, user_data);
        }
    });
    match result {
        Ok(()) => PsbtResult::Ok,
        Err(res) => res,
    }
}
</file>

<edit path="src/psbt.rs">
<search>
pub fn psbt_read(
    src: &[u8],
    src_size: usize,
    psbt: &mut Psbt,
    mut elem_handler: Option<PsbtElemHandler>,</search>
<replace>pub fn psbt_read(
    src: &[u8],
    src_size: usize,
    psbt: &mut Psbt,
    elem_handler: Option<PsbtElemHandler>,</replace>
</edit>

<edit path="src/psbt.rs">
<search>                    let in_global = psbt.state == PsbtState::Global;
                    if let Some(rec) = psbt
                        .records
                        .last()
                        .filter(|r| in_global && r.record_type == 0)
                    {
                        counts = match tx_io_counts(&rec.val) {
                            Ok(c) => c,
                            Err(res) => return res,
                        };
                    }

                    if let Some(handler) = elem_handler.as_mut() {
                        let mut elem = PsbtElem::Record {
                            index: kvs as i32,
                            record: psbt.records.last().unwrap().clone(),
                        };
                        handler(&mut elem, user_data);
                    }</search>
<replace>                    let in_global = psbt.state == PsbtState::Global;
                    if let Some(rec) = psbt.records.last().cloned() {
                        let txelems = if in_global && rec.record_type == 0 {
                            let v = match tx_elements(&rec.val) {
                                Ok(v) => v,
                                Err(res) => return res,
                            };
                            counts = (
                                v.iter()
                                    .filter(|e| matches!(e, PsbtTxElem::TxIn(_)))
                                    .count(),
                                v.iter()
                                    .filter(|e| matches!(e, PsbtTxElem::TxOut(_)))
                                    .count(),
                            );
                            v
                        } else {
                            Vec::new()
                        };

                        if let Some(handler) = elem_handler {
                            for txelem in txelems {
                                let mut elem = PsbtElem::TxElem {
                                    index: kvs as i32,
                                    txelem,
                                };
                                handler(&mut elem, user_data);
                            }
                            let mut elem = PsbtElem::Record {
                                index: kvs as i32,
                                record: rec,
                            };
                            handler(&mut elem, user_data);
                        }
                    }</replace>
</edit>

<notes>
- Fixed compile error: tx.rs now exposes pub(crate) tx_elements (returns all tx elements in C callback order) and no longer has tx_io_counts; psbt_read derives input/output counts from those elements.
- psbt_read now emits TxElem callbacks (txin, txout, tx) before the unsigned-tx Record callback, matching C tx_counter forwarding.
- Remaining failing tests: read_test_vector (suspected benchmark defect: checker asserts record_type==0 for all records), encode/decode declared-length tests (psbt_encode_raw/psbt_decode ignore src_size/declared lengths and dest limits), base64 decode dest limit, errors_include_useful_context (psbt_geterr returns constant message; C sets errmsg per failure).
- Clippy style warnings are in protected src/bin/test.rs; cannot fix from our files.
- Next: fix encode_hex/encode_base64 declared-source-length handling and decode prefix/length checks.
</notes>