<notes>
## Analysis
All tests pass. The unsafe metrics show 15 unsafe lines. The main sources are:
1. `xxh_read_le64` and `xxh_read32` - need safe slice-based functions
2. `xxh64` and `xxh64_h` - interface requires `*const u8`, must be marked unsafe
3. `cset_hash1_callback` and `cset_hash2_callback` - need safe slice interfaces
4. `matches` method - uses unsafe for byte comparison
5. `new()`, `clear()`, `resize()` - use `std::mem::zeroed()` which is unsafe

The interface requires `*const u8` for `xxh64` and `xxh64_h`, so those must remain but can be marked unsafe. The callback functions can be changed to take `&[u8]` instead of `&mut XXHU8`.

For CsetValue initialization, I can use `std::mem::MaybeUninit` or just use `Default` if available. Since `T: Clone`, I can use `T::default()` if T implements Default, but the interface doesn't require that.

Let me fix the unsafe code by:
1. Marking `xxh64` and `xxh64_h` as unsafe
2. Changing callback functions to take `&[u8]`
3. Using safe slice operations in `matches`
4. Using `MaybeUninit` for initialization
</notes>

<edit path="src/cset.rs">
<search>
// xxh64
pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    let slice = unsafe { std::slice::from_raw_parts(input, len) };
    xxh64_endian_align(slice, len, seed)
}

// xxh64_h
pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    let slice = unsafe { std::slice::from_raw_parts(input, len) };
    xxh64_endian_align_h(slice, len, seed)
}

// cset_hash1_callback
pub fn cset_hash1_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    let slice = unsafe { std::slice::from_raw_parts(memptr as *const u8, size) };
    xxh64_endian_align(slice, size, CSET_DEFAULT_SEED)
}

// cset_hash2_callback
pub fn cset_hash2_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    let slice = unsafe { std::slice::from_raw_parts(memptr as *const u8, size) };
    xxh64_endian_align_h(slice, size, CSET_DEFAULT_SEED) | 1
}
</search>
<replace>
// xxh64
pub unsafe fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    let slice = std::slice::from_raw_parts(input, len);
    xxh64_endian_align(slice, len, seed)
}

// xxh64_h
pub unsafe fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    let slice = std::slice::from_raw_parts(input, len);
    xxh64_endian_align_h(slice, len, seed)
}

// cset_hash1_callback
pub fn cset_hash1_callback(memptr: &[u8], size: usize) -> XXHU64 {
    xxh64_endian_align(memptr, size, CSET_DEFAULT_SEED)
}

// cset_hash2_callback
pub fn cset_hash2_callback(memptr: &[u8], size: usize) -> XXHU64 {
    xxh64_endian_align_h(memptr, size, CSET_DEFAULT_SEED) | 1
}
</replace>
</edit>