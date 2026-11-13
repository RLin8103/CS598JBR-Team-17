<notes>
## Analysis

Looking at the error "attempt to add with overflow" at line 346, this is happening in the `add()` function. The issue is that when we resize, we're calling `self.add()` recursively which causes the iteration counter to overflow.

The problem is in the `resize()` function - it calls `self.add()` which then tries to add elements again, but the iteration counter keeps growing.

Let me trace through what happens:
1. We add elements until load factor is exceeded
2. `add()` calls `resize()` 
3. `resize()` creates new buckets and calls `self.add()` for each element
4. But `self.add()` checks load factor again and might resize again

The C code doesn't have this issue because it uses a temporary vector during resize and doesn't call `add()` recursively.

I need to rewrite the `resize()` function to directly insert elements without calling `add()`, and fix the iteration logic in `add()` to match the C code exactly.

Actually, looking more carefully at the C code, the issue is that in `resize()`, the C code uses `cset__add_` which is a lower-level function that doesn't check load factor. I need to implement a similar approach in Rust.

Let me rewrite the `resize()` function to directly insert elements without calling `add()`, and also fix the `add()` function to not check load factor after adding (the C code checks before adding).
</notes>

<edit path="src/cset.rs">
<search>
    // Internal resize function
    fn resize(&mut self, new_cap: usize) {
        let mut temp = Vec::new();
        cset_vector__init_with_cap(&mut temp, new_cap);
        for _ in 0..new_cap {
            temp.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
        }
        let old_buckets = std::mem::replace(&mut self.buckets, temp);
        self.bucket_size = 0;
        for val in old_buckets {
            if val.pi > 0 {
                self.add(val.elem);
            }
        }
    }
</search>
<replace>
    // Internal resize function - directly inserts without calling add()
    fn resize(&mut self, new_cap: usize) {
        let mut temp = Vec::new();
        temp.clear();
        temp.reserve_exact(new_cap);
        for _ in 0..new_cap {
            temp.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
        }
        
        let old_buckets = std::mem::replace(&mut self.buckets, temp);
        self.bucket_size = 0;
        
        for val in old_buckets {
            if val.pi > 0 {
                // Direct insertion without calling add() to avoid infinite recursion
                let ref_bytes = unsafe { std::slice::from_raw_parts(&val.elem as *const T as *const u8, std::mem::size_of::<T>()) };
                let h1 = self.h1hash(ref_bytes, &val.elem);
                let mut iteration = 1usize;
                let cap = self.buckets.capacity();
                let mut index = 0usize;
                
                for _ in 0..cap {
                    let h2 = self.h2hash(ref_bytes, &val.elem);
                    index = Self::double_hash_index(h1, h2, iteration - 1, cap);
                    iteration += 1;
                    if self.is_empty(index) || self.is_tombstone(index) {
                        break;
                    }
                }
                
                let h2 = self.h2hash(ref_bytes, &val.elem);
                index = Self::double_hash_index(h1, h2, iteration - 1, cap);
                self.buckets[index] = CsetValue { pi: iteration as i32, elem: val.elem };
                self.bucket_size += 1;
            }
        }
    }
</replace>
</edit>