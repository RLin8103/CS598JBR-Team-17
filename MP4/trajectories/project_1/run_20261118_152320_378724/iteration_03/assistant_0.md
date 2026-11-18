The remaining four unsafe sites are each forced by a frozen signature, and I found no edit that removes one without changing a public contract. Re-deriving the same analysis would only burn budget, so this reply changes no code.

<notes>
Status: 15/15 tests pass, Clippy clean, 0 interface deviations. Not declaring done: 4 unsafe lines remain (goal is zero).

Why each site cannot be removed under the frozen interface:
1. raw_bytes (`from_raw_parts`): `xxh64` and `xxh64_h` take `*const u8`. Reading `len` bytes from a raw pointer requires unsafe. No safe read is possible.
2. alias_mut (`&mut *p`): `get_buckets_ref(&self) -> &mut Vec` and `get_temp_buckets_ref(&self) -> &mut Vec` return a mutable borrow from a shared receiver. Safe Rust needs interior mutability (RefCell/UnsafeCell), which the signature does not allow.
3. copy_of (`ptr::read`): `index(&self) -> T` and `iter(&mut self) -> Vec<T>` must return owned `T` from `&T` with no Clone bound. A bitwise copy is the only option. Unsound for owning T (Box, Vec, String): the set and the caller both own the value.
4. placeholder (`mem::zeroed`): `Cset::new()` must populate `CsetValue<T>` slots (capacity() must equal the bucket count) with no Default bound. Zeroed is UB for T such as &U, Box, NonNull.

Counterexamples to soundness under the frozen contract:
- T = Box<u8> or &u8: placeholder() and copy_of() are UB.
- `cset_hash1_callback(&mut u8, size > 1)`: view_bytes hashes only one byte, not `size`, so C behaviour is not reproduced.

Decision needed from a human, one of:
(a) add `T: Default` (or `T: Clone + Default`) to `impl<T>` bounds, which removes sites 3 and 4; or
(b) change `index`/`iter` to return references or require `T: Clone`; and
(c) change `get_*_buckets_ref` to take `&mut self`, which removes site 2; and
(d) change the callbacks/xxh64 to take `&[u8]`, which removes site 1 and the hash-length bug.

Until one of these is approved, do not attempt further unsafe-count reductions by moving code into helpers or adding lint suppressions.
</notes>