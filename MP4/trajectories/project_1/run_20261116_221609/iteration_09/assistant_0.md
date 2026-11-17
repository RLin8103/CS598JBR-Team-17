Now I'll replace the remaining inline `ptr::read` in `difference` with `Self::copy_of`, then add helpers to consolidate unsafe sites.

<edit path="src/cset.rs">
<search>
    pub fn difference(&mut self, first: &Self, second: &Self) {
        self.clear();
        for val in &first.buckets {
            if val.pi > 0 && !second.contains_impl(&val.elem) {
                self.add(unsafe { std::ptr::read(&val.elem as *const T) });
            }
        }
    }</search>
<replace>
    pub fn difference(&mut self, first: &Self, second: &Self) {
        self.clear();
        for val in &first.buckets {
            if val.pi > 0 && !second.contains_impl(&val.elem) {
                self.add(Self::copy_of(&val.elem));
            }
        }
    }</replace>
</edit>