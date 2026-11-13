<notes>
## Analysis
All tests pass. The unsafe metrics show 27 unsafe lines. The main sources are:
1. `xxh_read_le64` and `xxh_read32` - need safe slice-based functions
2. `xxh64` and `xxh64_h` - interface requires `*const u8`, must remain unsafe but can add safety docs
3. `matches` method - uses unsafe for byte comparison
4. `new()`, `clear()`, `resize()` - use `std::mem::zeroed()` which is unsafe

The interface requires `*const u8` for `xxh64` and `xxh64_h`, so those must remain unsafe. However, I can add safety documentation to satisfy Clippy.

For `xxh_read_le64` and `xxh_read32`, I can convert them to use safe slice operations by taking a slice directly instead of a pointer.

For `matches`, I can use `std::ptr::read` or `std::ptr::copy_nonoverlapping` to avoid unsafe pointer casts, but since `T: Clone`, I can just clone the value.

For initialization, I can use `std::mem::MaybeUninit` or just use `T::default()` if available. Since the interface doesn't require `Default`, I'll use `std::mem::MaybeUninit` to avoid unsafe `zeroed()`.

Let me fix the Clippy warnings first, then address the unsafe code.
</notes>

<edit path="src/cset.rs">
<search>
    fn resize(&mut self, new_cap: usize) {
        let old_buckets = std::mem::replace(&mut self.buckets, Vec::new());
        self.buckets.reserve_exact(new_cap);
        for _ in 0..new_cap {
            self.buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
        }
        self.bucket_size = 0;
        
        for val in old_buckets {
            if val.pi > 0 {
                self.add(val.elem);
            }
        }
    }
</search>
<replace>
    fn resize(&mut self, new_cap: usize) {
        let old_buckets = std::mem::take(&mut self.buckets);
        self.buckets.reserve_exact(new_cap);
        for _ in 0..new_cap {
            self.buckets.push(CsetValue { pi: 0, elem: unsafe { std::mem::zeroed() } });
        }
        self.bucket_size = 0;
        
        for val in old_buckets {
            if val.pi > 0 {
                self.add(val.elem);
            }
        }
    }
</replace>
</edit>