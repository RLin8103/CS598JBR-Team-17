The last edit gave no measurable improvement and was reverted, so the current file stays as it is. I found no safe, smaller change that reduces the unsafe count under the frozen interface, so I am not editing any files this turn.

The remaining four unsafe sites each need an interface change or a trait bound the frozen signatures forbid:

1. **`raw_bytes` (`from_raw_parts`)** is needed because `xxh64` and `xxh64_h` take `*const u8`. Safe Rust cannot read through a raw pointer, so this site stays unless those signatures change.
2. **`alias_mut` (`&mut *p`)** is needed because `get_buckets_ref(&self) -> &mut Vec<_>` returns a mutable reference from a shared receiver. Sound alternatives are `UnsafeCell`/`RefCell` in the struct, which changes fields, or `&mut self`, which changes the signature.
3. **`copy_of` (`ptr::read`)** is needed because `index`, `iter`, `intersect`, `union` and `difference` must return or store owned `T` from `&T`. Without a `Clone` bound this requires a bitwise copy. A bitwise copy of a `T` that owns heap data duplicates ownership, so this is unsound for such `T`.
4. **`placeholder` (`mem::zeroed`)** fills empty slots with a `T` that is never read. Zeroed bytes are not a valid value for types such as `&U`, `Box<U>` or `NonNull<U>`, so this is unsound for those `T`. A `Default` bound would fix it, and the interface does not allow one.

Also, `view_bytes` hashes only one byte of the callback buffer for `size > 1`. This is a correctness gap in `cset_hash1_callback` and `cset_hash2_callback` that the frozen `&mut u8` parameter causes. The tests pass because they do not exercise it.

A decision is needed from you. Options:
- (a) Allow `*const u8`/slice parameters in the xxhash and callback functions.
- (b) Allow `T: Clone` or `T: Default` bounds on the `Cset` impl.
- (c) Allow `&mut self` on the accessors and `RefCell` or `UnsafeCell` fields.
- (d) Accept the current 4 unsafe lines as a documented residual.

<notes>
Status: 15/15 tests pass, clippy clean, 0 interface deviations, 4 unsafe lines (raw_bytes from_raw_parts, alias_mut &mut *p, copy_of ptr::read, placeholder mem::zeroed).
No edit this turn: every remaining unsafe site is forced by a frozen signature or missing bound (see the four sites above).
Known correctness gap: view_bytes exposes only one byte of the &mut u8 buffer, so callbacks hash 1 byte for size > 1.
Awaiting a decision among options (a)-(d) from the previous turn. Not declaring done, since unsafe is non-zero.
</notes>