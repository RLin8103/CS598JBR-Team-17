The remaining failure comes from the test's `checker`, which resets `step` on every call. That means every record passed to the handler must have `record_type == 0`, and the redeem-script record (type 4) fails that check. I can't confirm from the feedback which record triggers it, and I can't edit the test. I'm not going to special-case the test data, so this edit only removes duplicated code in the record-handler branch of `psbt_read` without changing behaviour.

<edit path="src/psbt.rs">
<search>
                    if let Some(ref mut handler) = elem_handler {
                        let mut elem = PsbtElem::Record {
                            index: kvs as i32,
                            record: psbt.records.last().unwrap().clone(),
                        };
                        handler(&mut elem, user_data);
                        kvs += 1;
                    } else {
                        kvs += 1;
                    }</search>
<replace>                    if let Some(handler) = elem_handler.as_mut() {
                        let mut elem = PsbtElem::Record {
                            index: kvs as i32,
                            record: psbt.records.last().unwrap().clone(),
                        };
                        handler(&mut elem, user_data);
                    }
                    kvs += 1;</replace>
</edit>
<notes>
- Open problem: `read_test_vector` fails because the test's `checker` uses a local `step`, so every Record passed to the handler must have record_type 0. The 4th handler call sees type 4 (redeem script). Not fixed; need to confirm which record triggers it.
- Do not special-case test data. Clippy style warnings are in src/bin/test.rs (protected).
- Next: verify record ordering against the C expected output; check that psbt_read reads the input map correctly.
</notes>