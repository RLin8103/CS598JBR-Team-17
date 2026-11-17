<edit path="src/cset.rs">
<search>
pub fn xxh_is_little_endian() -> bool {
    cfg!(target_endian = "little")
}
</search>
<replace>
pub fn xxh_is_little_endian() -> bool {
    cfg!(target_endian = "little")
}

pub fn xxh_get64bits(mem_ptr: &mut XXHU8) -> XXHU64 {
    xxh_read_le64_align(mem_ptr)
}
</replace>
</edit>