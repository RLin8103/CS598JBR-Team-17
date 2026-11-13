<notes>
## Analysis
Looking at the test failures more carefully and comparing with C code:

1. The C code's `cset__add_` function uses iteration count to track probe attempts, but the index calculation uses `iteration - 1` as the i value
2. The key issue: in C, `iteration` starts at 1, and `index = (h1 + (iteration-1) * h2) % cap`
3. When we find an empty slot or match, we break, then insert at that index
4. The Rust code has issues with:
   - `add()`: After breaking from loop, it recalculates index using wrong iteration value
   - `remove()`: Same issue - uses wrong iteration value after loop
   - `contains()`: Same issue - uses wrong iteration value

The C code pattern is:
```c
for (;;) {
    index = (h1 + (iteration-1) * h2) % cap;
    iteration++;
    if (empty || tombstone) break;
    if (matches) { found = true; break; }
}
```

So when we break, `iteration` has already been incremented, so the index was computed with `iteration-1`.

Let me rewrite the core methods to match C behavior exactly.
</notes>

<edit path="src/cset.rs">
<search>
    pub fn add(&mut self, value: T) -> i32 {
        // Check load factor before adding
        let cap = self.buckets.capacity();
        if cap == 0 {
            // Initialize with initial capacity if empty
            for _ in 0..CSET_INITIAL_CAP {
                self.buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
            }
        }
        let current_load = self.bucket_size as f64 / cap as f64;
        if current_load >= self.max_load_factor && cap > 0 {
            self.resize(cap * 2);
        }
        
        // Compute hash
        let ref_bytes = unsafe { std::slice::from_raw_parts(&value as *const T as *const u8, std::mem::size_of::<T>()) };
        let h1 = self.h1hash(ref_bytes, &value);
        let mut iteration = 1usize;
        let cap = self.buckets.capacity();
        let mut index = 0usize;
        
        // Search for empty or matching slot
        for _ in 0..cap {
            let h2 = self.h2hash(ref_bytes, &value);
            index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            iteration += 1;
            if self.is_empty(index) || self.is_tombstone(index) {
                break;
            }
            if self.matches(&self.buckets, ref_bytes, &value, index) {
                // Found duplicate, don't add
                return 0;
            }
        }
        
        // Add new element
        let h2 = self.h2hash(ref_bytes, &value);
        index = Self::double_hash_index(h1, h2, iteration - 1, cap);
        self.buckets[index] = CsetValue { pi: iteration as i32, elem: value };
        self.bucket_size += 1;
        0
    }
</search>
<replace>
    pub fn add(&mut self, value: T) -> i32 {
        // Check load factor before adding
        let cap = self.buckets.capacity();
        if cap == 0 {
            // Initialize with initial capacity if empty
            for _ in 0..CSET_INITIAL_CAP {
                self.buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
            }
        }
        let current_load = self.bucket_size as f64 / cap as f64;
        if current_load >= self.max_load_factor && cap > 0 {
            self.resize(cap * 2);
        }
        
        // Compute hash
        let ref_bytes = unsafe { std::slice::from_raw_parts(&value as *const T as *const u8, std::mem::size_of::<T>()) };
        let h1 = self.h1hash(ref_bytes, &value);
        let h2 = self.h2hash(ref_bytes, &value);
        let mut iteration = 1usize;
        let cap = self.buckets.capacity();
        let mut index = 0usize;
        
        // Search for empty or matching slot
        for _ in 0..cap {
            index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            iteration += 1;
            if self.is_empty(index) || self.is_tombstone(index) {
                break;
            }
            if self.matches(&self.buckets, ref_bytes, &value, index) {
                // Found duplicate, don't add
                return 0;
            }
        }
        
        // Add new element at the found index
        self.buckets[index] = CsetValue { pi: iteration as i32, elem: value };
        self.bucket_size += 1;
        0
    }
</replace>
</edit>