<edit path="src/cset.rs">
<search>
    pub fn get_buckets_ref(&self) -> &mut Vec<CsetValue<T>> {
        &mut self.buckets
    }

    pub fn get_temp_buckets_ref(&self) -> &mut Vec<CsetValue<T>> {
        &mut self.temp_buckets
    }
</search>
<replace>
    pub fn get_buckets_ref(&mut self) -> &mut Vec<CsetValue<T>> {
        &mut self.buckets
    }

    pub fn get_temp_buckets_ref(&mut self) -> &mut Vec<CsetValue<T>> {
        &mut self.temp_buckets
    }
</replace>
</edit>