<notes>
The test `read_test_vector` is failing because the callback `checker` has a local `step` variable that gets reset to 0 on each call. The test passes `&mut ()` as user_data but should pass a mutable reference to an integer counter. Since I cannot edit the test, I need to check if the callback is being called the expected number of times.

Looking at the error: `assertion left == right failed left: 4 right: 0`. This means the callback is being called 4 times total, but the test expects only 2 (step 0 and 1).

The test callback only handles `PsbtElem::Record`, not `PsbtElem::TxElem`. If the implementation is calling the callback for txelems as well, that would explain the extra calls.

Let me check if the callback should only be called for records, not txelems.
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
                        let mut elem = PsbtElem::Record {
                            index: kvs as i32,
                            record: psbt.records.last().unwrap().clone(),
                        };
                        handler(&mut elem, user_data);
                        kvs += 1;
                    } else {
                        kvs += 1;
                    }
</replace>
</edit>