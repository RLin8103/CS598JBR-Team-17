Looking at the failing test, the issue is that the `checker` function in the test has a local `step` variable that's always 0, but the assertion fails with `left: 4, right: 0`. This means `record.record_type` is 4 when the test expects 0. 

The test expects:
- Step 0: first record type = 0 (PSBT_GLOBAL_UNSIGNED_TX)
- Step 1: second record type = 0 (PSBT_IN_NON_WITNESS_UTXO, simulated as 0)

But the actual record type is 4 (PSBT_IN_REDEEM_SCRIPT). This suggests the callback is being called with the wrong record - it's skipping the global record and going straight to input records.

The issue is in `psbt_read`: when we encounter a null byte in the Global state, we transition to InputsNew without calling the callback for the global records. But the C code calls the callback for every record, including global records.

Wait, looking more carefully at the C code, the callback is called for every record. The issue is that in my implementation, when we hit a null byte, we transition states but don't call the callback. But the null byte itself isn't a record - it's a separator.

Let me trace through the PSBT_HEX data more carefully. The first record should be the global unsigned transaction (type 0). The callback should be called with this record first.

The error shows `left: 4, right: 0`, meaning the first time the callback is called, the record type is 4. This means the global record is being skipped somehow.

Let me check the `read_record` function. The issue might be that the first record (global unsigned transaction) has a key_size that includes the type byte, and the parsing is incorrect.

Actually, looking at the C code more carefully:

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

Actually, I think the issue might be that the `psbt_read` function is not correctly handling the case where the src buffer is larger than the actual PSBT data. The `src_size` parameter should be the actual size of the PSBT data.

Let me look at the test:
```rust
let res = psbt_decode(PSBT_HEX, hexlen, &mut buf, 2048, &mut psbt_len);
// ...
let res = psbt_read(&buf, psbt_len, &mut psbt_instance, Some(checker), &mut ());
```

So `psbt_len` is the decoded length, and `buf` contains the decoded data. The `psbt_read` function is called with `&buf` and `psbt_len`.

In my implementation:
```rust
psbt.data.clear();
psbt.data.extend_from_slice(&src[..src_size.min(src.len())]);
```

This copies the first `src_size` bytes from `src` into `psbt.data`. Then:
```rust
let src = &src[..src_size.min(src.len())];
let src_size = src.len();
```

This shadows the original `src` with a slice of the first `src_size` bytes. This should work correctly.

Let me check if the issue is with the `read_record` function. The function reads the key length, then the type byte, then the key data, then the value length, then the value data.

Wait, I think I see the issue. In the `read_record` function, I'm using `psbt.data` to read the data, but `psbt.data` might not contain the full PSBT data. Let me check.

Actually, I think the issue is that `psbt.data` is being used as the source for reading, but `psbt.data` is also being modified during the read process. This could cause issues.

Let me look at the C code more carefully:

```c
if (src != tx->data)
    memcpy(tx->data, src, src_size);
```

So the C code copies the source data into the PSBT's data buffer. Then it uses `tx->data` for all subsequent reads.

In my Rust implementation, I'm doing the same thing:
```rust
psbt.data.clear();
psbt.data.extend_from_slice(&src[..src_size.min(src.len())]);
```

But then I shadow `src` with a slice of the original `src`, not `psbt.data`. This means I'm reading from the original `src` buffer, not from `psbt.data`. But the `read_record` function uses `psbt.data` to read the data.

Wait, looking at the code more carefully:

```rust
let src = &src[..src_size.min(src.len())];
let src_size = src.len();
```

This shadows the original `src` with a slice of the original `src`. But then in the `read_record` function, I'm using `psbt.data` to read the data:

```rust
let (key_size, res) = compactsize_read(&psbt.data[psbt.write_pos..]);
```

So I'm reading from `psbt.data`, which should contain the same data as `src`. This should work.

Let me check if there's an issue with the `compactsize_read` function. The first byte after the header should be 0x01, which is a compact size of 1. Let me check if `compactsize_read` returns the correct value.

Actually, I think I need to debug this more carefully. Let me add some debug output to understand what's happening.

Wait, I can't modify the test file. Let me look at the issue from a different angle.

The error message says `left: 4, right: 0`. This means `record.record_type` is 4. The test expects it to be 0. So the first record being processed has type 4 (PSBT_IN_REDEEM_SCRIPT).

This means the global record (type 0) is being skipped. Why would it be skipped?

Looking at the `psbt_read` function, when we're in the `Global` state and the current byte is not 0, we read a record. But if the current byte is 0, we transition to `InputsNew`.

The issue might be that after reading the header, the first byte is 0, which causes us to transition to `InputsNew` without reading any global records.

But the header is 5 bytes, and the first byte after the header should be 0x01 (compact size for key length), not 0x00.

Wait, let me check the PSBT_HEX data more carefully:

"70736274ff01009a0200000002..."

After the header "70736274ff", the next byte is "01". This is correct.

But wait, the `psbt_decode` function decodes the hex string into binary data. Let me check if the decoding is correct.

The hex string "70736274ff01009a0200000002..." should decode to:
0x70, 0x73, 0x62, 0x74, 0xff, 0x01, 0x00, 0x9a, 0x02, 0x00, 0x00, 0x00, 0x02, ...

So after the header (0x70, 0x73, 0x62, 0x74, 0xff), the next byte is 0x01, which is the compact size for the key length.

But wait, the hex string has "0100" after "ff". So the bytes are:
0x70, 0x73, 0x62, 0x74, 0xff, 0x01, 0x00, ...

So the first byte after the header is 0x01, which is correct.

Let me check if the `psbt_decode` function is decoding correctly. The hex string "70736274ff01009a0200000002..." should decode to the correct bytes.

Actually, I think I found the issue. Looking at the `psbt_decode` function:

```rust
for (i, c) in src.chars().enumerate() {
    if i % 2 == 0 {
        let c1 = c;
        let c2 = src.chars().nth(i + 1).unwrap();
        // ...
    }
}
```

This iterates over every character, but only processes every other pair. This should work correctly.

Let me check if the issue is with the `hex_to_val` function:

```rust
fn hex_to_val(c: char) -> u8 {
    if c.is_ascii_digit() {
        c as u8 - b'0'
    } else if ('a'..='f').contains(&c) {
        c as u8 - b'a' + 10
    } else if ('A'..='F').contains(&c) {
        c as u8 - b'A' + 10
    } else {
        0x80
    }
}
```

This should work correctly for hex characters.

Let me check if the issue is with the `psbt_read` function's handling of the `src_size` parameter. The test calls:

```rust
let res = psbt_read(&buf, psbt_len, &mut psbt_instance, Some(checker), &mut ());
```

Where `psbt_len` is the decoded length. In my implementation:

```rust
psbt.data.clear();
psbt.data.extend_from_slice(&src[..src_size.min(src.len())]);
```

This copies the first `src_size` bytes from `src` into `psbt.data`. But `src` is `&buf`, which has length 2048. `src_size` is `psbt_len`, which should be the actual decoded length.

Wait, I think I see the issue now. The `src` parameter is `&buf`, which has length 2048. But `src_size` is `psbt_len`, which is the actual decoded length. So `src[..src_size.min(src.len())]` should be `src[..psbt_len]`, which is correct.

But then I shadow `src` with:
```rust
let src = &src[..src_size.min(src.len())];
```

This creates a slice of the original `src` with length `src_size`. But then I use `src.len()` as `src_size`:
```rust
let src_size = src.len();
```

This should be correct.

I'm confused about why the first record is being skipped. Let me look at the `psbt_read` function more carefully.

Actually, I think I found the issue. In the `psbt_read` function, when we're in the `Global` state and we read a record, we check if the record type is 0 (global unsigned tx) and parse the transaction to get the input/output counts. But we also call the callback with the record.

But the issue might be that the callback is being called with the wrong record. Let me check the `read_record` function.

In the `read_record` function, I'm reading the key length, then the type byte, then the key data, then the value length, then the value data. But I'm using `psbt.data` to read the data, and `psbt.write_pos` to track the position.

Wait, I think I see the issue. In the `psbt_read` function, I'm using `psbt.data` to read the data, but `psbt.data` is also being modified during the read process. Specifically, I'm calling `psbt.data.clear()` and `psbt.data.extend_from_slice()` at the beginning of `psbt_read`. But then I'm also using `psbt.data` in the `read_record` function.

But the issue might be that `psbt.data` is being modified by the `write_record` function during a previous call to `psbt_write_global_record` or similar. Let me check if the test calls any write functions before `psbt_read`.

Looking at the test:
```rust
let res = psbt_decode(PSBT_HEX, hexlen, &mut buf, 2048, &mut psbt_len);
// ...
let res = psbt_init(&mut psbt_instance, &mut intbuf, 2048);
// ...
let res = psbt_read(&buf, psbt_len, &mut psbt_instance, Some(checker), &mut ());
```

So the test calls `psbt_init` before `psbt_read`. The `psbt_init` function clears the data and sets the state to Init. This should work correctly.

Let me check if the issue is with the `psbt_init` function:

```rust
pub fn psbt_init(psbt: &mut Psbt, _dest: &mut [u8], dest_size: usize) -> PsbtResult {
    psbt.data.clear();
    psbt.data_capacity = dest_size;
    psbt.write_pos = 0;
    psbt.state = PsbtState::Init;
    psbt.records.clear();
    PsbtResult::Ok
}
```

This clears the data and sets the state to Init. This should work correctly.

I'm running out of ideas. Let me try a different approach: let me check if the issue is with the `compactsize_read` function by looking at the first few bytes of the decoded PSBT data.

Actually, I think I should just add some debug output to the `psbt_read` function to understand what's happening. But I can't do that in the final code.

Let me look at the issue from a different angle. The error message says `left: 4, right: 0`. The test expects the first record to have type 0, but it has type 4. Type 4 is PSBT_IN_REDEEM_SCRIPT.

Looking at the test vector, the PSBT_HEX contains:
1. Global unsigned transaction (type 0)
2. Input records with redeem scripts (type 4)

So the first record should be type 0, but the callback is being called with type 4. This means the global record is being skipped.

Why would the global record be skipped? Let me check if the `psbt_read` function is correctly handling the transition from Init to Global.

In the C code:
```c
case PSBT_ST_INIT:
    debug("reading header at %zu\n", tx->write_pos - tx->data);
    res = psbt_read_header(tx);
    if (res != PSBT_OK)
        return res;
    break;
```

The `psbt_read_header` function reads the magic and the 0xff byte, then sets the state to `PSBT_ST_GLOBAL`.

In my Rust implementation:
```rust
PsbtState::Init => {
    // Read header
    if psbt.write_pos + 4 > src_size {
        return PsbtResult::ReadError;
    }
    
    if psbt.data[psbt.write_pos..psbt.write_pos + 4] != PSBT_MAGIC {
        return PsbtResult::ReadError;
    }
    psbt.write_pos += 4;
    
    if psbt.write_pos >= src_size || psbt.data[psbt.write_pos] != 0xff {
        return PsbtResult::ReadError;
    }
    psbt.write_pos += 1;
    
    psbt.state = PsbtState::Global;
}
```

This should work correctly.

After reading the header, the state is `Global` and `write_pos` is 5 (4 bytes for magic + 1 byte for 0xff).

Then in the next iteration of the loop, we're in the `Global` state. We check if the current byte is 0:

```rust
let current_byte = psbt.data.get(psbt.write_pos).copied().unwrap_or(0);
```

If `write_pos` is 5, then `psbt.data[5]` should be the first byte after the header, which is 0x01 (compact size for key length). So `current_byte` should be 0x01, which is not 0, so we read a record.

This should work correctly. Let me check if there's an issue with the `psbt.data` buffer.

Wait, I think I found the issue! In the `psbt_read` function, I'm copying the source data into `psbt.data`:

```rust
psbt.data.clear();
psbt.data.extend_from_slice(&src[..src_size.min(src.len())]);
```

But `src` is the original `&[u8]` parameter, and `src_size` is the second parameter. The `src` slice has length `src.len()`, which might be larger than `src_size`. So `src[..src_size.min(src.len())]` should be `src[..src_size]` if `src_size <= src.len()`.

But wait, I'm shadowing `src` with:
```rust
let src = &src[..src_size.min(src.len())];
```

This creates a new slice `src` that is a subslice of the original `src`. But then I'm using `psbt.data` to read the data, not `src`. So the data in `psbt.data` should be the same as `src`.

Actually, I think the issue might be that `psbt.data` is being modified by the `psbt_init` function, which is called before `psbt_read`. The `psbt_init` function clears `psbt.data`, so it should be empty when `psbt_read` is called.

Let me check the test again:
```rust
let res = psbt_init(&mut psbt_instance, &mut intbuf, 2048);
// ...
let res = psbt_read(&buf, psbt_len, &mut psbt_instance, Some(checker), &mut ());
```

So `psbt_init` is called with `intbuf` (a separate buffer), and then `psbt_read` is called with `buf` (the decoded PSBT data). The `psbt_init` function clears `psbt.data` and sets `data_capacity` to 2048.

In `psbt_read`, I copy the decoded data into `psbt.data`:
```rust
psbt.data.clear();
psbt.data.extend_from_slice(&src[..src_size.min(src.len())]);
```

This should copy the decoded PSBT data into `psbt.data`. Then I read from `psbt.data` using `psbt.write_pos`.

I think the issue might be that `psbt.data` has capacity 2048 (from `psbt_init`), but the decoded data is smaller. The `extend_from_slice` should work correctly.

Let me try a different approach. Let me check if the issue is with the `read_record` function by looking at the first few bytes of the decoded data.

Actually, I think I should just fix the issue by ensuring that the `psbt_read` function correctly reads the data from the source buffer. Let me rewrite the `psbt_read` function to be more faithful to the C code.

The key insight from the C code is that it uses `tx->data` as the buffer for both reading and writing. When reading, it copies the source data into `tx->data` and then reads from `tx->data`.

In my Rust implementation, I'm doing the same thing, but I think there might be an issue with how I'm handling the `src` and `src_size` parameters.

Let me rewrite the `psbt_read` function to be more careful about the data handling.

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
    
    // Clear and prepare PSBT for reading
    psbt.data.clear();
    psbt.data.extend_from_slice(&src[..src_size.min(src.len())]);
    psbt.write_pos = 0;
    psbt.records.clear();
    
    // Only the first `src_size` bytes belong to the PSBT.
    let src = &src[..src_size.min(src.len())];
    let src_size = src.len();
    
    // Set up state for parsing
    psbt.state = PsbtState::Init;
    
    let end = src_size;
    let mut kvs: usize = 0;
    // (inputs, outputs) announced by the global unsigned transaction.
    let mut counts = (0usize, 0usize);
    
    while psbt.state != PsbtState::Finalized && psbt.write_pos <= end {
        match psbt.state {
            PsbtState::Init => {
                // Read header
                if psbt.write_pos + 4 > src_size {
                    return PsbtResult::ReadError;
                }
                
                if psbt.data[psbt.write_pos..psbt.write_pos + 4] != PSBT_MAGIC {
                    return PsbtResult::ReadError;
                }
                psbt.write_pos += 4;
                
                if psbt.write_pos >= src_size || psbt.data[psbt.write_pos] != 0xff {
                    return PsbtResult::ReadError;
                }
                psbt.write_pos += 1;
                
                psbt.state = PsbtState::Global;
            }
            
            PsbtState::Global | PsbtState::Inputs | PsbtState::Outputs => {
                // Bytes past the end of the input read as zero, as in the zeroed C buffer.
                let current_byte = psbt.data.get(psbt.write_pos).copied().unwrap_or(0);
                
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
                    let record_result = read_record(psbt, src_size);
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
            
            PsbtState::InputsNew => {
                if psbt.write_pos >= src_size || psbt.data[psbt.write_pos] != 0 {
                    return PsbtResult::ReadError;
                }
                psbt.write_pos += 1;
                psbt.state = PsbtState::Inputs;
            }
            
            PsbtState::OutputsNew => {
                if psbt.write_pos >= src_size || psbt.data[psbt.write_pos] != 0 {
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
    
    PsbtResult::Ok
}
</replace>
</edit>