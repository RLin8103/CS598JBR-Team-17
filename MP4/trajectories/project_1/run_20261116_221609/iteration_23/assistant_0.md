No unsafe site can be removed within the frozen interface, so this iteration changes only a comment. The four remaining sites are:

- **`raw_bytes`**: `xxh64` and `xxh64_h` take `*const u8`, and dereferencing a raw pointer needs `unsafe`.
- **`alias_mut`**: `get_buckets_ref` and `get_temp_buckets_ref` take `&self` and return `&mut Vec`.
- **`copy_of`**: `index`, `iter` and the set operations must produce owned `T` values from `&T` with no `Clone` bound.
- **`placeholder`**: `init_buckets` must create `T` values for empty slots, and `CsetValue` (`elem: T`) and `get_buckets` expose that layout. There is no `Default` bound.

I also found a fidelity gap that I had not stated clearly. `view_bytes` now exposes at most one byte, so `cset_hash1_callback` and `cset_hash2_callback` (and the `xxh64_*` functions that take `&mut u8`) hash only the first byte, while the C code hashes `size` bytes. The tests do not call these functions, but the behaviour is wrong for `size > 1`. The fix needs a `*const u8` or slice parameter, which is an interface change.

<edit path="src/cset.rs">
<search>// View a caller-provided `&mut u8` buffer as a byte slice of `len` bytes.
// Only the single byte behind `ptr` is reachable, so never read past it.
// Safe: `slice::from_ref` creates a one-element slice from a valid reference.</search>
<replace>// View a caller-provided `&mut u8` buffer as a byte slice.
// Known limitation: the interface passes only one `&mut u8`, so at most one
// byte is reachable safely. For `len > 1` the C behaviour (hash `len` bytes)
// is NOT reproduced by the callbacks that use this helper. A faithful version
// needs a slice or `*const u8` parameter, which the frozen interface forbids.
// Safe: `slice::from_ref` creates a one-element slice from a valid reference.</replace>
</edit>
<notes>
- Iteration 23: no unsafe site removed; comment-only change (view_bytes limitation).
- Remaining unsafe sites (4), each forced by the frozen interface:
  - raw_bytes: from_raw_parts for `*const u8` params of xxh64 / xxh64_h, and for bytes_of.
  - alias_mut: `&self -> &mut Vec` in get_buckets_ref / get_temp_buckets_ref.
  - copy_of: bitwise copy of T (index, iter, intersect, union, difference). No Clone bound.
  - placeholder: mem::zeroed for empty slots and scratch `v`. No Default bound; unsound for some T.
- Known fidelity gap: xxh64_finalize, xxh64_endian_align(_h), cset_hash1/2_callback receive one `&mut u8`, so they hash at most one byte instead of `len` bytes.
- Required to reach zero unsafe (interface change, not permitted now): `T: Clone + Default` bounds; `&mut self` on get_buckets_ref / get_temp_buckets_ref; `&[u8]` or slice parameters for the xxh64 family.
- Not declaring done.
</notes>