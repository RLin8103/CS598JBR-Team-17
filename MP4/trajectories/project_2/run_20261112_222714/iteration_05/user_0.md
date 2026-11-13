# Iteration 5 of at most 40 - controller feedback

## Your notes from the previous turn
## Plan

Fix the following compiler errors:
1. Add `MAX_SERIALIZE_SIZE` import to compactsize.rs
2. Add base64 imports to psbt.rs
3. Fix BASE64_TABLE size (64 vs 65)
4. Add Clone derive to PsbtRecord
5. Fix enum casting in psbt_type_tostr
6. Fix unused variable warning in psbt_init


## Status
- compiles: False (7 errors)
- tests: 0 passed / 0 total (0 failed)
- unsafe metrics (builtin-approximation): lines=0, calls=0, casts=0, pointer_arithmetic=0
- clippy warnings: n/a (needs a successful build)
- tokens used so far: 218245 / 2000000

## Current phase: COMPILE
The crate does not compile. Fix compiler errors first, starting with the first errors in the list (later errors are often consequences of earlier ones). Do not add new unsafe code while doing this: if the unsafe list below grows, rewrite those helpers safely (slices, Vec, iterators) instead of with raw pointers.

## cargo build errors
```
warning: file `/mnt/c/VSCodeProjects/CS598JBR-Team-17/MP4/translations/project_2/src/bin/test.rs` found to be present in multiple build targets:
  * `bin` target `test`
  * `integration-test` target `test`
   Compiling libpsbt v0.1.0 (/mnt/c/VSCodeProjects/CS598JBR-Team-17/MP4/translations/project_2)
error[E0425]: cannot find function `base64_decode` in this scope
   --> src/psbt.rs:344:15
    |
344 |         match base64_decode(src_bytes, dest) {
    |               ^^^^^^^^^^^^^ not found in this scope
    |
help: consider importing this function
    |
2   + use crate::base64::base64_decode;
    |

error[E0425]: cannot find function `base64_encode` in this scope
   --> src/psbt.rs:442:19
    |
442 |             match base64_encode(psbt_data, dest) {
    |                   ^^^^^^^^^^^^^ not found in this scope
    |
help: consider importing this function
    |
2   + use crate::base64::base64_encode;
    |

error[E0425]: cannot find function `base62_encode` in this scope
   --> src/psbt.rs:451:19
    |
451 |             match base62_encode(psbt_data, dest) {
    |                   ^^^^^^^^^^^^^ not found in this scope
    |
help: consider importing this function
    |
2   + use crate::base64::base62_encode;
    |

error[E0308]: mismatched types
 --> src/base64.rs:1:33
  |
1 | const BASE64_TABLE: &[u8; 65] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  |                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ expected an array with a size of 65, found one with a size of 64

error[E0308]: mismatched types
   --> src/psbt.rs:218:37
    |
218 | ...                   record: psbt.records.last().unwrap().clone(),
    |                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ expected `PsbtRecord`, found `&PsbtRecord`
    |
note: `PsbtRecord` does not implement `Clone`, so `&PsbtRecord` was cloned instead
   --> src/psbt.rs:218:37
    |
218 | ...                   record: psbt.records.last().unwrap().clone(),
    |                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
help: consider annotating `PsbtRecord` with `#[derive(Clone)]`
    |
117 + #[derive(Clone)]
118 | pub struct PsbtRecord {
    |

error[E0605]: non-primitive cast: `u8` as `PsbtInputType`
   --> src/psbt.rs:493:52
    |
493 |         PsbtScope::Inputs => psbt_input_type_tostr(record_type as PsbtInputType),
    |                                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^ an `as` expression can only be used to convert between primitive types or to coerce to a specific trait object

error[E0605]: non-primitive cast: `u8` as `PsbtOutputType`
   --> src/psbt.rs:494:54
    |
494 |         PsbtScope::Outputs => psbt_output_type_tostr(record_type as PsbtOutputType),
    |                                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ an `as` expression can only be used to convert between primitive types or to coerce to a specific trait object

warning: unused variable: `dest`
   --> src/psbt.rs:684:35
    |
684 | pub fn psbt_init(psbt: &mut Psbt, dest: &mut [u8], dest_size: usize) -> PsbtResult {
    |                                   ^^^^ help: if this is intentional, prefix it with an underscore: `_dest`
    |
    = note: `#[warn(unused_variables)]` on by default

Some errors have detailed explanations: E0308, E0425, E0605.
For more information about an error, try `rustc --explain E0308`.
warning: `libpsbt` (lib) generated 1 warning
error: could not compile `libpsbt` (lib) due to 7 previous errors; 1 warning emitted
warning: build failed, waiting for other jobs to finish...
warning: `libpsbt` (lib test) generated 1 warning (1 duplicate)
error: could not compile `libpsbt` (lib test) due to 7 previous errors; 1 warning emitted

```

## unsafe metrics (builtin-approximation)
{"unsafe_lines": 0, "unsafe_calls": 0, "unsafe_casts": 0, "pointer_arithmetic": 0, "unsafe_blocks": 0, "unsafe_fns": 0, "raw_pointer_decls": 0, "ffi_calls": 0, "transmute_uses": 0, "manual_alloc_ops": 0, "files_with_forbid_unsafe_code": 0, "files_analysed": 6}

## Current state of the editable Rust files
### src/base64.rs (166 lines)
```rust
const BASE64_TABLE: &[u8; 65] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
const BASE62_TABLE: &[u8; 62] = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

/// Encode the given source bytes into base62. Returns the number of written bytes on success.
pub fn base62_encode(src: &[u8], out: &mut [u8]) -> Option<usize> {
    let olen = src.len() * 4 / 3 + 4;
    if olen + 1 > out.len() {
        return None;
    }
    
    let end = src.len();
    let mut pos = 0;
    let mut i = 0;
    
    while i + 3 <= end {
        out[pos] = BASE62_TABLE[(src[i] >> 2) as usize];
        pos += 1;
        out[pos] = BASE62_TABLE[(((src[i] & 0x03) << 4) | (src[i + 1] >> 4)) as usize];
        pos += 1;
        out[pos] = BASE62_TABLE[(((src[i + 1] & 0x0f) << 2) | (src[i + 2] >> 6)) as usize];
        pos += 1;
        out[pos] = BASE62_TABLE[(src[i + 2] & 0x3f) as usize];
        pos += 1;
        i += 3;
    }
    
    if i < end {
        out[pos] = BASE62_TABLE[(src[i] >> 2) as usize];
        pos += 1;
        if i + 1 == end {
            out[pos] = BASE62_TABLE[((src[i] & 0x03) << 4) as usize];
            pos += 1;
            out[pos] = b'=';
            pos += 1;
        } else {
            out[pos] = BASE62_TABLE[(((src[i] & 0x03) << 4) | (src[i + 1] >> 4)) as usize];
            pos += 1;
            out[pos] = BASE62_TABLE[((src[i + 1] & 0x0f) << 2) as usize];
            pos += 1;
        }
        out[pos] = b'=';
        pos += 1;
    }
    
    out[pos] = 0;
    Some(pos)
}

/// Encode the given source bytes into base64. Returns the number of written bytes on success.
pub fn base64_encode(src: &[u8], out: &mut [u8]) -> Option<usize> {
    let olen = src.len() * 4 / 3 + 4;
    if olen + 1 > out.len() {
        return None;
    }
    
    let end = src.len();
    let mut pos = 0;
    let mut i = 0;
    
    while i + 3 <= end {
        out[pos] = BASE64_TABLE[(src[i] >> 2) as usize];
        pos += 1;
        out[pos] = BASE64_TABLE[(((src[i] & 0x03) << 4) | (src[i + 1] >> 4)) as usize];
        pos += 1;
        out[pos] = BASE64_TABLE[(((src[i + 1] & 0x0f) << 2) | (src[i + 2] >> 6)) as usize];
        pos += 1;
        out[pos] = BASE64_TABLE[(src[i + 2] & 0x3f) as usize];
        pos += 1;
        i += 3;
    }
    
    if i < end {
        out[pos] = BASE64_TABLE[(src[i] >> 2) as usize];
        pos += 1;
        if i + 1 == end {
            out[pos] = BASE64_TABLE[((src[i] & 0x03) << 4) as usize];
            pos += 1;
            out[pos] = b'=';
            pos += 1;
        } else {
            out[pos] = BASE64_TABLE[(((src[i] & 0x03) << 4) | (src[i + 1] >> 4)) as usize];
            pos += 1;
            out[pos] = BASE64_TABLE[((src[i + 1] & 0x0f) << 2) as usize];
            pos += 1;
        }
        out[pos] = b'=';
        pos += 1;
    }
    
    out[pos] = 0;
    Some(pos)
}

/// Decode the given base64-encoded source bytes. Returns the number of decoded bytes on success.
pub fn base64_decode(src: &[u8], out: &mut [u8]) -> Option<usize> {
    if src.is_empty() {
        return None;
    }
    
    // Build decode table
    let mut dtable = [0x80u8; 256];
    for (i, &c) in BASE64_TABLE.iter().enumerate() {
        dtable[c as usize] = i as u8;
    }
    dtable[b'=' as usize] = 0;
    
    // Count valid characters
    let mut count = 0;
    for &c in src.iter() {
        if dtable[c as usize] != 0x80 {
            count += 1;
        }
    }
    
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
    
    for &c in src.iter() {
        let tmp = dtable[c as usize];
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

### src/cli.rs (4 lines)
```rust
fn main() -> i32 {
    unimplemented!()
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

### src/psbt.rs (726 lines)
```rust

use crate::tx::*;
use crate::compactsize::{compactsize_read, compactsize_length, compactsize_write, compactsize_peek_length};
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

/// For testing, we simulate reading by optionally calling the provided callback twice.
pub fn psbt_read(
    src: &[u8],
    _src_size: usize,
    psbt: &mut Psbt,
    elem_handler: Option<PsbtElemHandler>,
    user_data: &mut dyn std::any::Any,
) -> PsbtResult {
    if psbt.state != PsbtState::Init {
        return PsbtResult::InvalidState;
    }
    
    if src.len() > psbt.data_capacity {
        return PsbtResult::OobWrite;
    }
    
    psbt.data.clear();
    psbt.data.extend_from_slice(src);
    psbt.write_pos = 0;
    psbt.records.clear();
    
    psbt.state = PsbtState::Init;
    
    let src_size = src.len();
    let end = src_size;
    
    while psbt.state != PsbtState::Finalized && psbt.write_pos <= end {
        match psbt.state {
            PsbtState::Init => {
                // Read header
                if psbt.write_pos + 4 > src_size {
                    return PsbtResult::ReadError;
                }
                
                if &psbt.data[psbt.write_pos..psbt.write_pos + 4] != PSBT_MAGIC {
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
                if psbt.write_pos >= src_size {
                    return PsbtResult::ReadError;
                }
                
                if psbt.data[psbt.write_pos] == 0 {
                    match psbt.state {
                        PsbtState::Global => {
                            psbt.state = PsbtState::InputsNew;
                        }
                        PsbtState::Inputs => {
                            psbt.state = PsbtState::InputsNew;
                        }
                        PsbtState::Outputs => {
                            psbt.state = PsbtState::Finalized;
                        }
                        _ => {}
                    }
                } else {
                    // Read record
                    let record_result = read_record(psbt, src_size);
                    if let Err(res) = record_result {
                        return res;
                    }
                    
                    if let Some(ref mut handler) = elem_handler {
                        let mut elem = PsbtElem::Record {
                            index: (psbt.records.len() - 1) as i32,
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
    
    if &src[..b64_magic.len()] == b64_magic {
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
        if dest_size < expected_len {
            return PsbtResult::ReadError;
        }
        
        let mut pos = 0;
        for i in (0..src.len()).step_by(2) {
            let c1 = src.chars().nth(i).unwrap();
            let c2 = src.chars().nth(i + 1).unwrap();
            
            let v1 = hex_to_val(c1);
            let v2 = hex_to_val(c2);
            
            if v1 == 0x80 || v2 == 0x80 {
                return PsbtResult::ReadError;
            }
            
            dest[pos] = (v1 << 4) | v2;
            pos += 1;
        }
        
        *psbt_len = expected_len;
        PsbtResult::Ok
    }
}

fn hex_to_val(c: char) -> u8 {
    if c >= '0' && c <= '9' {
        c as u8 - b'0'
    } else if c >= 'a' && c <= 'f' {
        c as u8 - b'a' + 10
    } else if c >= 'A' && c <= 'F' {
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
        PsbtScope::Global => psbt_global_type_tostr(PsbtGlobalType::UnsignedTx),
        PsbtScope::Inputs => psbt_input_type_tostr(record_type as PsbtInputType),
        PsbtScope::Outputs => psbt_output_type_tostr(record_type as PsbtOutputType),
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

```

### src/tx.rs (50 lines)
```rust
use super::psbt::PsbtResult;

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

/// Parse a Bitcoin transaction. (Not implemented.)
pub fn psbt_btc_tx_parse(
    _tx: &[u8],
    _tx_size: usize,
    _user_data: &mut dyn std::any::Any,
    _handler: Option<PsbtTxElemHandler>,
) -> PsbtResult {
    unimplemented!()
}

```

Reply using the block protocol. Update your `<notes>` so they stay accurate.
