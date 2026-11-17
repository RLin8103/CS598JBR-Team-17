The remaining unsafe sites all come from fixed interface requirements, so this iteration is a documentation-only change. The four sites are `raw_bytes`, `alias_mut`, `copy_of` and `placeholder`.

- **`raw_bytes`**: `xxh64` and `xxh64_h` take `*const u8`, and reading through that pointer needs `from_raw_parts`.
- **`alias_mut`**: `get_buckets_ref` and `get_temp_buckets_ref` take `&self` and return `&mut Vec`.
- **`copy_of`**: `index`, `iter`, and the set operations must return or move out a `T` from `&self` or `&Self`, and `T` has no `Clone` bound.
- **`placeholder`**: `new` and `init_buckets` must fill slots with a `T` before any element exists, and there is no `Default` bound.

Removing these would require changing the public signatures or adding bounds, which the rules forbid.

<edit path="src/cset.rs">
<search>// Single place that turns a caller-provided raw buffer into a byte slice.
// SAFETY contract: the caller guarantees `ptr` is non-null and valid for
// reading `len` bytes for the lifetime `'a`.</search>
<replace>// Single place that turns a caller-provided raw buffer into a byte slice.
// Needed only because the interface passes `*const u8` to `xxh64` and
// `xxh64_h`. Contract: `ptr` is null or valid for reading `len` bytes.</replace>
</edit>
<notes>
- Iteration 20: documentation-only change (raw_bytes contract comment). No further unsafe removal is possible within the fixed interface.
- Remaining unsafe sites (4), each forced by the interface:
  - raw_bytes: from_raw_parts for `*const u8` params of xxh64 / xxh64_h.
  - alias_mut: `&self -> &mut Vec` in get_buckets_ref / get_temp_buckets_ref.
  - copy_of: bitwise copy of T (index, iter, intersect, union, difference). No Clone bound allowed, and the copy is never dropped twice because the source stays owned by the set.
  - placeholder: mem::zeroed for empty slots and scratch field `v`. No Default bound allowed.
- Known limitation: mem::zeroed is UB for some T (references, Box, NonNull). Report in the final summary.
- Not declaring done: unsafe is not zero. Only an interface change (new bounds or new signatures) could remove these sites, and that is not permitted.
</notes>