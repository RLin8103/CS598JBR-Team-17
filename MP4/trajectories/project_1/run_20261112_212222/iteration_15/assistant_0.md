<notes>
## Analysis

Looking at the test failures, the issue is that elements are not being found correctly after removal. The key insight is that in the C code, when we find an empty or tombstone slot during search, we break out of the loop and insert there. But in my Rust code, I'm computing the index again after the loop using `iteration - 1`, which might be wrong.

Actually, looking at the C code more carefully, the issue is that in the `add` function, when we find an empty or tombstone slot, we break out of the loop and insert there. The `index` variable is the last computed index when we break out of the loop.

But in my Rust code, I'm computing `index` again after the loop using `iteration - 1`, which is wrong because `iteration` has already been incremented.

Let me trace through the logic:
1. We start with `iteration = 1`
2. In the loop, we compute `index = double_hash_index(h1, h2, iteration - 1, cap)` which is `double_hash_index(h1, h2, 0, cap)`
3. We increment `iteration` to 2
4. If we find an empty or tombstone slot, we break out of the loop
5. Then we compute `index = double_hash_index(h1, h2, iteration - 1, cap)` which is `double_hash_index(h1, h2, 1, cap)`

But the correct index should be the one we computed in step 2, which is `double_hash_index(h1, h2, 0, cap)`.

So the issue is that I'm computing `index` again after the loop, but I should use the `index` from the loop.

Let me fix the `add` function to use the correct index.
</notes>

<edit path="src/cset.rs">
<search>
    pub fn add(&mut self, value: T) -> i32 {
        // Check load factor before adding
        let cap = self.buckets.capacity();
        let current_load = self.bucket_size as f64 / cap as f64;
        if current_load >= self.max_load_factor {
            self.resize(cap * 2);
        }
        
        // Compute hash
        let ref_bytes = unsafe { std::slice::from_raw_parts(&value as *const T as *const u8, std::mem::size_of::<T>()) };
        let h1 = self.h1hash(ref_bytes, &value);
        let mut found = false;
        let mut iteration = 1usize;
        let cap = self.buckets.capacity();
        let mut index = 0usize;
        
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
</search>
<replace>
    pub fn add(&mut self, value: T) -> i32 {
        // Check load factor before adding
        let cap = self.buckets.capacity();
        let current_load = self.bucket_size as f64 / cap as f64;
        if current_load >= self.max_load_factor {
            self.resize(cap * 2);
        }
        
        // Compute hash
        let ref_bytes = unsafe { std::slice::from_raw_parts(&value as *const T as *const u8, std::mem::size_of::<T>()) };
        let h1 = self.h1hash(ref_bytes, &value);
        let mut found = false;
        let mut iteration = 1usize;
        let cap = self.buckets.capacity();
        let mut index = 0usize;
        
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
            self.buckets[index] = CsetValue { pi: iteration as i32, elem: value };
            self.bucket_size += 1;
        }
        0
    }
</replace>