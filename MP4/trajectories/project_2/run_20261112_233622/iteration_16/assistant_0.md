I'm making one fidelity fix and then stopping. The C `psbt_read` forwards each transaction element (TXIN, TXOUT, TX) to the user handler through `tx_counter`. The Rust version only counts them. I'm adding that forwarding. It does not change the outcome of `read_test_vector`: the protected checker still sees the type-4 input record with `step` fixed at 0, and that assertion fails in the same way.

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
<replace>/// Walk a serialized transaction, passing each element to `emit`
/// (mirrors the C `psbt_btc_tx_parse` callback used by `psbt_read`).
pub(crate) fn tx_elements<F: FnMut(PsbtTxElem)>(tx: &[u8], emit: F) -> Result<(), PsbtResult> {
    parse_tx(tx, emit)
}
</replace>
</edit>
<edit path="src/psbt.rs">
<search>
    mut elem_handler: Option<PsbtElemHandler>,
</search>
<replace>    elem_handler: Option<PsbtElemHandler>,
</replace>
</edit>
<edit path="src/psbt.rs">
<search>
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
</search>
<replace>                    let Some(rec) = psbt.records.last().cloned() else {
                        return PsbtResult::ReadError;
                    };
                    if in_global && rec.record_type == 0 {
                        let mut new_counts = (0usize, 0usize);
                        let handler = elem_handler;
                        let res = tx_elements(&rec.val, |txelem| {
                            match &txelem {
                                PsbtTxElem::TxIn(_) => new_counts.0 += 1,
                                PsbtTxElem::TxOut(_) => new_counts.1 += 1,
                                _ => {}
                            }
                            if let Some(h) = handler {
                                let mut elem = PsbtElem::TxElem {
                                    index: kvs as i32,
                                    txelem,
                                };
                                h(&mut elem, &mut *user_data);
                            }
                        });
                        if let Err(e) = res {
                            return e;
                        }
                        counts = new_counts;
                    }
</replace>
</edit>
<edit path="src/psbt.rs">
<search>
                    if let Some(ref mut handler) = elem_handler {
                        let mut elem = PsbtElem::Record {
                            index: kvs as i32,
                            record: psbt.records.last().unwrap().clone(),
                        };
                        handler(&mut elem, user_data);
                    }
</search>
<replace>                    if let Some(handler) = elem_handler {
                        let mut elem = PsbtElem::Record {
                            index: kvs as i32,
                            record: rec,
                        };
                        handler(&mut elem, user_data);
                    }
</replace>
</edit>
<notes>
- All interface stubs implemented; no unimplemented!()/todo!() remains. Zero unsafe; every module has #![forbid(unsafe_code)].
- Iteration 16: psbt_read now forwards transaction elements (TXIN/TXOUT/TX) to the handler as PsbtElem::TxElem, matching C's tx_counter. Counts come from the same parse. Not yet compiled; check for borrow or unused-import errors first.
- 6/8 tests pass before this change. read_test_vector still fails in the protected test: its checker keeps `step` as a local (always 0) and asserts record_type == 0 on every Record callback. The C handler also gets the type-4 input record, so no faithful fix exists. Not special-casing.
- Clippy: 0 in src/*.rs; the 2 style warnings are in protected src/bin/test.rs.
- Not declaring done: two tests fail and clippy reports two warnings, all in protected files.
</notes>