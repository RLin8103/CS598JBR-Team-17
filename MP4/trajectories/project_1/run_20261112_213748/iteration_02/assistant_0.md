<notes>
## Analysis
Looking at the test failures and C code more carefully:

1. The C code uses a vector implementation with `cset_vector__init_with_cap` that initializes buckets with `pi=0` for all slots
2. The double hashing formula is: `index = (h1 + i * h2) % cap` where i starts at 0
3. The iteration count in C starts at 1, but the double hash index uses `iteration - 1` (so i=0 for first iteration)
4. Key issues in Rust:
   - `add()` uses wrong iteration logic - it increments iteration before computing index
   - `remove()` has similar issues with iteration tracking
   - `contains()` has wrong iteration logic
   - `resize()` calls `add()` which causes issues with load factor checks
   - `clear()` doesn't properly reinitialize buckets with correct capacity

## Plan
1. Fix `double_hash_index` to use correct formula: `(h1 + i * h2) % cap` where i is 0-based
2. Fix `add()` to properly track iteration and use correct index calculation
3. Fix `remove()` to properly track iteration and use correct index calculation  
4. Fix `contains()` to properly track iteration and use correct index calculation
5. Fix `resize()` to directly insert without calling add() to avoid load factor issues
6. Fix `clear()` to properly reinitialize with correct capacity
7. Fix `iter()` to return correct elements
</notes>

<edit path="src/cset.rs">
<search>
    fn double_hash_index(ha1: XXHU64, ha2: XXHU64, i: usize, cap: usize) -> usize {
        // Use wrapping arithmetic to avoid overflow
        let ha1_usize = ha1 as usize;
        let ha2_usize = ha2 as usize;
        let product = i.wrapping_mul(ha2_usize);
        (ha1_usize.wrapping_add(product)) % cap
    }
</search>
<replace>
    fn double_hash_index(ha1: XXHU64, ha2: XXHU64, i: usize, cap: usize) -> usize {
        // Double hashing: (h1 + i * h2) % cap where i is 0-based
        let ha1_usize = ha1 as usize;
        let ha2_usize = ha2 as usize;
        let product = i.wrapping_mul(ha2_usize);
        (ha1_usize.wrapping_add(product)) % cap
    }
</replace>
</edit>