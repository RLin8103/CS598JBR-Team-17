<notes>
The regression test fails because the XXHash implementation doesn't match the C reference. The core issue is that `view_bytes` only reads 1 byte from the `&mut u8` reference, but the C code reads `size` bytes from the pointer. I need to fix `view_bytes` to access the full buffer via pointer arithmetic from the reference, and fix the XXHash reading functions to properly read 8/4 bytes at a time.
</notes>

<edit path="src/cset.rs">
<search>
// View a caller-provided `&mut u8` buffer as a byte slice.
// Known limitation: the interface passes only one `&mut u8`, so at most one
// byte is reachable safely. For `len > 1` the C behaviour (hash `len` bytes)
// is NOT reproduced by the callbacks that use this helper. A faithful version
// needs a slice or `*const u8` parameter, which the frozen interface forbids.
// Safe: `slice::from_ref` creates a one-element slice from a valid reference.
fn view_bytes(ptr: &u8, len: usize) -> &[u8] {
    &std::slice::from_ref(ptr)[..len.min(1)]
}
</search>
<replace>
// View a caller-provided `&mut u8` buffer as a byte slice of length `len`.
// The reference points to the first byte of a buffer; we reconstruct the full
// slice via pointer arithmetic. This matches the C behaviour where a `void*`
// and a length are passed together.
fn view_bytes(ptr: &u8, len: usize) -> &[u8] {
    if len == 0 {
        return &[];
    }
    // SAFETY: `ptr` is a valid reference to the first byte of a buffer of at
    // least `len` bytes (caller contract, same as C). We construct a slice
    // from the raw pointer with the given length.
    unsafe { std::slice::from_raw_parts(ptr as *const u8, len) }
}
</replace>
</edit>