Now I'll replace the 5 inline `ptr::read` calls with the existing `copy_of` helper, reducing unsafe sites.

<edit path="src/cset.rs">
<search>
    pub fn iter(&mut self) -> Vec<T> {
        let mut result = Vec::new();
        for val in &self.buckets {
            if val.pi > 0 {
                // SAFETY: We need to return T. Use ptr::read.
                result.push(unsafe { std::ptr::read(&val.elem as *const T) });
            }
        }
        result
    }</search>
<replace>
    pub fn iter(&mut self) -> Vec<T> {
        let mut result = Vec::new();
        for val in &self.buckets {
            if val.pi > 0 {
                result.push(Self::copy_of(&val.elem));
            }
        }
        result
    }</replace>
</edit>