The tests, Clippy and the interface checks already pass. The only open failure is the unsafe metric (4 unsafe lines, 4 unsafe calls, 1 raw-pointer dereference). I checked each unsafe site against the frozen signatures and found no safe replacement, so I am not proposing an edit.

<notes>
Status: 15/15 tests pass, Clippy clean, 0 interface deviations. Remaining failure: unsafe metric (lines=4, calls=4, raw deref=1).

Unsafe sites and why each is forced by the frozen interface:
1. `raw_bytes` (`from_raw_parts`): `xxh64(input: *const u8, ..)` and `xxh64_h(input: *const u8, ..)` take raw pointers. Reading `len` bytes from a `*const u8` requires an unsafe dereference or `from_raw_parts`. No safe alternative exists under the frozen signature.
2. `alias_mut` (`&mut *p`): `get_buckets_ref(&self) -> &mut Vec<..>` and `get_temp_buckets_ref(&self) -> &mut Vec<..>` return `&mut` from `&self`. Safe Rust cannot produce this (RefCell/UnsafeCell cannot return a plain `&mut` tied to `&self`).
3. `copy_of` (`ptr::read`): `index(&self) -> T` and `iter(&mut self) -> Vec<T>` must return owned `T` from `&T` with no `Clone` bound. Only a bitwise copy works.
4. `placeholder` (`mem::zeroed`): `Cset::new()` and empty slots need a `T` value in `CsetValue<T>.elem` with no `Default` bound. `MaybeUninit` would also be unsafe.

Counterexample to a fully safe translation: for `T` = `Box<i32>` or `&i32`, `index` / `iter` / `placeholder` are unsound without `Clone`/`Default`. The frozen interface forbids adding those bounds.

Also noted: `cset_hash1_callback` / `cset_hash2_callback` / `xxh64_finalize` / `xxh64_endian_align*` take `&mut u8`, so they can only see one byte. For `len > 1` they hash the wrong input. This is a faithfulness gap the signatures force; the tests do not hit it.

Conclusion: zero unsafe is not reachable under the frozen interface. I stop here without an edit. I did not declare done because the unsafe goal is unmet.
</notes>