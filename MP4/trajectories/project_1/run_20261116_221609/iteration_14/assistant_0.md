The unsafe sites that remain are mostly forced by the interface. `xxh64`, `xxh64_h`, `view_bytes`, `bytes_of`, `copy_of`, `mem::zeroed` and the `&self -> &mut` casts all depend on raw pointers, bitwise copies or `T`-level assumptions that safe Rust can't express without adding bounds the interface forbids. This reply folds the two raw-pointer entry points into the same single helper as `view_bytes`, so the crate has one raw-slice unsafe site instead of three.

<edit path="src/cset.rs">
<search>// Single place that views a caller-provided buffer as a byte slice.
fn view_bytes(ptr: &u8, len: usize) -> &[u8] {
    // SAFETY: the caller guarantees that `ptr` points to at least `len` readable bytes.
    unsafe { std::slice::from_raw_parts(ptr, len) }
}</search>
<replace>// Single place that turns a caller-provided raw buffer into a byte slice.
// SAFETY contract: the caller guarantees `ptr` is non-null and valid for
// reading `len` bytes for the lifetime `'a`.
fn raw_bytes<'a>(ptr: *const u8, len: usize) -> &'a [u8] {
    if ptr.is_null() {
        return &[];
    }
    // SAFETY: see the contract above; null is handled before the call.
    unsafe { std::slice::from_raw_parts(ptr, len) }
}

// View a caller-provided `&mut u8` buffer as a byte slice of `len` bytes.
fn view_bytes(ptr: &u8, len: usize) -> &[u8] {
    raw_bytes(ptr as *const u8, len)
}</replace>
</edit>
<edit path="src/cset.rs">
<search>pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    // SAFETY: caller guarantees input points to valid memory of at least len bytes
    let slice = unsafe { std::slice::from_raw_parts(input, len) };
    xxh64_endian_align_inner(slice, len, seed)
}</search>
<replace>pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if len == 0 {
        return 0;
    }
    xxh64_endian_align_inner(raw_bytes(input, len), len, seed)
}</replace>
</edit>
<edit path="src/cset.rs">
<search>pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    // SAFETY: caller guarantees input points to valid memory of at least len bytes
    let slice = unsafe { std::slice::from_raw_parts(input, len) };
    xxh64_endian_align_h_inner(slice, len, seed)
}</search>
<replace>pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if len == 0 {
        return 0;
    }
    xxh64_endian_align_h_inner(raw_bytes(input, len), len, seed)
}</replace>
</edit>
<notes>
- Iteration 14: merged all raw-slice creation into one helper `raw_bytes` (single unsafe site); `view_bytes` and both `xxh64`/`xxh64_h` delegate to it. Null pointers yield an empty slice.
- Remaining unsafe (forced by interface): raw_bytes; bytes_of and copy_of (T-level byte view / bitwise copy); mem::zeroed x3 (generic T, no Default bound allowed); get_buckets_ref / get_temp_buckets_ref casts (&self -> &mut required by signature).
- Note: the interface forbids adding bounds such as T: Clone/Default, so these cannot be made safe without changing the public contract. Report this in the final summary.
- Next: verify build/test/clippy stay clean; then consider if `copy_of` can use `ManuallyDrop` clarity (no unsafe change).
</notes>