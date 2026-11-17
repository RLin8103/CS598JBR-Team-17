The remaining `unsafe` sites are all forced by the interface, so I can't delete them without changing the public contract. This iteration only fixes two misleading comments: `bytes_of` says "SAFETY" but contains no `unsafe`, and `copy_of`'s comment doesn't state the real ownership rule.

<edit path="src/cset.rs">
<search>    // Helper: view a &T as a &[u8] for hashing and comparison.
    // SAFETY: The caller must ensure the resulting slice is only used for
    // reading bytes, never for interpreting the bytes as a different type.
    fn bytes_of(v: &T) -> &[u8] {</search>
<replace>    // Helper: view a &T as its raw bytes for hashing and comparison.
    // Goes through `raw_bytes`, so this file has a single raw-slice site.
    fn bytes_of(v: &T) -> &[u8] {</replace>
</edit>
<edit path="src/cset.rs">
<search>    // Helper: bitwise-copy a T from a reference (used when T has no Clone bound).
    // SAFETY: The caller must ensure the source is a valid T and the copy is
    // not dropped twice (the destination takes ownership).
    fn copy_of(v: &T) -> T {</search>
<replace>    // Helper: bitwise-copy a T from a reference (used because T has no Clone
    // bound). The copy is the only owner the caller keeps; the source stays
    // inside the set and is never dropped by this function.
    fn copy_of(v: &T) -> T {</replace>
</edit>
<notes>
- Iteration 18: comment-only cleanup (bytes_of no longer claims a SAFETY contract it doesn't need; copy_of states the ownership rule).
- Remaining unsafe, all forced by the interface (fixed signatures, no Clone/Default bounds):
  - raw_bytes: the single from_raw_parts site, needed for xxh64/xxh64_h (`*const u8` params).
  - alias_mut: `&self -> &mut Vec` in get_buckets_ref / get_temp_buckets_ref.
  - copy_of: bitwise copy of T for index/iter/intersect/union/difference (no Clone bound).
  - mem::zeroed x2: placeholder T for empty slots and the scratch field `v` (no Default bound).
- Known limitation: mem::zeroed is UB for some T (references, Box, NonNull). Report in the final summary.
- Not declaring done: unsafe is not zero. Further progress requires changing the interface, which is not allowed.
</notes>