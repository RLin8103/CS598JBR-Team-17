This iteration removes three `as` pointer casts without changing any behaviour. `view_bytes` relies on the implicit `&u8` to `*const u8` coercion. `alias_mut` and `copy_of` use `ptr::from_ref`, `cast_mut` and `ptr::read` instead of `as`. The `unsafe` blocks remain, because the interface forces them (see the notes).

<edit path="src/cset.rs">
<search>fn view_bytes(ptr: &u8, len: usize) -> &[u8] {
    raw_bytes(ptr as *const u8, len)
}</search>
<replace>fn view_bytes(ptr: &u8, len: usize) -> &[u8] {
    raw_bytes(ptr, len)
}</replace>
</edit>
<edit path="src/cset.rs">
<search>fn alias_mut<U>(r: &U) -> &mut U {
    let p = r as *const U as *mut U;</search>
<replace>fn alias_mut<U>(r: &U) -> &mut U {
    let p = std::ptr::from_ref(r).cast_mut();</replace>
</edit>
<edit path="src/cset.rs">
<search>    fn copy_of(v: &T) -> T {
        unsafe { std::ptr::read(v as *const T) }
    }</search>
<replace>    fn copy_of(v: &T) -> T {
        unsafe { std::ptr::read(std::ptr::from_ref(v)) }
    }</replace>
</edit>
<notes>
- Iteration 17: removed three `as` pointer casts (view_bytes uses implicit coercion; alias_mut and copy_of use ptr::from_ref / cast_mut).
- Remaining unsafe, all forced by the interface (no Clone/Default bounds, fixed signatures):
  - raw_bytes: the single from_raw_parts site, needed for xxh64/xxh64_h (`*const u8` params).
  - alias_mut: `&self -> &mut Vec` in get_buckets_ref / get_temp_buckets_ref.
  - copy_of: bitwise copy of T for index/iter/intersect/union/difference (no Clone bound).
  - mem::zeroed x2: placeholder T for empty slots and scratch field `v` (no Default bound).
- Known limitation: mem::zeroed is UB for some T (references, Box, NonNull). Report in the final summary.
- Next: verify build/test/clippy stay clean; then declare done with these limitations.
</notes>