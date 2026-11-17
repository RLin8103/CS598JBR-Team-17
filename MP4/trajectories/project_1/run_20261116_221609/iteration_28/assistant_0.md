The review found four behaviour differences from the C code. I'm fixing them now and leaving the unsafe count unchanged, since the frozen interface forces those four sites.

1. **`xxh64_merge_round` (wrong result):** C computes `acc ^= round(0, val); acc = acc * P1 + P4`. The Rust expression xor-ed `acc` with `(val * P1 + P4)`, which is a different function. This affects the hash of every element of 32 bytes or more, and therefore the set's hashing for any `T` of 32 bytes or more.
2. **`capacity()` used as the table size:** the probing code indexes `self.buckets` with values reduced modulo `Vec::capacity()`. If the allocator ever gives a capacity above the length, indexing panics. The table size should be `len()`.
3. **`intersect`, `union` and `difference` clear the result:** the C macros only add to `result` and never clear it, so existing elements remain. The visible tests still pass with accumulation.
4. **`add` on an empty table:** a guard for the empty-table case is now written with `is_empty()`, so the modulo by zero cannot happen.

<edit path="src/cset.rs">
<search>pub fn xxh64_merge_round(acc: XXHU64, val: XXHU64) -> XXHU64 {
    let val = xxh64_round(0, val);
    acc ^ val.wrapping_mul(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_4)
}</search>
<replace>pub fn xxh64_merge_round(acc: XXHU64, val: XXHU64) -> XXHU64 {
    let val = xxh64_round(0, val);
    let acc = acc ^ val;
    acc.wrapping_mul(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_4)
}</replace>
</edit>
<edit path="src/cset.rs">
<search>    pub fn add(&mut self, value: T) -> i32 {
        let cap = self.buckets.capacity();
        if cap == 0 {
            self.buckets = Self::init_buckets(CSET_INITIAL_CAP);
        }
        let cap = self.buckets.capacity();
        let current_load = self.bucket_size as f64 / cap as f64;
        if current_load >= self.max_load_factor && cap > 0 {
            self.resize(cap * 2);
        }

        let h1 = self.h1hash(&value);
        let h2 = self.h2hash(&value);
        let cap = self.buckets.capacity();</search>
<replace>    pub fn add(&mut self, value: T) -> i32 {
        if self.buckets.is_empty() {
            self.buckets = Self::init_buckets(CSET_INITIAL_CAP);
        }
        let cap = self.buckets.len();
        let current_load = self.bucket_size as f64 / cap as f64;
        if current_load >= self.max_load_factor {
            self.resize(cap * 2);
        }

        let h1 = self.h1hash(&value);
        let h2 = self.h2hash(&value);
        let cap = self.buckets.len();</replace>
</edit>
<edit path="src/cset.rs">
<search>    pub fn remove(&mut self, value: T) -> i32 {
        let h1 = self.h1hash(&value);
        let cap = self.buckets.capacity();</search>
<replace>    pub fn remove(&mut self, value: T) -> i32 {
        let h1 = self.h1hash(&value);
        let cap = self.buckets.len();</replace>
</edit>
<edit path="src/cset.rs">
<search>        let h1 = self.h1hash(value);
        let cap = self.buckets.capacity();</search>
<replace>        let h1 = self.h1hash(value);
        let cap = self.buckets.len();</replace>
</edit>
<edit path="src/cset.rs">
<search>        self.buckets.capacity() as i32</search>
<replace>        self.buckets.len() as i32</replace>
</edit>
<edit path="src/cset.rs">
<search>    pub fn intersect(&mut self, first: &Self, second: &Self) {
        self.clear();
</search>
<replace>    pub fn intersect(&mut self, first: &Self, second: &Self) {
</replace>
</edit>
<edit path="src/cset.rs">
<search>    pub fn union(&mut self, first: &Self, second: &Self) {
        self.clear();
</search>
<replace>    pub fn union(&mut self, first: &Self, second: &Self) {
</replace>
</edit>
<edit path="src/cset.rs">
<search>    pub fn difference(&mut self, first: &Self, second: &Self) {
        self.clear();
</search>
<replace>    pub fn difference(&mut self, first: &Self, second: &Self) {
</replace>
</edit>
<notes>
- Iteration 28 (review): fixed four differences from C.
  - xxh64_merge_round now computes (acc ^ round(0,val)) * P1 + P4, as in C (it previously xor-ed with the multiplied value).
  - add/remove/contains_impl/capacity use the table length (`len()`), not `Vec::capacity()`; add initialises an empty table before probing.
  - intersect/union/difference no longer clear the result first, matching the C macros, which only add to `result`.
- Unsafe sites (4), each forced by the frozen interface:
  - raw_bytes: from_raw_parts for the `*const u8` params of xxh64 / xxh64_h, and for bytes_of.
  - alias_mut: `&self -> &mut Vec` in get_buckets_ref / get_temp_buckets_ref.
  - copy_of: bitwise copy of T (index, iter, intersect, union, difference); no Clone bound.
  - placeholder: mem::zeroed for empty slots and scratch `v`; no Default bound; unsound for some T.
- Known gaps (interface-caused): xxh64_finalize, xxh64_endian_align(_h), cset_hash1/2_callback receive one `&mut u8`, so they hash at most one byte instead of `len`; xxh64/xxh64_h with null and len > 0 panic (C would crash).
- Not declaring done yet: the next review pass should re-check the probing loops after the len() change and confirm the tests still pass.
</notes>