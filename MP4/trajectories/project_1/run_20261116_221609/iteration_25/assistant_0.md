No unsafe site can be removed this iteration. I checked each one against the frozen interface:

- **`raw_bytes`**: `xxh64` and `xxh64_h` take `*const u8`, and reading through a raw pointer needs `unsafe`. A safe wrapper would change the signature.
- **`alias_mut`**: `get_buckets_ref` and `get_temp_buckets_ref` take `&self` and return `&mut Vec`. Returning a mutable reference from a shared borrow needs an unsafe cast, unless the fields are wrapped in `UnsafeCell`, and that still needs `unsafe` to dereference.
- **`copy_of`**: `index`, `iter` and the set operations must return owned `T` from `&T`. Without a `Clone` bound, only a bitwise copy works. Bitwise copies are never dropped twice here, because the source stays owned by the set.
- **`placeholder`**: `CsetValue::elem` is a public field of type `T`, so every empty slot must hold a real `T`. Without `Default`, only `mem::zeroed` can produce one. It is unsound for some `T`, and I cannot fix that within the contract.

I am not declaring done. The unsafe count stays at 4 sites, and the `placeholder` soundness gap is open.

<edit path="src/cset.rs">
<search>    // Helper: bitwise-copy a T from a reference (used because T has no Clone
    // bound). The copy is the only owner the caller keeps; the source stays
    // inside the set and is never dropped by this function.</search>
<replace>    // Helper: bitwise-copy a T from a reference (used because T has no Clone
    // bound, so this is the only way to return an owned T from &T). The
    // source stays owned by the set; the copy is returned to the caller, who
    // becomes the single owner of that value. Known limitation: if T owns
    // heap data, the caller and the set both hold it until the set is
    // cleared, so the interface's missing `Clone` bound makes this a risk.</replace>
</edit>
<notes>
- Iteration 25: no unsafe site removed. Each remaining site is forced by the frozen interface (signatures and bounds):
  - raw_bytes: from_raw_parts for the `*const u8` params of xxh64 / xxh64_h (also used by bytes_of).
  - alias_mut: `&self -> &mut Vec` in get_buckets_ref / get_temp_buckets_ref (one cast site).
  - copy_of: bitwise copy of T for index / iter / intersect / union / difference (no Clone bound).
  - placeholder: mem::zeroed for empty slots and scratch `v` (no Default bound; unsound for some T such as references, Box, NonNull).
- Known gaps (interface-caused):
  - `copy_of` on a T that owns heap data yields two owners (set and caller) until the set's slot is overwritten, cleared or dropped. It is not dropped twice while the set holds the same value, but aliasing is possible after `index` / `iter`.
  - xxh64_finalize, xxh64_endian_align(_h), cset_hash1/2_callback take one `&mut u8`, so they hash at most one byte instead of `len` bytes.
- Reaching zero unsafe needs an interface change that is not permitted: `T: Clone + Default` bounds, `&mut self` on get_buckets_ref / get_temp_buckets_ref, and slice parameters for the xxh64 family.
- Not declaring done.
</notes>