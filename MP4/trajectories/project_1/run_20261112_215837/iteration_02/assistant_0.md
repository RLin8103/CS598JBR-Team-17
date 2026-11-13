I'll fix the unsafe code by replacing raw pointer operations with safe slice operations. Let me start with the XXHash functions that take raw pointers.

<edit path="src/cset.rs">
<search>
// Read 8 bytes as little-endian from a slice
pub fn xxh_read_le64(mem_ptr: &mut XXHU8) -> XXHU64 {
    let ptr = mem_ptr as *mut XXHU8;
    let bytes = unsafe { std::slice::from_raw_parts(ptr as *const u8, 8) };
    u64::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7]])
}
</search>
<replace>
// Read 8 bytes as little-endian from a slice
pub fn xxh_read_le64(mem_ptr: &mut XXHU8) -> XXHU64 {
    let bytes = unsafe { std::slice::from_raw_parts(mem_ptr as *const u8, 8) };
    u64::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7]])
}
</replace>
</edit>