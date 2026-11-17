<notes>
The test `read_test_vector` is failing because the callback `checker` has a local `step` variable that gets reset to 0 on each call. The callback should receive a mutable reference to a counter that persists across calls. Looking at the C code, the callback receives `user_data` which points to the `step` variable. The Rust interface uses `&mut dyn std::any::Any` for user_data, so we need to pass a mutable reference to an integer.

The issue is that the test creates a new `step = 0` on each callback invocation instead of using the user_data. We need to fix the test to properly use the user_data parameter.

However, I cannot edit the test file. Let me check if there's an issue with how the callback is being called in the implementation. Looking at the C code more carefully, the callback is called for each record read, and the step counter should increment. The Rust implementation should be calling the callback correctly.

Let me re-examine the psbt_read implementation to see if callbacks are being called correctly.
</notes>

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
                        let mut elem = PsbtElem::Record {
                            index: kvs as i32,
                            record: psbt.records.last().unwrap().clone(),
                        };
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
                        let mut elem = PsbtElem::Record {
                            index: kvs as i32,
                            record: psbt.records.last().unwrap().clone(),
                        };
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
</replace>
</edit>