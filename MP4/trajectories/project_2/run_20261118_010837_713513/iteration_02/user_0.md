# Iteration 2 of at most 2 - controller feedback


## Status
- compiles: False (2 errors)
- tests: 0 passed / 0 total (0 failed)
- unsafe metrics (builtin-approximation): lines=0, calls=0, casts=0, pointer_arithmetic=0
- validation: test_ok=None, clippy_ok=None, unsafe_valid=True
- clippy warnings: n/a (needs a successful build)
- interface deviations (signatures that differ from src/interfaces/*.rs): 24
- untranslated bodies (`unimplemented!()`/`todo!()`): 0
- tokens used so far: 122661 / 1000000

## Current phase: COMPILE
The crate does not compile. Fix compiler errors first, starting with the first errors in the list (later errors are often consequences of earlier ones). Do not add new unsafe code while doing this: if the unsafe list below grows, rewrite those helpers safely (slices, Vec, iterators) instead of with raw pointers.

## Interface deviations (the interface files are part of the specification and hidden tests are compiled against them)
- src/psbt.rs: type `PsbtResult` differs from the interface.
      interface: `pub enum PsbtResult { Ok, CompactReadError, ReadError, WriteError, InvalidState, NotImplemented, OobWrite, }`
      yours    : `pub enum PsbtResult { Ok, CompactReadError, ReadError, WriteError, InvalidState, NotImplemented, OobWrite }`
- src/psbt.rs: type `PsbtEncoding` differs from the interface.
      interface: `pub enum PsbtEncoding { Hex, Base64, Base62, Protobuf, }`
      yours    : `pub enum PsbtEncoding { Hex, Base64, Base62, Protobuf }`
- src/psbt.rs: type `PsbtOutputType` differs from the interface.
      interface: `pub enum PsbtOutputType { RedeemScript = 0, WitnessScript = 1, Bip32Derivation = 2, }`
      yours    : `pub enum PsbtOutputType { RedeemScript = 0, WitnessScript = 1, Bip32Derivation = 2 }`
- src/psbt.rs: type `PsbtScope` differs from the interface.
      interface: `pub enum PsbtScope { Global, Inputs, Outputs, }`
      yours    : `pub enum PsbtScope { Global, Inputs, Outputs }`
- src/psbt.rs: type `PsbtState` differs from the interface.
      interface: `pub enum PsbtState { Init = 2, Global, Inputs, InputsNew, Outputs, OutputsNew, Finalized, }`
      yours    : `pub enum PsbtState { Init = 2, Global, Inputs, InputsNew, Outputs, OutputsNew, Finalized }`
- src/psbt.rs: type `PsbtElemType` differs from the interface.
      interface: `pub enum PsbtElemType { Record, TxElem, }`
      yours    : `pub enum PsbtElemType { Record, TxElem }`
- src/psbt.rs: type `PsbtTxElemType` differs from the interface.
      interface: `pub enum PsbtTxElemType { TxIn, TxOut, Tx, WitnessItem, }`
      yours    : `pub enum PsbtTxElemType { TxIn, TxOut, Tx, WitnessItem }`
- src/psbt.rs: missing function required by the interface: `pub fn psbt_encode(psbt: &Psbt, encoding: PsbtEncoding, dest: &mut [u8], dest_size: usize, out_len: &mut usize,) -> PsbtResult`
- src/psbt.rs: missing function required by the interface: `pub fn psbt_encode_raw(psbt_data: &[u8], _psbt_len: usize, encoding: PsbtEncoding, dest: &mut [u8], dest_size: usize, out_len: &mut usize,) -> PsbtResult`
- src/psbt.rs: missing function required by the interface: `pub fn psbt_geterr() -> &'static str`
- src/psbt.rs: missing function required by the interface: `pub fn psbt_state_tostr(state: PsbtState) -> &'static str`
- src/psbt.rs: missing function required by the interface: `pub fn psbt_type_tostr(record_type: u8, scope: PsbtScope) -> &'static str`
- src/psbt.rs: missing function required by the interface: `pub fn psbt_txelem_type_tostr(txelem_type: PsbtTxElemType) -> &'static str`
- src/psbt.rs: missing function required by the interface: `pub fn psbt_global_type_tostr(gt: PsbtGlobalType) -> &'static str`
- ... more omitted
Restore every signature, struct/enum definition and `impl` header exactly as in `src/interfaces/`. Do not add or remove generic bounds, change `&self`/`&mut self`, or change parameter or return types to make the body easier. If a signature cannot be implemented soundly, document a precise counterexample. Moving unsafe operations into helpers does not establish soundness.

## cargo build errors
```
warning: file `/Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/translations/project_2/src/bin/test.rs` found to be present in multiple build targets:
  * `bin` target `test`
  * `integration-test` target `test`
   Compiling libpsbt v0.1.0 (/Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/translations/project_2)
error[E0432]: unresolved imports `crate::psbt::psbt_encode`, `crate::psbt::psbt_init`
 --> src/cli.rs:3:18
  |
3 |     psbt_decode, psbt_encode, psbt_init, psbt_read, PsbtEncoding, PsbtResult, Psbt,
  |                  ^^^^^^^^^^^  ^^^^^^^^^ no `psbt_init` in `psbt`
  |                  |
  |                  no `psbt_encode` in `psbt`
  |                  help: a similar name exists in the module: `psbt_decode`

warning: unused imports: `base62_encode` and `base64_encode`
 --> src/psbt.rs:2:21
  |
2 | use crate::base64::{base62_encode, base64_decode, base64_encode};
  |                     ^^^^^^^^^^^^^                 ^^^^^^^^^^^^^
  |
  = note: `#[warn(unused_imports)]` on by default

warning: unused imports: `compactsize_length` and `compactsize_write`
 --> src/psbt.rs:4:5
  |
4 |     compactsize_length, compactsize_peek_length, compactsize_read, compactsize_write,
  |     ^^^^^^^^^^^^^^^^^^                                             ^^^^^^^^^^^^^^^^^

error[E0502]: cannot borrow `*dest` as immutable because it is also borrowed as mutable
   --> src/psbt.rs:375:42
    |
375 |     let dest = &mut dest[..dest_size.min(dest.len())];
    |                     ---------------------^^^^--------
    |                     |   |                |
    |                     |   |                immutable borrow occurs here
    |                     |   mutable borrow later used here
    |                     mutable borrow occurs here
    |
help: try adding a local storing this...
   --> src/psbt.rs:375:42
    |
375 |     let dest = &mut dest[..dest_size.min(dest.len())];
    |                                          ^^^^^^^^^^
help: ...and then using that local here
   --> src/psbt.rs:375:25
    |
375 |     let dest = &mut dest[..dest_size.min(dest.len())];
    |                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some errors have detailed explanations: E0432, E0502.
For more information about an error, try `rustc --explain E0432`.
warning: `libpsbt` (lib) generated 2 warnings (2 duplicates)
error: could not compile `libpsbt` (lib) due to 2 previous errors; 2 warnings emitted
warning: build failed, waiting for other jobs to finish...
warning: `libpsbt` (lib test) generated 2 warnings
error: could not compile `libpsbt` (lib test) due to 2 previous errors; 2 warnings emitted

```

## unsafe metrics (builtin-approximation)
{"unsafe_lines": 0, "unsafe_calls": 0, "unsafe_casts": 0, "pointer_arithmetic": 0, "unsafe_blocks": 0, "unsafe_fns": 0, "raw_pointer_decls": 0, "ffi_calls": 0, "transmute_uses": 0, "manual_alloc_ops": 0, "files_with_forbid_unsafe_code": 4, "files_analysed": 6}
Mandatory official safety validation unavailable/invalid: official analyzer not configured

## Separate regression check
$ /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/.venv/bin/python /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/src/run_regressions.py --project-id 2 --output /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/trajectories/project_2/run_20261118_010837_713513/additional_checks/2
returncode=1 timed_out=False
```
warning: field `v` is never read
   --> /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/translations/project_1/src/cset.rs:291:5
    |
286 | pub struct Cset<T> {
    |            ---- field in this struct
...
291 |     v: CsetValue<T>,
    |     ^
    |
    = note: `#[warn(dead_code)]` on by default

warning: `cset` (lib) generated 1 warning
   Compiling libpsbt v0.1.0 (/Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/translations/project_2)
error[E0432]: unresolved imports `crate::psbt::psbt_encode`, `crate::psbt::psbt_init`
 --> /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/translations/project_2/src/cli.rs:3:18
  |
3 |     psbt_decode, psbt_encode, psbt_init, psbt_read, PsbtEncoding, PsbtResult, Psbt,
  |                  ^^^^^^^^^^^  ^^^^^^^^^ no `psbt_init` in `psbt`
  |                  |
  |                  no `psbt_encode` in `psbt`
  |                  help: a similar name exists in the module: `psbt_decode`

warning: unused imports: `base62_encode` and `base64_encode`
 --> /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/translations/project_2/src/psbt.rs:2:21
  |
2 | use crate::base64::{base62_encode, base64_decode, base64_encode};
  |                     ^^^^^^^^^^^^^                 ^^^^^^^^^^^^^
  |
  = note: `#[warn(unused_imports)]` on by default

warning: unused imports: `compactsize_length` and `compactsize_write`
 --> /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/translations/project_2/src/psbt.rs:4:5
  |
4 |     compactsize_length, compactsize_peek_length, compactsize_read, compactsize_write,
  |     ^^^^^^^^^^^^^^^^^^                                             ^^^^^^^^^^^^^^^^^

error[E0502]: cannot borrow `*dest` as immutable because it is also borrowed as mutable
   --> /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/translations/project_2/src/psbt.rs:375:42
    |
375 |     let dest = &mut dest[..dest_size.min(dest.len())];
    |                     ---------------------^^^^--------
    |                     |   |                |
    |                     |   |                immutable borrow occurs here
    |                     |   mutable borrow later used here
    |                     mutable borrow occurs here
    |
help: try adding a local storing this...
   --> /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/translations/project_2/src/psbt.rs:375:42
    |
375 |     let dest = &mut dest[..dest_size.min(dest.len())];
    |                                          ^^^^^^^^^^
help: ...and then using that local here
   --> /Users/oscar/Dev/UNI/CS598JBR-Team-17/MP4/translations/project_2/src/psbt.rs:375:25
    |
375 |     let dest = &mut dest[..dest_size.min(dest.len())];
    |                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some errors have detailed explanations: E0432, E0502.
For more information about an error, try `rustc --explain E0432`.
warning: `libpsbt` (lib) generated 2 warnings
error: could not compile `libpsbt` (lib) due to 2 previous errors; 2 warnings emitted



```

## Current state of the editable Rust files
### src/base64.rs (105 lines)
```rust
#![forbid(unsafe_code)]
const BASE64_TABLE: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
const BASE62_TABLE: &[u8; 62] = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

/// Shared encoder mirroring the C `base_encode`. A table index outside the
/// table (the C code reads the NUL terminator or past it) is reported as failure.
fn base_encode(src: &[u8], out: &mut [u8], table: &[u8]) -> Option<usize> {
    // 4 output bytes per 3-byte block, plus the nul terminator.
    let olen = src.len() * 4 / 3 + 4 + 1;
    if olen > out.len() {
        return None;
    }
    let sym = |v: u8| table.get(usize::from(v)).copied();
    let mut enc = Vec::with_capacity(olen);
    let mut chunks = src.chunks_exact(3);
    for c in &mut chunks {
        let (a, b, d) = (c[0], c[1], c[2]);
        enc.push(sym(a >> 2)?);
        enc.push(sym(((a & 0x03) << 4) | (b >> 4))?);
        enc.push(sym(((b & 0x0f) << 2) | (d >> 6))?);
        enc.push(sym(d & 0x3f)?);
    }
    match *chunks.remainder() {
        [a] => {
            enc.push(sym(a >> 2)?);
            enc.push(sym((a & 0x03) << 4)?);
            enc.extend_from_slice(b"==");
        }
        [a, b] => {
            enc.push(sym(a >> 2)?);
            enc.push(sym(((a & 0x03) << 4) | (b >> 4))?);
            enc.push(sym((b & 0x0f) << 2)?);
            enc.push(b'=');
        }
        _ => {}
    }
    let n = enc.len();
    out[..n].copy_from_slice(&enc);
    out[n] = 0;
    Some(n)
}

/// Encode the given source bytes into base62. Returns the number of written bytes on success.
pub fn base62_encode(src: &[u8], out: &mut [u8]) -> Option<usize> {
    base_encode(src, out, BASE62_TABLE)
}

/// Encode the given source bytes into base64. Returns the number of written bytes on success.
pub fn base64_encode(src: &[u8], out: &mut [u8]) -> Option<usize> {
    base_encode(src, out, BASE64_TABLE)
}

/// Decode the given base64-encoded source bytes. Returns the number of decoded bytes on success.
pub fn base64_decode(src: &[u8], out: &mut [u8]) -> Option<usize> {
    let mut dtable = [0x80u8; 256];
    for (i, &c) in BASE64_TABLE.iter().enumerate() {
        dtable[usize::from(c)] = i as u8;
    }
    dtable[usize::from(b'=')] = 0;

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

    let mut pos = 0usize;
    let mut block = [0u8; 4];
    let mut n = 0usize;
    let mut pad = 0usize;
    for &c in src {
        let tmp = dtable[usize::from(c)];
        if tmp == 0x80 {
            continue;
        }
        if c == b'=' {
            pad += 1;
        }
        block[n] = tmp;
        n += 1;
        if n == 4 {
            out[pos] = (block[0] << 2) | (block[1] >> 4);
            out[pos + 1] = (block[1] << 4) | (block[2] >> 2);
            out[pos + 2] = (block[2] << 6) | block[3];
            pos += 3;
            n = 0;
            if pad > 0 {
                match pad {
                    1 => pos -= 1,
                    2 => pos -= 2,
                    _ => return None,
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

### src/psbt.rs (390 lines)
```rust
#![forbid(unsafe_code)]
use crate::base64::{base62_encode, base64_decode, base64_encode};
use crate::compactsize::{
    compactsize_length, compactsize_peek_length, compactsize_read, compactsize_write,
};
use crate::tx::*;
use std::fmt;
use std::sync::{Mutex, PoisonError};

// Common constant from common.h
pub const MAX_SERIALIZE_SIZE: u32 = 0x02000000;

/// Last error message, the Rust counterpart of the C global `psbt_errmsg`.
static LAST_ERR: Mutex<&'static str> = Mutex::new("psbt error");

fn set_err(msg: &'static str) {
    *LAST_ERR.lock().unwrap_or_else(PoisonError::into_inner) = msg;
}

fn read_err<T>(msg: &'static str) -> Result<T, PsbtResult> {
    set_err(msg);
    Err(PsbtResult::ReadError)
}

// --- Enum definitions ---
#[derive(Debug, PartialEq, Eq)]
pub enum PsbtResult { Ok, CompactReadError, ReadError, WriteError, InvalidState, NotImplemented, OobWrite }

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
pub enum PsbtEncoding { Hex, Base64, Base62, Protobuf }

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
pub enum PsbtOutputType { RedeemScript = 0, WitnessScript = 1, Bip32Derivation = 2 }

#[derive(Debug, PartialEq, Eq, Clone)]
pub enum PsbtScope { Global, Inputs, Outputs }

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtState { Init = 2, Global, Inputs, InputsNew, Outputs, OutputsNew, Finalized }

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtElemType { Record, TxElem }

#[derive(Debug, PartialEq, Eq)]
pub enum PsbtTxElemType { TxIn, TxOut, Tx, WitnessItem }

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

/// Read a compactsize at `*pos`, advancing the cursor past it.
fn read_compact(data: &[u8], pos: &mut usize) -> Result<u64, PsbtResult> {
    let rest = data.get(*pos..).ok_or(PsbtResult::ReadError)?;
    let first = *rest.first().ok_or(PsbtResult::ReadError)?;
    let (val, res) = compactsize_read(rest);
    if res != PsbtResult::Ok {
        set_err("compactsize_read: non-canonical or truncated compactsize");
        return Err(res);
    }
    *pos += compactsize_peek_length(first) as usize;
    Ok(val)
}

/// Take `len` bytes at `*pos`, advancing the cursor past them.
fn read_bytes<'a>(data: &'a [u8], pos: &mut usize, len: u64) -> Result<&'a [u8], PsbtResult> {
    let end = usize::try_from(len)
        .ok()
        .and_then(|n| pos.checked_add(n))
        .filter(|&e| e <= data.len());
    let Some(end) = end else {
        set_err("psbt_read: record size too large");
        return Err(PsbtResult::ReadError);
    };
    let bytes = data.get(*pos..end).ok_or(PsbtResult::ReadError)?;
    *pos = end;
    Ok(bytes)
}

fn byte_at(data: &[u8], pos: usize) -> Result<u8, PsbtResult> {
    match data.get(pos) {
        Some(&b) => Ok(b),
        None => read_err("psbt_read: unexpected end of psbt data"),
    }
}

/// Read one key/value record at `*pos` (C psbt_read_record).
fn read_record(data: &[u8], pos: &mut usize, scope: PsbtScope) -> Result<PsbtRecord, PsbtResult> {
    let key_with_type = read_compact(data, pos)?;
    let key_bytes = read_bytes(data, pos, key_with_type)?;
    let Some((&record_type, key)) = key_bytes.split_first() else {
        return read_err("psbt_read: zero-length key");
    };
    let val_len = read_compact(data, pos)?;
    let val = read_bytes(data, pos, val_len)?;
    Ok(PsbtRecord {
        record_type,
        key: key.to_vec(),
        val: val.to_vec(),
        scope,
    })
}

/// Walk the embedded transaction, forwarding every element to the handler
/// and counting inputs and outputs (C tx_counter).
fn forward_tx(
    tx: &[u8],
    index: i32,
    handler: Option<PsbtElemHandler>,
    user_data: &mut dyn std::any::Any,
) -> Result<(usize, usize), PsbtResult> {
    let mut counts = (0usize, 0usize);
    parse_tx(tx, |txelem| {
        match txelem {
            PsbtTxElem::TxIn(_) => counts.0 += 1,
            PsbtTxElem::TxOut(_) => counts.1 += 1,
            _ => {}
        }
        if let Some(h) = handler {
            let mut elem = PsbtElem::TxElem { index, txelem };
            h(&mut elem, user_data);
        }
    })?;
    Ok(counts)
}

/// Parse the PSBT body after the buffer has been loaded (C psbt_read loop).
fn read_body(
    psbt: &mut Psbt,
    data: &[u8],
    elem_handler: Option<PsbtElemHandler>,
    user_data: &mut dyn std::any::Any,
) -> Result<(), PsbtResult> {
    let end = data.len();
    let mut pos = 0usize;
    let mut kvs = 0usize;
    // (inputs, outputs) announced by the global unsigned transaction.
    let mut counts = (0usize, 0usize);

    while psbt.state != PsbtState::Finalized && pos <= end {
        match psbt.state {
            PsbtState::Init => {
                if data.get(pos..pos + 4) != Some(PSBT_MAGIC.as_slice()) {
                    return read_err("psbt_read: invalid magic header");
                }
                pos += 4;
                if byte_at(data, pos)? != 0xff {
                    return read_err("psbt_read: no 0xff found after magic");
                }
                pos += 1;
                psbt.state = PsbtState::Global;
            }
            PsbtState::Global | PsbtState::Inputs | PsbtState::Outputs => {
                if byte_at(data, pos)? == 0 {
                    match psbt.state {
                        PsbtState::Global => psbt.state = PsbtState::InputsNew,
                        PsbtState::Inputs => {
                            kvs += 1;
                            psbt.state = if kvs >= counts.0 {
                                kvs = 0;
                                PsbtState::OutputsNew
                            } else {
                                PsbtState::InputsNew
                            };
                        }
                        PsbtState::Outputs => {
                            kvs += 1;
                            psbt.state = if kvs >= counts.1 {
                                PsbtState::Finalized
                            } else {
                                PsbtState::OutputsNew
                            };
                        }
                        _ => {}
                    }
                } else {
                    let scope = match psbt.state {
                        PsbtState::Inputs => PsbtScope::Inputs,
                        PsbtState::Outputs => PsbtScope::Outputs,
                        _ => PsbtScope::Global,
                    };
                    let rec = read_record(data, &mut pos, scope)?;
                    if psbt.state == PsbtState::Global
                        && rec.record_type == PsbtGlobalType::UnsignedTx as u8
                    {
                        counts = forward_tx(&rec.val, kvs as i32, elem_handler, user_data)?;
                    }
                    let mut elem = PsbtElem::Record {
                        index: kvs as i32,
                        record: rec,
                    };
                    if let Some(handler) = elem_handler {
                        handler(&mut elem, user_data);
                    }
                    if let PsbtElem::Record { record, .. } = elem {
                        psbt.records.push(record);
                    }
                }
            }
            PsbtState::InputsNew | PsbtState::OutputsNew => {
                if byte_at(data, pos)? != 0 {
                    return read_err("psbt_read: expected null byte between record sets");
                }
                pos += 1;
                psbt.state = if psbt.state == PsbtState::InputsNew {
                    PsbtState::Inputs
                } else {
                    PsbtState::Outputs
                };
            }
            PsbtState::Finalized => break,
        }
    }

    if psbt.state != PsbtState::Finalized {
        set_err("psbt_read: invalid psbt");
        return Err(PsbtResult::InvalidState);
    }
    if byte_at(data, pos)? != 0 {
        return read_err("psbt_read: expected null byte at end of psbt");
    }
    psbt.write_pos = pos + 1;
    Ok(())
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
        set_err("psbt_read: psbt not initialized, use psbt_init first");
        return PsbtResult::InvalidState;
    }
    if src_size > psbt.data_capacity {
        set_err("psbt_read: read buffer is larger than psbt capacity");
        return PsbtResult::OobWrite;
    }
    let Some(data) = src.get(..src_size) else {
        set_err("psbt_read: length larger than backing slice");
        return PsbtResult::ReadError;
    };
    psbt.data = data.to_vec();
    psbt.data_capacity = src_size;
    psbt.records.clear();
    psbt.write_pos = 0;

    match read_body(psbt, data, elem_handler, user_data) {
        Ok(()) => PsbtResult::Ok,
        Err(res) => res,
    }
}

fn hex_val(c: u8) -> Option<u8> {
    match c {
        b'0'..=b'9' => Some(c - b'0'),
        b'a'..=b'f' => Some(c - b'a' + 10),
        b'A'..=b'F' => Some(c - b'A' + 10),
        _ => None,
    }
}

fn hex_decode(src: &[u8], dest: &mut [u8], psbt_len: &mut usize) -> PsbtResult {
    if src.len() % 2 != 0 {
        set_err("psbt_decode: invalid hex string");
        return PsbtResult::ReadError;
    }
    let n = src.len() / 2;
    if dest.len() < n {
        set_err("psbt_decode: dest_size must be at least half the size of src_size");
        return PsbtResult::ReadError;
    }
    for (out, pair) in dest.iter_mut().zip(src.chunks_exact(2)) {
        match (hex_val(pair[0]), hex_val(pair[1])) {
            (Some(hi), Some(lo)) => *out = (hi << 4) | lo,
            _ => {
                set_err("psbt_decode: invalid hex string");
                return PsbtResult::ReadError;
            }
        }
    }
    *psbt_len = n;
    PsbtResult::Ok
}

/// Decode a hex or base64 PSBT string into dest.
pub fn psbt_decode(
    src: &str,
    _src_size: usize,
    dest: &mut [u8],
    dest_size: usize,
    psbt_len: &mut usize,
) -> PsbtResult {
    let Some(bytes) = src.as_bytes().get(.._src_size) else {
        set_err("psbt_decode: source length larger than source string");
        return PsbtResult::ReadError;
    };
    if bytes.len() < 5 {
        set_err("psbt_decode: psbt too small");
        return PsbtResult::ReadError;
    }
    let dest = &mut dest[..dest_size.min(dest.len())];
    if bytes.starts_with(b"cHNid") {
        return match base64_decode(bytes, dest) {
            Some(n) => {
                *psbt_len = n;
                PsbtResult::Ok
            }
            None => {
                set_err("psbt_decode: base64 decode failure");
                PsbtResult::ReadError
            }
        };
    }
    hex_decode(bytes, dest, psbt_len)
}

```

### src/tx.rs (131 lines)
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

fn take_u32(data: &[u8], pos: &mut usize) -> Result<u32, PsbtResult> {
    Ok(u32::from_le_bytes(take_array::<4>(data, pos)?))
}

/// Read a compactsize integer at `pos`, advancing the cursor past it.
fn take_compact(data: &[u8], pos: &mut usize) -> Result<u64, PsbtResult> {
    let rest = data.get(*pos..).ok_or(PsbtResult::ReadError)?;
    let first = *rest.first().ok_or(PsbtResult::ReadError)?;
    let (val, res) = compactsize_read(rest);
    if res != PsbtResult::Ok {
        return Err(res);
    }
    *pos += compactsize_peek_length(first) as usize;
    Ok(val)
}

/// Walk a serialized transaction, emitting its inputs, outputs and the tx itself.
pub(crate) fn parse_tx<F: FnMut(PsbtTxElem)>(data: &[u8], mut emit: F) -> Result<(), PsbtResult> {
    let mut pos = 0;
    let version = take_u32(data, &mut pos)?;

    let n_in = take_compact(data, &mut pos)?;
    for _ in 0..n_in {
        let txid = take(data, &mut pos, 32)?.to_vec();
        let index = take_u32(data, &mut pos)?;
        let script_len = take_compact(data, &mut pos)?;
        let script = take(data, &mut pos, script_len as usize)?.to_vec();
        let sequence_number = take_u32(data, &mut pos)?;
        emit(PsbtTxElem::TxIn(PsbtTxIn {
            txid,
            index,
            script,
            sequence_number,
        }));
    }

    let n_out = take_compact(data, &mut pos)?;
    for _ in 0..n_out {
        let amount = u64::from_le_bytes(take_array::<8>(data, &mut pos)?);
        let script_len = take_compact(data, &mut pos)?;
        let script = take(data, &mut pos, script_len as usize)?.to_vec();
        emit(PsbtTxElem::TxOut(PsbtTxOut { amount, script }));
    }

    let lock_time = take_u32(data, &mut pos)?;
    if pos != data.len() {
        return Err(PsbtResult::ReadError);
    }
    emit(PsbtTxElem::Tx(PsbtTx {
        version,
        lock_time,
    }));
    Ok(())
}



/// Parse a Bitcoin transaction, forwarding every element to `handler`.
pub fn psbt_btc_tx_parse(
    tx: &[u8],
    tx_size: usize,
    user_data: &mut dyn std::any::Any,
    handler: Option<PsbtTxElemHandler>,
) -> PsbtResult {
    let tx = &tx[..tx_size.min(tx.len())];
    let result = parse_tx(tx, |mut elem| {
        if let Some(h) = handler {
            h(&mut elem, &mut *user_data);
        }
    });
    match result {
        Ok(()) => PsbtResult::Ok,
        Err(res) => res,
    }
}

```

Reply using the block protocol. Update your `<notes>` so they stay accurate.
