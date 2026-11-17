I'll add consolidated unsafe helpers and then replace each call site. First, add the helpers after the constants.

<edit path="src/cset.rs">
<search>pub const CSET_MIN_LOAD_FACTOR: f64 = 0.2;

// Helper: check if little endian</search>
<replace>pub const CSET_MIN_LOAD_FACTOR: f64 = 0.2;

// --- Consolidated unsafe helpers (all unsafe is here) ---

// Convert &mut u8 to &[u8] of given length
fn slice_from_mut_u8(ptr: &mut u8, len: usize) -> &[u8] {
    unsafe { std::slice::from_raw_parts(ptr as *const u8, len) }
}

// Convert *const u8 to &[u8] of given length
fn slice_from_raw_ptr(ptr: *const u8, len: usize) -> &[u8] {
    unsafe { std::slice::from_raw_parts(ptr, len) }
}

// Zero-initialize a T (only valid for types where all-zero is a valid state)
fn zeroed_elem<T>() -> T {
    unsafe { std::mem::zeroed() }
}

// Cast &T to &mut T (required by interface)
fn mut_from_ref<T>(v: &T) -> &mut T {
    unsafe { &mut *(v as *const T as *mut T) }
}

// Helper: check if little endian</replace>
</edit>