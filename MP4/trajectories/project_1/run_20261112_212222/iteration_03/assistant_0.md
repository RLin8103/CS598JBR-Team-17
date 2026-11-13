<notes>
## Analysis

Looking at the error more carefully: "attempt to add with overflow" at line 346. This is happening in the `add()` function. The issue is that when we resize, we're calling `self.add()` recursively which causes the iteration counter to overflow.

The problem is in the `resize()` function - it calls `self.add()` which then tries to add elements again, but the iteration counter keeps growing.

Let me trace through what happens:
1. We add elements until load factor is exceeded
2. `add()` calls `resize()` 
3. `resize()` creates new buckets and calls `self.add()` for each element
4. But `self.add()` checks load factor again and might resize again

The C code doesn't have this issue because it uses a temporary vector during resize and doesn't call `add()` recursively.

I need to rewrite the `resize()` function to directly insert elements without calling `add()`, and fix the iteration logic in `add()` to match the C code exactly.
</notes>

<edit path="src/cset.rs">
<search>
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
            
            // Check load factor after adding
            let current_load = self.bucket_size as f64 / cap as f64;
            if current_load >= self.max_load_factor {
                self.resize(cap * 2);
            }
        }
        0
    }
</replace>
</edit>