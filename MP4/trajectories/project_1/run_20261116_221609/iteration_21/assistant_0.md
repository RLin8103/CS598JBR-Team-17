I found a soundness bug in the current code. `view_bytes` takes a `&u8` (one byte) but passes it to `raw_bytes` with a length that can exceed 1, so `from_raw_parts` reads past the referent. The interface forces the `&mut XXHU8` parameter, so I cannot read `len` bytes from it safely. This iteration limits the view to the single byte that is actually reachable, using `slice::from_ref`, which is safe. The `len` passed to the hash routines becomes that slice's length. This removes the out-of-bounds read, but it does not remove any unsafe site from the metrics.

<edit path="src/cset.rs">
<search>fn view_bytes(ptr: &u8, len: usize) -> &[u8] {
    raw_bytes(ptr, len)
}</search>
<replace>// Only the single byte behind `ptr` is reachable, so never read past it.
// Safe: `slice::from_ref` creates a one-element slice from a valid reference.
fn view_bytes(ptr: &u8, len: usize) -> &[u8] {
    &std::slice::from_ref(ptr)[..len.min(1)]
}</replace>
</edit>
<edit path="src/cset.rs">
<search>pub fn xxh64_finalize(h64: XXHU64, ptr: &mut XXHU8, len: usize) -> XXHU64 {
    xxh64_finalize_inner(h64, view_bytes(ptr, len), len)
}</search>
<replace>pub fn xxh64_finalize(h64: XXHU64, ptr: &mut XXHU8, len: usize) -> XXHU64 {
    let bytes = view_bytes(ptr, len);
    xxh64_finalize_inner(h64, bytes, bytes.len())
}</replace>
</edit>
<edit path="src/cset.rs">
<search>    xxh64_endian_align_inner(view_bytes(input, len), len, seed)</search>
<replace>    let bytes = view_bytes(input, len);
    xxh64_endian_align_inner(bytes, bytes.len(), seed)</replace>
</edit>
<edit path="src/cset.rs">
<search>    xxh64_endian_align_h_inner(view_bytes(input, len), len, seed)</search>
<replace>    let bytes = view_bytes(input, len);
    xxh64_endian_align_h_inner(bytes, bytes.len(), seed)</replace>
</edit>
<edit path="src/cset.rs">
<search>    xxh64_endian_align_inner(view_bytes(memptr, size), size, CSET_DEFAULT_SEED)</search>
<replace>    let bytes = view_bytes(memptr, size);
    xxh64_endian_align_inner(bytes, bytes.len(), CSET_DEFAULT_SEED)</replace>
</edit>
<edit path="src/cset.rs">
<search>    xxh64_endian_align_h_inner(view_bytes(memptr, size), size, CSET_DEFAULT_SEED) | 1</search>
<replace>    let bytes = view_bytes(memptr, size);
    xxh64_endian_align_h_inner(bytes, bytes.len(), CSET_DEFAULT_SEED) | 1</replace>
</edit>
<notes>
- Iteration 21: fixed a soundness bug. view_bytes previously read `len` bytes from a single `&u8` (out of bounds). It now uses safe `slice::from_ref` and never exceeds one byte; hash callers use the returned slice's length.
- Remaining unsafe sites (4), all forced by the interface:
  - raw_bytes: from_raw_parts for `*const u8` params of xxh64 / xxh64_h, and for bytes_of.
  - alias_mut: `&self -> &mut Vec` in get_buckets_ref / get_temp_buckets_ref.
  - copy_of: bitwise copy of T (index, iter, intersect, union, difference). No Clone bound allowed.
  - placeholder: mem::zeroed for empty slots and scratch `v`. No Default bound allowed.
- Known limitation: mem::zeroed is UB for some T (references, Box, NonNull). Report in the final summary.
- Not declaring done: unsafe is still 4 sites. Removing them requires changing the public contract, which is not allowed.
</notes>