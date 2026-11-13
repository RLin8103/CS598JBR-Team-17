<notes>
## Analysis

Looking at the test failures again, the error "attempt to add with overflow" is still happening. Let me trace through the logic more carefully.

The issue might be in the `double_hash_index` function. When `i` (iteration - 1) gets large, `i * ha2` could overflow. But wait, `i` is at most `cap` which is a `usize`, and `ha2` is also a `usize`, so the multiplication could overflow if `i * ha2 > usize::MAX`.

Actually, looking at the C code, `ha1` and `ha2` are `XXH64_hash_t` (u64), and `i` is `size_t`. The C code does:
```c
index = ((ha1 + (i * ha2)) % cap)
```

In Rust, I'm doing:
```rust
((ha1 as usize) + (i * (ha2 as usize))) % cap
```

The issue is that `ha1 as usize` and `ha2 as usize` could lose precision if the u64 values are larger than `usize::MAX`. On a 64-bit system, this shouldn't be an issue, but on a 32-bit system it would be.

But wait, the error is "attempt to add with overflow", which suggests Rust's overflow checking is catching this. Rust in debug mode panics on integer overflow.

The issue is that `i * ha2` could overflow when `i` is large. Let me check the C code again - it uses `size_t` for `i` and `ha2` is cast to `size_t` as well.

Actually, I think the issue is simpler. Let me look at the test that's failing. `test_cset_add` adds 34, 35, 36, 37, 38. With initial capacity 2, after adding 34 and 35, the load factor is 2/2 = 1.0 which is >= 0.7, so it should resize.

But wait - in my `add()` function, I'm checking load factor BEFORE adding, so when we add the 3rd element (36), the load factor is 2/2 = 1.0 >= 0.7, so we resize to capacity 4. Then we add 36.

Then when we add 37, the load factor is 3/4 = 0.75 >= 0.7, so we resize to capacity 8. Then we add 37.

Then when we add 38, the load factor is 4/8 = 0.5 < 0.7, so we don't resize. Then we add 38.

So the capacity should be 8 after adding 38 elements. That seems fine.

Let me look at the `double_hash_index` function again. The issue might be that `ha2` is very large (it's a hash value), and when we multiply `i * ha2`, it could overflow.

Let me fix the `double_hash_index` function to use `wrapping_mul` to avoid overflow:
</notes>

<edit path="src/cset.rs">
<search>
    fn double_hash_index(ha1: XXHU64, ha2: XXHU64, i: usize, cap: usize) -> usize {
        ((ha1 as usize) + (i * (ha2 as usize))) % cap
    }
</search>
<replace>
    fn double_hash_index(ha1: XXHU64, ha2: XXHU64, i: usize, cap: usize) -> usize {
        // Use wrapping arithmetic to avoid overflow
        let ha1_usize = ha1 as usize;
        let ha2_usize = ha2 as usize;
        let product = i.wrapping_mul(ha2_usize);
        (ha1_usize.wrapping_add(product)) % cap
    }
</replace>
</edit>