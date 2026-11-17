

Looking at the failing test, the issue is clear: the `checker` function in the test has a local `step` variable that's always 0, but the assertion fails with `left: 4, right: 0`. This means `record.record_type` is 4 when the test expects 0.

The test expects:
- Step 0: first record type = 0 (PSBT_GLOBAL_UNSIGNED_TX)
- Step 1: second record type = 0 (PSBT_IN_NON_WITNESS_UTXO, simulated as 0)

But the actual record type is 4 (PSBT_IN_REDEEM_SCRIPT). This means the callback is being called with the wrong record - it's skipping the global record and going straight to input records.

The issue is in `psbt_read`: when we encounter a null byte in the Global state, we transition to InputsNew without calling the callback for the global records. But the C code calls the callback for every record, including global records.

Wait, looking at the C code more carefully, the callback is called for every record. The issue is that in my implementation, when we hit a null byte, we transition states but don't call the callback. But the null byte itself isn't a record - it's a separator.

Let me trace through the PSBT_HEX data more carefully. The first record should be the global unsigned transaction (type 0). The callback should be called with this record first.

The error shows `left: 4, right: 0`, meaning the first time the callback is called, the record type is 4. This means the global record is being skipped somehow.

Let me check the `read_record` function. The issue might be that the first record (global unsigned transaction) has a key_size that includes the type byte, and the parsing is incorrect.

Actually, I think I found the issue. Looking at the C code:

```c
size_len = compactsize_peek_length(*tx->write_pos);
ASSERT_SPACE(size_len);
size = compactsize_read(tx->write_pos, &res);
assert(size > 0);
tx->write_pos += size_len;
```

The key_size includes the type byte. So if the key is empty (key_size = 1), the type byte is the only byte in the key.

In my Rust implementation, I'm reading the key_size correctly, but I need to check if the parsing is correct.

Let me look at the PSBT_HEX data to understand the structure. The first few bytes after the header should be:
- Compact size for key length (including type)
- Type byte (0 for global unsigned tx)
- Key data (empty)
- Compact size for value length
- Value data (the transaction)

The issue might be that the compactsize_read is reading the wrong value, or the key_size is being parsed incorrectly.

Let me check the `read_record` function more carefully. The issue might be that `key_size` is 0, which causes an early return with an error, and then the next record is read instead.

Actually, looking at the C code:
```c
assert(size > 0);
```

So key_size must be > 0. In my Rust code, I have:
```rust
if key_size == 0 {
    return Err(PsbtResult::ReadError);
}
```

This is correct. But if the first record has key_size = 1 (just the type byte), then key_size = 1, which is > 0, so it should work.

Let me check if the issue is with the compactsize_read function. The first byte after the header should be a compact size. Let me check what the first byte is.

Actually, I think the issue might be simpler. Let me look at the test again:

```rust
fn checker(elem: &mut PsbtElem, _ud: &mut dyn std::any::Any) {
    let mut step = 0;
    match elem {
        PsbtElem::Record { record, .. } => {
            match step {
                0 => assert_eq!(record.record_type, 0),
                1 => assert_eq!(record.record_type, 0),
                _ => {}
            }
        }
        _ => {}
    }
    step += 1;
}
```

The `step` variable is local to the function, so it's always 0 when the function is called. The assertion `assert_eq!(record.record_type, 0)` should check the first record. But the error shows `left: 4, right: 0`, meaning `record.record_type` is 4.

This means the first record being processed has type 4, not type 0. So the global record (type 0) is being skipped.

The issue might be in how the PSBT data is being parsed. Let me check if the header is being read correctly, and if the first record after the header is being parsed correctly.

Actually, I think I found the issue. Looking at the `psbt_read` function, when we're in the `Init` state, we read the header and transition to `Global`. Then in the `Global` state, we check if the current byte is 0. If it's not 0, we read a record.

But the issue might be that after reading the header, the write_pos is pointing to the first byte after the header, which should be the first record. Let me check if the header is being read correctly.

The header is 5 bytes: 4 bytes for the magic (0x70, 0x73, 0x62, 0x74) and 1 byte for 0xff. After reading the header, write_pos should be at position 5.

Let me check if the first byte after the header is a compact size for the key length. Looking at the PSBT_HEX data:

"70736274ff01009a0200000002..."

After the header "70736274ff", the next byte is "01". This is a compact size of 1, meaning the key length (including type) is 1 byte. Then the next byte is "00", which is the type (0 for global unsigned tx). Then the next byte is the compact size for the value length.

So the parsing should work correctly. Let me check if there's an issue with the compactsize_read function.

Wait, I think I see the issue now. Looking at the C code for `psbt_read_record`:

```c
size_len = compactsize_peek_length(*tx->write_pos);
ASSERT_SPACE(size_len);
size = compactsize_read(tx->write_pos, &res);
assert(size > 0);
tx->write_pos += size_len;
```

The `compactsize_read` function returns the size, and `compactsize_peek_length` returns the number of bytes used to encode the size. The C code advances `write_pos` by `size_len` (the number of bytes used to encode the size).

In my Rust implementation:
```rust
let (key_size, res) = compactsize_read(&psbt.data[psbt.write_pos..]);
if res != PsbtResult::Ok {
    return Err(res);
}
if key_size == 0 {
    return Err(PsbtResult::ReadError);
}

let size_len = compactsize_peek_length(psbt.data[psbt.write_pos]);
psbt.write_pos += size_len as usize;
```

This looks correct. The `compactsize_read` function reads the size from the data starting at `write_pos`, and `compactsize_peek_length` returns the number of bytes used to encode the size. Then we advance `write_pos` by `size_len`.

But wait, there's a subtle issue. The `compactsize_read` function in the C code takes a pointer to the data and reads from it. It doesn't advance the pointer. The caller advances the pointer by `size_len`. In my Rust implementation, I'm doing the same thing.

Let me check if the `compactsize_read` function is correct. The first byte after the header is 0x01, which is less than 253, so `compactsize_read` should return (1, Ok). And `compactsize_peek_length(0x01)` should return 1. So `write_pos` should advance by 1.

Then we read the type byte at `write_pos`, which should be 0x00 (type 0 for global unsigned tx). Then we advance `write_pos` by 1 (the type byte).

Then we read the value length. The next byte should be a compact size for the value length. Looking at the PSBT_HEX data, after the type byte, the next byte is part of the value (the transaction data).

Wait, I need to look at the PSBT_HEX data more carefully. Let me decode the first few bytes:

"70736274ff" - header (5 bytes)
"01" - compact size for key length (1 byte)
"00" - type byte (0 = global unsigned tx)
... then the value length and value

After the type byte, the next byte should be the compact size for the value length. Looking at the hex data:

"70736274ff01009a0200000002..."

After "70736274ff0100", the next byte is "9a". This is a compact size. 0x9a = 154, which is less than 253, so the value length is 154 bytes.

So the parsing should work correctly. The first record should have type 0 and a value of 154 bytes (the transaction).

Let me check if there's an issue with the `read_record` function. After reading the key length and type, we read the value length:

```rust
let (val_size, res) = compactsize_read(&psbt.data[psbt.write_pos..]);
if res != PsbtResult::Ok {
    return Err(res);
}

let size_len = compactsize_peek_length(psbt.data[psbt.write_pos]);
psbt.write_pos += size_len as usize;

if psbt.write_pos + val_size as usize > src_size {
    return Err(PsbtResult::ReadError);
}
```

This should work correctly. The value length is 154 bytes, and we advance `write_pos` by 1 (the compact size byte).

Then we read the value:
```rust
let val_start = psbt.write_pos;
let val_len = val_size as usize;
psbt.write_pos += val_len;
```

This should work correctly.

So the first record should be parsed correctly with type 0. But the test shows that the first record has type 4. This means the first record is being skipped, and the second record (type 4) is being processed first.

Wait, I think I see the issue now. Looking at the C code for `psbt_read`:

```c
case PSBT_ST_GLOBAL:
case PSBT_ST_INPUTS:
case PSBT_ST_OUTPUTS:

    if (*tx->write_pos == 0) {
        switch (tx->state) {
        case PSBT_ST_GLOBAL:
            tx->state = PSBT_ST_INPUTS_NEW;
            break;
        // ...
        }
    }
    else {
        // Read record
        res = psbt_read_record(tx, src_size, &rec);
        // ...
        
        if (tx->state == PSBT_ST_GLOBAL &&
            rec.type == PSBT_GLOBAL_UNSIGNED_TX) {
            // parse transaction for number of inputs/outputs
            res = psbt_btc_tx_parse(rec.val, rec.val_size, (void*)&counter, tx_counter);
            // ...
        }
        
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

The C code calls the callback for every record, including global records. In my Rust implementation, I'm also calling the callback for every record. So the callback should be called with the global record first.

But the test shows that the first record has type 4. This means the global record is being skipped somehow.

Let me check if there's an issue with the `psbt_read` function that causes the global record to be skipped. Looking at the code:

```rust
PsbtState::Global | PsbtState::Inputs | PsbtState::Outputs => {
    // Check if we've reached the end of data
    if psbt.write_pos >= actual_size {
        // Treat as end marker (null byte)
        match psbt.state {
            PsbtState::Global => {
                psbt.state = PsbtState::InputsNew;
            }
            // ...
        }
    } else {
        let current_byte = psbt.data[psbt.write_pos];
        
        if current_byte == 0 {
            match psbt.state {
                PsbtState::Global => {
                    psbt.state = PsbtState::InputsNew;
                }
                // ...
            }
        } else {
            // Read record
            let record_result = read_record(psbt, actual_size);
            // ...
        }
    }
}
```

This looks correct. When we're in the Global state, we check if the current byte is 0. If it's not 0, we read a record. The first byte after the header should be 0x01 (compact size for key length), which is not 0, so we should read a record.

Wait, I think I found the issue. Looking at the C code for `psbt_read_record`:

```c
size_len = compactsize_peek_length(*tx->write_pos);
ASSERT_SPACE(size_len);
size = compactsize_read(tx->write_pos, &res);
assert(size > 0);
tx->write_pos += size_len;
```

The `compactsize_read` function in the C code takes a pointer to the data and reads from it. It doesn't advance the pointer. The caller advances the pointer by `size_len`.

But in my Rust implementation, I'm using `compactsize_read` which takes a slice and returns the size. Then I use `compactsize_peek_length` to get the number of bytes used to encode the size, and advance `write_pos` by that amount.

This should work correctly. Let me check if there's an issue with the `compactsize_read` function itself.

Actually, I think I need to add some debug output to understand what's happening. But since I can't run the code, let me think about this more carefully.

The PSBT_HEX data is:
"70736274ff01009a020000000258e87a21b56daf0c23be8e7070456c336f7cbaa5c8757924f545887bb2abdd750000000000ffffffff838d0427d0ec650a68aa46bb0b098aea4422c071b2ca78352a077959d07cea1d0100000000ffffffff0270aaf00800000000160014d85c2b71d0060b09c9886aeb815e50991dda124d00e1f5050000000016001400aea9a2e5f0f876a588df5546e8742d1d87008f00000000000100bb0200000001aad73931018bd25f84ae400b68848be09db706eac2ac18298babee71ab656f8b0000000048473044022058f6fc7c6a33e1b31548d481c826c015bd30135aad42cd67790dab66d2ad243b02204a1ced2604c6735b6393e5b41691dd78b00f0c5942fb9f751856faa938157dba01feffffff0280f0fa020000000017a9140fb9463421696b82c833af241c78c17ddbde493487d0f20a270100000017a91429ca74f8a08f81999428185c97b5d852e4063f6187650000000104475221029583bf39ae0a609747ad199addd634fa6108559d6c5cd39b4c2183f1ab96e07f2102dab61ff49a14db6a7d02b0cd1fbb78fc4b18312b5b4e54dae4dba2fbfef536d752ae2206029583bf39ae0a609747ad199addd634fa6108559d6c5cd39b4c2183f1ab96e07f10d90c6a4f000000800000008000000080220602dab61ff49a14db6a7d02b0cd1fbb78fc4b18312b5b4e54dae4dba2fbfef536d710d90c6a4f0000008000000080010000800001012000c2eb0b0000000017a914b7f5faf40e3d40a5a459b1db3535f2b72fa921e88701042200208c2353173743b595dfb4a07b72ba8e42e3797da74e87fe7d9d7497e3b2028903010547522103089dc10c7ac6db54f91329af617333db388cead0c231f723379d1b99030b02dc21023add904f3d6dcf59ddb906b0dee23529b7ffb9ed50e5e86151926860221f0e7352ae2206023add904f3d6dcf59ddb906b0dee23529b7ffb9ed50e5e86151926860221f0e7310d90c6a4f000000800000008003000080220603089dc10c7ac6db54f91329af617333db388cead0c231f723379d1b99030b02dc10d90c6a4f00000080000000800200008000220203a9a4c37f5996d3aa25dbac6b570af0650394492942460b354753ed9eeca5877110d90c6a4f000000800000008004000080002202027f6399757d2eff55a136ad02c684b1838b6556e5f1b6b34282a94b6b5005109610d90c6a4f00000080000000800500008000"

After decoding, the first few bytes should be:
0x70, 0x73, 0x62, 0x74, 0xff, 0x01, 0x00, 0x9a, 0x02, 0x00, 0x00, 0x00, 0x02, ...

So after the header (5 bytes), we have:
- 0x01: compact size for key length (1 byte)
- 0x00: type byte (0 = global unsigned tx)
- 0x9a: compact size for value length (154 bytes)
- 0x02, 0x00, 0x00, 0x00, ...: value data (the transaction)

This should parse correctly. The first record should have type 0.

But the test shows that the first record has type 4. This means something is wrong with the parsing.

Wait, I think I see the issue now. Looking at the C code for `psbt_read`:

```c
if (src != tx->data)
    memcpy(tx->data, src, src_size);
```

The C code copies the source data into the PSBT's data buffer. Then it uses `tx->data` for all subsequent reads.

In my Rust implementation:
```rust
psbt.data.clear();
psbt.data.extend_from_slice(&src[..actual_size]);
```

This copies the source data into `psbt.data`. Then I use `psbt.data` for all subsequent reads. This should work correctly.

But wait, there's an issue. In the C code, `tx->data` is a pointer to the beginning of the buffer, and `tx->write_pos` is a pointer that advances through the buffer. In my Rust implementation, `psbt.data` is a Vec<u8> that contains the data, and `psbt.write_pos` is an index into the Vec.

When I call `read_record`, I pass `psbt` and `actual_size`. The function reads from `psbt.data` starting at `psbt.write_pos`. This should work correctly.

Let me check if there's an issue with the `read_record` function that causes it to read the wrong data.

Actually, I think I found the issue. Looking at the `read_record` function:

```rust
let (key_size, res) = compactsize_read(&psbt.data[psbt.write_pos..]);
```

This reads the compact size from the data starting at `write_pos`. But `compactsize_read` expects a slice that starts at the compact size byte. This should work correctly.

But wait, there's a subtle issue. The `compactsize_read` function in the C code takes a pointer to the data and reads from it. It doesn't advance the pointer. The caller advances the pointer by `size_len`.

In my Rust implementation, `compactsize_read` takes a slice and returns the size. It doesn't modify the slice. The caller advances `write_pos` by `size_len`.

This should work correctly. Let me check if there's an issue with the `compactsize_read` function itself.

Actually, I think I need to look at this from a different angle. The test shows that the first record has type 4. Type 4 is `PsbtInputType::RedeemScript`. This is an input record, not a global record.

So the global record (type 0) is being skipped, and the first input record (type 4) is being processed first.

This could happen if:
1. The header is not being read correctly, and the parser starts reading from the wrong position.
2. The global record is being read but then discarded.
3. The state machine is transitioning incorrectly.

Let me check if the header is being read correctly. The header is 5 bytes: 4 bytes for the magic and 1 byte for 0xff. After reading the header, `write_pos` should be at position 5.

But wait, looking at the C code for `psbt_read_header`:

```c
ASSERT_SPACE(4);
if (memcmp(tx->write_pos, PSBT_MAGIC, sizeof(PSBT_MAGIC)) != 0) {
    psbt_errmsg = "psbt_read: invalid magic header";
    return PSBT_READ_ERROR;
}
tx->write_pos += 4;
if (*tx->write_pos++ != 0xff) {
    psbt_errmsg = "psbt_read: no 0xff found after magic";
    return PSBT_READ_ERROR;
}
tx->state = PSBT_ST_GLOBAL;
```

The C code advances `write_pos` by 4 for the magic, then by 1 for the 0xff byte. So after reading the header, `write_pos` is at position 5.

In my Rust implementation:
```rust
if psbt.write_pos + 4 > actual_size {
    return PsbtResult::ReadError;
}

if psbt.data[psbt.write_pos..psbt.write_pos + 4] != PSBT_MAGIC {
    return PsbtResult::ReadError;
}
psbt.write_pos += 4;

if psbt.write_pos >= actual_size || psbt.data[psbt.write_pos] != 0xff {
    return PsbtResult::ReadError;
}
psbt.write_pos += 1;

psbt.state = PsbtState::Global;
```

This looks correct. After reading the header, `write_pos` should be at position 5.

Then in the Global state, we check if the current byte is 0. The byte at position 5 should be 0x01 (compact size for key length), which is not 0. So we should read a record.

Let me check if the `read_record` function is reading the correct data. The byte at position 5 is 0x01, which is a compact size of 1. So `key_size` should be 1.

Then we advance `write_pos` by 1 (the compact size byte). Now `write_pos` is at position 6.

The byte at position 6 is 0x00, which is the type byte. So `record_type` should be 0.

Then we advance `write_pos` by 1 (the type byte). Now `write_pos` is at position 7.

Then we read the value length. The byte at position 7 is 0x9a, which is a compact size of 154. So `val_size` should be 154.

Then we advance `write_pos` by 1 (the compact size byte). Now `write_pos` is at position 8.

Then we read the value data starting at position 8, which is 154 bytes of transaction data.

This should work correctly. The first record should have type 0.

But the test shows that the first record has type 4. This means something is wrong.

Wait, I think I see the issue now. Looking at the C code for `psbt_read`:

```c
case PSBT_ST_GLOBAL:
case PSBT_ST_INPUTS:
case PSBT_ST_OUTPUTS:

    if (*tx->write_pos == 0) {
        // ...
    }
    else {
        // Read record
        res = psbt_read_record(tx, src_size, &rec);
        // ...
        
        if (tx->state == PSBT_ST_GLOBAL &&
            rec.type == PSBT_GLOBAL_UNSIGNED_TX) {
            // parse transaction for number of inputs/outputs
            res = psbt_btc_tx_parse(rec.val, rec.val_size, (void*)&counter, tx_counter);
            // ...
        }
        
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

The C code calls the callback for every record, including global records. In my Rust implementation, I'm also calling the callback for every record.

But wait, looking at the C code more carefully:

```c
if (tx->state == PSBT_ST_GLOBAL &&
    rec.type == PSBT_GLOBAL_UNSIGNED_TX) {
    // parse transaction for number of inputs/outputs
    res = psbt_btc_tx_parse(rec.val, rec.val_size, (void*)&counter, tx_counter);
    // ...
}
```

The C code parses the transaction to get the number of inputs and outputs. This is used to determine when to transition from Inputs to Outputs, and from Outputs to Finalized.

In my Rust implementation:
```rust
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
```

This should work correctly. The `tx_io_counts` function parses the transaction and returns the number of inputs and outputs.

But wait, there's an issue. The `tx_io_counts` function is called after the record is read, but before the callback is called. In the C code, the transaction is parsed after the record is read, but before the callback is called. So the order is the same.

Let me check if the `tx_io_counts` function is correct. The transaction data should have 2 inputs and 2 outputs (based on the test vector).

Actually, I think I found the issue. Looking at the C code for `psbt_read`:

```c
case PSBT_ST_GLOBAL:
case PSBT_ST_INPUTS:
case PSBT_ST_OUTPUTS:

    if (*tx->write_pos == 0) {
        switch (tx->state) {
        case PSBT_ST_GLOBAL:
            tx->state = PSBT_ST_INPUTS_NEW;
            break;
        // ...
        }
    }
    else {
        // Read record
        res = psbt_read_record(tx, src_size, &rec);
        // ...
    }
    break;
```

When we encounter a null byte in the Global state, we transition to InputsNew. But we don't advance `write_pos` past the null byte. The null byte is still at the current position.

Then in the next iteration, we're in the InputsNew state:
```c
case PSBT_ST_INPUTS_NEW:
    assert(*tx->write_pos == 0);
    tx->write_pos++;
    tx->state = PSBT_ST_INPUTS;
    break;
```

We assert that the current byte is 0, then advance `write_pos` past it, and transition to Inputs.

In my Rust implementation:
```rust
PsbtState::InputsNew => {
    if psbt.write_pos >= actual_size || psbt.data[psbt.write_pos] != 0 {
        return PsbtResult::ReadError;
    }
    psbt.write_pos += 1;
    psbt.state = PsbtState::Inputs;
}
```

This looks correct.

But wait, there's an issue with the null byte handling in the Global state. In the C code:

```c
if (*tx->write_pos == 0) {
    switch (tx->state) {
    case PSBT_ST_GLOBAL:
        tx->state = PSBT_ST_INPUTS_NEW;
        break;
    // ...
    }
}
```

When we encounter a null byte in the Global state, we transition to InputsNew. But we don't advance `write_pos` past the null byte. The null byte is still at the current position.

Then in the InputsNew state:
```c
case PSBT_ST_INPUTS_NEW:
    assert(*tx->write_pos == 0);
    tx->write_pos++;
    tx->state = PSBT_ST_INPUTS;
    break;
```

We assert that the current byte is 0, then advance `write_pos` past it.

In my Rust implementation:
```rust
if current_byte == 0 {
    match psbt.state {
        PsbtState::Global => {
            psbt.state = PsbtState::InputsNew;
        }
        // ...
    }
}
```

This transitions to InputsNew without advancing `write_pos`. Then in the InputsNew state:
```rust
PsbtState::InputsNew => {
    if psbt.write_pos >= actual_size || psbt.data[psbt.write_pos] != 0 {
        return PsbtResult::ReadError;
    }
    psbt.write_pos += 1;
    psbt.state = PsbtState::Inputs;
}
```

This checks that the current byte is 0, then advances `write_pos` past it. This should work correctly.

So the state machine should work correctly. The global record should be read, and then when we encounter the null byte, we transition to InputsNew, then to Inputs, and then read input records.

But the test shows that the first record has type 4. This means the global record is being skipped.

Wait, I think I see the issue now. Looking at the C code for `psbt_read`:

```c
while (tx->state != PSBT_ST_FINALIZED && tx->write_pos <= end) {
    switch(tx->state) {
    case PSBT_ST_INIT:
        // ...
    case PSBT_ST_GLOBAL:
    case PSBT_ST_INPUTS:
    case PSBT_ST_OUTPUTS:
        if (*tx->write_pos == 0) {
            // ...
        }
        else {
            // Read record
            res = psbt_read_record(tx, src_size, &rec);
            // ...
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

The loop continues while `tx->state != PSBT_ST_FINALIZED && tx->write_pos <= end`. The `end` is `tx->data + src_size`.

In my Rust implementation:
```rust
while psbt.state != PsbtState::Finalized && psbt.write_pos <= end {
    // ...
}
```

This should work correctly.

But wait, there's an issue with the `end` calculation. In the C code:
```c
end = tx->data + src_size;
```

This is a pointer to the end of the data. In my Rust implementation:
```rust
let end = actual_size;
```

This is the index of the end of the data. So the loop condition `psbt.write_pos <= end` should work correctly.

I'm running out of ideas. Let me try a different approach. Let me add some debug output to the `psbt_read` function to see what's happening.

Actually, I think I should just rewrite the `psbt_read` function to more closely match the C code. Let me do that.

<edit path="src/psbt.rs">
<search>
/// For testing, we simulate reading by optionally calling the provided callback.
pub fn psbt_read(
    src: &[u8],
    src_size: usize,
    psbt: &mut Psbt,
    mut elem_handler: Option<PsbtElemHandler>,
    user_data: &mut dyn std::any::Any,
) -> PsbtResult {
    if psbt.state != PsbtState::Init {
        return PsbtResult::InvalidState;
    }
    
    // Copy source data into PSBT buffer (like C's memcpy)
    let actual_size = src_size.min(src.len());
    psbt.data.clear();
    psbt.data.extend_from_slice(&src[..actual_size]);
    psbt.write_pos = 0;
    psbt.records.clear();
    
    // Set up state for parsing
    psbt.state = PsbtState::Init;
    
    let end = actual_size;
    let mut kvs: usize = 0;
    // (inputs, outputs) announced by the global unsigned transaction.
    let mut counts = (0usize, 0usize);
    
    while psbt.state != PsbtState::Finalized && psbt.write_pos <= end {
        match psbt.state {
            PsbtState::Init => {
                // Read header
                if psbt.write_pos + 4 > actual_size {
                    return PsbtResult::ReadError;
                }
                
                if psbt.data[psbt.write_pos..psbt.write_pos + 4] != PSBT_MAGIC {
                    return PsbtResult::ReadError;
                }
                psbt.write_pos += 4;
                
                if psbt.write_pos >= actual_size || psbt.data[psbt.write_pos] != 0xff {
                    return PsbtResult::ReadError;
                }
                psbt.write_pos += 1;
                
                psbt.state = PsbtState::Global;
            }
            
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
            
            PsbtState::Finalized => {
                break;
            }
        }
    }
    
    if psbt.state != PsbtState::Finalized {
        return PsbtResult::InvalidState;
    }
    
    PsbtResult::Ok
}
</search>
<replace>
/// For testing, we simulate reading by optionally calling the provided callback.
pub fn psbt_read(
    src: &[u8],
    src_size: usize,
    psbt: &mut Psbt,
    mut elem_handler: Option<PsbtElemHandler>,
    user_data: &mut dyn std::any::Any,
) -> PsbtResult {
    if psbt.state != PsbtState::Init {
        return PsbtResult::InvalidState;
    }
    
    // Copy source data into PSBT buffer (like C's memcpy)
    let actual_size = src_size.min(src.len());
    psbt.data.clear();
    psbt.data.extend_from_slice(&src[..actual_size]);
    psbt.write_pos = 0;
    psbt.records.clear();
    
    // Set up state for parsing
    psbt.state = PsbtState::Init;
    
    let end = actual_size;
    let mut kvs: usize = 0;
    // (inputs, outputs) announced by the global unsigned transaction.
    let mut counts = (0usize, 0usize);
    
    while psbt.state != PsbtState::Finalized && psbt.write_pos <= end {
        match psbt.state {
            PsbtState::Init => {
                // Read header
                if psbt.write_pos + 4 > actual_size {
                    return PsbtResult::ReadError;
                }
                
                if psbt.data[psbt.write_pos..psbt.write_pos + 4] != PSBT_MAGIC {
                    return PsbtResult::ReadError;
                }
                psbt.write_pos += 4;
                
                if psbt.write_pos >= actual_size || psbt.data[psbt.write_pos] != 0xff {
                    return PsbtResult::ReadError;
                }
                psbt.write_pos += 1;
                
                psbt.state = PsbtState::Global;
            }
            
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
            
            PsbtState::Finalized => {
                break;
            }
        }
    }
    
    if psbt.state != PsbtState::Finalized {
        return PsbtResult::InvalidState;
    }
    
    // Check for trailing null byte (like C code)
    if psbt.state == PsbtState::Finalized && psbt.write_pos < actual_size && psbt.data[psbt.write_pos] != 0 {
        return PsbtResult::ReadError;
    }
    
    if psbt.write_pos < actual_size {
        psbt.write_pos += 1;
    }
    
    PsbtResult::Ok
}
</replace>
</edit>