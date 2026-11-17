I checked each remaining unsafe site against the frozen interface, and none can be removed without changing a public signature or adding a bound:

- **`raw_bytes`**: `xxh64` and `xxh64_h` take `*const u8`. Reading through a raw pointer requires `from_raw_parts`. The `bytes_of` helper also goes through this site.
- **`alias_mut`**: `get_buckets_ref` and `get_temp_buckets_ref` take `&self` and return `&mut Vec`. Returning a `&mut` from a shared borrow needs unsafe, and `RefCell` would change the return type.
- **`copy_of`**: `index` and the set operations need an owned `T` from a shared reference. Without a `Clone` bound, only a bitwise copy works, so it is unsafe.
- **`placeholder`**: every bucket slot must hold a `T` before any element is inserted, and there is no `Default` bound. `mem::zeroed` is the only option, and it is unsound for some `T`.

This iteration only clarifies the `placeholder` comment so it states the constraint and the known soundness limitation accurately.

<edit path="src/cset.rs">
<search>    // Placeholder element for slots that are never read (pi == 0 or -1).
    // The interface gives no Default bound, so a value of T must be supplied.</search>
<replace>    // Placeholder element for slots that are never read (pi == 0 or -1).
    // Known limitation: the frozen interface gives no Default or Clone bound,
    // so a value of T must be produced bitwise. This is unsound for some T
    // (e.g. references, Box, NonNull). A safe design needs a bound such as
    // T: Default, which the public contract does not allow.</replace>
</edit>
<notes>
- Iteration 22: no unsafe site could be removed. Each is forced by the frozen interface:
  - raw_bytes: from_raw_parts for the `*const u8` params of xxh64 / xxh64_h, and for bytes_of.
  - alias_mut: `&self -> &mut Vec` in get_buckets_ref / get_temp_buckets_ref.
  - copy_of: bitwise copy of T for index / iter / intersect / union / difference (no Clone bound).
  - placeholder: mem::zeroed for empty slots and scratch `v` (no Default bound). Unsound for some T; documented.
- view_bytes is safe (from_ref); no out-of-bounds read remains.
- Unsafe count stays at 4 sites. Reaching zero needs an approved interface change, e.g. `T: Clone + Default` bounds plus `&mut self` on get_buckets_ref / get_temp_buckets_ref, and a `*const u8` to slice signature change for xxh64 / xxh64_h. Not declaring done.
</notes>