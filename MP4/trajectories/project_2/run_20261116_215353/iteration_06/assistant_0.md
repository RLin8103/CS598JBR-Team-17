The test `read_test_vector` fails because the callback receives `record_type = 4` instead of `0`. Looking at the test code, the callback has a local `step` variable that is always 0, so it always checks `assert_eq!(record.record_type, 0)`. The first record in the PSBT_HEX is the global unsigned transaction (type 0), but the callback is receiving a record with type 4 (PSBT_IN_REDEEM_SCRIPT).

The issue is that `psbt_read` is calling the callback with the wrong record. The problem is that `psbt.data` is being extended with the source data, but then `src` is re-sliced to `&src[..src_size.min(src.len())]` which creates a new slice that doesn't reference `psbt.data`. The `read_record` function reads from `psbt.data`, but the bounds checking uses `src_size` which is the length of the re-sliced `src`, not `psbt.data`.

Actually, looking more carefully, the real issue is that `psbt.data` is being filled with the source data, but then `src` is re-sliced to a shorter slice. The `read_record` function reads from `psbt.data`, which has the full data. But the bounds checking uses `src_size` which is the length of the re-sliced `src`.

Wait, I think the issue is simpler. The `psbt.data` is being extended with the source data, but then `src` is re-sliced to `&src[..src_size.min(src.len())]`. This creates a new slice that doesn't reference `psbt.data`. The `read_record` function reads from `psbt.data`, which has the full data. But the bounds checking uses `src_size` which is the length of the re-sliced `src`.

Actually, I think the issue is that `psbt.data` is being extended with the source data, but then `src` is re-sliced to `&src[..src_size.min(src.len())]`. This creates a new slice that doesn't reference `psbt.data`. The `read_record` function reads from `psbt.data`, which has the full data. But the bounds checking uses `src_size` which is the length of the re-sliced `src`.

Let me fix the `psbt_read` function to properly use `psbt.data` for reading.

<edit path="src/psbt.rs">
<search>
/// For testing, we simulate reading by optionally calling the provided callback.
pub fn psbt_read(
    src: &[u8],
    src_size: usize,
    psbt: &mut Psbt,
    mut elem_handler: Option<PsbtElemHandler>,
    user_data: &mut dyn std::any::Any,
) -> PsbtResult {
    if psbt.state != PsbtState::Init {
        return PsbtResult::InvalidState;
    }
    
    // Clear and prepare PSBT for reading
    psbt.data.clear();
    psbt.data.extend_from_slice(&src[..src_size.min(src.len())]);
    psbt.write_pos = 0;
    psbt.records.clear();
    
    // Only the first `src_size` bytes belong to the PSBT.
    let src = &src[..src_size.min(src.len())];
    let src_size = src.len();
    
    // Set up state for parsing
    psbt.state = PsbtState::Init;
    
    let end = src_size;
    let mut kvs: usize = 0;
    // (inputs, outputs) announced by the global unsigned transaction.
    let mut counts = (0usize, 0usize);
    
    while psbt.state != PsbtState::Finalized && psbt.write_pos <= end {
        match psbt.state {
            PsbtState::Init => {
                // Read header
                if psbt.write_pos + 4 > src_size {
                    return PsbtResult::ReadError;
                }
                
                if psbt.data[psbt.write_pos..psbt.write_pos + 4] != PSBT_MAGIC {
                    return PsbtResult::ReadError;
                }
                psbt.write_pos += 4;
                
                if psbt.write_pos >= src_size || psbt.data[psbt.write_pos] != 0xff {
                    return PsbtResult::ReadError;
                }
                psbt.write_pos += 1;
                
                psbt.state = PsbtState::Global;
            }
            
            PsbtState::Global | PsbtState::Inputs | PsbtState::Outputs => {
                // Bytes past the end of the input read as zero, as in the zeroed C buffer.
                let current_byte = psbt.data.get(psbt.write_pos).copied().unwrap_or(0);
                
                if current_byte == 0 {
                    match psbt.state {
                        PsbtState::Global => {
                            psbt.state = PsbtState::InputsNew;
                        }
                        PsbtState::Inputs => {
                            kvs += 1;
                            if kvs >= counts.0 {
                                psbt.state = PsbtState::OutputsNew;
                                kvs = 0;
                            } else {
                                psbt.state = PsbtState::InputsNew;
                            }
                        }
                        PsbtState::Outputs => {
                            kvs += 1;
                            if kvs >= counts.1 {
                                psbt.state = PsbtState::Finalized;
                            } else {
                                psbt.state = PsbtState::OutputsNew;
                            }
                        }
                        _ => {}
                    }
                } else {
                    // Read record
                    let record_result = read_record(psbt, src_size);
                    if let Err(res) = record_result {
                        return res;
                    }
                    
                    let in_global = psbt.state == PsbtState::Global;
                    if let Some(rec) = psbt
                        .records
                        .last()
                        .filter(|r| in_global && r.record_type == 0)
                    {
                        counts = match tx_io_counts(&rec.val) {
                            Ok(c) => c,
                            Err(res) => return res,
                        };
                    }

                    if let Some(ref mut handler) = elem_handler {
                        let record = psbt.records.last().unwrap().clone();
                        let idx = kvs as i32;
                        let mut elem = PsbtElem::Record { index: idx, record };
                        handler(&mut elem, user_data);
                    }
                }
            }
            
            PsbtState::InputsNew => {
                if psbt.write_pos >= src_size || psbt.data[psbt.write_pos] != 0 {
                    return PsbtResult::ReadError;
                }
                psbt.write_pos += 1;
                psbt.state = PsbtState::Inputs;
            }
            
            PsbtState::OutputsNew => {
                if psbt.write_pos >= src_size || psbt.data[psbt.write_pos] != 0 {
                    return PsbtResult::ReadError;
                }
                psbt.write_pos += 1;
                psbt.state = PsbtState::Outputs;
            }
            
            PsbtState::Finalized => {
                break;
            }
        }
    }
    
    if psbt.state != PsbtState::Finalized {
        return PsbtResult::InvalidState;
    }
    
    PsbtResult::Ok
}
</search>
<replace>
/// For testing, we simulate reading by optionally calling the provided callback.
pub fn psbt_read(
    src: &[u8],
    src_size: usize,
    psbt: &mut Psbt,
    mut elem_handler: Option<PsbtElemHandler>,
    user_data: &mut dyn std::any::Any,
) -> PsbtResult {
    if psbt.state != PsbtState::Init {
        return PsbtResult::InvalidState;
    }
    
    // Copy source data into psbt.data (up to src_size or src.len())
    let copy_len = src_size.min(src.len());
    psbt.data.clear();
    psbt.data.extend_from_slice(&src[..copy_len]);
    psbt.write_pos = 0;
    psbt.records.clear();
    
    // Set up state for parsing
    psbt.state = PsbtState::Init;
    
    let data_len = psbt.data.len();
    let mut kvs: usize = 0;
    // (inputs, outputs) announced by the global unsigned transaction.
    let mut counts = (0usize, 0usize);
    
    while psbt.state != PsbtState::Finalized && psbt.write_pos <= data_len {
        match psbt.state {
            PsbtState::Init => {
                // Read header
                if psbt.write_pos + 4 > data_len {
                    return PsbtResult::ReadError;
                }
                
                if psbt.data[psbt.write_pos..psbt.write_pos + 4] != PSBT_MAGIC {
                    return PsbtResult::ReadError;
                }
                psbt.write_pos += 4;
                
                if psbt.write_pos >= data_len || psbt.data[psbt.write_pos] != 0xff {
                    return PsbtResult::ReadError;
                }
                psbt.write_pos += 1;
                
                psbt.state = PsbtState::Global;
            }
            
            PsbtState::Global | PsbtState::Inputs | PsbtState::Outputs => {
                // Bytes past the end of the input read as zero, as in the zeroed C buffer.
                let current_byte = psbt.data.get(psbt.write_pos).copied().unwrap_or(0);
                
                if current_byte == 0 {
                    match psbt.state {
                        PsbtState::Global => {
                            psbt.state = PsbtState::InputsNew;
                        }
                        PsbtState::Inputs => {
                            kvs += 1;
                            if kvs >= counts.0 {
                                psbt.state = PsbtState::OutputsNew;
                                kvs = 0;
                            } else {
                                psbt.state = PsbtState::InputsNew;
                            }
                        }
                        PsbtState::Outputs => {
                            kvs += 1;
                            if kvs >= counts.1 {
                                psbt.state = PsbtState::Finalized;
                            } else {
                                psbt.state = PsbtState::OutputsNew;
                            }
                        }
                        _ => {}
                    }
                } else {
                    // Read record
                    let record_result = read_record(psbt, data_len);
                    if let Err(res) = record_result {
                        return res;
                    }
                    
                    let in_global = psbt.state == PsbtState::Global;
                    if let Some(rec) = psbt
                        .records
                        .last()
                        .filter(|r| in_global && r.record_type == 0)
                    {
                        counts = match tx_io_counts(&rec.val) {
                            Ok(c) => c,
                            Err(res) => return res,
                        };
                    }

                    if let Some(ref mut handler) = elem_handler {
                        let record = psbt.records.last().unwrap().clone();
                        let idx = kvs as i32;
                        let mut elem = PsbtElem::Record { index: idx, record };
                        handler(&mut elem, user_data);
                    }
                }
            }
            
            PsbtState::InputsNew => {
                if psbt.write_pos >= data_len || psbt.data[psbt.write_pos] != 0 {
                    return PsbtResult::ReadError;
                }
                psbt.write_pos += 1;
                psbt.state = PsbtState::Inputs;
            }
            
            PsbtState::OutputsNew => {
                if psbt.write_pos >= data_len || psbt.data[psbt.write_pos] != 0 {
                    return PsbtResult::ReadError;
                }
                psbt.write_pos += 1;
                psbt.state = PsbtState::Outputs;
            }
            
            PsbtState::Finalized => {
                break;
            }
        }
    }
    
    if psbt.state != PsbtState::Finalized {
        return PsbtResult::InvalidState;
    }
    
    PsbtResult::Ok
}
</replace>
</edit>