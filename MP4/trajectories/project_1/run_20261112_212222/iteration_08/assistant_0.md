<notes>
## Analysis

Looking at the test failures, the issue is that elements are not being found correctly after removal or during iteration. The key insight is that in the C code, when we find a tombstone during search, we continue, but when we find an empty slot, we break. This means that if we have a tombstone followed by an element that hashes to the same probe sequence, we might skip over the element.

But wait, looking at the C code more carefully, the issue is that in `cset__contains_`, the loop checks `(iteration - 1) >= cset__cap(cset)` at the BEGINNING of the loop, not after computing the index. This means we iterate at most `cap` times.

But in my Rust code, I'm using `for _ in 0..cap` which also iterates `cap` times, so that should be fine.

Let me look at the `test_cset_contains` test more carefully:
```rust
let mut cset_int = cset::Cset::<i32>::new();
cset_int.add(34);
cset_int.add(36);
cset_int.remove(36);
assert!(!cset_int.contains(&12));
assert!(cset_int.contains(&34));
```

So we add 34, add 36, remove 36, and then check if 34 is contained. The test fails at `cset_int.contains(&34)`.

This suggests that after removing 36, 34 is no longer found. This could be because:
1. The hash function is different for different values
2. The removal is corrupting the bucket

Wait, I think I see the issue. In the C code, the `cset__remove_` macro uses `cset__tombstone` to check if a slot is a tombstone, and `cset__empty` to check if a slot is empty. But in my Rust code, I'm using `is_tombstone` and `is_empty` which check `pi == -1` and `pi == 0`.

But wait, in the C code, `cset__empty` checks `pi == 0`, and `cset__tombstone` checks `pi == -1`. So my Rust code should be correct.

Let me look at the `add` function more carefully. In the C code, when we find an empty or tombstone slot, we break out of the loop and insert there. But in my Rust code, I'm computing the index again after the loop using `iteration - 1`, which might be wrong.

Actually, looking at the C code again:
```c
for (;;) {
    if ((iteration - 1) >= cset__cap(cset)) {
        break;
    }
    cset__u64 h2 = cset__h2hash(cset, ref, value);
    index = cset__double_hash_index(h1, h2, (iteration - 1), cap);
    iteration++;
    if (cset__tombstone(cset__vector_buckets_ref(cset), index)) {
        continue;
    }
    if (cset__empty(cset__vector_buckets_ref(cset), index)) {
        break;
    }
    bool matches = cset__matches(cset, cset__vector_buckets_ref(cset), ref, value, index);
    if (matches) {
        found = true;
        break;
    }
}
if (!found) {
    ((cset_vector__index(vector_ref, index))->elem) = value;
    ((cset_vector__index(vector_ref, index))->pi) = iteration;
    cset__set_size(cset, (cset__size(cset)) + 1);
}
```

The key difference is that in the C code, `index` is the last computed index when we break out of the loop. But in my Rust code, I'm computing `index` again after the loop using `iteration - 1`, which is wrong.

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