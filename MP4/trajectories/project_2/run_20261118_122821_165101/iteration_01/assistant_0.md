I'm not picking `read_test_vector` as the next target. Its checker asserts `record_type == 0` for every record and resets `step` on each call, so it rejects the type-4 input records that the C code correctly delivers. That looks like a defect in the test, and I won't work around it.

The regression failure `transaction_callbacks_precede_unsigned_record` points to a real gap. The C `psbt_read` runs `psbt_btc_tx_parse` on the unsigned-tx record and forwards each txin, txout and tx element to the user handler before the record callback. The Rust `psbt_read` only counts inputs and outputs and never emits `PsbtElem::TxElem` events. I'll replace the counter with an element collector that emits those events first, then keep the counts.

<notes>
Hypothesis: read_test_vector is a suspected benchmark defect. Its checker has `let mut step = 0` inside the callback, so it asserts record_type==0 for every record, including legitimate type-4 input records that C also delivers. Not special-casing it.
Real gap: Rust psbt_read never emits TxElem callbacks for the unsigned tx (C tx_counter forwards txin/txout/tx before the record callback). Fix: tx.rs collects elements via parse_tx; psbt.rs emits them to the handler and derives counts from them.
Next: check whether transaction_callbacks_precede_unsigned_record passes; then look at encode_hex/encode_honors_input_prefix (declared source length ignored) and decode prefix/length checks.
</notes>

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
<replace>/// Parse a serialized transaction into its elements, in C emission order.
pub(crate) fn tx_elements(tx: &[u8]) -> Result<Vec<PsbtTxElem>, PsbtResult> {
    let mut elems = Vec::new();
    parse_tx(tx, |elem| elems.push(elem))?;
    Ok(elems)
}
</replace>
</edit>
<edit path="src/psbt.rs">
<search>
                    let in_global = psbt.state == PsbtState::Global;
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
<replace>                    let in_global = psbt.state == PsbtState::Global;
                    let unsigned_tx = psbt
                        .records
                        .last()
                        .filter(|r| in_global && r.record_type == 0)
                        .map(|r| r.val.clone());
                    if let Some(tx_bytes) = unsigned_tx {
                        let elems = match tx_elements(&tx_bytes) {
                            Ok(e) => e,
                            Err(res) => return res,
                        };
                        counts = (
                            elems
                                .iter()
                                .filter(|e| matches!(e, PsbtTxElem::TxIn(_)))
                                .count(),
                            elems
                                .iter()
                                .filter(|e| matches!(e, PsbtTxElem::TxOut(_)))
                                .count(),
                        );
                        if let Some(handler) = elem_handler.as_mut() {
                            for txelem in elems {
                                let mut elem = PsbtElem::TxElem {
                                    index: kvs as i32,
                                    txelem,
                                };
                                handler(&mut elem, user_data);
                            }
                        }
                    }
</search>
</edit>
 