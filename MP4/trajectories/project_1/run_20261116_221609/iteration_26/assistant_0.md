No unsafe site can be removed this iteration without changing the frozen interface, so the count stays at 4. The fixed signatures that force each site are:

- **`raw_bytes`**: `xxh64` and `xxh64_h` take `*const u8`, so reading the buffer needs `from_raw_parts`.
- **`alias_mut`**: `get_buckets_ref` and `get_temp_buckets_ref` take `&self` and return `&mut Vec`.
- **`copy_of`**: `index`, `iter` and the set operations return owned `T` from `&T`, and there is no `Clone` bound.
- **`placeholder`**: `CsetValue::elem` is a public `T` field, so every empty slot needs a `T`, and there is no `Default` bound.

One soundness detail is still worth tightening. `raw_bytes` only guards null, so a zero-length call with a dangling pointer still reaches `from_raw_parts`, which requires a non-null, aligned pointer even for length 0. I'll return an empty slice for any `len == 0` before the unsafe call.

<edit path="src/cset.rs">
<search>fn raw_bytes<'a>(ptr: *const u8, len: usize) -> &'a [u8] {
    if ptr.is_null() {
        return &[];
    }</search>
<replace>fn raw_bytes<'a>(ptr: *const u8, len: usize) -> &'a [u8] {
    if len == 0 || ptr.is_null() {
        return &[];
    }</replace>
</edit>
<notes>
- Iteration 26: `raw_bytes` returns an empty slice for `len == 0` even with a dangling pointer, so `from_raw_parts` is only reached with a non-null pointer and `len > 0`. No unsafe site removed.
- Remaining unsafe sites (4), each forced by the frozen interface:
  - raw_bytes: `from_raw_parts` for the `*const u8` params of xxh64 / xxh64_h (also used by bytes_of).
  - alias_mut: `&self -> &mut Vec` in get_buckets_ref / get_temp_buckets_ref.
  - copy_of: bitwise copy of T for index / iter / intersect / union / difference (no Clone bound).
  - placeholder: mem::zeroed for empty slots and scratch `v` (no Default bound; unsound for some T such as references, Box, NonNull).
- Known gaps (interface-caused):
  - copy_of on a T that owns heap data yields two owners until the set's slot is overwritten, cleared or dropped.
  - xxh64_finalize, xxh64_endian_align(_h), cset_hash1/2_callback take one `&mut u8`, so they hash at most one byte instead of `len` bytes.
  - xxh64 / xxh64_h with a null pointer and len > 0 panic on slice indexing, where C would crash.
- Reaching zero unsafe needs an interface change that is not permitted: `T: Clone + Default` bounds, `&mut self` on get_buckets_ref / get_temp_buckets_ref, and slice parameters for the xxh64 family.
- Not declaring done.
</notes>