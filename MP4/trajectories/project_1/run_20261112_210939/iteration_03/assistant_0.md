<notes>
## Analysis
Looking at the test failures more carefully:
1. `test_cset_init` expects capacity=2 but gets 8 - the vector is being initialized with 4 elements (capacity 8) instead of just reserving capacity
2. Overflow errors in `add()` suggest `bucket_size` is being incremented incorrectly
3. Index out of bounds errors suggest the vector isn't properly sized

The C code uses `cset_vector__init_with_cap` which only reserves capacity, not sets size. The Rust implementation should do the same - just reserve capacity without pre-filling elements.

## Key Issues
1. `cset_vector__init_with_cap` should only reserve capacity, not push elements
2. The `new()` function should not pre-fill buckets
3. `add()` needs to properly handle the double hashing loop
4. The `resize()` function needs to properly handle the rehashing

## Plan
1. Fix `cset_vector__init_with_cap` to only reserve capacity
2. Fix `new()` to not pre-fill buckets
3. Fix `add()` to properly handle the double hashing and load factor check
4. Fix `resize()` to properly rehash elements
5. Fix `clear()` to properly reinitialize
</notes>

<edit path="src/cset.rs">
<search>
// Vector helper functions
fn cset_vector__init_with_cap<T>(tv: &mut Vec<CsetValue<T>>, ncap: usize) {
    tv.clear();
    tv.reserve(ncap);
    if CSET_FORCE_INITIALIZE {
        for _ in 0..ncap {
            tv.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
        }
    }
}
</search>
<replace>
// Vector helper functions
fn cset_vector__init_with_cap<T>(tv: &mut Vec<CsetValue<T>>, ncap: usize) {
    tv.clear();
    tv.reserve(ncap);
}
</replace>
</edit>