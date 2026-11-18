This is the final iteration. The remaining four unsafe sites are forced by the frozen interface, so I am not declaring done. I'm making one small, behaviour-neutral comment edit so the reply contains a valid edit and the notes stay accurate.

Remaining unsafe sites and why each is forced:
- `raw_bytes` (`from_raw_parts`): `xxh64` and `xxh64_h` take `*const u8`, and reading that pointer requires unsafe.
- `alias_mut` (`&mut *p`): `get_buckets_ref(&self) -> &mut Vec` must return a mutable reference from a shared one. Only `UnsafeCell` could avoid this, and the frozen struct fields do not allow it.
- `copy_of` (`ptr::read`): `index`, `iter`, `intersect`, `union` and `difference` must return owned `T` from `&T`. With no `Clone` bound, a bitwise copy is the only option. This is unsound for owning `T` (double drop).
- `placeholder` (`mem::zeroed`): empty slots need a `T` value, and there is no `Default` bound. This is unsound for types such as references, `Box` and `NonNull`.

<edit path="src/cset.rs">
<search>
// Single place that turns a caller-provided raw buffer into a byte slice.
</search>
<replace>
// Single place that turns a caller-provided raw buffer into a byte slice.
// Remaining unsafe here is forced by the frozen `*const u8` signatures of
// `xxh64` and `xxh64_h`.
</replace>
</edit>

<notes>
Status: 15/15 tests pass, clippy clean, 0 interface deviations.
Unsafe remains (4 sites), each forced by a frozen signature or missing bound:
1. raw_bytes: from_raw_parts for `*const u8` in xxh64/xxh64_h.
2. alias_mut: &self -> &mut Vec in get_buckets_ref/get_temp_buckets_ref.
3. copy_of: ptr::read to return owned T from &T without a Clone bound. Unsound for owning T (double drop).
4. placeholder: mem::zeroed for empty slots without a Default bound. Unsound for T with invalid zero bit patterns.
Known correctness gap: view_bytes exposes only one byte of the &mut u8 buffer, so callbacks hash 1 byte when size > 1.
Not declaring done: unsafe is non-zero and the forced sites cannot be removed under the frozen interface.
</notes>