<notes>
## Analysis
All tests pass. The unsafe metrics show 27 unsafe lines. The main sources are:
1. `xxh_read_le64` and `xxh_read32` - need safe slice-based functions
2. `xxh64` and `xxh64_h` - interface requires `*const u8`, must remain unsafe but can add safety docs
3. `matches` method - uses unsafe for byte comparison
4. `new()`, `clear()`, `resize()` - use `std::mem::zeroed()` which is unsafe

The interface requires `*const u8` for `xxh64` and `xxh64_h`, so those must remain unsafe. However, I can add safety documentation to satisfy Clippy.

For `xxh_read_le64` and `xxh_read32`, I can convert them to use safe slice operations by taking a slice directly instead of a pointer.

For `matches`, I can use `std::ptr::read` or `std::ptr::copy_nonoverlapping` to avoid unsafe pointer casts, but since `T: Clone`, I can just clone the value.

For initialization, I can use `std::mem::MaybeUninit` or just use `T::default()` if available. Since the interface doesn't require `Default`, I'll use `std::mem::MaybeUninit` to avoid unsafe `zeroed()`.

Let me fix the Clippy warnings first by adding safety documentation to the unsafe functions, then address the unsafe code.
</notes>

<edit path="src/cset.rs">
<search>
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
</search>
<replace>
/// # Safety
/// The `input` pointer must be valid for reads of `len` bytes.
pub unsafe fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    let slice = std::slice::from_raw_parts(input, len);
    xxh64_endian_align(slice, len, seed)
}

/// # Safety
/// The `input` pointer must be valid for reads of `len` bytes.
pub unsafe fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    let slice = std::slice::from_raw_parts(input, len);
    xxh64_endian_align_h(slice, len, seed)
}
</replace>
</edit>