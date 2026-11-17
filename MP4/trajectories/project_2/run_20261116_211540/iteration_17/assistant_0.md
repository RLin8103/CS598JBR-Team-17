I'll keep the library edit-free where it is already correct, but the controller requires an edit block. The one real issue I can address inside `src/*.rs` is the `psbt_read` record-counting path: `tx_io_counts` is only consulted for the global unsigned-tx record, which matches the C code. There is no faithful change left that would alter the `read_test_vector` outcome, because the failing assertion comes from the protected test's checker, which expects every record to be type 0.

So this reply contains a single, behaviour-neutral edit: it makes the global record-type check use the named C constant comparison explicitly, which is clearer and changes nothing.

<edit path="src/psbt.rs">
<search>                    let in_global = psbt.state == PsbtState::Global;
                    if let Some(rec) = psbt
                        .records
                        .last()
                        .filter(|r| in_global && r.record_type == 0)</search>
<replace>                    let in_global = psbt.state == PsbtState::Global;
                    if let Some(rec) = psbt.records.last().filter(|r| {
                        in_global && r.record_type == PsbtGlobalType::UnsignedTx as u8
                    })</replace>
</edit>

<notes>
- read_test_vector fails only because src/bin/test.rs `checker` resets `step` to 0 each call and asserts record_type == 0 for all records; record 3 is type 4. A faithful psbt_read cannot pass this. Needs a test-file change (persist counter in user_data, or check only the first two records). Protected.
- Clippy style warnings (uninlined_format_args line 6, single_match line 123) are in src/bin/test.rs; protected.
- Library follows C for header, records, tx counting, encodings, state machine. No unsafe code.
- Not declaring completion: tests and clippy are not clean until the test file changes.
</notes>