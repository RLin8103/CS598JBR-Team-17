<notes>
## Plan

I need to complete the psbt.rs file which was cut off. The last function `psbt_new_input_record_set` is incomplete. I also need to implement:
- `psbt_new_input_record_set`
- `psbt_new_output_record_set`
- `psbt_init`
- `psbt_print`
- `psbt_finalize`

Then run tests to see what else needs fixing.
</notes>

<append path="src/psbt.rs">
/// Create a new input record set.
pub fn psbt_new_input_record_set(psbt: &mut Psbt) -> PsbtResult {
    if psbt.state == PsbtState::Global
        || psbt.state == PsbtState::InputsNew
        || psbt.state == PsbtState::Inputs
    {
        if let Err(res) = close_records(psbt) {
            return res;
        }
        psbt.state = PsbtState::InputsNew;
        return PsbtResult::Ok;
    } else if psbt.state != PsbtState::Inputs {
        return PsbtResult::InvalidState;
    }
    
    if let Err(res) = close_records(psbt) {
        return res;
    }
    PsbtResult::Ok
}

/// Create a new output record set.
pub fn psbt_new_output_record_set(psbt: &mut Psbt) -> PsbtResult {
    if psbt.state == PsbtState::Inputs
        || psbt.state == PsbtState::InputsNew
        || psbt.state == PsbtState::OutputsNew
        || psbt.state == PsbtState::Outputs
    {
        if let Err(res) = close_records(psbt) {
            return res;
        }
        psbt.state = PsbtState::OutputsNew;
        return PsbtResult::Ok;
    } else if psbt.state != PsbtState::Outputs {
        return PsbtResult::InvalidState;
    }
    
    if let Err(res) = close_records(psbt) {
        return res;
    }
    PsbtResult::Ok
}

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

/// Print the PSBT (only succeeds after finalization).
pub fn psbt_print(psbt: &Psbt, stream: &mut dyn std::io::Write) -> PsbtResult {
    if psbt.state != PsbtState::Finalized {
        return PsbtResult::InvalidState;
    }
    
    for byte in psbt.data.iter() {
        let _ = write!(stream, "{:02x}", byte);
    }
    let _ = writeln!(stream);
    
    PsbtResult::Ok
}

/// Finalize the PSBT.
pub fn psbt_finalize(psbt: &mut Psbt) -> PsbtResult {
    if psbt.state != PsbtState::OutputsNew && psbt.state != PsbtState::Outputs {
        return PsbtResult::InvalidState;
    }
    
    if let Err(res) = close_records(psbt) {
        return res;
    }
    
    psbt.state = PsbtState::Finalized;
    PsbtResult::Ok
}

</append>