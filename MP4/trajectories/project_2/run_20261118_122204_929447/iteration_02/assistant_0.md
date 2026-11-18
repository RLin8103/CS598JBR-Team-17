The remaining failures come from ignoring declared sizes, not from the reader core. I'm fixing four things:

- **Declared lengths:** `psbt_read`, `psbt_decode` and `psbt_encode_raw` now reject a declared length larger than the backing slice, honour the declared length as a prefix, and clamp destinations to `dest_size`.
- **Transaction callbacks:** the unsigned-tx parse now emits `TxElem` events through the handler before the global record callback. The element list is shared with the counting logic.
- **Error context:** `psbt_geterr` returns the last message set by the encoder, via a `Mutex` static.
- **Unknown global type:** `psbt_type_tostr` returns `UNKNOWN_GLOBAL_TYPE` for non-zero global types.

`read_test_vector` is still treated as a suspected benchmark defect (its checker asserts type 0 on every record, but the fixture contains type 4). I am not changing the translation for it.

<notes>
- Iteration 3. Fixes applied: declared src/dest sizes honoured (prefix + reject oversized), tx callbacks emitted as PsbtElem::TxElem before the unsigned-tx record callback, psbt_geterr backed by a Mutex with a finalization message, psbt_type_tostr Global unknown -> UNKNOWN_GLOBAL_TYPE.
- Suspected benchmark defect (unresolved, not translated around): read_test_vector asserts record_type == 0 for every record, but fixture has type 4 record. Report, do not special-case.
- Remaining risk: clippy style warnings are only in protected src/bin/test.rs.
</notes>

<edit path="src/psbt.rs">
<search>
    if src_size > psbt.data_capacity {
        return PsbtResult::OobWrite;
    }
</search>
<replace>
    if src_size > psbt.data_capacity {
        return PsbtResult::OobWrite;
    }
    if src_size > src.len() {
        return PsbtResult::ReadError;
    }
</replace>
</edit>
<edit path="src/psbt.rs">
<search>
                        counts = match tx_io_counts(&rec.val) {
                            Ok(c) => c,
                            Err(res) => return res,
                        };
</search>
<replace>
                        let elems = match tx_elements(&rec.val) {
                            Ok(e) => e,
                            Err(res) => return res,
                        };
                        counts = count_io(&elems);
                        if let Some(handler) = elem_handler {
                            for txelem in elems {
                                let mut elem = PsbtElem::TxElem {
                                    index: kvs as i32,
                                    txelem,
                                };
                                handler(&mut elem, user_data);
                            }
                        }
</replace>
</edit>
<edit path="src/psbt.rs">
<search>
    _src_size: usize,
    dest: &mut [u8],
    dest_size: usize,
    psbt_len: &mut usize,
) -> PsbtResult {
    let b64_magic = "cHNid";
</search>
<replace>
    src_size: usize,
    dest: &mut [u8],
    dest_size: usize,
    psbt_len: &mut usize,
) -> PsbtResult {
    let Some(src) = src.get(..src_size) else {
        return PsbtResult::ReadError;
    };
    let dest = &mut dest[..dest_size.min(dest.len())];
    let b64_magic = "cHNid";
</replace>
</edit>
<edit path="src/psbt.rs">
<search>
    _psbt_len: usize,
    encoding: PsbtEncoding,
    dest: &mut [u8],
    dest_size: usize,
    out_len: &mut usize,
) -> PsbtResult {
    match encoding {
        PsbtEncoding::Hex => {
            if dest_size < psbt_data.len() * 2 + 1 {
</search>
<replace>
    psbt_len: usize,
    encoding: PsbtEncoding,
    dest: &mut [u8],
    dest_size: usize,
    out_len: &mut usize,
) -> PsbtResult {
    let Some(psbt_data) = psbt_data.get(..psbt_len) else {
        return PsbtResult::ReadError;
    };
    let dest = &mut dest[..dest_size.min(dest.len())];
    match encoding {
        PsbtEncoding::Hex => {
            if dest.len() < psbt_data.len() * 2 + 1 {
</replace>
</edit>
<edit path="src/psbt.rs">
<search>
        return PsbtResult::WriteError;
</search>
<replace>
        set_err("psbt_encode: psbt not in finalized state; use psbt_read or the psbt_write functions");
        return PsbtResult::WriteError;
</replace>
</edit>
<edit path="src/psbt.rs">
<search>
pub fn psbt_geterr() -> &'static str {
    PSBT_ERRMSG
}
</search>
<replace>
static LAST_ERR: std::sync::Mutex<&'static str> = std::sync::Mutex::new("psbt error");

fn set_err(msg: &'static str) {
    if let Ok(mut slot) = LAST_ERR.lock() {
        *slot = msg;
    }
}

fn count_io(elems: &[PsbtTxElem]) -> (usize, usize) {
    elems.iter().fold((0, 0), |(i, o), e| match e {
        PsbtTxElem::TxIn(_) => (i + 1, o),
        PsbtTxElem::TxOut(_) => (i, o + 1),
        _ => (i, o),
    })
}

pub fn psbt_geterr() -> &'static str {
    LAST_ERR.lock().map_or(PSBT_ERRMSG, |slot| *slot)
}
</replace>
</edit>
<edit path="src/psbt.rs">
<search>
        PsbtScope::Global => psbt_global_type_tostr(PsbtGlobalType::UnsignedTx),
</search>
<replace>
        PsbtScope::Global => match record_type {
            0 => psbt_global_type_tostr(PsbtGlobalType::UnsignedTx),
            _ => "UNKNOWN_GLOBAL_TYPE",
        },
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
<replace>/// Collect all elements of a serialized transaction, in C callback order.
pub(crate) fn tx_elements(tx: &[u8]) -> Result<Vec<PsbtTxElem>, PsbtResult> {
    let mut elems = Vec::new();
    parse_tx(tx, |elem| elems.push(elem))?;
    Ok(elems)
}
</replace>
</edit>