This iteration merges the two `mem::zeroed` sites into one private `placeholder()` helper. That leaves a single unsafe placeholder site instead of two. It does not remove the unsafe, because the interface requires a `T` in every empty slot and has no `Default` bound.

<edit path="src/cset.rs">
<search>    fn init_buckets(cap: usize) -> Vec<CsetValue<T>> {
        let mut v = Vec::with_capacity(cap);
        for _ in 0..cap {
            // SAFETY: Zero-initialized memory is valid for types used in tests
            // (i32, char, Node). The elem field is never read for empty slots.
            let elem = unsafe { std::mem::zeroed() };
            v.push(CsetValue { pi: 0, elem });
        }
        v
    }</search>
<replace>    // Placeholder element for slots that are never read (pi == 0 or -1).
    // The interface gives no Default bound, so a value of T must be supplied.
    fn placeholder() -> T {
        // SAFETY: the value is only stored in empty slots and never read.
        unsafe { std::mem::zeroed() }
    }

    fn init_buckets(cap: usize) -> Vec<CsetValue<T>> {
        (0..cap)
            .map(|_| CsetValue {
                pi: 0,
                elem: Self::placeholder(),
            })
            .collect()
    }</replace>
</edit>
<edit path="src/cset.rs">
<search>        // SAFETY: Zero-initialized memory is valid for types used in tests.
        // The v field is a scratch slot, initialized before use.
        let elem = unsafe { std::mem::zeroed() };
        Cset {</search>
<replace>        Cset {</replace>
</edit>
<edit path="src/cset.rs">
<search>            v: CsetValue { pi: 0, elem },</search>
<replace>            v: CsetValue {
                pi: 0,
                elem: Self::placeholder(),
            },</replace>
</edit>
<notes>
- Iteration 19: the two `mem::zeroed` sites are now one private `placeholder()` helper, used by `init_buckets` and `new` (scratch field `v`).
- Remaining unsafe, all forced by the interface (fixed signatures, no Clone/Default bounds):
  - raw_bytes: the single from_raw_parts site, for xxh64/xxh64_h (`*const u8` params).
  - alias_mut: `&self -> &mut Vec` in get_buckets_ref / get_temp_buckets_ref.
  - copy_of: bitwise copy of T for index/iter/intersect/union/difference (no Clone bound).
  - placeholder: mem::zeroed for empty slots and scratch `v` (no Default bound).
- Known limitation: mem::zeroed is UB for some T (references, Box, NonNull). Report in the final summary.
- Not declaring done: unsafe is still 4 sites. Removing them needs a public-interface change, which is not allowed.
</notes>