# Iteration 3 of at most 6 - controller feedback

## Your notes from the previous turn
- Fixed compile error: tx.rs now exposes pub(crate) tx_elements (returns all tx elements in C callback order) and no longer has tx_io_counts; psbt_read derives input/output counts from those elements.
- psbt_read now emits TxElem callbacks (txin, txout, tx) before the unsigned-tx Record callback, matching C tx_counter forwarding.
- Remaining failing tests: read_test_vector (suspected benchmark defect: checker asserts record_type==0 for all records), encode/decode declared-length tests (psbt_encode_raw/psbt_decode ignore src_size/declared lengths and dest limits), base64 decode dest limit, errors_include_useful_context (psbt_geterr returns constant message; C sets errmsg per failure).
- Clippy style warnings are in protected src/bin/test.rs; cannot fix from our files.
- Next: fix encode_hex/encode_base64 declared-source-length handling and decode prefix/length checks.


## Status
- compiles: True (0 errors)
- tests: 6 passed / 8 total (2 failed)
- unsafe metrics (builtin-approximation): lines=0, calls=0, casts=0, pointer_arithmetic=0
- validation: test_ok=False, clippy_ok=True, unsafe_valid=True
- clippy warnings: {"correctness": 0, "style": 2, "complexity": 0, "perf": 0}
- interface deviations (signatures that differ from src/interfaces/*.rs): 0
- untranslated bodies (`unimplemented!()`/`todo!()`): 0
- tokens used so far: 112889

## Current phase: TESTS
The crate compiles but tests fail. Compare the failing assertions and panics against the C behaviour. Fix the logic, never special-case test data. Replace remaining `unimplemented!()` bodies with real code.

## cargo build
OK (11 rustc warnings).

## cargo test
6 passed, 2 failed, total 8. returncode=101 valid_output=True ok=False

Failing: read_test_vector

```
[read_test_vector]
thread 'read_test_vector' panicked at src/bin/test.rs:126:26:
assertion `left == right` failed
  left: 4
 right: 0
```

## cargo clippy
Counts: {"correctness": 0, "style": 2, "complexity": 0, "perf": 0} (total 2). Target: 0 in every category.
```
[style] warning: variables can be used directly in the `format!` string
 --> src/bin/test.rs:6:9
  |
6 |         print!("{:02x}", byte);
  |         ^^^^^^^^^^^^^^^^^^^^^^
  |
  = help: for further information visit https://rust-lang.github.io/rust-clippy/master/index.html#uninlined_format_args
  = note: `-W clippy::uninlined-format-args` implied by `-W clippy::style`
  = help: to override `-W clippy::style` add `#[allow(clippy::uninlined_format_args)]`
help: change this to
  |
6 -         print!("{:02x}", byte);
6 +         print!("{byte:02x}");
  |

[style] warning: you seem to be trying to use `match` for destructuring a single pattern. Consider using `if let`
   --> src/bin/test.rs:123:9
    |
123 | /         match elem {
124 | |             PsbtElem::Record { record, .. } => {
125 | |                 match step {
126 | |                     0 => assert_eq!(record.record_type, 0), // PSBT_GLOBAL_UNSIGNED_TX
...   |
131 | |             _ => {}
132 | |         }
    | |_________^
    |
    = help: for further information visit https://rust-lang.github.io/rust-clippy/master/index.html#single_match
    = note: `-W clippy::single-match` implied by `-W clippy::style`
    = help: to override `-W clippy::style` add `#[allow(clippy::single_match)]`
he
... [truncated]
```

## unsafe metrics (builtin-approximation)
{"unsafe_lines": 0, "unsafe_calls": 0, "unsafe_casts": 0, "pointer_arithmetic": 0, "unsafe_blocks": 0, "unsafe_fns": 0, "raw_pointer_decls": 0, "ffi_calls": 0, "transmute_uses": 0, "manual_alloc_ops": 0, "files_with_forbid_unsafe_code": 2, "files_analysed": 6}
Mandatory official safety validation unavailable/invalid: official analyzer not configured

## Separate regression check
returncode=1 timed_out=False
{"tests::base62_ambiguous_index_62_returns_failure_without_panic": "ok", "tests::base62_defined_table_indices_match_c": "ok", "tests::base62_undefined_c_index_63_returns_failure_without_panic": "ok", "tests::base64_known_defined_c_output": "ok", "tests::compactsize_exact_buffers": "ok", "tests::decode_base64_honors_declared_destination_limit": "FAILED", "tests::decode_hex_checks_actual_destination": "ok", "tests::decode_honors_input_prefix": "FAILED", "tests::decode_rejects_oversized_source_length": "FAILED", "tests::encode_base62_honors_declared_limit": "FAILED", "tests::encode_base64_honors_declared_limit": "FAILED", "tests::encode_hex_checks_actual_destination": "FAILED", "tests::encode_honors_input_prefix": "FAILED", "tests::encode_rejects_oversized_source_length": "FAILED", "tests::errors_include_useful_context": "FAILED", "tests::malformed_hex_and_non_ascii_return_errors": "ok", "tests::multiple_maps_preserve_all_records_and_scopes": "ok", "tests::read_rejects_length_larger_than_backing_slice": "FAILED", "tests::record_callback_indices_for_multi_map_fixture": "ok", "tests::transaction_callbacks_precede_unsigned_record": "ok", "tests::unknown_global_type_label": "ok"}
```
[tests::decode_base64_honors_declared_destination_limit]
thread 'tests::decode_base64_honors_declared_destination_limit' panicked at evaluation/harness/src/lib.rs:133:9:
assertion `left != right` failed: input cHNidP8=, declared destination capacity 1, backing slice capacity 20
  left: Ok
 right: Ok

[tests::decode_honors_input_prefix]
thread 'tests::decode_honors_input_prefix' panicked at evaluation/harness/src/lib.rs:112:9:
assertion `left == right` failed: input 70736274ffNOT_HEX, declared source length 10, destination capacity 20
  left: ReadError
 right: Ok

[tests::decode_rejects_oversized_source_length]
thread 'tests::decode_rejects_oversized_source_length' panicked at evaluation/harness/src/lib.rs:120:9:
assertion `left != right` failed: hex input has 10 bytes, declared source length is 11, destination capacity 20
  left: Ok
 right: Ok

[tests::encode_base62_honors_declared_limit]
thread 'tests::encode_base62_honors_declared_limit' panicked at evaluation/harness/src/lib.rs:177:9:
assertion `left != right` failed: Base62 source [0x12, 0x34], declared destination capacity 1, backing slice capacity 32
  left: Ok
 right: Ok

[tests::encode_base64_honors_declared_limit]
thread 'tests::encode_base64_honors_declared_limit' panicked at evaluation/harness/src/lib.rs:169:9:
assertion `left != right` failed: Base64 source [0x12, 0x34], declared destination capacity 1, backing slice capacity 32
  left: Ok
 right: Ok

[tests::encode_hex_checks_actual_destination]
thread 'tests::encode_hex_checks_actual_destination' panicked at src/psbt.rs:483:17:
index out of bounds: the len is 1 but the index is 1

[tests::encode_honors_input_prefix]
thread 'tests::encode_honors_input_prefix' panicked at evaluation/harness/src/lib.rs:150:9:
assertion `left == right` failed: hex encoding [0x12, 0x34, 0xff] with declared source length 2
  left: [49, 50, 51, 52, 102, 102, 0]
 right: [49, 50, 51, 52, 0]

[tests::encode_rejects_oversized_source_length]
thread 'tests::encode_rejects_oversized_source_length' panicked at evaluation/harness/src/lib.rs:156:9:
assertion `left != right` failed: hex source [0x12] with declared source length 2
  left: Ok
 right: Ok

[tests::errors_include_useful_context]
thread 'tests::errors_include_useful_context' panicked at evaluation/harness/src/lib.rs:219:9:
encoding a fresh PSBT, expected finalization context, got "psbt error"

[tests::read_rejects_length_larger_than_backing_slice]
thread 'tests::read_rejects_length_larger_than_backing_slice' panicked at evaluation/harness/src/lib.rs:105:9:
assertion `left != right` failed: declared length 160, backing slice length 159
  left: Ok
 right: Ok
```

## Current state of the editable Rust files
### src/base64.rs (125 lines)
```rust
const BASE64_TABLE: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
const BASE62_TABLE: &[u8; 62] = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

/// Checked table lookup. Indices outside the alphabet yield `None` instead of panicking.
fn sym(table: &[u8], idx: u8) -> Option<u8> {
    table.get(usize::from(idx)).copied()
}

/// Shared encoder for the 4-character-per-3-byte schemes (RFC 1341 layout).
/// Returns the number of symbols written, excluding the NUL terminator.
fn encode_with(src: &[u8], out: &mut [u8], table: &[u8]) -> Option<usize> {
    let olen = src.len() * 4 / 3 + 4;
    if olen + 1 > out.len() {
        return None;
    }

    let mut symbols: Vec<u8> = Vec::with_capacity(olen);
    for chunk in src.chunks(3) {
        let b0 = chunk[0];
        let b1 = chunk.get(1).copied().unwrap_or(0);
        let b2 = chunk.get(2).copied().unwrap_or(0);
        let idx = [
            b0 >> 2,
            ((b0 & 0x03) << 4) | (b1 >> 4),
            ((b1 & 0x0f) << 2) | (b2 >> 6),
            b2 & 0x3f,
        ];
        // Significant characters: one byte -> 2, two bytes -> 3, three bytes -> 4.
        let significant = chunk.len() + 1;
        for (k, &v) in idx.iter().enumerate() {
            if k < significant {
                symbols.push(sym(table, v)?);
            } else {
                symbols.push(b'=');
            }
        }
    }

    let len = symbols.len();
    out.get_mut(..len)?.copy_from_slice(&symbols);
    *out.get_mut(len)? = 0;
    Some(len)
}

/// Encode the given source bytes into base62. Returns the number of written bytes on success.
pub fn base62_encode(src: &[u8], out: &mut [u8]) -> Option<usize> {
    encode_with(src, out, BASE62_TABLE)
}

/// Encode the given source bytes into base64. Returns the number of written bytes on success.
pub fn base64_encode(src: &[u8], out: &mut [u8]) -> Option<usize> {
    encode_with(src, out, BASE64_TABLE)
}

/// Decode the given base64-encoded source bytes. Returns the number of decoded bytes on success.
pub fn base64_decode(src: &[u8], out: &mut [u8]) -> Option<usize> {
    if src.is_empty() {
        return None;
    }

    // Build decode table
    let mut dtable = [0x80u8; 256];
    for (i, &c) in BASE64_TABLE.iter().enumerate() {
        dtable[usize::from(c)] = i as u8;
    }
    dtable[usize::from(b'=')] = 0;

    // Count valid characters
    let count = src
        .iter()
        .filter(|&&c| dtable[usize::from(c)] != 0x80)
        .count();

    if count == 0 || count % 4 != 0 {
        return None;
    }

    let olen = count / 4 * 3;
    if out.len() < olen {
        return None;
    }

    let mut pos = 0;
    let mut block = [0u8; 4];
    let mut block_count = 0;
    let mut pad = 0;

    for &c in src {
        let tmp = dtable[usize::from(c)];
        if tmp == 0x80 {
            continue;
        }

        if c == b'=' {
            pad += 1;
        }
        block[block_count] = tmp;
        block_count += 1;

        if block_count == 4 {
            out[pos] = (block[0] << 2) | (block[1] >> 4);
            pos += 1;
            out[pos] = (block[1] << 4) | (block[2] >> 2);
            pos += 1;
            out[pos] = (block[2] << 6) | block[3];
            pos += 1;

            block_count = 0;

            if pad > 0 {
                if pad == 1 {
                    pos -= 1;
                } else if pad == 2 {
                    pos -= 2;
                } else {
                    return None;
                }
                break;
            }
        }
    }

    Some(pos)
}

```

### src/cli.rs (53 lines)
```rust
#![forbid(unsafe_code)]
use crate::psbt::{
    psbt_decode, psbt_encode, psbt_init, psbt_read, PsbtEncoding, PsbtResult, Psbt,
};

const BUF_SIZE: usize = 4096;

fn main() -> i32 {
    let args: Vec<String> = std::env::args().collect();
    let Some(hex) = args.get(1) else {
        println!("usage: psbt <psbt>");
        return 1;
    };

    let mut buffer = vec![0u8; BUF_SIZE];
    let mut psbt_len = 0usize;
    let mut psbt = Psbt::new(BUF_SIZE);

    let res = psbt_decode(hex, hex.len(), &mut buffer, BUF_SIZE, &mut psbt_len);
    if res != PsbtResult::Ok {
        println!("error ({res}): decode failed");
        return 1;
    }

    let res = psbt_init(&mut psbt, &mut buffer, BUF_SIZE);
    if res != PsbtResult::Ok {
        println!("error ({res}): init failed");
        return 1;
    }

    let res = psbt_read(&buffer, psbt_len, &mut psbt, None, &mut ());
    if res != PsbtResult::Ok {
        println!("error ({res}): read failed");
        return 1;
    }

    let mut out_len = 0usize;
    let res = psbt_encode(
        &psbt,
        PsbtEncoding::Base62,
        &mut buffer,
        BUF_SIZE,
        &mut out_len,
    );
    if res != PsbtResult::Ok {
        println!("error ({res}): encode failed");
        return 1;
    }

    println!("{}", String::from_utf8_lossy(&buffer[..out_len]));
    0
}

```

### src/compactsize.rs (102 lines)
```rust
use crate::psbt::{PsbtResult, MAX_SERIALIZE_SIZE};

pub fn compactsize_read(data: &[u8]) -> (u64, PsbtResult) {
    if data.is_empty() {
        return (0, PsbtResult::CompactReadError);
    }
    
    let chsize = data[0];
    
    let (size, err) = if chsize < 253 {
        (chsize as u64, PsbtResult::Ok)
    } else if chsize == 253 {
        if data.len() < 3 {
            return (0, PsbtResult::CompactReadError);
        }
        let val = u16::from_le_bytes([data[1], data[2]]);
        if val < 253 {
            return (0, PsbtResult::CompactReadError);
        }
        (val as u64, PsbtResult::Ok)
    } else if chsize == 254 {
        if data.len() < 5 {
            return (0, PsbtResult::CompactReadError);
        }
        let val = u32::from_le_bytes([data[1], data[2], data[3], data[4]]);
        if val < 0x10000 {
            return (0, PsbtResult::CompactReadError);
        }
        (val as u64, PsbtResult::Ok)
    } else {
        if data.len() < 9 {
            return (0, PsbtResult::CompactReadError);
        }
        let val = u64::from_le_bytes([
            data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]
        ]);
        if val < 0x100000000 {
            return (0, PsbtResult::CompactReadError);
        }
        (val, PsbtResult::Ok)
    };
    
    if size > MAX_SERIALIZE_SIZE as u64 {
        return (0, PsbtResult::CompactReadError);
    }
    
    (size, err)
}

pub fn compactsize_length(data: u64) -> u32 {
    if data < 253 {
        1
    } else if data <= u16::MAX as u64 {
        3
    } else if data <= u32::MAX as u64 {
        5
    } else {
        9
    }
}

pub fn compactsize_write(dest: &mut [u8], size: u64) {
    if size < 253 {
        dest[0] = size as u8;
    } else if size <= u16::MAX as u64 {
        dest[0] = 253;
        let bytes = (size as u16).to_le_bytes();
        dest[1] = bytes[0];
        dest[2] = bytes[1];
    } else if size <= u32::MAX as u64 {
        dest[0] = 254;
        let bytes = (size as u32).to_le_bytes();
        dest[1] = bytes[0];
        dest[2] = bytes[1];
        dest[3] = bytes[2];
        dest[4] = bytes[3];
    } else {
        dest[0] = 255;
        let bytes = size.to_le_bytes();
        dest[1] = bytes[0];
        dest[2] = bytes[1];
        dest[3] = bytes[2];
        dest[4] = bytes[3];
        dest[5] = bytes[4];
        dest[6] = bytes[5];
        dest[7] = bytes[6];
        dest[8] = bytes[7];
    }
}

pub fn compactsize_peek_length(chsize: u8) -> u32 {
    if chsize < 253 {
        1
    } else if chsize == 253 {
        3
    } else if chsize == 254 {
        5
    } else {
        9
    }
}

```

### src/psbt.rs (794 lines)
```rust

use crate::tx::*;
use crate::compactsize::{compactsize_read, compactsize_length, compactsize_write, compactsize_peek_length};
use crate::base64::{base64_encode, base64_decode, base62_encode};
use std::fmt;

// Common constant from common.h
pub const MAX_SERIALIZE_SIZE: u32 = 0x02000000;

// --- Enum definitions ---
#[derive(Debug, PartialEq, Eq)]
pub enum PsbtResult {
    Ok,
    CompactReadError,
    ReadError,
    WriteError,
    InvalidState,
    NotImplemented,
    OobWrite,
}

impl fmt::Display for PsbtResult {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{self:?}")
    }
}

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtGlobalType {
    UnsignedTx = 0,
}

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtEncoding {
    Hex,
    Base64,
    Base62,
    Protobuf,
}

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtInputType {
    NonWitnessUtxo = 0,
    WitnessUtxo = 1,
    PartialSig = 2,
    SighashType = 3,
    RedeemScript = 4,
    WitnessScript = 5,
    Bip32Derivation = 6,
    FinalScriptSig = 7,
    FinalScriptWitness = 8,
}

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtOutputType {
    RedeemScript = 0,
    WitnessScript = 1,
    Bip32Derivation = 2,
}

#[derive(Debug, PartialEq, Eq, Clone)]
pub enum PsbtScope {
    Global,
    Inputs,
    Outputs,
}

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtState {
    Init = 2,
    Global,
    Inputs,
    InputsNew,
    Outputs,
    OutputsNew,
    Finalized,
}

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtElemType {
    Record,
    TxElem,
}

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtTxElemType {
    TxIn,
    TxOut,
    Tx,
    WitnessItem,
}

// --- Struct definitions ---
/// Translates the C struct psbt.
/// (Here we use a Vec<u8> to hold the PSBT data and a write position index.)
pub struct Psbt {
    pub state: PsbtState,
    pub data: Vec<u8>,
    pub write_pos: usize,
    pub data_capacity: usize,
    // For simulation purposes we keep a list of records.
    pub records: Vec<PsbtRecord>,
}

impl Psbt {
    pub fn new(capacity: usize) -> Self {
        Self {
            state: PsbtState::Init,
            data: Vec::with_capacity(capacity),
            write_pos: 0,
            data_capacity: capacity,
            records: Vec::new(),
        }
    }
}

/// Translates the C struct psbt_record.
#[derive(Clone)]
pub struct PsbtRecord {
    /// (The C field "type" is renamed to avoid conflict with the Rust keyword.)
    pub record_type: u8,
    pub key: Vec<u8>,
    pub val: Vec<u8>,
    pub scope: PsbtScope,
}

/// Translates the C union (record/txelem) in psbt_elem into an enum.
pub enum PsbtElem {
    Record { index: i32, record: PsbtRecord },
    TxElem { index: i32, txelem: PsbtTxElem },
}

/// The C typedef for a handler function.
pub type PsbtElemHandler = fn(elem: &mut PsbtElem, user_data: &mut dyn std::any::Any);

// External constants
pub const PSBT_MAGIC: [u8; 4] = [0x70, 0x73, 0x62, 0x74]; // "psbt"
pub static PSBT_ERRMSG: &str = "psbt error";

/// Return the number of bytes stored in the PSBT.
pub fn psbt_size(tx: &Psbt) -> usize {
    tx.data.len()
}

/// For testing, we simulate reading by optionally calling the provided callback.
pub fn psbt_read(
    src: &[u8],
    src_size: usize,
    psbt: &mut Psbt,
    elem_handler: Option<PsbtElemHandler>,
    user_data: &mut dyn std::any::Any,
) -> PsbtResult {
    if psbt.state != PsbtState::Init {
        return PsbtResult::InvalidState;
    }
    
    if src_size > psbt.data_capacity {
        return PsbtResult::OobWrite;
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
                    if let Some(rec) = psbt.records.last().cloned() {
                        let txelems = if in_global && rec.record_type == 0 {
                            let v = match tx_elements(&rec.val) {
                                Ok(v) => v,
                                Err(res) => return res,
                            };
                            counts = (
                                v.iter()
                                    .filter(|e| matches!(e, PsbtTxElem::TxIn(_)))
                                    .count(),
                                v.iter()
                                    .filter(|e| matches!(e, PsbtTxElem::TxOut(_)))
                                    .count(),
                            );
                            v
                        } else {
                            Vec::new()
                        };

                        if let Some(handler) = elem_handler {
                            for txelem in txelems {
                                let mut elem = PsbtElem::TxElem {
                                    index: kvs as i32,
                                    txelem,
                                };
                                handler(&mut elem, user_data);
                            }
                            let mut elem = PsbtElem::Record {
                                index: kvs as i32,
                                record: rec,
                            };
                            handler(&mut elem, user_data);
                        }
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

fn read_record(psbt: &mut Psbt, src_size: usize) -> Result<(), PsbtResult> {
    // Read key length
    if psbt.write_pos >= src_size {
        return Err(PsbtResult::ReadError);
    }
    
    let (key_size, res) = compactsize_read(&psbt.data[psbt.write_pos..]);
    if res != PsbtResult::Ok {
        return Err(res);
    }
    if key_size == 0 {
        return Err(PsbtResult::ReadError);
    }
    
    let size_len = compactsize_peek_length(psbt.data[psbt.write_pos]);
    psbt.write_pos += size_len as usize;
    
    if psbt.write_pos + key_size as usize > src_size {
        return Err(PsbtResult::ReadError);
    }
    
    let key_with_type = key_size as usize;
    let record_type = psbt.data[psbt.write_pos];
    let key_start = psbt.write_pos + 1;
    let key_len = key_with_type - 1;
    
    psbt.write_pos += key_with_type;
    
    // Read value length
    if psbt.write_pos >= src_size {
        return Err(PsbtResult::ReadError);
    }
    
    let (val_size, res) = compactsize_read(&psbt.data[psbt.write_pos..]);
    if res != PsbtResult::Ok {
        return Err(res);
    }
    
    let size_len = compactsize_peek_length(psbt.data[psbt.write_pos]);
    psbt.write_pos += size_len as usize;
    
    if psbt.write_pos + val_size as usize > src_size {
        return Err(PsbtResult::ReadError);
    }
    
    let val_start = psbt.write_pos;
    let val_len = val_size as usize;
    
    psbt.write_pos += val_len;
    
    // Determine scope based on current state
    let scope = match psbt.state {
        PsbtState::Global => PsbtScope::Global,
        PsbtState::Inputs => PsbtScope::Inputs,
        PsbtState::Outputs => PsbtScope::Outputs,
        _ => return Err(PsbtResult::InvalidState),
    };
    
    let key = psbt.data[key_start..key_start + key_len].to_vec();
    let val = psbt.data[val_start..val_start + val_len].to_vec();
    
    let record = PsbtRecord {
        record_type,
        key,
        val,
        scope,
    };
    
    psbt.records.push(record);
    
    Ok(())
}

/// Decode a hex string into dest. (This simple implementation uses the `hex` crate.)
pub fn psbt_decode(
    src: &str,
    _src_size: usize,
    dest: &mut [u8],
    dest_size: usize,
    psbt_len: &mut usize,
) -> PsbtResult {
    let b64_magic = "cHNid";
    
    if src.len() < b64_magic.len() {
        return PsbtResult::ReadError;
    }
    
    if src.as_bytes().starts_with(b64_magic.as_bytes()) {
        // Base64 decode
        let src_bytes = src.as_bytes();
        match base64_decode(src_bytes, dest) {
            Some(len) => {
                *psbt_len = len;
                PsbtResult::Ok
            }
            None => PsbtResult::ReadError,
        }
    } else {
        // Hex decode
        if src.len() % 2 != 0 {
            return PsbtResult::ReadError;
        }
        
        let expected_len = src.len() / 2;
        if dest_size < expected_len || dest.len() < expected_len {
            return PsbtResult::ReadError;
        }
        
        let mut pos = 0;
        for (i, &c) in src.as_bytes().iter().enumerate() {
            if i % 2 == 0 {
                let c1 = c as char;
                let c2 = src.as_bytes()[i + 1] as char;
                
                let v1 = hex_to_val(c1);
                let v2 = hex_to_val(c2);
                
                if v1 == 0x80 || v2 == 0x80 {
                    return PsbtResult::ReadError;
                }
                
                dest[pos] = (v1 << 4) | v2;
                pos += 1;
            }
        }
        
        *psbt_len = expected_len;
        PsbtResult::Ok
    }
}

fn hex_to_val(c: char) -> u8 {
    if c.is_ascii_digit() {
        c as u8 - b'0'
    } else if ('a'..='f').contains(&c) {
        c as u8 - b'a' + 10
    } else if ('A'..='F').contains(&c) {
        c as u8 - b'A' + 10
    } else {
        0x80
    }
}

/// Encode the PSBT data into a destination buffer using the requested encoding.
/// (Only Hex encoding is implemented for simplicity.)
pub fn psbt_encode(
    psbt: &Psbt,
    encoding: PsbtEncoding,
    dest: &mut [u8],
    dest_size: usize,
    out_len: &mut usize,
) -> PsbtResult {
    if psbt.state != PsbtState::Finalized {
        return PsbtResult::WriteError;
    }
    
    psbt_encode_raw(&psbt.data, psbt.data.len(), encoding, dest, dest_size, out_len)
}

/// Encode raw PSBT data into dest using the requested encoding.
pub fn psbt_encode_raw(
    psbt_data: &[u8],
    _psbt_len: usize,
    encoding: PsbtEncoding,
    dest: &mut [u8],
    dest_size: usize,
    out_len: &mut usize,
) -> PsbtResult {
    match encoding {
        PsbtEncoding::Hex => {
            if dest_size < psbt_data.len() * 2 + 1 {
                return PsbtResult::OobWrite;
            }
            
            let mut pos = 0;
            for &byte in psbt_data.iter() {
                let high = (byte >> 4) & 0x0F;
                let low = byte & 0x0F;
                
                dest[pos] = hex_char(high);
                pos += 1;
                dest[pos] = hex_char(low);
                pos += 1;
            }
            
            dest[pos] = 0;
            *out_len = psbt_data.len() * 2 + 1;
            PsbtResult::Ok
        }
        PsbtEncoding::Base64 => {
            match base64_encode(psbt_data, dest) {
                Some(len) => {
                    *out_len = len;
                    PsbtResult::Ok
                }
                None => PsbtResult::WriteError,
            }
        }
        PsbtEncoding::Base62 => {
            match base62_encode(psbt_data, dest) {
                Some(len) => {
                    *out_len = len;
                    PsbtResult::Ok
                }
                None => PsbtResult::WriteError,
            }
        }
        PsbtEncoding::Protobuf => PsbtResult::NotImplemented,
    }
}

fn hex_char(val: u8) -> u8 {
    if val < 10 {
        b'0' + val
    } else {
        b'a' + val - 10
    }
}

/// Return the last error message.
pub fn psbt_geterr() -> &'static str {
    PSBT_ERRMSG
}

/// Convert a PSBT state to a human–readable string.
pub fn psbt_state_tostr(state: PsbtState) -> &'static str {
    match state {
        PsbtState::Init => "INIT",
        PsbtState::Global => "GLOBAL",
        PsbtState::Inputs => "INPUTS",
        PsbtState::InputsNew => "INPUTS_NEW",
        PsbtState::Outputs => "OUTPUTS",
        PsbtState::OutputsNew => "OUTPUTS_NEW",
        PsbtState::Finalized => "FINALIZED",
    }
}

/// Return a string for a record type and scope.
pub fn psbt_type_tostr(record_type: u8, scope: PsbtScope) -> &'static str {
    match scope {
        PsbtScope::Global => match record_type {
            0 => psbt_global_type_tostr(PsbtGlobalType::UnsignedTx),
            _ => "UNKNOWN_GLOBAL_TYPE",
        },
        PsbtScope::Inputs => {
            match record_type {
                0 => psbt_input_type_tostr(PsbtInputType::NonWitnessUtxo),
                1 => psbt_input_type_tostr(PsbtInputType::WitnessUtxo),
                2 => psbt_input_type_tostr(PsbtInputType::PartialSig),
                3 => psbt_input_type_tostr(PsbtInputType::SighashType),
                4 => psbt_input_type_tostr(PsbtInputType::RedeemScript),
                5 => psbt_input_type_tostr(PsbtInputType::WitnessScript),
                6 => psbt_input_type_tostr(PsbtInputType::Bip32Derivation),
                7 => psbt_input_type_tostr(PsbtInputType::FinalScriptSig),
                8 => psbt_input_type_tostr(PsbtInputType::FinalScriptWitness),
                _ => "UNKNOWN_INPUT_TYPE",
            }
        }
        PsbtScope::Outputs => {
            match record_type {
                0 => psbt_output_type_tostr(PsbtOutputType::RedeemScript),
                1 => psbt_output_type_tostr(PsbtOutputType::WitnessScript),
                2 => psbt_output_type_tostr(PsbtOutputType::Bip32Derivation),
                _ => "UNKNOWN_OUTPUT_TYPE",
            }
        }
    }
}

/// Return a string for a psbt_txelem type.
pub fn psbt_txelem_type_tostr(txelem_type: PsbtTxElemType) -> &'static str {
    match txelem_type {
        PsbtTxElemType::Tx => "TX",
        PsbtTxElemType::TxIn => "TXIN",
        PsbtTxElemType::TxOut => "TXOUT",
        PsbtTxElemType::WitnessItem => "WITNESS_ITEM",
    }
}

pub fn psbt_global_type_tostr(gt: PsbtGlobalType) -> &'static str {
    match gt {
        PsbtGlobalType::UnsignedTx => "GLOBAL_UNSIGNED_TX",
    }
}

pub fn psbt_output_type_tostr(ot: PsbtOutputType) -> &'static str {
    match ot {
        PsbtOutputType::RedeemScript => "OUT_REDEEM_SCRIPT",
        PsbtOutputType::WitnessScript => "OUT_WITNESS_SCRIPT",
        PsbtOutputType::Bip32Derivation => "OUT_BIP32_DERIVATION",
    }
}

pub fn psbt_input_type_tostr(it: PsbtInputType) -> &'static str {
    match it {
        PsbtInputType::NonWitnessUtxo => "IN_NON_WITNESS_UTXO",
        PsbtInputType::WitnessUtxo => "IN_WITNESS_UTXO",
        PsbtInputType::PartialSig => "IN_PARTIAL_SIG",
        PsbtInputType::SighashType => "IN_SIGHASH_TYPE",
        PsbtInputType::RedeemScript => "IN_REDEEM_SCRIPT",
        PsbtInputType::WitnessScript => "IN_WITNESS_SCRIPT",
        PsbtInputType::Bip32Derivation => "IN_BIP32_DERIVATION",
        PsbtInputType::FinalScriptSig => "IN_FINAL_SCRIPTSIG",
        PsbtInputType::FinalScriptWitness => "IN_FINAL_SCRIPTWITNESS",
    }
}

/// Write a global record into the PSBT.
pub fn psbt_write_global_record(psbt: &mut Psbt, rec: &PsbtRecord) -> PsbtResult {
    if psbt.state == PsbtState::Init {
        // Write header
        if psbt.data.len() + 5 > psbt.data_capacity {
            return PsbtResult::OobWrite;
        }
        
        psbt.data.extend_from_slice(&PSBT_MAGIC);
        psbt.data.push(0xff);
        psbt.write_pos = psbt.data.len();
        psbt.state = PsbtState::Global;
    } else if psbt.state != PsbtState::Global {
        return PsbtResult::InvalidState;
    }
    
    write_record(psbt, rec)
}

/// Write an input record into the PSBT.
pub fn psbt_write_input_record(psbt: &mut Psbt, rec: &PsbtRecord) -> PsbtResult {
    if psbt.state == PsbtState::Global {
        // Close global records
        if let Err(res) = close_records(psbt) {
            return res;
        }
        psbt.state = PsbtState::Inputs;
    } else if psbt.state != PsbtState::Inputs && psbt.state != PsbtState::InputsNew {
        return PsbtResult::InvalidState;
    }
    
    write_record(psbt, rec)
}

/// Write an output record into the PSBT.
pub fn psbt_write_output_record(psbt: &mut Psbt, rec: &PsbtRecord) -> PsbtResult {
    if psbt.state == PsbtState::Inputs {
        // Close input records
        if let Err(res) = close_records(psbt) {
            return res;
        }
        psbt.state = PsbtState::Outputs;
    } else if psbt.state != PsbtState::Outputs && psbt.state != PsbtState::OutputsNew {
        return PsbtResult::InvalidState;
    }
    
    write_record(psbt, rec)
}

fn write_record(psbt: &mut Psbt, rec: &PsbtRecord) -> PsbtResult {
    let key_size_with_type = rec.key.len() + 1;
    
    // Write key length
    let key_len_size = compactsize_length(key_size_with_type as u64);
    if psbt.data.len() + key_len_size as usize + 1 > psbt.data_capacity {
        return PsbtResult::OobWrite;
    }
    
    let pos = psbt.data.len();
    psbt.data.resize(pos + key_len_size as usize, 0);
    compactsize_write(&mut psbt.data[pos..pos + key_len_size as usize], key_size_with_type as u64);
    
    // Write type
    if psbt.data.len() + 1 > psbt.data_capacity {
        return PsbtResult::OobWrite;
    }
    psbt.data.push(rec.record_type);
    
    // Write key
    if psbt.data.len() + rec.key.len() > psbt.data_capacity {
        return PsbtResult::OobWrite;
    }
    psbt.data.extend_from_slice(&rec.key);
    
    // Write value length
    let val_len_size = compactsize_length(rec.val.len() as u64);
    if psbt.data.len() + val_len_size as usize > psbt.data_capacity {
        return PsbtResult::OobWrite;
    }
    
    let pos = psbt.data.len();
    psbt.data.resize(pos + val_len_size as usize, 0);
    compactsize_write(&mut psbt.data[pos..pos + val_len_size as usize], rec.val.len() as u64);
    
    // Write value
    if psbt.data.len() + rec.val.len() > psbt.data_capacity {
        return PsbtResult::OobWrite;
    }
    psbt.data.extend_from_slice(&rec.val);
    
    psbt.write_pos = psbt.data.len();
    
    PsbtResult::Ok
}

fn close_records(psbt: &mut Psbt) -> Result<(), PsbtResult> {
    if psbt.data.len() + 1 > psbt.data_capacity {
        return Err(PsbtResult::OobWrite);
    }
    psbt.data.push(0);
    psbt.write_pos = psbt.data.len();
    Ok(())
}

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
pub fn psbt_init(psbt: &mut Psbt, _dest: &mut [u8], dest_size: usize) -> PsbtResult {
    psbt.data.clear();
    psbt.data_capacity = dest_size;
    psbt.write_pos = 0;
    psbt.state = PsbtState::Init;
    psbt.records.clear();
    
    PsbtResult::Ok
}

/// Print the PSBT (only succeeds after finalization).
pub fn psbt_print(psbt: &Psbt, stream: &mut dyn std::io::Write) -> PsbtResult {
    if psbt.state != PsbtState::Finalized {
        return PsbtResult::InvalidState;
    }
    
    for byte in psbt.data.iter() {
        let _ = write!(stream, "{byte:02x}");
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

```

### src/tx.rs (136 lines)
```rust
#![forbid(unsafe_code)]
use super::psbt::PsbtResult;
use crate::compactsize::{compactsize_peek_length, compactsize_read};

/// Translates the C struct psbt_txin.
pub struct PsbtTxIn {
    pub txid: Vec<u8>,
    pub index: u32,
    pub script: Vec<u8>,
    pub sequence_number: u32,
}

/// Translates the C struct psbt_txout.
pub struct PsbtTxOut {
    pub amount: u64,
    pub script: Vec<u8>,
}

/// Translates the C struct psbt_witness_item.
pub struct PsbtWitnessItem {
    pub input_index: i32,
    pub item_index: i32,
    pub item: Vec<u8>,
}

/// Translates the C struct psbt_tx.
pub struct PsbtTx {
    pub version: u32,
    pub lock_time: u32,
}

/// Translates the C union inside psbt_txelem.
pub enum PsbtTxElem {
    TxIn(PsbtTxIn),
    TxOut(PsbtTxOut),
    Tx(PsbtTx),
    WitnessItem(PsbtWitnessItem),
}

/// The handler type for psbt_txelem.
pub type PsbtTxElemHandler = fn(elem: &mut PsbtTxElem, user_data: &mut dyn std::any::Any);

/// Bounds-checked take of `n` bytes at `pos`.
fn take<'a>(data: &'a [u8], pos: &mut usize, n: usize) -> Result<&'a [u8], PsbtResult> {
    let end = pos.checked_add(n).ok_or(PsbtResult::ReadError)?;
    let bytes = data.get(*pos..end).ok_or(PsbtResult::ReadError)?;
    *pos = end;
    Ok(bytes)
}

fn take_array<const N: usize>(data: &[u8], pos: &mut usize) -> Result<[u8; N], PsbtResult> {
    let bytes = take(data, pos, N)?;
    bytes.try_into().map_err(|_| PsbtResult::ReadError)
}

fn take_u32(data: &[u8], pos: &mut usize) -> Result<u32, Psbt
... [truncated; use <read> for the rest]
```
(file shown only partially to save context; use <read path="src/tx.rs"/> for all of it)

Reply using the block protocol. Update your `<notes>` so they stay accurate.
