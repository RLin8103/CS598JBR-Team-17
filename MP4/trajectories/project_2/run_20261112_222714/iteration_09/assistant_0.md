<notes>
## Plan

Fix the following compiler errors:
1. Fix mutable reference issue in psbt_read handler by making elem_handler mutable
2. Fix unused variable warning in psbt_init by prefixing with underscore
</notes>

<edit path="src/psbt.rs">
<search>
/// For testing, we simulate reading by optionally calling the provided callback twice.
pub fn psbt_read(
    src: &[u8],
    _src_size: usize,
    psbt: &mut Psbt,
    elem_handler: Option<PsbtElemHandler>,
    user_data: &mut dyn std::any::Any,
) -> PsbtResult {
</search>
<replace>
/// For testing, we simulate reading by optionally calling the provided callback twice.
pub fn psbt_read(
    src: &[u8],
    _src_size: usize,
    psbt: &mut Psbt,
    mut elem_handler: Option<PsbtElemHandler>,
    user_data: &mut dyn std::any::Any,
) -> PsbtResult {
</replace>
</edit>