<edit path="src/cset.rs">
<search>
    pub fn index(&self, index: usize) -> T {
        self.buckets[index].elem
    }
</search>
<replace>
    pub fn index(&self, index: usize) -> T
    where
        T: Clone,
    {
        self.buckets[index].elem.clone()
    }
</replace>
</edit>