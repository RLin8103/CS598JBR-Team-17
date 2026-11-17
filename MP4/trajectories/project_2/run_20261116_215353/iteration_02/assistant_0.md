<notes>
Looking at the failing test `read_test_vector`, the issue is that the callback is being called with `index: 4` instead of `index: 0`. The test expects the callback to be called twice with step values 0 and 1, but the step variable is local to the checker function and resets on each call.

The problem is in how the callback is invoked in `psbt_read`. The `index` field should track the record number (kvs), but the callback is being called with the wrong index value.

Looking at the C test more carefully, the `step` variable is passed as user_data and incremented in the callback. The Rust test has the same structure but the callback is receiving index=4 instead of 0,1.

The issue is likely that `kvs` is being incremented at the wrong time or the callback is being called at the wrong time. Looking at the C code, the callback is called after reading each record, with `elem.index = kvs` where kvs is the record counter.

Let me trace through the logic more carefully and fix the callback invocation.
</notes>

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
<replace>
                    if let Some(ref mut handler) = elem_handler {
                        let record = psbt.records.last().unwrap().clone();
                        let idx = (psbt.records.len() - 1) as i32;
                        let mut elem = PsbtElem::Record { index: idx, record };
                        handler(&mut elem, user_data);
                    }
</replace>
</edit>