No unsafe site can be removed this iteration without changing the frozen interface. I re-checked the four sites:

- **`raw_bytes`**: `xxh64` and `xxh64_h` take `*const u8`, so reading the buffer needs `from_raw_parts`. `bytes_of` also depends on it, because hashing and comparing a `T` need its bytes. Safe code cannot view an arbitrary `T` as bytes.
- **`alias_mut`**: `get_buckets_ref` and `get_temp_buckets_ref` take `&self` and return `&mut Vec`. Doing that safely needs `UnsafeCell` or `RefCell`, which changes the stored field types, and the fields are private but part of the frozen struct definition.
- **`copy_of`**: `index`, `iter` and the set operations return owned `T` from `&T`. Without `Clone`, only a bitwise copy works.
- **`placeholder`**: `CsetValue::elem` is a `T` field, so each empty slot needs a `T`. Without `Default`, only `mem::zeroed` can produce one.

The null-pointer behaviour needs to be stated accurately. A null `input` with `len > 0` is a caller contract violation. C would crash, and Rust currently panics on slice indexing. I'll document that in `raw_bytes`.

I am not declaring done. The unsafe count stays at 4 sites.

<edit path="src/cset.rs">
<search>// Single place that turns a caller-provided raw buffer into a byte slice.
// Needed only because the interface passes `*const u8` to `xxh64` and
// `xxh64_h`. Contract: `ptr` is null or valid for reading `len` bytes.</search>
<replace>// Single place that turns a caller-provided raw buffer into a byte slice.
// Needed because the interface passes `*const u8` to `xxh64` and `xxh64_h`,
// and because `bytes_of` views a `T` through the same path.
// Contract: `ptr` is valid for reading `len` bytes, or `len == 0`. A null
// `ptr` with `len > 0` is a caller contract violation (C would crash); here
// it yields an empty slice, so the hash then panics on indexing.</replace>
</edit>
<notes>
- Iteration 27: no unsafe site removed; only the `raw_bytes` contract comment was clarified (null with len > 0 is a caller violation, yields an empty slice, and then panics on indexing).
- Remaining unsafe sites (4), each forced by the frozen interface:
  - raw_bytes: `from_raw_parts` for the `*const u8` params of xxh64 / xxh64_h, and for `bytes_of` (hashing and equality of T need its bytes).
  - alias_mut: `&self -> &mut Vec` in get_buckets_ref / get_temp_buckets_ref. Safe alternatives (UnsafeCell / RefCell) change the private field types, which are part of the frozen struct.
  - copy_of: bitwise copy of T for index / iter / intersect / union / difference (no Clone bound).
  - placeholder: mem::zeroed for empty slots and scratch `v` (no Default bound; unsound for some T such as references, Box, NonNull).
- Known gaps (interface-caused):
  - copy_of on a T that owns heap data yields two owners until the set's slot is overwritten, cleared or dropped.
  - xxh64_finalize, xxh64_endian_align(_h), cset_hash1/2_callback take one `&mut u8`, so they hash at most one byte instead of `len` bytes.
- Reaching zero unsafe needs an interface change that is not permitted: `T: Clone + Default` bounds, `&mut self` on get_buckets_ref / get_temp_buckets_ref, and slice parameters for the xxh64 family.
- Not declaring done.
</notes>