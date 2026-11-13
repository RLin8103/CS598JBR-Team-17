<notes>
## Analysis
All tests pass. Clippy shows 0 warnings. The unsafe metrics show 27 unsafe lines. The main sources are:
1. `xxh_read_le64` and `xxh_read32` - need safe slice-based functions
2. `xxh64` and `xxh64_h` - interface requires `*const u8`, must remain unsafe
3. `matches` method - uses unsafe for byte comparison
4. `new()`, `clear()`, `resize()` - use `std::mem::zeroed()` which is unsafe

The interface requires `*const u8` for `xxh64` and `xxh64_h`, so those must remain unsafe. However, I can add safety documentation to satisfy Clippy.

For `xxh_read_le64` and `xxh_read32`, I can convert them to use safe slice operations by taking a slice directly instead of a pointer.

For `matches`, I can use `std::ptr::read` or `std::ptr::copy_nonoverlapping` to avoid unsafe pointer casts, but since `T: Clone`, I can just clone the value.

For initialization, I can use `std::mem::MaybeUninit` or just use `T::default()` if available. Since the interface doesn't require `Default`, I'll use `std::mem::MaybeUninit` to avoid unsafe `zeroed()`.

Let me fix the unsafe code by:
1. Converting `xxh_read_le64` and `xxh_read32` to use safe slice operations
2. Using `std::ptr::read` in `matches` to avoid unsafe pointer casts
3. Using `std::mem::MaybeUninit` for initialization
</notes>

<edit path="src/cset.rs">
<search>
    fn matches(&self, vector_ref: &[CsetValue<T>], ref_bytes: &[u8], value: &T, index: usize) -> bool {
        match self.compare {
            Some(compare) => {
                let elem_ref = Self::value_elem_ref(&vector_ref[index]);
                compare(elem_ref, value)
            }
            None => {
                let elem_ref = Self::value_elem_ref(&vector_ref[index]);
                // Safe because we're reading from a reference that's guaranteed to be valid
                let elem_ptr = elem_ref as *const T as *const u8;
                let elem_bytes = unsafe { std::slice::from_raw_parts(elem_ptr, std::mem::size_of::<T>()) };
                Self::bytes_compare(elem_bytes, ref_bytes, std::mem::size_of::<T>())
            }
        }
    }
</search>
<replace>
    fn matches(&self, vector_ref: &[CsetValue<T>], ref_bytes: &[u8], value: &T, index: usize) -> bool {
        match self.compare {
            Some(compare) => {
                let elem_ref = Self::value_elem_ref(&vector_ref[index]);
                compare(elem_ref, value)
            }
            None => {
                let elem_ref = Self::value_elem_ref(&vector_ref[index]);
                // Safe because we're reading from a reference that's guaranteed to be valid
                let elem_ptr = elem_ref as *const T as *const u8;
                let elem_bytes = unsafe { std::slice::from_raw_parts(elem_ptr, std::mem::size_of::<T>()) };
                Self::bytes_compare(elem_bytes, ref_bytes, std::mem::size_of::<T>())
            }
        }
    }
</replace>
</edit>