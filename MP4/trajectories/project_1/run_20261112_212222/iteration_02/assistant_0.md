<notes>
## Analysis

Looking at the test failures and C code behavior:

1. **Overflow issue**: The error "attempt to add with overflow" at line 346 (in `add()`) suggests the iteration counter is overflowing. The C code uses `size_t iteration` which wraps around, but Rust's `usize` should handle this. The issue is likely in how we're computing the hash index.

2. **Key insight from C code**: In the C implementation, the iteration counter starts at 1 and increments AFTER computing the index. The loop checks if `(iteration - 1) >= cap` to break. This means we iterate at most `cap` times.

3. **Current bug**: In `add()`, we're computing the hash index AFTER incrementing iteration, but we're using `iteration - 1` which could cause issues. Also, we're not properly handling the case where we need to resize BEFORE inserting.

4. **Test failure pattern**: All tests that add elements fail with overflow, suggesting the issue is in the `add()` function's loop logic.

Let me rewrite the `add()`, `remove()`, and `contains()` functions to match the C behavior exactly.
</notes>

<edit path="src/cset.rs">
<search>
    pub fn add(&mut self, value: T) -> i32 {
        // Compute hash
        let ref_bytes = unsafe { std::slice::from_raw_parts(&value as *const T as *const u8, std::mem::size_of::<T>()) };
        let h1 = self.h1hash(ref_bytes, &value);
        let mut found = false;
        let mut iteration = 1;
        let cap = self.buckets.capacity();
        let mut index = 0;
        for _ in 0..cap {
            let h2 = self.h2hash(ref_bytes, &value);
            index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            iteration += 1;
            if self.is_empty(index) || self.is_tombstone(index) {
                break;
            }
            if self.matches(&self.buckets, ref_bytes, &value, index) {
                found = true;
                break;
            }
        }
        if !found {
            // Ensure capacity
            if self.bucket_size >= cap {
                self.resize(cap * 2);
            }
            let h2 = self.h2hash(ref_bytes, &value);
            index = Self::double_hash_index(h1, h2, iteration - 1, self.buckets.capacity());
            self.buckets[index] = CsetValue { pi: iteration as i32, elem: value };
            self.bucket_size += 1;
        }
        0
    }
</search>
<replace>
    pub fn add(&mut self, value: T) -> i32 {
        // Compute hash
        let ref_bytes = unsafe { std::slice::from_raw_parts(&value as *const T as *const u8, std::mem::size_of::<T>()) };
        let h1 = self.h1hash(ref_bytes, &value);
        let mut found = false;
        let mut iteration = 1usize;
        let cap = self.buckets.capacity();
        let mut index = 0usize;
        
        // Check load factor before adding
        let current_load = self.bucket_size as f64 / cap as f64;
        if current_load >= self.max_load_factor {
            self.resize(cap * 2);
        }
        
        let cap = self.buckets.capacity();
        for _ in 0..cap {
            let h2 = self.h2hash(ref_bytes, &value);
            index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            iteration += 1;
            if self.is_empty(index) || self.is_tombstone(index) {
                break;
            }
            if self.matches(&self.buckets, ref_bytes, &value, index) {
                found = true;
                break;
            }
        }
        if !found {
            let h2 = self.h2hash(ref_bytes, &value);
            index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            self.buckets[index] = CsetValue { pi: iteration as i32, elem: value };
            self.bucket_size += 1;
        }
        0
    }
</replace>
</edit>