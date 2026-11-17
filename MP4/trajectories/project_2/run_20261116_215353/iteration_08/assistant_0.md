The test `read_test_vector` fails because the callback receives `record_type = 4` instead of `0`. The test's `checker` function has a local `step` variable that is always 0, so it always checks `assert_eq!(record.record_type, 0)`. The first record in the PSBT_HEX is the global unsigned transaction (type 0), but the callback is receiving a record with type 4 (PSBT_IN_REDEEM_SCRIPT).

The issue is that `psbt_read` is calling the callback with the wrong record. Looking at the C code, the callback is called with `elem.index = kvs` where `kvs` is the record counter. The `kvs` counter is incremented when we encounter a null byte (end of record set).

In my implementation, `kvs` starts at 0 and is incremented when we encounter a null byte. But the callback is called with `kvs` as the index, which should be 0 for the first record, 1 for the second, etc.

The problem is that `kvs` is being incremented at the wrong time. In the C code, `kvs` is incremented when we encounter a null byte in the Inputs or Outputs state. But in my implementation, `kvs` is incremented when we encounter a null byte, which is correct.

Wait, I think the issue is that the callback is being called with the wrong record. The test expects the first callback to have `record_type = 0` (PSBT_GLOBAL_UNSIGNED_TX), but it's getting `record_type = 4` (PSBT_IN_REDEEM_SCRIPT).

This suggests that the callback is being called with the 5th record instead of the 1st record. The 5th record has type 4 (PSBT_IN_REDEEM_SCRIPT).

The issue is that `kvs` is 4 when the callback is called, which means the callback is being called 5 times before the test checks. But the test only checks the first 2 callbacks.

Actually, looking at the test output again: `assertion left == right failed left: 4 right: 0`. This means `record.record_type` is 4, not 0. So the callback is receiving a record with type 4.

The issue is that the callback is being called with the wrong record. The first record should have type 0 (PSBT_GLOBAL_UNSIGNED_TX), but it's getting type 4.

Let me trace through the logic. The PSBT_HEX is decoded and then read. The first record should be the global unsigned transaction (type 0). But the callback is receiving type 4.

I think the issue is that `psbt.data` is being filled with the source data, but then the bounds checking uses `data_len` which is the length of `psbt.data`. The `read_record` function reads from `psbt.data`, which should be correct.

Wait, I think I see the issue. The `psbt_read` function copies the source data into `psbt.data`, but then the `read_record` function reads from `psbt.data` using `src_size` which is `data_len`. This should be correct.

Let me add some debug output to understand what's happening. Actually, let me just look at the C code more carefully.

In the C code, the `psbt_read` function copies the source data into `tx->data`:
```c
if (src != tx->data)
    memcpy(tx->data, src, src_size);
```

Then it sets `tx->write_pos = tx->data` and `tx->data_capacity = src_size`.

The `read_record` function reads from `tx->write_pos` and advances it.

In my Rust implementation, I'm doing the same thing: copying the source data into `psbt.data`, setting `psbt.write_pos = 0`, and reading from `psbt.data`.

The issue must be in how the records are being read. Let me check the `read_record` function.

Actually, I think the issue is that the `read_record` function is reading the wrong data. Let me check if the data is being copied correctly.

The test calls `psbt_read(&buf, psbt_len, &mut psbt_instance, Some(checker), &mut ())`. The `buf` contains the decoded PSBT data. The `psbt_len` is the length of the decoded data.

In `psbt_read`, I copy the source data into `psbt.data`:
```rust
let copy_len = src_size.min(src.len());
psbt.data.clear();
psbt.data.extend_from_slice(&src[..copy_len]);
```

This should copy the first `src_size` bytes of `src` into `psbt.data`. Then `data_len = psbt.data.len()`.

Then I read records from `psbt.data` using `psbt.write_pos` as the cursor.

The `read_record` function reads the key length, key, value length, and value from `psbt.data` starting at `psbt.write_pos`.

I think the issue might be in how the compactsize is read. Let me check the `compactsize_read` function.

Actually, I think the issue is that the `read_record` function is reading the wrong data because `psbt.data` might not contain the correct data.

Let me add a debug print to see what's happening. But I can't do that in the final code.

Let me think about this differently. The test `read_test_vector` decodes PSBT_HEX into `buf`, then reads it. The decoded data should be a valid PSBT with a global unsigned transaction record (type 0) followed by input records.

The callback is called with `record_type = 4`, which is PSBT_IN_REDEEM_SCRIPT. This means the callback is being called with an input record instead of the global record.

This suggests that the global record is not being read correctly, or the callback is being called with the wrong record.

Wait, I think I see the issue now. The `psbt_read` function is called with `src_size = psbt_len`, which is the length of the decoded data. But the `buf` might have more data than `psbt_len` because it was allocated with size 2048.

In my implementation, I copy `src_size.min(src.len())` bytes from `src` into `psbt.data`. Since `src_size = psbt_len` and `src.len() = 2048`, this copies `psbt_len` bytes.

But then `data_len = psbt.data.len()` which should be `psbt_len`.

The `read_record` function reads from `psbt.data` using `psbt.write_pos` as the cursor. This should be correct.

Let me check if the issue is in the `read_record` function. The function reads the key length using `compactsize_read`, then reads the key, then reads the value length, then reads the value.

The key length includes the type byte. So if the key length is 1, the key is just the type byte (1 byte), and the key data is empty (0 bytes).

The value is the actual data.

I think the issue might be that the `read_record` function is reading the wrong data because `psbt.data` doesn't contain the correct data.

Let me check if the `psbt_decode` function is working correctly. The test `encode_decode_test` passes, which means `psbt_decode` is working correctly.

So the decoded data in `buf` should be correct. The issue must be in how `psbt_read` reads the data.

Let me add a debug print to see what's happening. Actually, let me just look at the code more carefully.

In the `psbt_read` function, I have:
```rust
let copy_len = src_size.min(src.len());
psbt.data.clear();
psbt.data.extend_from_slice(&src[..copy_len]);
```

This copies the first `src_size` bytes of `src` into `psbt.data`. But `src` is the `buf` parameter, which has length 2048. `src_size` is `psbt_len`, which is the length of the decoded data.

So `copy_len = psbt_len.min(2048) = psbt_len`. This should copy the correct number of bytes.

Then `data_len = psbt.data.len() = psbt_len`.

The `read_record` function reads from `psbt.data` using `psbt.write_pos` as the cursor. This should be correct.

I'm confused about why the callback is receiving the wrong record. Let me add a debug print to see what's happening.

Actually, I think I need to look at the C code more carefully. In the C code, the `psbt_read` function has:
```c
if (src != tx->data)
    memcpy(tx->data, src, src_size);
```

This copies `src_size` bytes from `src` to `tx->data`. Then `tx->write_pos = tx->data` and `tx->data_capacity = src_size`.

In my Rust implementation, I'm doing the same thing. But there's a subtle difference: in the C code, `tx->data` is a pointer to the buffer that was passed to `psbt_init`. In my Rust implementation, `psbt.data` is a `Vec<u8>` that is cleared and extended with the source data.

The issue might be that `psbt.data` is being extended with the source data, but the `psbt_init` function was called with a different buffer. In the test, `psbt_init` is called with `&mut intbuf`, but then `psbt_read` is called with `&buf`. The `psbt
... [reply truncated in history]