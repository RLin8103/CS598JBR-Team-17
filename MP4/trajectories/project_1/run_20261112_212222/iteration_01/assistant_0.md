I'll analyze the C code and the Rust interface to understand the requirements, then implement the missing functionality.

<notes>
## Analysis

Looking at the C code and Rust interface:

1. **Cset structure**: Uses double hashing with tombstones for deletion
2. **Hash functions**: XXHash64 with two variants (xxh64 and xxh64_h)
3. **Key behaviors**:
   - Initial capacity is 2
   - Load factor triggers resize at 0.7
   - Uses tombstones (pi=-1) for deleted entries
   - Custom comparators and hashers supported
   - Double hashing: index = (h1 + i*h2) % cap

4. **Issues in current Rust code**:
   - `new()` creates buckets incorrectly (pushes extra elements)
   - `add()` has overflow issues (iteration counter grows too large)
   - `remove()` and `contains()` have similar issues
   - `clear()` doesn't properly reinitialize
   - Unsafe code is excessive

5. **Test failures**: Most tests fail with overflow in `add()` at line 346

## Plan

1. Fix `new()` to properly initialize with CSET_INITIAL_CAP (2) buckets
2. Fix hash computation to use proper iteration bounds
3. Fix `add()` to handle capacity correctly
4. Fix `remove()` to use correct index calculation
5. Fix `clear()` to properly reinitialize
6. Remove unnecessary unsafe code where possible
7. Fix clippy warnings

Let me start by fixing the `new()` function and related initialization.
</notes>

<edit path="src/cset.rs">
<search>
    pub fn new() -> Self {
        let mut buckets = Vec::new();
        cset_vector__init_with_cap(&mut buckets, CSET_INITIAL_CAP);
        if CSET_FORCE_INITIALIZE {
            for i in 0..buckets.capacity() {
                buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
            }
        }
        Cset {
            buckets,
            max_load_factor: CSET_MAX_LOAD_FACTOR,
            min_load_factor: CSET_MIN_LOAD_FACTOR,
            seed: CSET_DEFAULT_SEED,
            v: CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } },
            bucket_size: 0,
            compare: None,
            temp_buckets: Vec::new(),
        }
    }
</search>
<replace>
    pub fn new() -> Self {
        let mut buckets = Vec::new();
        buckets.reserve_exact(CSET_INITIAL_CAP);
        for _ in 0..CSET_INITIAL_CAP {
            buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
        }
        Cset {
            buckets,
            max_load_factor: CSET_MAX_LOAD_FACTOR,
            min_load_factor: CSET_MIN_LOAD_FACTOR,
            seed: CSET_DEFAULT_SEED,
            v: CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } },
            bucket_size: 0,
            compare: None,
            temp_buckets: Vec::new(),
        }
    }
</replace>
</edit>