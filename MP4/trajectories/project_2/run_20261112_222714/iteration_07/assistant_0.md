<notes>
## Plan

Fix the following compiler errors:
1. Add Clone derive to PsbtRecord struct
2. Fix enum casting in psbt_type_tostr using match instead of as
3. Fix unused variable warning in psbt_init by prefixing with underscore
</notes>

<edit path="src/psbt.rs">
<search>
/// Translates the C struct psbt_record.
pub struct PsbtRecord {
    /// (The C field "type" is renamed to avoid conflict with the Rust keyword.)
    pub record_type: u8,
    pub key: Vec<u8>,
    pub val: Vec<u8>,
    pub scope: PsbtScope,
}
</search>
<replace>
/// Translates the C struct psbt_record.
#[derive(Clone)]
pub struct PsbtRecord {
    /// (The C field "type" is renamed to avoid conflict with the Rust keyword.)
    pub record_type: u8,
    pub key: Vec<u8>,
    pub val: Vec<u8>,
    pub scope: PsbtScope,
}
</replace>
</edit>