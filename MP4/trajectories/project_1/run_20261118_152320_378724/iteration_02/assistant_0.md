The four remaining unsafe sites are each forced by the frozen signatures, as the previous notes explain. I checked each one again and found no safe replacement that keeps the public contract. The unsafe count therefore stays at 4, and I am not declaring completion. I am making one small, behaviour-neutral edit so the reply contains a valid block: it turns the `placeholder` comment into an explicit statement of the blocking counterexample.

<edit path="src/cset.rs">
<search>
    // Placeholder element for slots that are never read (pi == 0 or -1).
    // Known limitation: the frozen interface gives no Default or Clone bound,
    // so a value of T must be produced bitwise. This is unsound for some T
    // (e.g. references, Box, NonNull). A safe design needs a bound such as
    // T: Default, which the public contract does not allow.</search>
<replace>    // Placeholder element for slots that are never read (pi == 0 or -1).
    // Blocker (frozen interface): `Cset::new()` must build `CsetValue<T>`
    // slots with no Default bound, so `capacity()` equals the bucket count.
    // Counterexample: T = Box<u8> or &u8 makes this zeroed value undefined
    // behaviour. Safe removal needs a `T: Default` bound, which the
    // interface does not allow.</replace>
</edit>

Notes:
- Status: 15/15 tests pass, Clippy clean, 0 interface deviations, 4 unsafe lines (goal is 0).
- Remaining unsafe sites, each blocked by the frozen signatures:
  1. `raw_bytes`: `xxh64` and `xxh64_h` take `*const u8`. Reading `len` bytes needs unsafe.
  2. `alias_mut`: `get_buckets_ref(&self) -> &mut Vec` cannot be safe without interior mutability.
  3. `copy_of`: `index`/`iter`/`intersect` must return owned `T` from `&T` without a Clone bound.
  4. `placeholder`: slots need a `T` value without a Default bound.
- Known conflict: `cset_hash1_callback`/`cset_hash2_callback` take a single `&mut u8`, so `size > 1` hashes only one byte. This cannot be fixed without changing the signature.
- Decision needed from a human: relax signatures (e.g. `T: Clone + Default`, or slice/`&[u8]` callback parameters) to reach zero unsafe.
- Not declaring done.