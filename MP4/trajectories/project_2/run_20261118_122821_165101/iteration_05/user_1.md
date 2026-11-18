Requested files:

### src/bin/test.rs (lines 100–135)
```
    // Now psbt_print should succeed.
    let res = psbt_print(&psbt_instance, &mut stdout);
    assert_eq!(res, PsbtResult::Ok);
}

/// Transpiled from test.c: simulate reading a PSBT with a callback.
#[test]
fn read_test_vector() {
    let mut buf = vec![0u8; 2048];
    let mut intbuf = vec![0u8; 2048];
    let mut psbt_len = 0;
    let hexlen = PSBT_HEX.len();
    let mut psbt_instance = Psbt::new(2048);

    let res = psbt_decode(PSBT_HEX, hexlen, &mut buf, 2048, &mut psbt_len);
    assert_eq!(res, PsbtResult::Ok);

    let res = psbt_init(&mut psbt_instance, &mut intbuf, 2048);
    assert_eq!(res, PsbtResult::Ok);

    // The callback checks that the first element is a global record and the second is an input record.
    fn checker(elem: &mut PsbtElem, _ud: &mut dyn std::any::Any) {
        let mut step = 0;
        match elem {
            PsbtElem::Record { record, .. } => {
                match step {
                    0 => assert_eq!(record.record_type, 0), // PSBT_GLOBAL_UNSIGNED_TX
                    1 => assert_eq!(record.record_type, 0), // PSBT_IN_NON_WITNESS_UTXO (simulated as 0)
                    _ => {}
                }
            }
            _ => {}
        }
        step += 1;
    }
    let res = psbt_read(&buf, psbt_len, &mut psbt_instance, Some(checker), &mut ());

```

Now write your edits in this same turn. Do not reply with only <read> blocks again.