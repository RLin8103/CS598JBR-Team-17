I re-checked the probing loops after the `len()` change against the C macros, and found no new difference, so I am making no edits.

- **Probing:** `add`, `remove` and `contains_impl` each run at most `len()` probes with the same `iteration - 1` indexing as `cset__add_`, `cset__remove_` and `cset__contains_`. `pi` is stored as `iteration` (≥ 2), as in C. Tombstones and empty slots are handled as in C.
- **Resize:** the load check uses `size / len >= max_load_factor`, and resize doubles the table. Re-inserting into a table of twice the size cannot trigger another resize.
- **Empty table:** `add` reinitialises an empty table; `clear` and `new` always produce `CSET_INITIAL_CAP` slots, so the modulo by zero is unreachable.
- **Hashing:** the `xxh64_endian_align` and `_h` paths match the C branches for `len < 32` and `len >= 32`, including the seed constants and the final `+ len` before finalize.
- **Set operations:** `intersect`, `union` and `difference` accumulate into `self` as the C macros do. `contains` on `second` uses `second`'s own comparator, as C does.

The remaining differences are the ones the frozen interface forces:
- The xxh64 callbacks and `xxh64_endian_align(_h)` see only one `&mut u8`, so they hash at most one byte.
- A null pointer with `len > 0` panics here, where C would crash.
- The custom hasher field of the C struct has no counterpart in the Rust struct.

<notes>
- Iteration 29 (review): re-checked probing, resize, empty-table handling, hash branches and set operations after the len() change. No new differences found; no edits.
- Unsafe sites (4), each forced by the frozen interface:
  - raw_bytes: from_raw_parts for the `*const u8` params of xxh64 / xxh64_h, and for bytes_of.
  - alias_mut: `&self -> &mut Vec` in get_buckets_ref / get_temp_buckets_ref.
  - copy_of: bitwise copy of T (index, iter, intersect, union, difference); no Clone bound.
  - placeholder: mem::zeroed for empty slots and scratch `v`; no Default bound; unsound for some T.
- Known gaps (interface-caused): xxh64_finalize, xxh64_endian_align(_h), cset_hash1/2_callback receive one `&mut u8`, so they hash at most one byte; xxh64/xxh64_h with null and len > 0 panic (C would crash); the C custom hasher has no Rust counterpart.
</notes>

<done/>