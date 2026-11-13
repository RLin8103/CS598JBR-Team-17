<edit path="src/cset.rs">
<search>
    fn value_elem(val: &CsetValue<T>) -> T {
        val.elem
    }
</search>
<replace>
    fn value_elem(val: &CsetValue<T>) -> T
    where
        T: Clone,
    {
        val.elem.clone()
    }
</replace>
</edit>