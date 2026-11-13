<notes>
## Analysis
The remaining failures are in `test_cset_clear` and `test_cset_union`. Looking at the errors:
- `test_cset_clear`: index out of bounds at line 245 (in `index()` method)
- `test_cset_union`: index out of bounds at line 245

The issue is that `clear()` doesn't properly reinitialize the buckets with the correct capacity. After `clear()`, the buckets vector is empty, but then we push elements without ensuring proper capacity.

Looking at the C code, `cset__clear` calls `cset__free` then `cset_vector__init_with_cap` which reinitializes with the initial capacity. The Rust version needs to do the same.

Also, the `union` test is failing because after `clear()`, the buckets are empty but then we try to add elements. The issue is that `clear()` should reinitialize the buckets with proper capacity.

Let me fix the `clear()` method to properly reinitialize with the initial capacity.
</notes>

<edit path="src/cset.rs">
<search>
    pub fn clear(&mut self) {
        self.buckets.clear();
        self.bucket_size = 0;
        if CSET_FORCE_INITIALIZE {
            // Re-initialize with initial capacity
            for _ in 0..CSET_INITIAL_CAP {
                self.buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
            }
        }
    }
</search>
<replace>
    pub fn clear(&mut self) {
        self.buckets.clear();
        self.buckets.shrink_to_fit();
        self.bucket_size = 0;
        if CSET_FORCE_INITIALIZE {
            // Re-initialize with initial capacity
            self.buckets.reserve_exact(CSET_INITIAL_CAP);
            for _ in 0..CSET_INITIAL_CAP {
                self.buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
            }
        }
    }
</replace>
</edit>