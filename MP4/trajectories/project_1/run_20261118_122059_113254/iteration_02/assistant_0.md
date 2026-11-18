The tests pass and Clippy is clean. The remaining `unsafe` is forced by the frozen interface, so I am not making code edits this turn.

Plan: record why each remaining `unsafe` site cannot be removed without changing a frozen signature or adding a bound the interface forbids, and leave the crate as it is.

<notes>
Status: 15/15 tests pass, Clippy clean, no interface deviations. Correctness fix from iteration 1 (merge rounds only in the len>=32 branch) is in place and verified.

Remaining unsafe (4 blocks), each forced by the frozen interface:
1. raw_bytes (from_raw_parts): xxh64 and xxh64_h take `*const u8`. Reading the buffer requires a raw deref. Safety depends on the caller passing a valid pointer for `len` bytes, which a safe fn cannot enforce.
2. alias_mut (&*mut cast): get_buckets_ref(&self) -> &mut Vec and get_temp_buckets_ref(&self) -> &mut Vec are frozen. Returning &mut from &self needs unsafe or interior mutability. The field types are frozen, so UnsafeCell is not available. Unsound for callers that hold overlapping references.
3. copy_of (ptr::read): index, iter, intersect, union, difference need to return or store owned T from &T. The interface has no Clone bound, so a bitwise copy is the only option. Unsound for T that owns heap data (double free).
4. placeholder (mem::zeroed): new() and empty slots need a T value. No Default bound exists. Zeroed is UB for types like &T, Box, NonNull.
Also bytes_of uses a raw cast plus from_raw_parts to hash/compare T bytes, as C does. It is not counted as a separate block here only because it goes through raw_bytes.

Known limitation: view_bytes with len > 1 hashes only one byte, because cset_hash*_callback takes `&mut u8`. This is a frozen-signature conflict. Conclusion: no safe repair is possible under the frozen interface. Next step if the interface may change: add `T: Clone`/`Default` bounds and store elements in Option<T> or similar, and take `&[u8]` in callbacks.

No code changes this turn. Not declaring done, since unsafe is not zero.
</notes>