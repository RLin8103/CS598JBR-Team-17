This iteration can only remove one small unsafe block. `bytes_of` has its own `from_raw_parts` call, which duplicates what `raw_bytes` already does. I'll route it through `raw_bytes`, so the crate has one raw-slice construction site.

The other remaining sites are forced by the interface. `copy_of` (`index`, `iter`, `intersect`, `union`, `difference`) needs a bitwise copy because the interface gives `T` no `Clone` bound. `mem::zeroed` fills empty slots and the `v` scratch field, but the interface gives `T` no `Default` bound and the struct layout is fixed. `alias_mut` exists because `get_buckets_ref` takes `&self` and returns `&mut`. Removing these would change the public contract.

<edit path="src/cset.rs">
<search>    fn bytes_of(v: &T) -> &[u8] {
        unsafe {
            std::slice::from_raw_parts(
                v as *const T as *const u8,
                std::mem::size_of::<T>(),
            )
        }
    }</search>
<replace>    fn bytes_of(v: &T) -> &[u8] {
        raw_bytes(std::ptr::from_ref(v).cast::<u8>(), std::mem::size_of::<T>())
    }</replace>
</edit>
<notes>
- Iteration 16: `bytes_of` now delegates to `raw_bytes` (one raw-slice construction site for the whole crate, besides `alias_mut`).
- Remaining unsafe (all forced by the interface contract, no Clone/Default bounds and fixed signatures):
  - raw_bytes (xxh64/xxh64_h take *const u8)
  - alias_mut (&self -> &mut Vec)
  - copy_of (bitwise copy of T for index/iter/set ops; needs Clone otherwise)
  - mem::zeroed x2 (placeholder T for empty slots and the scratch field `v`)
- Known limitation: mem::zeroed is UB for some T (references, Box, NonNull). Report in the final summary.
- Next: verify build/test/clippy stay clean. Remaining work is only tidy-up; if nothing else is reachable, declare done with the limitations above.
</notes>