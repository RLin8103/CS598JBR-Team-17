<notes>
## Analysis

Looking at the test failures more carefully:

1. The error "attempt to add with overflow" at line 346 is happening in `add()`
2. Looking at the C code, the issue is that in `cset__add_`, the iteration counter starts at 1 and increments AFTER computing the index
3. The C code checks `if ((iteration - 1) >= cset__cap(cset))` to break

But wait - looking at the Rust code, I'm using `iteration - 1` which should work. Let me trace through more carefully:

In the C code:
```c
size_t iteration = 1;
for (;;) {
    if ((iteration - 1) >= cset__cap(cset)) break;
    // ... compute index using (iteration - 1)
    iteration++;
}
```

In my Rust code:
```rust
let mut iteration = 1usize;
for _ in 0..cap {
    let h2 = self.h2hash(ref_bytes, &value);
    index = Self::double_hash_index(h1, h2, iteration - 1, cap);
    iteration += 1;
    // ...
}
```

This looks correct. The issue might be elsewhere.

Actually, looking at the test output again, the error is happening at line 346 which is in the `add()` function. Let me check what line 346 is...

Looking at the code, line 346 would be around the `self.buckets[index] = ...` line. The overflow might be in the index calculation itself.

Wait - I see the issue! In `double_hash_index`, I'm doing:
```rust
((ha1 as usize) + (i * (ha2 as usize))) % cap
```

But `ha2` is already `| 1` from the C code, so it's always odd. The issue might be that `i * ha2` overflows when `i` is large.

Actually, looking at the C code more carefully, the iteration counter is `size_t` which is `usize` in Rust, so that should be fine.

Let me look at the test that's failing. `test_cset_add` adds 34, 35, 36, 37, 38. With initial capacity 2, after adding 34 and 35, the load factor is 2/2 = 1.0 which is >= 0.7, so it should resize.

But wait - in my `add()` function, I'm checking load factor AFTER adding, not before. Let me fix that.

Actually, looking at the C code again:
```c
double current_load_factor = ((double)(cset__size(cset)) / (cset__cap(cset)));
if (current_load_factor >= cset__max_load_factor(cset)) {
  cset__resize(cset, (cset__cap(cset) * 2));
}
```

This check happens BEFORE adding in the `cset__add` macro. So I should check load factor BEFORE adding, not after.

Let me fix the `add()` function to check load factor before adding.
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
            let h2 = self.h2hash(ref_bytes, &value);
            index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            self.buckets[index] = CsetValue { pi: iteration as i32, elem: value };
            self.bucket_size += 1;
        }
        0
    }
</replace>
</edit>