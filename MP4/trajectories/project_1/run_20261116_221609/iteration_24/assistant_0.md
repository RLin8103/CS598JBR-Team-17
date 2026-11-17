No further unsafe site can be removed inside the frozen interface, so I'm not changing the unsafe count this round. Each remaining site is forced by a signature or bound I'm not allowed to change:

- **`raw_bytes`**: `xxh64` and `xxh64_h` take `*const u8`, so reading the buffer needs `from_raw_parts`.
- **`alias_mut`**: `get_buckets_ref` and `get_temp_buckets_ref` take `&self` and return `&mut Vec`.
- **`copy_of`**: `index`, `iter` and the set operations must return owned `T` from `&T` without a `Clone` bound.
- **`placeholder`**: empty slots and the `v` field must hold a `T` without a `Default` bound.

While checking fidelity I found a real bug in `xxh64` and `xxh64_h`. They return 0 for `len == 0`, but the C `XXH64_endian_align` hashes the empty input to `seed + PRIME64_5` (or `+ PRIME64_1` for the `_h` variant) and then finalizes. The inner functions already handle an empty slice with `len == 0`, so I'm removing the early return.

<edit path="src/cset.rs">
<search>pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if len == 0 {
        return 0;
    }
    xxh64_endian_align_inner(raw_bytes(input, len), len, seed)</search>
<replace>pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    xxh64_endian_align_inner(raw_bytes(input, len), len, seed)</replace>
</edit>
<edit path="src/cset.rs">
<search>pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if len == 0 {
        return 0;
    }
    xxh64_endian_align_h_inner(raw_bytes(input, len), len, seed)</search>
<replace>pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    xxh64_endian_align_h_inner(raw_bytes(input, len), len, seed)</replace>
</edit>
<notes>
- Iteration 24: removed the `len == 0 => return 0` shortcut from xxh64 / xxh64_h. The C code hashes the empty input (seed + PRIME64_5 or PRIME64_1, then finalize), so the old result was wrong. Tests are unaffected.
- Remaining unsafe sites (4), each forced by the frozen interface:
  - raw_bytes: from_raw_parts for `*const u8` params of xxh64 / xxh64_h (also used by bytes_of).
  - alias_mut: `&self -> &mut Vec` in get_buckets_ref / get_temp_buckets_ref.
  - copy_of: bitwise copy of T (index, iter, intersect, union, difference). No Clone bound.
  - placeholder: mem::zeroed for empty slots and scratch `v`. No Default bound; unsound for some T.
- Known fidelity gap: xxh64_finalize, xxh64_endian_align(_h), cset_hash1/2_callback receive one `&mut u8`, so they hash at most one byte instead of `len` bytes.
- Reaching zero unsafe needs an interface change that is not permitted: `T: Clone + Default` bounds, `&mut self` on get_buckets_ref / get_temp_buckets_ref, and slice parameters for the xxh64 family.
- Not declaring done.
</notes>