This reply consolidates the five `&mut u8` buffer views into one `view_bytes` helper and removes the unused `mut` on `xxh64_finalize`. The helper takes a `&u8` with an elided lifetime, which avoids the missing-lifetime error from the reverted attempts.

<edit path="src/cset.rs">
<search>pub const CSET_MIN_LOAD_FACTOR: f64 = 0.2;</search>
<replace>pub const CSET_MIN_LOAD_FACTOR: f64 = 0.2;

// Single place that views a caller-provided buffer as a byte slice.
fn view_bytes(ptr: &u8, len: usize) -> &[u8] {
    // SAFETY: the caller guarantees that `ptr` points to at least `len` readable bytes.
    unsafe { std::slice::from_raw_parts(ptr, len) }
}</replace>
</edit>
<edit path="src/cset.rs">
<search>pub fn xxh64_finalize(mut h64: XXHU64, ptr: &mut XXHU8, len: usize) -> XXHU64 {
    // SAFETY: caller guarantees ptr points to at least len bytes of valid memory
    let slice = unsafe { std::slice::from_raw_parts(ptr as *const u8, len) };
    xxh64_finalize_inner(h64, slice, len)
}</search>
<replace>pub fn xxh64_finalize(h64: XXHU64, ptr: &mut XXHU8, len: usize) -> XXHU64 {
    xxh64_finalize_inner(h64, view_bytes(ptr, len), len)
}</replace>
</edit>
<edit path="src/cset.rs">
<search>pub fn xxh64_endian_align(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    // SAFETY: caller guarantees input points to at least len bytes of valid memory
    let slice = unsafe { std::slice::from_raw_parts(input as *const u8, len) };
    xxh64_endian_align_inner(slice, len, seed)
}</search>
<replace>pub fn xxh64_endian_align(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    xxh64_endian_align_inner(view_bytes(input, len), len, seed)
}</replace>
</edit>
<edit path="src/cset.rs">
<search>pub fn xxh64_endian_align_h(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    // SAFETY: caller guarantees input points to at least len bytes of valid memory
    let slice = unsafe { std::slice::from_raw_parts(input as *const u8, len) };
    xxh64_endian_align_h_inner(slice, len, seed)
}</search>
<replace>pub fn xxh64_endian_align_h(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    xxh64_endian_align_h_inner(view_bytes(input, len), len, seed)
}</replace>
</edit>
<edit path="src/cset.rs">
<search>pub fn cset_hash1_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    // SAFETY: memptr points to at least size bytes of valid memory
    let slice = unsafe { std::slice::from_raw_parts(memptr as *const u8, size) };
    xxh64_endian_align_inner(slice, size, CSET_DEFAULT_SEED)
}</search>
<replace>pub fn cset_hash1_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    xxh64_endian_align_inner(view_bytes(memptr, size), size, CSET_DEFAULT_SEED)
}</replace>
</edit>
<edit path="src/cset.rs">
<search>pub fn cset_hash2_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    // SAFETY: memptr points to at least size bytes of valid memory
    let slice = unsafe { std::slice::from_raw_parts(memptr as *const u8, size) };
    xxh64_endian_align_h_inner(slice, size, CSET_DEFAULT_SEED) | 1
}</search>
<replace>pub fn cset_hash2_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    xxh64_endian_align_h_inner(view_bytes(memptr, size), size, CSET_DEFAULT_SEED) | 1
}</replace>
</edit>
<notes>
- Iteration 13: consolidated the five `&mut u8` -> `&[u8]` raw-slice sites into one private `view_bytes` helper (elided lifetime, single unsafe site).
- Remaining unsafe: view_bytes, xxh64/xxh64_h raw-pointer slices, bytes_of, copy_of, mem::zeroed x3, get_buckets_ref/get_temp_buckets_ref casts (required by interface &self -> &mut).
- TODO next: replace the three mem::zeroed sites (generic T, risky) and merge bytes_of/copy_of helpers.
- Keep each reply to one or two small edits; verify tests stay at 15/15.
</notes>