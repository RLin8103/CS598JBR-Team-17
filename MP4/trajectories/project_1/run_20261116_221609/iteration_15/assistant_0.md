This reply makes a small change: the two `&self -> &mut Vec` casts in `get_buckets_ref` and `get_temp_buckets_ref` now go through one private helper, so the crate has one cast site instead of two. Behaviour is unchanged.

Two sites I'm leaving alone for now. `mem::zeroed` for a generic `T` is undefined behaviour for some types (references, `Box`), and the interface forbids adding a `Default` bound. Fixing that needs a design change, not a local edit, so I'll record it in the notes rather than guess.

<edit path="src/cset.rs">
<search>    #[allow(invalid_reference_casting, clippy::mut_from_ref)]
    pub fn get_buckets_ref(&self) -> &mut Vec<CsetValue<T>> {
        // SAFETY: The interface requires &self -> &mut Vec, which is inherently unsafe.
        // This matches the C code's behavior where const-correctness is not enforced.
        unsafe { &mut *( &self.buckets as *const Vec<CsetValue<T>> as *mut Vec<CsetValue<T>> ) }
    }

    #[allow(invalid_reference_casting, clippy::mut_from_ref)]
    pub fn get_temp_buckets_ref(&self) -> &mut Vec<CsetValue<T>> {
        // SAFETY: Same as get_buckets_ref - required by interface.
        unsafe { &mut *( &self.temp_buckets as *const Vec<CsetValue<T>> as *mut Vec<CsetValue<T>> ) }
    }</search>
<replace>    pub fn get_buckets_ref(&self) -> &mut Vec<CsetValue<T>> {
        alias_mut(&self.buckets)
    }

    pub fn get_temp_buckets_ref(&self) -> &mut Vec<CsetValue<T>> {
        alias_mut(&self.temp_buckets)
    }</replace>
</edit>
<edit path="src/cset.rs">
<search>// Helper: check if little endian
pub fn xxh_is_little_endian() -> bool {</search>
<replace>// Single place that re-exposes a shared reference as mutable. Required only
// because the interface takes `&self` and returns `&mut Vec`, mirroring the
// C code, which does not enforce const-correctness.
#[allow(invalid_reference_casting, clippy::mut_from_ref)]
fn alias_mut<U>(r: &U) -> &mut U {
    let p = r as *const U as *mut U;
    // SAFETY: `p` derives from a live shared reference; the interface contract
    // is that callers do not use the returned reference while others alias it.
    unsafe { &mut *p }
}

// Helper: check if little endian
pub fn xxh_is_little_endian() -> bool {</replace>
</edit>
<notes>
- Iteration 15: get_buckets_ref / get_temp_buckets_ref now delegate to one private `alias_mut` helper (one cast site instead of two).
- Remaining unsafe: raw_bytes (xxh64/xxh64_h raw ptr input), alias_mut, bytes_of, copy_of, mem::zeroed x3.
- OPEN ISSUE: mem::zeroed for generic T is UB for some T (references, Box, NonNull). Empty slots need a T; interface forbids Default/Clone bounds. Needs a design change (e.g. Vec<Option<T>>-like storage is not allowed by the interface struct), so report as a known limitation.
- Next: verify build/test/clippy clean; then consider replacing bytes_of/copy_of with safe alternatives only if the interface allows.
</notes>