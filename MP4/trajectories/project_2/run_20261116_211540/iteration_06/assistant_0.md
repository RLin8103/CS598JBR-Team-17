The test failure shows `left: 4, right: 0` at line 126. The test's `checker` function has a local `step` variable that's always 0, and it checks `record.record_type == 0` at step 0. But the record type is 4 (PSBT_IN_REDEEM_SCRIPT), meaning the first record being processed is an input record, not the global unsigned transaction.

The issue is in `psbt_read`: the global record (type 0) is being skipped. Looking at the C code, when the global unsigned transaction record is read, the callback is called with it. But in my implementation, the callback is only called after reading the record, and the record is pushed to `psbt.records`. The problem might be that the global record is being read but the callback is not being called for it, or the parsing is wrong.

Let me trace through the PSBT_HEX data. The first few bytes after the header should be:
- Compact size for key length (including type)
- Type byte (0 for global unsigned tx)
- Key data (empty)
- Compact size for value length
- Value data (the transaction)

The issue might be that `compactsize_read` is returning the wrong value, or the key_size is being parsed incorrectly.

Actually, I think I found the real issue. Looking at the C code for `psbt_read_record`:

```c
size_len = compactsize_peek_length(*tx->write_pos);
ASSERT_SPACE(size_len);
size = compactsize_read(tx->write_pos, &res);
assert(size > 0);
tx->write_pos += size_len;
```

The `compactsize_read` function reads from `tx->write_pos` and returns the size. The `compactsize_peek_length` returns the number of bytes used to encode the size. The C code advances `write_pos` by `size_len`.

In my Rust implementation, I'm doing the same thing. But the issue might be that `compactsize_read` is reading the wrong value because the data slice passed to it is wrong.

Let me check the `compactsize_read` function. The first byte after the header is 0x01, which is less than 253, so `compactsize_read` should return (1, Ok). And `compactsize_peek_length(0x01)` should return 1. So `write_pos` should advance by 1.

Then we read the type byte at `write_pos`, which should be 0x00 (type 0 for global unsigned tx). Then we advance `write_pos` by 1 (the type byte).

Then we read the value length. The next byte should be a compact size for the value length.

Wait, I need to look at the PSBT_HEX data more carefully. Let me decode the first few bytes:

"70736274ff" - header (5 bytes)
"01" - compact size for key length (1 byte)
"00" - type byte (0 = global unsigned tx)
... then the value length and value

After "70736274ff0100", the next byte is "9a". This is a compact size. 0x9a = 154, which is less than 253, so the value length is 154 bytes.

So the parsing should work correctly. The first record should have type 0 and a value of 154 bytes (the transaction).

But the test shows that the first record has type 4. This means the global record is being skipped entirely, and the first record being processed is an input record with type 4 (PSBT_IN_REDEEM_SCRIPT).

The issue might be in how the state transitions work. Let me check the C code for `psbt_read`:

```c
case PSBT_ST_GLOBAL:
case PSBT_ST_INPUTS:
case PSBT_ST_OUTPUTS:
    if (*tx->write_pos == 0) {
        switch (tx->state) {
        case PSBT_ST_GLOBAL:
            tx->state = PSBT_ST_INPUTS_NEW;
            break;
        ...
        }
    }
    else {
        // Read record
        res = psbt_read_record(tx, src_size, &rec);
        ...
        // record callback
        if (elem_handler) {
            elem.type = PSBT_ELEM_RECORD;
            elem.index = kvs;
            elem.elem.rec = &rec;
            elem_handler(&elem);
        }
    }
    break;
```

So when the current byte is not 0, it reads a record and calls the callback. When the current byte is 0, it transitions to the next state.

The issue in my implementation might be that after reading the header, the `write_pos` is pointing to the first byte after the header, which should be the first record. But if the first byte is 0, it would transition to InputsNew without reading any records.

But the first byte after the header is 0x01, not 0x00. So it should read a record.

Wait, let me check the PSBT_HEX data again. The full hex string is:

"70736274ff01009a020000000258e87a21b56daf0c23be8e7070456c336f7cbaa5c8757924f545887bb2abdd750000000000ffffffff..."

After the header "70736274ff", the next byte is "01". This is the compact size for the key length. So the first record has a key length of 1 (just the type byte).

Then the type byte is "00" (type 0 for global unsigned tx).

Then the value length is "9a" (154 bytes).

So the parsing should work correctly. The first record should have type 0.

But the test shows type 4. This means something is wrong with the parsing.

Let me check if the issue is with the `compactsize_read` function. The first byte after the header is 0x01, which is less than 253, so `compactsize_read` should return (1, Ok). But what if the data slice passed to `compactsize_read` is wrong?

In my implementation:
```rust
let (key_size, res) = compactsize_read(&psbt.data[psbt.write_pos..]);
```

This should pass the data starting at `write_pos`. If `write_pos` is 5 (after the header), then the data slice starts at byte 5, which is 0x01. So `compactsize_read` should return (1, Ok).

Then `compactsize_peek_length(psbt.data[psbt.write_pos])` should return 1 (since 0x01 < 253).

Then `write_pos` advances by 1 to 6.

Then we read the type byte at `write_pos` (6), which is 0x00. So `record_type` is 0.

Then we advance `write_pos` by 1 (the type byte) to 7.

Then we read the value length. The byte at position 7 is 0x9a, which is less than 253, so `compactsize_read` should return (154, Ok).

Then `compactsize_peek_length(0x9a)` should return 1.

Then `write_pos` advances by 1 to 8.

Then we read 154 bytes of value data.

This all seems correct. So why is the test showing type 4?

Let me check if there's an issue with the `psbt_decode` function. The test calls `psbt_decode` first to decode the hex string into binary data. If the decode function is wrong, the binary data would be wrong.

Let me check the `psbt_decode` function. It checks if the string starts with "cHNid" (base64 magic). If not, it does hex decoding.

The PSBT_HEX string starts with "70736274ff", which is hex, not base64. So it should do hex decoding.

The hex decoding function:
```rust
for (i, c) in src.chars().enumerate() {
    if i % 2 == 0 {
        let c1 = c;
        let c2 = src.chars().nth(i + 1).unwrap();
        ...
    }
}
```

This iterates over every character, but only processes every other character (when i % 2 == 0). For each pair, it reads the current character and the next character. This should work correctly.

But wait, there's a potential issue. The `src.chars().nth(i + 1)` call is O(n) for each iteration, which is inefficient but should still produce the correct result.

Let me check if the hex decoding is producing the correct output. The first few bytes of the decoded data should be:
- 0x70, 0x73, 0x62, 0x74 (PSBT_MAGIC)
- 0xff
- 0x01 (compact size for key length)
- 0x00 (type byte)
- 0x9a (compact size for value length)
- ... (154 bytes of transaction data)

If the hex decoding is correct, then the parsing should work correctly.

But the test shows type 4, which means the first record has type 4. This could happen if the hex decoding is wrong and the first byte after the header is not 0x01 but something else.

Let me check the hex decoding more carefully. The first few characters of PSBT_HEX are:
"70736274ff01009a0200000002..."

The hex decoding should produce:
- "70" -> 0x70
- "73" -> 0x73
- "62" -> 0x62
- "74" -> 0x74
- "ff" -> 0xff
- "01" -> 0x01
- "00" -> 0x00
- "9a" -> 0x9a
- "02" -> 0x02
- ...

This looks correct. So the first byte after the header should be 0x01.

Wait, I think I found the issue. Let me check the `psbt_decode` function more carefully:

```rust
for (i, c) in src.chars().enumerate() {
    if i % 2 == 0 {
        let c1 = c;
        let c2 = src.chars().nth(i + 1).unwrap();
```

The `src.chars().nth(i + 1)` call creates a new iterator and skips `i + 1` characters. This is O(n^2) but should still produce the correct result. However, there's a subtle issue: if the string contains non-ASCII characters, `chars()` might not return the expected characters. But since the input is a hex string, it should only contain ASCII characters.

Actually, I think the issue might be elsewhere. Let me check if the `psbt_read` function is being called with the correct parameters.

In the test:
```rust
let res = psbt_decode(PSBT_HEX, hexlen, &mut buf, 2048, &mut psbt_len);
assert_eq!(res, PsbtResult::Ok);

let res = psbt_init(&mut psbt_instance, &mut intbuf, 2048);
assert_eq!(res, PsbtResult::Ok);

let res = psbt_read(&buf, psbt_len, &mut psbt_instance, Some(checker), &mut ());
assert_eq!(res, PsbtResult::Ok);
```

The `psbt_read` function is called with `&buf` and `psbt_len`. The `buf` contains the decoded binary data. The `psbt_len` is the length of the decoded data.

In `psbt_read`:
```rust
let actual_size = src_size.min(src.len());
psbt.data.clear();
psbt.data.extend_from_slice(&src[..actual_size]);
```

This copies the first `actual_size` bytes from `src` into `psbt.data`. Since `src_size` is `psbt_len` and `src.len()` is 2048, `actual_size` should be `psbt_len`.

But wait, there's a problem. The `psbt_init` function is called with `&mut intbuf`, but the `psbt_read` function uses `src` (which is `&buf`), not `intbuf`. In the C code, `psbt_init` sets up the PSBT with the destination buffer, and then `psbt_read` copies the source data into the PSBT's buffer.

In my implementation, `psbt_init` clears `psbt.data` and sets `data_capacity` to `dest_size`. But it doesn't use the `dest` buffer at all. The `psbt_read` function then copies the source data into `psbt.data`.

This should work correctly. The issue must be elsewhere.

Let me add some debug output to understand what's happening. Actually, I can't modify the test file. Let me look at the code more carefully.

Wait, I think I see the issue now. In the `psbt_read` function, after reading the header and transitioning to `Global`, the code checks if the current byte is 0. If it's not 0, it reads a record. But the issue might be that after reading the header, the `write_pos` is pointing to the first byte after the header, which should be the first record.

But what if the `psbt_decode` function is producing the wrong output? Let me check the hex decoding more carefully.

The PSBT_HEX string is:
"70736274ff01009a020000000258e87a21b56daf0c23be8e7070456c336f7cbaa5c8757924f545887bb2abdd750000000000ffffffff838d0427d0ec650a68aa46bb0b098aea4422c071b2ca78352a077959d07cea1d0100000000ffffffff0270aaf00800000000160014d85c2b71d0060b09c9886aeb815e50991dda124d00e1f5050000000016001400aea9a2e5f0f876a588df5546e8742d1d87008f00000000000100bb0200000001aad73931018bd25f84ae400b68848be09db706eac2ac18298babee71ab656f8b0000000048473044022058f6fc7c6a33e1b31548d481c826c015bd30135aad42cd67790dab66d2ad243b02204a1ced2604c6735b6393e5b41691dd78b00f0c5942fb9f751856faa938157dba01feffffff0280f0fa020000000017a9140fb9463421696b82c833af241c78c17ddbde493487d0f20a270100000017a91429ca74f8a08f81999428185c97b5d852e4063f6187650000000104475221029583bf39ae0a609747ad199addd634fa6108559d6c5cd39b4c2183f1ab96e07f2102dab61ff49a14db6a7d02b0cd1fbb78fc4b18312b5b4e54dae4dba2fbfef536d752ae2206029583bf39ae0a609747ad199addd634fa6108559d6c5cd39b4c2183f1ab96e07f10d90c6a4f000000800000008000000080220602dab61ff49a14db6a7d02b0cd1fbb78fc4b18312b5b4e54dae4dba2fbfef536d710d90c6a4f0000008000000080010000800001012000c2eb0b0000000017a914b7f5faf40e3d40a5a459b1db3535f2b72fa921e88701042200208c2353173743b595dfb4a07b72ba8e42e3797da74e87fe7d9d7497e3b2028903010547522103089dc10c7ac6db54f91329af617333db388cead0c231f723379d1b99030b02dc21023add904f3d6dcf59ddb906b0dee23529b7ffb9ed50e5e86151926860221f0e7352ae2206023add904f3d6dcf59ddb906b0dee23529b7ffb9ed50e5e86151926860221f0e7310d90c6a4f000000800000008003000080220603089dc10c7ac6db54f91329af617333db388cead0c231f723379d1b99030b02dc10d90c6a4f00000080000000800200008000220203a9a4c37f5996d3aa25dbac6b570af0650394492942460b354753ed9eeca5877110d90c6a4f000000800000008004000080002202027f6399757d2eff55a136ad02c684b1838b6556e5f1b6b34282a94b6b5005109610d90c6a4f00000080000000800500008000"

The first few bytes after decoding should be:
0x70, 0x73, 0x62, 0x74, 0xff, 0x01, 0x00, 0x9a, 0x02, 0x00, 0x00, 0x00, 0x02, ...

So after the header (5 bytes), the next byte is 0x01, which is the compact size for the key length. This should work correctly.

But wait, I just realized something. The `psbt_decode` function in the C code also handles base64 decoding. The test's `psbt_decode` function checks if the string starts with "cHNid" (base64 magic). If it does, it does base64 decoding. Otherwise, it does hex decoding.

The PSBT_HEX string starts with "70736274ff", which is hex, not base64. So it should do hex decoding.

But what if the hex decoding is producing the wrong output? Let me check the hex decoding function more carefully.

The hex decoding function:
```rust
for (i, c) in src.chars().enumerate() {
    if i % 2 == 0 {
        let c1 = c;
        let c2 = src.chars().nth(i + 1).unwrap();
        
        let v1 = hex_to_val(c1);
        let v2 = hex_to_val(c2);
        
        if v1 == 0x80 || v2 == 0x80 {
            return PsbtResult::ReadError;
        }
        
        dest[pos] = (v1 << 4) | v2;
        pos += 1;
    }
}
```

This iterates over every character, but only processes every other character (when i % 2 == 0). For each pair, it reads the current character and the next character.

But there's a problem: `src.chars().nth(i + 1)` creates a new iterator and skips `i + 1` characters. This is O(n^2) but should still produce the correct result.

However, there's a subtle issue. The `enumerate()` method returns the index of each character in the iterator. But `chars()` returns Unicode scalar values, not bytes. For ASCII strings, this is fine. But the index might not correspond to the byte position.

Actually, for ASCII strings, `chars()` returns one character per byte, so the index should correspond to the byte position. So this should work correctly.

Let me check if there's an issue with the `psbt_read` function's state machine. The C code has:

```c
while (tx->state != PSBT_ST_FINALIZED && tx->write_pos <= end) {
    switch(tx->state) {
    case PSBT_ST_INIT:
        res = psbt_read_header(tx);
        if (res != PSBT_OK)
            return res;
        break;
    case PSBT_ST_GLOBAL:
    case PSBT_ST_INPUTS:
    case PSBT_ST_OUTPUTS:
        if (*tx->write_pos == 0) {
            switch (tx->state) {
            case PSBT_ST_GLOBAL:
                tx->state = PSBT_ST_INPUTS_NEW;
                break;
            case PSBT_ST_INPUTS:
                if (++kvs >= counter.inputs) {
                    tx->state = PSBT_ST_OUTPUTS_NEW;
                    kvs = 0;
                } else
                    tx->state = PSBT_ST_INPUTS_NEW;
                break;
            case PSBT_ST_OUTPUTS:
                if (++kvs >= counter.outputs)
                    tx->state = PSBT_ST_FINALIZED;
                else
                    tx->state = PSBT_ST_OUTPUTS_NEW;
                break;
            default:
                assert(!"psbt_read: invalid state at null byte");
            }
        }
        else {
            debug("reading record @ %zu\n", tx->write_pos - tx->data);
            res = psbt_read_record(tx, src_size, &rec);
            if (res != PSBT_OK)
                return res;
            if (tx->state == PSBT_ST_GLOBAL &&
                rec.type == PSBT_GLOBAL_UNSIGNED_TX) {
                res = psbt_btc_tx_parse(rec.val, rec.val_size, (void*)&counter, tx_counter);
                if (res != PSBT_OK)
                    return res;
            }
            if (elem_handler) {
                elem.type = PSBT_ELEM_RECORD;
                elem.index = kvs;
                elem.elem.rec = &rec;
                elem_handler(&elem);
            }
        }
        break;
    case PSBT_ST_OUTPUTS_NEW:
        assert(*tx->write_pos == 0);
        tx->write_pos++;
        tx->state = PSBT_ST_OUTPUTS;
        break;
    case PSBT_ST_INPUTS_NEW:
        assert(*tx->write_pos == 0);
        tx->write_pos++;
        tx->state = PSBT_ST_INPUTS;
        break;
    case PSBT_ST_FINALIZED:
        assert(!"impossible");
        break;
    }
}
```

In my implementation, I have a similar state machine. But there's a key difference: in the C code, when the current byte is 0 in the Global state, it transitions to InputsNew. But in my implementation, I also have a check for `psbt.write_pos >= actual_size` that treats it as an end marker.

But the issue might be that after reading the header, the `write_pos` is pointing to the first byte after the header, which should be 0x01. So it should read a record, not transition.

Wait, I think I found the issue. Let me check the `psbt_read` function's handling of the `InputsNew` and `OutputsNew` states.

In the C code:
```c
case PSBT_ST_OUTPUTS_NEW:
    assert(*tx->write_pos == 0);
    tx->write_pos++;
    tx->state = PSBT_ST_OUTPUTS;
    break;
case PSBT_ST_INPUTS_NEW:
    assert(*tx->write_pos == 0);
    tx->write_pos++;
    tx->state = PSBT_ST_INPUTS;
    break;
```

In my implementation:
```rust
PsbtState::InputsNew => {
    if psbt.write_pos >= actual_size || psbt.data[psbt.write_pos] != 0 {
        return PsbtResult::ReadError;
    }
    psbt.write_pos += 1;
    psbt.state = PsbtState::Inputs;
}

PsbtState::OutputsNew => {
    if psbt.write_pos >= actual_size || psbt.data[psbt.write_pos] != 0 {
        return PsbtResult::ReadError;
    }
    psbt.write_pos += 1;
    psbt.state = PsbtState::Outputs;
}
```

This looks correct. The null byte is consumed and the state is updated.

But wait, there's an issue with the order of operations. In the C code, when the current byte is 0 in the Global state, it transitions to InputsNew. Then in the next iteration of the while loop, it processes the InputsNew state, which consumes the null byte and transitions to Inputs.

In my implementation, I do the same thing. But there's a subtle difference: in the C code, the null byte is consumed in the InputsNew/OutputsNew states, not in the Global/Inputs/Outputs states. So when the current byte is 0 in the Global state, it transitions to InputsNew, and then in the next iteration, the InputsNew state consumes the null byte.

But in my implementation, I also have a check for `psbt.write_pos >= actual_size` that treats it as an end marker. This might be causing issues.

Actually, I think the issue is simpler. Let me check the `psbt_read` function's handling of the `Global` state when the current byte is 0.

In the C code:
```c
case PSBT_ST_GLOBAL:
    if (*tx->write_pos == 0) {
        tx->state = PSBT_ST_INPUTS_NEW;
    }
    else {
        // Read record
    }
    break;
```

In my implementation:
```rust
PsbtState::Global | PsbtState::Inputs | PsbtState::Outputs => {
    if psbt.write_pos >= actual_size {
        // Treat as end marker
        match psbt.state {
            PsbtState::Global => {
                psbt.state = PsbtState::InputsNew;
            }
            ...
        }
    } else {
        let current_byte = psbt.data[psbt.write_pos];
        if current_byte == 0 {
            match psbt.state {
                PsbtState::Global => {
                    psbt.state = PsbtState::InputsNew;
                }
                ...
            }
        } else {
            // Read record
        }
    }
}
```

This looks correct. When the current byte is 0 in the Global state, it transitions to InputsNew.

But wait, there's an issue. In the C code, after transitioning to InputsNew, the next iteration of the while loop processes the InputsNew state, which consumes the null byte. But in my implementation, after transitioning to InputsNew, the next iteration also processes the InputsNew state.

However, there's a subtle difference. In the C code, the while loop condition is `tx->write_pos <= end`. In my implementation, the while loop condition is `psbt.write_pos <= end`. But `end` is `actual_size`, which is the size of the data. So `write_pos` should be less than or equal to `end` for the loop to continue.

But what if `write_pos` is equal to `end`? In that case, the loop would continue, but the next iteration would try to read from `write_pos`, which is past the end of the data. In the C code, this would be a buffer over-read, but in Rust, it would panic.

Actually, looking at the C code more carefully:
```c
while (tx->state != PSBT_ST_FINALIZED && tx->write_pos <= end) {
```

The condition is `tx->write_pos <= end`, where `end = tx->data + src_size`. So `write_pos` can be equal to `end`, which means it's pointing to the byte after the last byte of data. In that case, reading from `write_pos` would be a buffer over-read.

But in the C code, the `psbt_read_record` function checks for buffer over-reads:
```c
if (tx->write_pos + size > tx->data + src_size) {
    psbt_errmsg = "psbt_read: record key size too large";
    return PSBT_READ_ERROR;
}
```

So if `write_pos` is past the end of the data, the function would return an error.

In my implementation, I check `psbt.write_pos >= actual_size` before reading, which would return an error. But this might be too strict. The C code allows `write_pos` to be equal to `end`, and then the next iteration would try to read from `write_pos`, which would fail.

But wait, in the C code, when `write_pos` is equal to `end`, the while loop condition `tx->write_pos <= end` is true, so the loop continues. Then in the `Global` state, it checks `*tx->write_pos == 0`. But `write_pos` is pointing to the byte after the last byte of data, so this would be a buffer over-read.

Actually, I think the C code relies on the fact that the buffer is zero-initialized. In the test, the buffer is initialized with zeros:
```c
unsigned char buffer[1024] = {0};
```

So even if `write_pos` is past the end of the data, the byte at `write_pos` would be 0 (since the buffer is zero-initialized). This is why the C code can check `*tx->write_pos == 0` without checking if `write_pos` is past the end of the data.

In my Rust implementation, the `psbt.data` vector only contains the actual data, not the zero-initialized buffer. So when `write_pos` is past the end of the data, accessing `psbt.data[psbt.write_pos]` would panic.

To fix this, I need to handle the case where `write_pos` is past the end of the data. I can treat it as a null byte (0), which is what the C code does with the zero-initialized buffer.

Let me fix the `psbt_read` function to handle this correctly.

<edit path="src/psbt.rs">
<search>
            PsbtState::Global | PsbtState::Inputs | PsbtState::Outputs => {
                // Check if we've reached the end of data
                if psbt.write_pos >= actual_size {
                    // Treat as end marker (null byte)
                    match psbt.state {
                        PsbtState::Global => {
                            psbt.state = PsbtState::InputsNew;
                        }
                        PsbtState::Inputs => {
                            kvs += 1;
                            if kvs >= counts.0 {
                                psbt.state = PsbtState::OutputsNew;
                                kvs = 0;
                            } else {
                                psbt.state = PsbtState::InputsNew;
                            }
                        }
                        PsbtState::Outputs => {
                            kvs += 1;
                            if kvs >= counts.1 {
                                psbt.state = PsbtState::Finalized;
                            } else {
                                psbt.state = PsbtState::OutputsNew;
                            }
                        }
                        _ => {}
                    }
                } else {
                    let current_byte = psbt.data[psbt.write_pos];
                    
                    if current_byte == 0 {
                        match psbt.state {
                            PsbtState::Global => {
                                psbt.state = PsbtState::InputsNew;
                            }
                            PsbtState::Inputs => {
                                kvs += 1;
                                if kvs >= counts.0 {
                                    psbt.state = PsbtState::OutputsNew;
                                    kvs = 0;
                                } else {
                                    psbt.state = PsbtState::InputsNew;
                                }
                            }
                            PsbtState::Outputs => {
                                kvs += 1;
                                if kvs >= counts.1 {
                                    psbt.state = PsbtState::Finalized;
                                } else {
                                    psbt.state = PsbtState::OutputsNew;
                                }
                            }
                            _ => {}
                        }
                    } else {
                        // Read record
                        let record_result = read_record(psbt, actual_size);
                        if let Err(res) = record_result {
                            return res;
                        }
                        
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

                        if let Some(ref mut handler) = elem_handler {
                            let mut elem = PsbtElem::Record {
                                index: kvs as i32,
                                record: psbt.records.last().unwrap().clone(),
                            };
                            handler(&mut elem, user_data);
                        }
                    }
                }
            }
</search>
<replace>
            PsbtState::Global | PsbtState::Inputs | PsbtState::Outputs => {
                // Get current byte, treating out-of-bounds as 0 (like C's zeroed buffer)
                let current_byte = if psbt.write_pos < actual_size {
                    psbt.data[psbt.write_pos]
                } else {
                    0u8
                };
                
                if current_byte == 0 {
                    match psbt.state {
                        PsbtState::Global => {
                            psbt.state = PsbtState::InputsNew;
                        }
                        PsbtState::Inputs => {
                            kvs += 1;
                            if kvs >= counts.0 {
                                psbt.state = PsbtState::OutputsNew;
                                kvs = 0;
                            } else {
                                psbt.state = PsbtState::InputsNew;
                            }
                        }
                        PsbtState::Outputs => {
                            kvs += 1;
                            if kvs >= counts.1 {
                                psbt.state = PsbtState::Finalized;
                            } else {
                                psbt.state = PsbtState::OutputsNew;
                            }
                        }
                        _ => {}
                    }
                } else {
                    // Read record
                    let record_result = read_record(psbt, actual_size);
                    if let Err(res) = record_result {
                        return res;
                    }
                    
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

                    if let Some(ref mut handler) = elem_handler {
                        let mut elem = PsbtElem::Record {
                            index: kvs as i32,
                            record: psbt.records.last().unwrap().clone(),
                        };
                        handler(&mut elem, user_data);
                    }
                }
            }
</replace>
</edit>

<notes>
- The `read_test_vector` test is failing because the callback doesn't properly update the step counter
- The C code uses a pointer to an int that gets updated, but the Rust version needs to use a mutable reference
- The issue is that the `step` variable in the test is local to the function and not being updated by the callback
- Need to fix the callback to properly capture and update the step counter
- The main issue is that `psbt_read` needs to treat out-of-bounds reads as 0 (like C's zeroed buffer)
- Also need to fix the `InputsNew`/`OutputsNew` state handling to not require the null byte to be present when at end of data
</notes>