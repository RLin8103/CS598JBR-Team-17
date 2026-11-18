The controller reports no applied edit last turn. I'm at the final iteration and found no safe change that reduces the remaining unsafe under the frozen interface, so I'm leaving the files unchanged rather than risk breaking the 15 passing tests.

The four remaining unsafe sites each need a frozen signature to change before they can go:

1. **`raw_bytes` / `xxh64`, `xxh64_h`**: these take `*const u8`. Reading `len` bytes requires a raw dereference, and a safe function cannot check the caller's pointer validity.
2. **`alias_mut`**: `get_buckets_ref(&self)` and `get_temp_buckets_ref(&self)` return `&mut Vec`. Returning `&mut` from `&self` needs unsafe or interior mutability, and the field types are frozen.
3. **`copy_of`**: `index`, `iter`, `intersect`, `union` and `difference` must return owned `T` from `&T`. Without a `Clone` bound, only a bitwise copy is possible, which double-frees if `T` owns heap data.
4. **`placeholder`**: `new()` and empty slots need a `T` value. Without a `Default` bound, `mem::zeroed` is the only option, and it is UB for `&T`, `Box` and `NonNull`.

Additionally, `view_bytes` can only hash one byte of a buffer of `len > 1`, because the callbacks take `&mut u8`. This is a second frozen-signature conflict and it affects correctness, not just safety.

<notes>
Status: 15/15 tests pass, Clippy clean, no interface deviations. Not done: unsafe count is 4 blocks.
Blockers (need interface change, not fixable in frozen signatures):
- xxh64/xxh64_h take *const u8 -> raw deref in raw_bytes.
- get_buckets_ref/get_temp_buckets_ref(&self) -> &mut Vec forces alias_mut cast.
- No Clone bound: copy_of uses ptr::read (double-free risk for owning T).
- No Default bound: placeholder uses mem::zeroed (UB for &T, Box, NonNull).
- callbacks take &mut u8, so view_bytes hashes at most 1 byte for len > 1 (correctness gap vs C).
Suggested interface change: add T: Clone or Default bounds (or store Option<T>), take &[u8] in callbacks and hashes.
No code change this iteration.
</notes>