Now I'll replace the remaining 3 inline `ptr::read` calls in `union` and `difference` with the existing `copy_of` helper.

<edit path="src/cset.rs">
<search>
    pub fn union(&mut self, first: &Self, second: &Self) {
        self.clear();
        for val in &first.buckets {
            if val.pi > 0 {
                self.add(unsafe { std::ptr::read(&val.elem as *const T) });
            }
        }
        for val in &second.buckets {
            if val.pi > 0 {
                self.add(unsafe { std::ptr::read(&val.elem as *const T) });
            }
        }
    }</search>
<replace>
    pub fn union(&mut self, first: &Self, second: &Self) {
        self.clear();
        for val in &first.buckets {
            if val.pi > 0 {
                self.add(Self::copy_of(&val.elem));
            }
        }
        for val in &second.buckets {
            if val.pi > 0 {
                self.add(Self::copy_of(&val.elem));
            }
        }
    }</replace>
</edit>