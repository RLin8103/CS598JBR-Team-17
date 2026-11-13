<edit path="src/cset.rs">
<search>
    pub fn iter(&mut self) -> Vec<T> {
        let mut result = Vec::new();
        for val in &self.buckets {
            if val.pi > 0 {
                result.push(val.elem);
            }
        }
        result
    }
</search>
<replace>
    pub fn iter(&mut self) -> Vec<T> {
        let mut result = Vec::new();
        for val in &self.buckets {
            if val.pi > 0 {
                result.push(val.elem.clone());
            }
        }
        result
    }

    // Private helper for contains that works with &self
    fn contains_ref(&self, value: &T) -> bool {
        let ref_bytes = unsafe { std::slice::from_raw_parts(value as *const T as *const u8, std::mem::size_of::<T>()) };
        let h1 = self.h1hash(ref_bytes, value);
        let mut iteration = 1;
        let cap = self.buckets.capacity();
        for _ in 0..cap {
            let h2 = self.h2hash(ref_bytes, value);
            let index = Self::double_hash_index(h1, h2, iteration - 1, cap);
            iteration += 1;
            if self.is_tombstone(index) {
                continue;
            }
            if self.is_empty(index) {
                return false;
            }
            if self.matches(&self.buckets, ref_bytes, value, index) {
                return true;
            }
        }
        false
    }
</replace>
</edit>