<notes>
## Analysis
All tests pass now. The unsafe metrics show 15 unsafe lines with 15 calls and 14 casts. The main sources of unsafe code are:

1. `xxh_read_le64` and `xxh_read32` - need to convert to safe slice-based functions
2. `xxh64` and `xxh64_h` - need to be marked unsafe or use safe interfaces
3. `cset_hash1_callback` and `cset_hash2_callback` - need safe slice interfaces
4. `matches` method - uses unsafe for byte comparison
5. `new()`, `clear()`, `resize()` - use `std::mem::zeroed()` which is unsafe

The interface requires `*const u8` parameters for `xxh64` and `xxh64_h`, so those must remain as-is but can be marked unsafe. The callback functions can be changed to take `&[u8]` instead of `&mut XXHU8`.

For the CsetValue initialization, I can use `std::mem::MaybeUninit` or just use `Default` if available. Since `T: Clone`, I can use `T::default()` if T implements Default, but the interface doesn't require that.

Let me fix the unsafe code by:
1. Marking `xxh64` and `xxh64_h` as unsafe
2. Changing callback functions to take `&[u8]`
3. Using safe slice operations in `matches`
4. Using `MaybeUninit` for initialization
</notes>

<edit path="src/cset.rs">
<search>
// Read 8 bytes as little-endian from a pointer
pub fn xxh_read_le64(mem_ptr: &mut XXHU8) -> XXHU64 {
    let ptr = mem_ptr as *mut XXHU8;
    let bytes = unsafe { std::slice::from_raw_parts(ptr as *const u8, 8) };
    u64::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7]])
}

// Read 8 bytes as little-endian from a pointer (aligned version)
pub fn xxh_read_le64_align(mem_ptr: &mut XXHU8) -> XXHU64 {
    xxh_read_le64(mem_ptr)
}
</search>
<replace>
// Read 8 bytes as little-endian from a pointer
pub fn xxh_read_le64(mem_ptr: &mut XXHU8) -> XXHU64 {
    let ptr = mem_ptr as *mut XXHU8;
    let bytes = unsafe { std::slice::from_raw_parts(ptr as *const u8, 8) };
    u64::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7]])
}

// Read 8 bytes as little-endian from a pointer (aligned version)
pub fn xxh_read_le64_align(mem_ptr: &mut XXHU8) -> XXHU64 {
    xxh_read_le64(mem_ptr)
}
</replace>
</edit>