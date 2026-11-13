<notes>
## Plan

Fix the following test failures:
1. `empty_input_test` and `encode_decode_test` fail with `OobWrite` - the issue is likely in `psbt_init` where we're not properly setting up the data buffer
2. `read_test_vector` fails with step=4 instead of 0 - the handler is being called multiple times but the test expects only 2 calls

Looking at the C code, `psbt_init` should set up the PSBT with the destination buffer, not clear it. The data should be copied from src in `psbt_read`, not in `psbt_init`.

Also, the handler in `read_test_vector` is checking step=0 and step=1, but it's being called more times. The issue is that the handler is called for each record, but the test expects only 2 records. Need to check the test more carefully.
</notes>

<edit path="src/psbt.rs">
<search>
/// Initialize a PSBT using the given destination buffer.
pub fn psbt_init(psbt: &mut Psbt, dest: &mut [u8], dest_size: usize) -> PsbtResult {
    psbt.data.clear();
    psbt.data_capacity = dest_size;
    psbt.write_pos = 0;
    psbt.state = PsbtState::Init;
    psbt.records.clear();
    
    // Pre-allocate if needed
    if psbt.data.capacity() < dest_size {
        psbt.data.reserve(dest_size);
    }
    
    PsbtResult::Ok
}
</search>
<replace>
/// Initialize a PSBT using the given destination buffer.
pub fn psbt_init(psbt: &mut Psbt, _dest: &mut [u8], dest_size: usize) -> PsbtResult {
    psbt.data.clear();
    psbt.data_capacity = dest_size;
    psbt.write_pos = 0;
    psbt.state = PsbtState::Init;
    psbt.records.clear();
    
    PsbtResult::Ok
}
</replace>
</edit>