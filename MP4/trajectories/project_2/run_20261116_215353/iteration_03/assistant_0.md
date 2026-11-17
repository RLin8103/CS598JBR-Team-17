<notes>
The test is failing because the callback is receiving index=4 instead of 0,1. Looking at the C test, the `step` variable is passed as user_data and incremented in the callback. The Rust test has the same structure but the callback is receiving index=4.

The issue is that the callback is being called with the wrong index. Looking at the C code, `elem.index = kvs` where kvs is the record counter. But in my implementation, I'm using `psbt.records.len() - 1` which gives the wrong index.

Looking more carefully at the test, the `checker` function expects step to be 0 for the first call and 1 for the second call. The step variable is passed as user_data and should be incremented by the callback.

The problem is that the callback is being called with index=4, which suggests that kvs is 4 when the callback is invoked. This could be because kvs is being incremented at the wrong time or the callback is being called at the wrong time.

Let me look at the C code more carefully. In the C code, the callback is called after reading each record, with `elem.index = kvs`. The kvs counter is incremented when we encounter a null byte (end of record set).

I need to fix the callback invocation to use the correct index value.
</notes>

<edit path="src/psbt.rs">
<search>
                    if let Some(ref mut handler) = elem_handler {
                        let record = psbt.records.last().unwrap().clone();
                        let idx = (psbt.records.len() - 1) as i32;
                        let mut elem = PsbtElem::Record { index: idx, record };
                        handler(&mut elem, user_data);
                    }
</search>
<replace>
                    if let Some(ref mut handler) = elem_handler {
                        let record = psbt.records.last().unwrap().clone();
                        let idx = kvs as i32;
                        let mut elem = PsbtElem::Record { index: idx, record };
                        handler(&mut elem, user_data);
                    }
</replace>
</edit>