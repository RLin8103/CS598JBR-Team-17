# Project: libpsbt

Translate the C project `libpsbt` to Rust. The Rust crate already exists in your workspace. The module files declared by `src/lib.rs` are copies of the interface stubs, with `unimplemented!()` bodies that you must replace by real implementations.

## Workspace layout
crate (editable area: src/*.rs):
  .gitignore  (8 bytes)
  Cargo.lock  (1777 bytes)
  Cargo.toml  (188 bytes)
  src/base64.rs  (566 bytes)
  src/bin/test.rs  (8853 bytes)
  src/cli.rs  (41 bytes)
  src/compactsize.rs  (338 bytes)
  src/interfaces/base64.rs  (566 bytes)
  src/interfaces/cli.rs  (41 bytes)
  src/interfaces/compactsize.rs  (338 bytes)
  src/interfaces/psbt.rs  (5932 bytes)
  src/interfaces/tx.rs  (1086 bytes)
  src/lib.rs  (76 bytes)
  src/psbt.rs  (5932 bytes)
  src/tx.rs  (1086 bytes)
c_source (read-only original C project):
  c_source/.dir-locals.el  (193 bytes)
  c_source/.gitignore  (40 bytes)
  c_source/.travis.yml  (67 bytes)
  c_source/CONTRIBUTING  (90 bytes)
  c_source/COPYING  (1071 bytes)
  c_source/Makefile  (942 bytes)
  c_source/README.md  (433 bytes)
  c_source/base64.c  (4143 bytes)
  c_source/base64.h  (715 bytes)
  c_source/cli.c  (3953 bytes)
  c_source/common.h  (331 bytes)
  c_source/compactsize.c  (2571 bytes)
  c_source/compactsize.h  (301 bytes)
  c_source/psbt.c  (18215 bytes)
  c_source/psbt.h  (3243 bytes)
  c_source/result.h  (231 bytes)
  c_source/test.c  (12861 bytes)
  c_source/tx.c  (4513 bytes)
  c_source/tx.h  (1087 bytes)

## Toolchain and checks run after every iteration
- `cargo +nightly-2025-05-13 build --all-targets`
- `cargo +nightly-2025-05-13 test --no-fail-fast`
- `cargo +nightly-2025-05-13 clippy --all-targets --all-features -- -W clippy::<group>` for correctness, style, complexity and perf (reported separately)
- unsafe metrics: unsafe lines, unsafe calls, unsafe casts, pointer arithmetic

## Specification: Rust interface (do not change public items)
### src/interfaces/base64.rs (12 lines)
```rust
/// Encode the given source bytes into base62. Returns the number of written bytes on success.
pub fn base62_encode(_src: &[u8], _out: &mut [u8]) -> Option<usize> {
    unimplemented!()
}
/// Encode the given source bytes into base64. Returns the number of written bytes on success.
pub fn base64_encode(_src: &[u8], _out: &mut [u8]) -> Option<usize> {
    unimplemented!()
}
/// Decode the given base64-encoded source bytes. Returns the number of decoded bytes on success.
pub fn base64_decode(_src: &[u8], _out: &mut [u8]) -> Option<usize> {
    unimplemented!()
}
```

### src/interfaces/cli.rs (3 lines)
```rust
fn main() -> i32 {
    unimplemented!()
}
```

### src/interfaces/compactsize.rs (13 lines)
```rust
use crate::psbt::PsbtResult;
pub fn compactsize_read(_data: &[u8]) -> (u64, PsbtResult) {
    unimplemented!()
}
pub fn compactsize_length(_data: u64) -> u32 {
    unimplemented!()
}
pub fn compactsize_write(_dest: &mut [u8], _size: u64) {
    unimplemented!()
}
pub fn compactsize_peek_length(_chsize: u8) -> u32 {
    unimplemented!()
}
```

### src/interfaces/psbt.rs (220 lines)
```rust
use crate::tx::*;
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
        write!(f, "{:?}", self)
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
    /// (The C field “type” is renamed to avoid conflict with the Rust keyword.)
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
    unimplemented!()
}
/// Decode a hex string into dest. (This simple implementation uses the `hex` crate.)
pub fn psbt_decode(
    src: &str,
    _src_size: usize,
    dest: &mut [u8],
    dest_size: usize,
    psbt_len: &mut usize,
) -> PsbtResult {
    unimplemented!()
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
    unimplemented!()
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
    unimplemented!()
}
/// Return the last error message.
pub fn psbt_geterr() -> &'static str {
    PSBT_ERRMSG
}
/// Convert a PSBT state to a human–readable string.
pub fn psbt_state_tostr(state: PsbtState) -> &'static str {
    unimplemented!()
}
/// Return a string for a record type and scope.
pub fn psbt_type_tostr(record_type: u8, scope: PsbtScope) -> &'static str {
    unimplemented!()
}
/// Return a string for a psbt_txelem type.
pub fn psbt_txelem_type_tostr(txelem_type: PsbtTxElemType) -> &'static str {
    unimplemented!()
}
pub fn psbt_global_type_tostr(gt: PsbtGlobalType) -> &'static str {
    unimplemented!()
}
pub fn psbt_output_type_tostr(ot: PsbtOutputType) -> &'static str {
    unimplemented!()
}
pub fn psbt_input_type_tostr(it: PsbtInputType) -> &'static str {
    unimplemented!()
}
/// Write a global record into the PSBT.
pub fn psbt_write_global_record(psbt: &mut Psbt, rec: &PsbtRecord) -> PsbtResult {
    unimplemented!()
}
/// Write an input record into the PSBT.
pub fn psbt_write_input_record(psbt: &mut Psbt, rec: &PsbtRecord) -> PsbtResult {
    unimplemented!()
}
/// Write an output record into the PSBT.
pub fn psbt_write_output_record(psbt: &mut Psbt, rec: &PsbtRecord) -> PsbtResult {
    unimplemented!()
}
/// Create a new input record set.
pub fn psbt_new_input_record_set(_psbt: &mut Psbt) -> PsbtResult {
    unimplemented!()
}
/// Create a new output record set.
pub fn psbt_new_output_record_set(psbt: &mut Psbt) -> PsbtResult {
    unimplemented!()
}
/// Initialize a PSBT using the given destination buffer.
pub fn psbt_init(psbt: &mut Psbt, _dest: &mut [u8], dest_size: usize) -> PsbtResult {
    unimplemented!()
}
/// Print the PSBT (only succeeds after finalization).
pub fn psbt_print(psbt: &Psbt, stream: &mut dyn std::io::Write) -> PsbtResult {
    unimplemented!()
}
/// Finalize the PSBT.
pub fn psbt_finalize(psbt: &mut Psbt) -> PsbtResult {
    unimplemented!()
}
```

### src/interfaces/tx.rs (42 lines)
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

## Tests (read-only, they are part of the specification)
### src/bin/test.rs (196 lines)
```rust
use libpsbt::psbt::*;

/// Utility function to print a byte slice as a hex string.
fn hex_print(data: &[u8]) {
    for byte in data {
        print!("{:02x}", byte);
    }
    println!();
}

// Test vectors (taken from test.c)
const PSBT_HEX: &str = "70736274ff01009a020000000258e87a21b56daf0c23be8e7070456c336f7cbaa5c8757924f545887bb2abdd750000000000ffffffff838d0427d0ec650a68aa46bb0b098aea4422c071b2ca78352a077959d07cea1d0100000000ffffffff0270aaf00800000000160014d85c2b71d0060b09c9886aeb815e50991dda124d00e1f5050000000016001400aea9a2e5f0f876a588df5546e8742d1d87008f00000000000100bb0200000001aad73931018bd25f84ae400b68848be09db706eac2ac18298babee71ab656f8b0000000048473044022058f6fc7c6a33e1b31548d481c826c015bd30135aad42cd67790dab66d2ad243b02204a1ced2604c6735b6393e5b41691dd78b00f0c5942fb9f751856faa938157dba01feffffff0280f0fa020000000017a9140fb9463421696b82c833af241c78c17ddbde493487d0f20a270100000017a91429ca74f8a08f81999428185c97b5d852e4063f6187650000000104475221029583bf39ae0a609747ad199addd634fa6108559d6c5cd39b4c2183f1ab96e07f2102dab61ff49a14db6a7d02b0cd1fbb78fc4b18312b5b4e54dae4dba2fbfef536d752ae2206029583bf39ae0a609747ad199addd634fa6108559d6c5cd39b4c2183f1ab96e07f10d90c6a4f000000800000008000000080220602dab61ff49a14db6a7d02b0cd1fbb78fc4b18312b5b4e54dae4dba2fbfef536d710d90c6a4f0000008000000080010000800001012000c2eb0b0000000017a914b7f5faf40e3d40a5a459b1db3535f2b72fa921e88701042200208c2353173743b595dfb4a07b72ba8e42e3797da74e87fe7d9d7497e3b2028903010547522103089dc10c7ac6db54f91329af617333db388cead0c231f723379d1b99030b02dc21023add904f3d6dcf59ddb906b0dee23529b7ffb9ed50e5e86151926860221f0e7352ae2206023add904f3d6dcf59ddb906b0dee23529b7ffb9ed50e5e86151926860221f0e7310d90c6a4f000000800000008003000080220603089dc10c7ac6db54f91329af617333db388cead0c231f723379d1b99030b02dc10d90c6a4f00000080000000800200008000220203a9a4c37f5996d3aa25dbac6b570af0650394492942460b354753ed9eeca5877110d90c6a4f000000800000008004000080002202027f6399757d2eff55a136ad02c684b1838b6556e5f1b6b34282a94b6b5005109610d90c6a4f00000080000000800500008000";
const TRANSACTION: &[u8] = &[
    0x02, 0x00, 0x00, 0x00, 0x02, 0x2e, 0x8c, 0x7d, 0x8d, 0x37, 0xc4, 0x27, 0xe0, 0x60, 0xec, 0x00,
    0x2e, 0xc1, 0xc2, 0xbc, 0x30, 0x19, 0x6f, 0xc2, 0xf7, 0x5d, 0x6a, 0x88, 0x44, 0xcb, 0xc0, 0x36,
    0x51, 0xc0, 0x81, 0x43, 0x0a, 0x01, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0x96, 0xa0,
    0x4e, 0x0c, 0xc6, 0x36, 0xf3, 0x77, 0x93, 0x3e, 0x3d, 0x93, 0xac, 0xcc, 0x62, 0x7f, 0xaa, 0xcd,
    0xbc, 0xdb, 0x5a, 0x96, 0x24, 0xdf, 0x1b, 0x49, 0x0b, 0xd0, 0x45, 0xf2, 0x4d, 0x2c, 0x00, 0x00,
    0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0x01, 0xe0, 0x2b, 0xe5, 0x0e, 0x00, 0x00, 0x00, 0x00,
    0x17, 0xa9, 0x14, 0xb5, 0x3b, 0xb0, 0xdc, 0x1d, 0xb8, 0xc8, 0xd8, 0x03, 0xe3, 0xe3, 0x9f, 0x78,
    0x4d, 0x42, 0xe4, 0x73, 0x7f, 0xfa, 0x0d, 0x87, 0x00, 0x00, 0x00, 0x00,
];
const REDEEM_SCRIPT_A: &[u8] = &[
    0x52, 0x21, 0x03, 0xc8, 0x72, 0x7c, 0xe3, 0x5f, 0x1c, 0x93, 0xeb, 0x0b, 0xe2, 0x14, 0x06, 0xee,
    0x9a, 0x92, 0x3c, 0x89, 0x21, 0x9f, 0xe9, 0xc9, 0xe8, 0x50, 0x4c, 0x83, 0x14, 0xa6, 0xa2, 0x2d,
    0x12, 0x95, 0xc0, 0x21, 0x03, 0xc7, 0x4d, 0xc7, 0x10, 0xc4, 0x07, 0xd7, 0xdb, 0x6e, 0x04, 0x1e,
    0xe2, 0x12, 0xd9, 0x85, 0xcd, 0x28, 0x26, 0xd9, 0x3f, 0x80, 0x6e, 0xd4, 0x49, 0x12, 0xb9, 0xa1,
    0xda, 0x69, 0x1c, 0x97, 0x73, 0x52, 0xae,
];
const REDEEM_SCRIPT_B: &[u8] = &[
    0x00, 0x20, 0xa8, 0xf4, 0x44, 0x67, 0xbf, 0x17, 0x1d, 0x51, 0x49, 0x91, 0x53, 0xe0, 0x1c, 0x0b,
    0xd6, 0x29, 0x11, 0x09, 0xfc, 0x38, 0xbd, 0x21, 0xb3, 0xc3, 0x22, 0x4c, 0x9d, 0xc6, 0xb5, 0x75,
    0x90, 0xdf,
];
const EMPTY_INPUTS: &str =
    "cHNidP8BACoCAAAAAAGA8PoCAAAAABepFCufG2xKKzFR7+3XGjiAZPO/VDBkhwAAAAAAAA==";

/// Transpiled from test.c: tests a PSBT write/read/finalize cycle.
#[test]
fn test_vector() {
    let mut psbt_instance = Psbt::new(1024);
    let mut buffer = vec![0u8; 1024];

    // psbt_init
    let res = psbt_init(&mut psbt_instance, &mut buffer, 1024);
    assert_eq!(res, PsbtResult::Ok);

    // psbt_write_input_record should fail in INIT state.
    let dummy_record = PsbtRecord {
        record_type: 0,
        key: vec![],
        val: vec![],
        scope: PsbtScope::Inputs,
    };
    let res = psbt_write_input_record(&mut psbt_instance, &dummy_record);
    assert_eq!(res, PsbtResult::InvalidState);

    // Write global record.
    let global_record = PsbtRecord {
        record_type: 0, // PSBT_GLOBAL_UNSIGNED_TX
        key: vec![],
        val: TRANSACTION.to_vec(),
        scope: PsbtScope::Global,
    };
    let res = psbt_write_global_record(&mut psbt_instance, &global_record);
    assert_eq!(res, PsbtResult::Ok);

    // Write two input records (with redeem scripts).
    let input_record_a = PsbtRecord {
        record_type: 4, // PSBT_IN_REDEEM_SCRIPT
        key: vec![],
        val: REDEEM_SCRIPT_A.to_vec(),
        scope: PsbtScope::Inputs,
    };
    let res = psbt_write_input_record(&mut psbt_instance, &input_record_a);
    assert_eq!(res, PsbtResult::Ok);

    let input_record_b = PsbtRecord {
        record_type: 4, // PSBT_IN_REDEEM_SCRIPT
        key: vec![],
        val: REDEEM_SCRIPT_B.to_vec(),
        scope: PsbtScope::Inputs,
    };
    let res = psbt_write_input_record(&mut psbt_instance, &input_record_b);
    assert_eq!(res, PsbtResult::Ok);

    // Start new output record set.
    let res = psbt_new_output_record_set(&mut psbt_instance);
    assert_eq!(res, PsbtResult::Ok);

    // psbt_print should fail before finalization.
    let mut stdout = std::io::stdout();
    let res = psbt_print(&psbt_instance, &mut stdout);
    assert_eq!(res, PsbtResult::InvalidState);

    // Finalize the PSBT.
    let res = psbt_finalize(&mut psbt_instance);
    assert_eq!(res, PsbtResult::Ok);

    // Now psbt_print should succeed.
    let res = psbt_print(&psbt_instance, &mut stdout);
    assert_eq!(res, PsbtResult::Ok);
}

/// Transpiled from test.c: simulate reading a PSBT with a callback.
#[test]
fn read_test_vector() {
    let mut buf = vec![0u8; 2048];
    let mut intbuf = vec![0u8; 2048];
    let mut psbt_len = 0;
    let hexlen = PSBT_HEX.len();
    let mut psbt_instance = Psbt::new(2048);

    let res = psbt_decode(PSBT_HEX, hexlen, &mut buf, 2048, &mut psbt_len);
    assert_eq!(res, PsbtResult::Ok);

    let res = psbt_init(&mut psbt_instance, &mut intbuf, 2048);
    assert_eq!(res, PsbtResult::Ok);

    // The callback checks that the first element is a global record and the second is an input record.
    fn checker(elem: &mut PsbtElem, _ud: &mut dyn std::any::Any) {
        let mut step = 0;
        match elem {
            PsbtElem::Record { record, .. } => {
                match step {
                    0 => assert_eq!(record.record_type, 0), // PSBT_GLOBAL_UNSIGNED_TX
                    1 => assert_eq!(record.record_type, 0), // PSBT_IN_NON_WITNESS_UTXO (simulated as 0)
                    _ => {}
                }
            }
            _ => {}
        }
        step += 1;
    }
    let res = psbt_read(&buf, psbt_len, &mut psbt_instance, Some(checker), &mut ());
    assert_eq!(res, PsbtResult::Ok);
}

#[test]
/// Transpiled from test.c: a simple encode–decode test.
fn encode_decode_test() {
    let mut buf = vec![0u8; 2048];
    let mut intbuf = vec![0u8; 2048];
    let mut psbt_len = 0;
    let hexlen = PSBT_HEX.len();
    let mut psbt_instance = Psbt::new(2048);

    let res = psbt_decode(PSBT_HEX, hexlen, &mut intbuf, 2048, &mut psbt_len);
    assert_eq!(res, PsbtResult::Ok);
    // Expect decoded length to be half the hex string length.
    assert_eq!(psbt_len, hexlen / 2);

    let res = psbt_init(&mut psbt_instance, &mut intbuf, psbt_len);
    assert_eq!(res, PsbtResult::Ok);

    let res = psbt_read(&intbuf, psbt_len, &mut psbt_instance, None, &mut ());
    assert_eq!(res, PsbtResult::Ok);

    let mut out_len = 0;
    let res = psbt_encode(
        &psbt_instance,
        PsbtEncoding::Hex,
        &mut buf,
        2048,
        &mut out_len,
    );
    assert_eq!(res, PsbtResult::Ok);
    // Expect a null terminator so out_len equals hexlen + 1.
    assert_eq!(out_len, hexlen + 1);
    let encoded_str = String::from_utf8_lossy(&buf[..hexlen]);
    assert_eq!(encoded_str, PSBT_HEX);
}

/// Transpiled from test.c: a test for an “empty input” PSBT.
#[test]
fn empty_input_test() {
    let mut buf = vec![0u8; 2048];
    let mut psbt_len = 0;
    let mut psbt_instance = Psbt::new(2048);
    let buf_len = buf.len();
    let res = psbt_decode(
        EMPTY_INPUTS,
        EMPTY_INPUTS.len(),
        &mut buf,
        buf_len,
        &mut psbt_len,
    );
    assert_eq!(res, PsbtResult::Ok);

    let res = psbt_init(&mut psbt_instance, &mut buf, psbt_len);
    assert_eq!(res, PsbtResult::Ok);

    let res = psbt_read(&buf, psbt_len, &mut psbt_instance, None, &mut ());
    assert_eq!(res, PsbtResult::Ok);
}
pub fn main(){}
```

## Original C source (this is the behaviour to preserve)
### c_source/Makefile (55 lines)
```
NAME ?= libpsbt
SHLIB ?= $(NAME).so
BIN = psbt
STATICLIB ?= $(NAME).a
PREFIX ?= /usr/local

CFLAGS = -g -O1 -fpic -Wall -Werror -Wextra -std=c99 \
						-Wno-unused-function \
						-Wno-unused-parameter \
						-Wno-unused-variable \
						-Wno-cast-align \
						-Wno-padded

OBJS += psbt.o
OBJS += base64.o
OBJS += tx.o
OBJS += compactsize.o

SRCS=$(OBJS:.o=.c)

all: $(SHLIB) $(STATICLIB) $(BIN)

include $(OBJS:.o=.d)

%.d: %.c
	$(CC) -MM $(CFLAGS) $< > $@

$(BIN): $(OBJS) cli.c
	$(CC) $(CFLAGS) cli.c $(OBJS) -o $@

$(STATICLIB): $(OBJS)
	ar rcs $@ $(OBJS)

$(SHLIB): $(OBJS)
	$(CC) -shared -o $@ $(OBJS)

install: $(STATICLIB) $(SHLIB)
	install -d $(PREFIX)/lib $(PREFIX)/include
	install $(STATICLIB) $(SHLIB) $(PREFIX)/lib
	install psbt.h $(PREFIX)/include

check: test
	./test

test: test.c $(STATICLIB)
	$(CC) $(CFLAGS) test.c $(OBJS) -o $@

TAGS:
	etags *.c

clean:
	rm -f $(OBJS) $(SHLIB) $(BIN) $(STATICLIB) *.d*

.PHONY: TAGS

```

### c_source/README.md (26 lines)
```

# libpsbt

[![Build Status](https://travis-ci.org/jb55/libpsbt.svg)](https://travis-ci.org/jb55/libpsbt)

  C library for Partially Signed Bitcoin Transactions (bip174)

  This is a SAX-style parser/serializer. It allocates no memory during its
  operation.

## Progress

- [x] Serialization
- [x] Deserialization
- [ ] Validation
- [ ] Merging

## Installation

    $ make install PREFIX=out_dir

## Example

See [test.c](test.c)


```

### c_source/base64.c (170 lines)
```c
/*
 * Base64 encoding/decoding (RFC1341)
 * Copyright (c) 2005-2011, Jouni Malinen <j@w1.fi>
 *
 * This software may be distributed under the terms of the BSD license.
 * See README for more details.
 */

#include "base64.h"
#include <stdlib.h>
#include <string.h>
#include <assert.h>

static const unsigned char base64_table[65] =
	"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

static const unsigned char base62_table[] =
	"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

/**
 * base64_encode - Base64 encode
 * @src: Data to be encoded
 * @len: Length of the data to be encoded
 * @out_len: Pointer to output length variable, or %NULL if not used
 * Returns: Allocated buffer of out_len bytes of encoded data,
 * or %NULL on failure
 *
 * Caller is responsible for freeing the returned buffer. Returned buffer is
 * nul terminated to make it easier to use as a C string. The nul terminator is
 * not included in out_len.
 */

unsigned char * base_encode(const unsigned char *src, size_t len,
			    unsigned char *out, size_t out_capacity,
			    size_t *out_len, const unsigned char *base_table)
{
	unsigned char *pos;
	const unsigned char *end, *in;
	size_t olen;

	olen = len * 4 / 3 + 4; /* 3-byte blocks to 4-byte */
	olen++; /* nul termination */
	if (olen < len)
		return NULL; /* integer overflow */
	if (olen > out_capacity)
		return NULL; /* buffer overflow */
	if (out == NULL)
		return NULL;

	end = src + len;
	in = src;
	pos = out;
	while (end - in >= 3) {
		*pos++ = base_table[in[0] >> 2];
		*pos++ = base_table[((in[0] & 0x03) << 4) | (in[1] >> 4)];
		*pos++ = base_table[((in[1] & 0x0f) << 2) | (in[2] >> 6)];
		*pos++ = base_table[in[2] & 0x3f];
		in += 3;
	}

	if (end - in) {
		*pos++ = base_table[in[0] >> 2];
		if (end - in == 1) {
			*pos++ = base_table[(in[0] & 0x03) << 4];
			*pos++ = '=';
		} else {
			*pos++ = base_table[((in[0] & 0x03) << 4) |
					      (in[1] >> 4)];
			*pos++ = base_table[(in[1] & 0x0f) << 2];
		}
		*pos++ = '=';
	}

	*pos = '\0';
	if (out_len)
		*out_len = pos - out;
	return out;
}

unsigned char *
base64_encode(const unsigned char *src, size_t len, unsigned char *out,
	      size_t out_capacity, size_t *out_len) {
	return base_encode(src, len, out, out_capacity, out_len, base64_table);
}

unsigned char *
base62_encode(const unsigned char *src, size_t len, unsigned char *out,
	      size_t out_capacity, size_t *out_len) {
	return base_encode(src, len, out, out_capacity, out_len, base62_table);
}


/**
 * base64_decode - Base64 decode
 * @src: Data to be decoded
 * @len: Length of the data to be decoded
 * @out: Pointer to output buffer
 * @out_len: Pointer to output length variable
 * Returns: Allocated buffer of out_len bytes of decoded data,
 * or %NULL on failure
 *
 * Caller is responsible for freeing the returned buffer.
 */
unsigned char * base64_decode(const unsigned char *src, size_t len,
			      unsigned char *out, size_t out_capacity,
			      size_t *out_size)
{
	unsigned char dtable[256], *pos, block[4], tmp;
	size_t i, count, olen;
	int pad = 0;

	memset(dtable, 0x80, 256);
	for (i = 0; i < sizeof(base64_table) - 1; i++)
		dtable[base64_table[i]] = (unsigned char) i;
	dtable['='] = 0;

	count = 0;
	for (i = 0; i < len; i++) {
		if (dtable[src[i]] != 0x80)
			count++;
	}

	if (count == 0 || count % 4)
		return NULL;

	olen = count / 4 * 3;

	if (out_capacity < olen)
		return NULL;

	pos = out;
	if (out == NULL)
		return NULL;

	count = 0;
	for (i = 0; i < len; i++) {
		tmp = dtable[src[i]];
		if (tmp == 0x80)
			continue;

		if (src[i] == '=')
			pad++;
		block[count] = tmp;
		count++;
		if (count == 4) {
			*pos++ = (block[0] << 2) | (block[1] >> 4);
			assert((size_t)(pos - out) < out_capacity);
			*pos++ = (block[1] << 4) | (block[2] >> 2);
			assert((size_t)(pos - out) < out_capacity);
			*pos++ = (block[2] << 6) | block[3];
			assert((size_t)(pos - out) < out_capacity);
			count = 0;
			if (pad) {
				if (pad == 1)
					pos--;
				else if (pad == 2)
					pos -= 2;
				else {
					/* Invalid padding */
					return NULL;
				}
				break;
			}
		}
	}

	*out_size = pos - out;
	return out;
}

```

### c_source/base64.h (25 lines)
```c
/*
 * Base64 encoding/decoding (RFC1341)
 * Copyright (c) 2005, Jouni Malinen <j@w1.fi>
 *
 * This software may be distributed under the terms of the BSD license.
 * See README for more details.
 */

#ifndef BASE64_H
#define BASE64_H

#include <stddef.h>

unsigned char * base62_encode(const unsigned char *src, size_t len,
			      unsigned char *out, size_t out_capacity,
			      size_t *out_len);
unsigned char * base64_encode(const unsigned char *src, size_t len,
			      unsigned char *out, size_t out_capacity,
			      size_t *out_len);
unsigned char * base64_decode(const unsigned char *src, size_t len,
			      unsigned char *out, size_t out_capacity,
			      size_t *out_size);

#endif /* BASE64_H */

```

### c_source/cli.c (126 lines)
```c

#include "psbt.h"
#include "string.h"
#include <inttypes.h>

#define ARRAY_SIZE(arr) (sizeof(arr) / sizeof(arr[0]))

const char *psbt_example = "70736274ff0100a00200000002ab0949a08c5af7c49b8212f417e2f15ab3f5c33dcf153821a8139f877a5b7be40000000000feffffffab0949a08c5af7c49b8212f417e2f15ab3f5c33dcf153821a8139f877a5b7be40100000000feffffff02603bea0b000000001976a914768a40bbd740cbe81d988e71de2a4d5c71396b1d88ac8e240000000000001976a9146f4620b553fa095e721b9ee0efe9fa039cca459788ac00000000000100df0200000001268171371edff285e937adeea4b37b78000c0566cbb3ad64641713ca42171bf6000000006a473044022070b2245123e6bf474d60c5b50c043d4c691a5d2435f09a34a7662a9dc251790a022001329ca9dacf280bdf30740ec0390422422c81cb45839457aeb76fc12edd95b3012102657d118d3357b8e0f4c2cd46db7b39f6d9c38d9a70abcb9b2de5dc8dbfe4ce31feffffff02d3dff505000000001976a914d0c59903c5bac2868760e90fd521a4665aa7652088ac00e1f5050000000017a9143545e6e33b832c47050f24d3eeb93c9c03948bc787b32e13000001012000e1f5050000000017a9143545e6e33b832c47050f24d3eeb93c9c03948bc787010416001485d13537f2e265405a34dbafa9e3dda01fb8230800220202ead596687ca806043edc3de116cdf29d5e9257c196cd055cf698c8d02bf24e9910b4a6ba670000008000000080020000800022020394f62be9df19952c5587768aeb7698061ad2c4a25c894f47d8c162b4d7213d0510b4a6ba6700000080010000800200008000";

void print_json_rec(void *user_data, struct psbt_record *rec) {
	printf("{\n    ");
	printf("\"tx\": \"");

	/* for (int i = 0; i < rec->) */

	printf("\"type\": \"%s\"", psbt_type_tostr(rec->type, rec->scope));
}

static void txid_print(unsigned char *data) {
	for (int i = 31; i >= 0; i--)
		printf("%02x", data[i]);
}

static void hex_print(unsigned char *data, size_t len) {
	for (size_t i = 0; i < len; ++i)
		printf("%02x", data[i]);
}

void print_rec(struct psbt_elem *elem) {
	const char *type_str = NULL;
	struct psbt_record *rec = NULL;
	struct psbt_txelem *txelem = NULL;
	struct psbt_txin *txin = NULL;
	struct psbt_txout *txout = NULL;
	struct psbt_tx *tx = NULL;

	switch (elem->type) {
	case PSBT_ELEM_RECORD:
		rec = elem->elem.rec;
		type_str = psbt_type_tostr(rec->type, rec->scope);
		printf("%s\t%d ", type_str, elem->index);
		if (rec->key_size != 0) {
			hex_print(rec->key, rec->key_size);
			printf(" ");
		}
		hex_print(rec->val, rec->val_size);
		printf("\n");
		break;
	case PSBT_ELEM_TXELEM:
		txelem = elem->elem.txelem;
		type_str = psbt_txelem_type_tostr(txelem->elem_type);
		printf("%s\t", type_str);
		switch (txelem->elem_type) {
		case PSBT_TXELEM_TXIN:
			txin = txelem->elem.txin;
			txid_print(txin->txid);
			printf(" ind:%d", txin->index);
			printf(" seq:%u", txin->sequence_number);
			if (txin->script_len) {
				printf(" ");
				hex_print(txin->script, txin->script_len);
			}
			printf("\n");
			break;
		case PSBT_TXELEM_TXOUT:
			txout = txelem->elem.txout;
			if (txout->script_len) {
				hex_print(txout->script, txout->script_len);
				printf(" ");
			}
			printf("amount:%"PRIu64"\n", txout->amount);
			break;
		case PSBT_TXELEM_TX:
			tx = txelem->elem.tx;
			printf("ver:%u locktime:%u\n", tx->version, tx->lock_time);
			break;
		default:
			break;
		}
	}
}

int usage() {
	printf ("usage: psbt <psbt>\n");
	return 1;
}

#define CHECK(res) \
	if ((res) != PSBT_OK) {					\
		printf("error (%d): %s. last_state = %s\n", res, psbt_errmsg, \
		       psbt_state_tostr(psbt.state));			\
		return 1;					\
	}


int main(int argc, char *argv[])
{
	struct psbt psbt;
	static unsigned char buffer[4096];
	enum psbt_result res;
	size_t psbt_len;
	size_t out_len;

	if (argc < 2)
		return usage();

	size_t psbt_hex_len = strlen(argv[1]);

	psbt_init(&psbt, buffer, 4096);

	res = psbt_decode(argv[1], psbt_hex_len, buffer, 4096, &psbt_len);
	CHECK(res);

	res = psbt_read(buffer, psbt_len, &psbt, print_rec, NULL);
	CHECK(res);

	res = psbt_encode(&psbt, PSBT_ENCODING_BASE62, buffer, 4096, &out_len);
	CHECK(res);

	/* printf("%.*s", (int)out_len, buffer); */

	/* printf("%.*s\n", (int)out_len, (char*)buffer); */

	return 0;
}

```

### c_source/common.h (19 lines)
```c

#ifndef PSBT_COMMON_H
#define PSBT_COMMON_H

#include <stdint.h>

typedef unsigned char u8;
typedef unsigned short u16;
typedef uint64_t u64;
typedef unsigned int u32;

static const unsigned int MAX_SERIALIZE_SIZE = 0x02000000;

#define STRINGIZE_DETAIL(x) #x
#define STRINGIZE(x) STRINGIZE_DETAIL(x)


#endif /* PSBT_COMMON_H */

```

### c_source/compactsize.c (132 lines)
```c

#define _DEFAULT_SOURCE

#include <limits.h>
#include <endian.h>
#include <string.h>

#include "compactsize.h"

u32 compactsize_peek_length(u8 chsize) {
	if (chsize < 253)
		return sizeof(u8);
	else if (chsize == 253)
		return sizeof(u8) + sizeof(u16);
	else if (chsize == 254)
		return sizeof(u8) + sizeof(u32);
	else
		return sizeof(u8) + sizeof(u64);
}

u32 compactsize_length(u64 data) {
	if (data < 253)
		return sizeof(u8);
	else if (data <= USHRT_MAX)
		return sizeof(u8) + sizeof(u16);
	else if (data <= UINT_MAX)
		return sizeof(u8) + sizeof(u32);
	else
		return sizeof(u8) + sizeof(u64);
}

inline static void serialize_u8(u8 *dest, u8 data) {
	*dest = data;
}

inline static void serialize_u16(u8 *dest, u16 data) {
	data = htole16(data);
	memcpy(dest, &data, sizeof(data));
}

inline static void serialize_u32(u8 *dest, u32 data) {
	data = htole32(data);
	memcpy(dest, &data, sizeof(data));
}

inline static void serialize_u64(u8 *dest, u64 data) {
	data = htole64(data);
	memcpy(dest, &data, sizeof(data));
}

inline static u8 deserialize_u8(u8 *src) {
	return *src;
}

inline static u16 deserialize_u16(u8 *src) {
	u16 data;
	memcpy(&data, src, sizeof(data));
	return le16toh(data);
}

inline static u32 deserialize_u32(u8 *src) {
	u32 data;
	memcpy(&data, src, sizeof(data));
	return le32toh(data);
}

inline static u64 deserialize_u64(u8 *src) {
	u64 data;
	memcpy(&data, src, sizeof(data));
	return le64toh(data);
}

void compactsize_write(u8 *dest, u64 size)
{
	if (size < 253) {
		serialize_u8(dest, size);
	}
	else if (size <= USHRT_MAX) {
		serialize_u8(dest, 253);
		serialize_u16(dest, size);
	}
	else if (size <= UINT_MAX) {
		serialize_u8(dest, 254);
		serialize_u32(dest, size);
	}
	else {
		serialize_u8(dest, 255);
		serialize_u64(dest, size);
	}
}



#define READERR(msg) \
	{if (err)				\
		*err = PSBT_COMPACT_READ_ERROR; \
	psbt_errmsg = msg; \
	return -1;}

u64 compactsize_read(u8 *data, enum psbt_result *err) {
	u8 *p = data;
	u8 chsize = deserialize_u8(p++);
	u64 ret_size = 0;

	if (chsize < 253) {
		ret_size = chsize;
	}

	else if (chsize == 253) {
		ret_size = deserialize_u16(p);
		if (ret_size < 253)
			READERR("non-canonical compactsize_read()");

	}
	else if (chsize == 254) {
		ret_size = deserialize_u32(p);

		if (ret_size < 0x10000u)
			READERR("non-canonical compactsize_read()");
	}
	else {
		ret_size = deserialize_u64(p);
		if (ret_size < 0x100000000ULL)
			READERR("non-canonical compactsize_read()");
	}

	if (ret_size > (u64)MAX_SERIALIZE_SIZE)
		READERR("non-canonical compactsize_read()");

	return ret_size;
}

```

### c_source/compactsize.h (14 lines)
```c

#ifndef PSBT_COMPACTSIZE_H
#define PSBT_COMPACTSIZE_H

#include "psbt.h"
#include "common.h"

u64 compactsize_read(u8 *data, enum psbt_result *err);
u32 compactsize_length(u64 data);
void compactsize_write(u8 *dest, u64 size);
u32 compactsize_peek_length(u8 chsize);

#endif /* PSBT_COMPACTSIZE_H */

```

### c_source/psbt.c (796 lines)
```c

#define _DEFAULT_SOURCE

#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <endian.h>
#include <assert.h>
#include <inttypes.h>
#include "compactsize.h"
#include "tx.h"
#include "base64.h"

#ifdef DEBUG
  #define debug(...) fprintf(stderr, __VA_ARGS__)
#else
  #define debug(...)
#endif

char *psbt_errmsg = NULL;

const unsigned char PSBT_MAGIC[4] = {0x70, 0x73, 0x62, 0x74};

#define ASSERT_SPACE(s) \
	if (tx->write_pos+(s) > tx->data + tx->data_capacity) { \
		psbt_errmsg = "write out of bounds " __FILE__ ":" STRINGIZE(__LINE__); \
		return PSBT_OOB_WRITE; \
	}

size_t psbt_size(struct psbt *tx) {
	return tx->write_pos - tx->data;
}

static void hex_print(unsigned char *data, size_t len) {
	for (size_t i = 0; i < len; ++i)
		printf("%02x", data[i]);
}



static enum psbt_result
psbt_write_header(struct psbt *tx) {
	ASSERT_SPACE(sizeof(PSBT_MAGIC));
	memcpy(tx->write_pos, PSBT_MAGIC, sizeof(PSBT_MAGIC));
	tx->write_pos += sizeof(PSBT_MAGIC);

	ASSERT_SPACE(1);
	*tx->write_pos = 0xff;
	tx->write_pos++;

	tx->state = PSBT_ST_GLOBAL;

	return PSBT_OK;
}


enum psbt_result
psbt_init(struct psbt *tx, unsigned char *dest, size_t dest_size) {
	tx->write_pos = dest;
	tx->data = dest;
	tx->data_capacity = dest_size;
	tx->state = PSBT_ST_INIT;
	return PSBT_OK;
}

/* enum psbt_result */
/* psbt_end_transaction(char *dest, size_t dest_len) */
/* { */
/* 	ASSERT_SPACE(1); */
/* 	*dest =  */
/* } */


enum psbt_result
psbt_close_records(struct psbt *tx) {
	ASSERT_SPACE(1);
	*tx->write_pos = '\0';
	tx->write_pos++;
	return PSBT_OK;
}


enum psbt_result
psbt_finalize(struct psbt *tx) {
	enum psbt_result res;

	if (tx->state != PSBT_ST_OUTPUTS_NEW && tx->state != PSBT_ST_OUTPUTS) {
		psbt_errmsg = "psbt_finalize: no output records found";
		return PSBT_INVALID_STATE;
	}

	res = psbt_close_records(tx);
	if (res != PSBT_OK)
		return res;

	tx->state = PSBT_ST_FINALIZED;

	return PSBT_OK;
}

static enum psbt_result
psbt_write_record(struct psbt *tx, struct psbt_record *rec) {
	u32 size;
	u32 key_size_with_type = rec->key_size + 1;

	// write key length
	size = compactsize_length(key_size_with_type);
	ASSERT_SPACE(size);
	compactsize_write((u8*)tx->write_pos, key_size_with_type);
	tx->write_pos += size;

	// write type
	ASSERT_SPACE(1);
	*tx->write_pos++ = rec->type;

	// write key
	ASSERT_SPACE(rec->key_size);
	memcpy(tx->write_pos, rec->key, rec->key_size);
	tx->write_pos += rec->key_size;

	// write value length
	size = compactsize_length(rec->val_size);
	ASSERT_SPACE(size);
	compactsize_write((u8*)tx->write_pos, rec->val_size);
	tx->write_pos += size;

	// write value
	ASSERT_SPACE(rec->val_size);
	memcpy(tx->write_pos, rec->val, rec->val_size);
	tx->write_pos += rec->val_size;

	return PSBT_OK;
}

static enum psbt_result
psbt_read_header(struct psbt *tx) {
	ASSERT_SPACE(4);

	debug("magic %02X %02X %02X %02X\n",
		*tx->write_pos,
		*(tx->write_pos+1),
		*(tx->write_pos+2),
		*(tx->write_pos+3));

	if (memcmp(tx->write_pos, PSBT_MAGIC, sizeof(PSBT_MAGIC)) != 0) {
		psbt_errmsg = "psbt_read: invalid magic header";
		return PSBT_READ_ERROR;
	}

	tx->write_pos += 4;

	if (*tx->write_pos++ != 0xff) {
		psbt_errmsg = "psbt_read: no 0xff found after magic";
		return PSBT_READ_ERROR;
	}

	tx->state = PSBT_ST_GLOBAL;

	return PSBT_OK;
}

const char *
psbt_input_type_tostr(enum psbt_input_type type) {
	switch (type) {
	case PSBT_IN_NON_WITNESS_UTXO:
		return "IN_NON_WITNESS_UTXO";
	case PSBT_IN_WITNESS_UTXO:
		return "IN_WITNESS_UTXO";
	case PSBT_IN_PARTIAL_SIG:
		return "IN_PARTIAL_SIG";
	case PSBT_IN_SIGHASH_TYPE:
		return "IN_SIGHASH_TYPE";
	case PSBT_IN_REDEEM_SCRIPT:
		return "IN_REDEEM_SCRIPT";
	case PSBT_IN_WITNESS_SCRIPT:
		return "IN_WITNESS_SCRIPT";
	case PSBT_IN_BIP32_DERIVATION:
		return "IN_BIP32_DERIVATION";
	case PSBT_IN_FINAL_SCRIPTSIG:
		return "IN_FINAL_SCRIPTSIG";
	case PSBT_IN_FINAL_SCRIPTWITNESS:
		return "IN_FINAL_SCRIPTWITNESS";
	}

	return "UNKNOWN_INPUT_TYPE";
}

const char *
psbt_state_tostr(enum psbt_state state) {
	switch (state) {
	case PSBT_ST_INIT:
		return "INIT";
	case PSBT_ST_GLOBAL:
		return "GLOBAL";
	case PSBT_ST_INPUTS:
		return "INPUTS";
	case PSBT_ST_INPUTS_NEW:
		return "INPUTS_NEW";
	case PSBT_ST_OUTPUTS:
		return "OUTPUTS";
	case PSBT_ST_OUTPUTS_NEW:
		return "OUTPUTS_NEW";
	case PSBT_ST_FINALIZED:
		return "FINALIZED";
	}

	return "UNKNOWN_STATE";
}

const char *
psbt_output_type_tostr(enum psbt_output_type type) {
	switch (type) {
	case PSBT_OUT_REDEEM_SCRIPT:
		return "OUT_REDEEM_SCRIPT";
	case PSBT_OUT_WITNESS_SCRIPT:
		return "OUT_WITNESS_SCRIPT";
	case PSBT_OUT_BIP32_DERIVATION:
		return "OUT_BIP32_DERIVATION";
	}

	return "UNKNOWN_OUTPUT_TYPE";
}

const char *
psbt_global_type_tostr(enum psbt_global_type type) {
	switch (type) {
	case PSBT_GLOBAL_UNSIGNED_TX: return "GLOBAL_UNSIGNED_TX";
	}

	return "UNKNOWN_GLOBAL_TYPE";
}

const char *
psbt_txelem_type_tostr(enum psbt_txelem_type txelem_type) {
	switch (txelem_type) {
	case PSBT_TXELEM_TX:
		return "TX";
	case PSBT_TXELEM_TXIN:
		return "TXIN";
	case PSBT_TXELEM_TXOUT:
		return "TXOUT";
	case PSBT_TXELEM_WITNESS_ITEM:
		return "WITNESS_ITEM";
	}

	return "UNKNOWN_TXELEM";
}

const char *
psbt_type_tostr(unsigned char type, enum psbt_scope scope) {
	switch (scope) {
	case PSBT_SCOPE_GLOBAL:
		return psbt_global_type_tostr((enum psbt_global_type)type);
	case PSBT_SCOPE_INPUTS:
		return psbt_input_type_tostr((enum psbt_input_type)type);
	case PSBT_SCOPE_OUTPUTS:
		return psbt_output_type_tostr((enum psbt_output_type)type);
	}

	return "UNKNOWN_SCOPE";
}

static enum psbt_result
psbt_read_record(struct psbt *tx, size_t src_size, struct psbt_record *rec)
{
	enum psbt_result res = PSBT_OK;
	u64 size;
	u32 size_len;

	size_len = compactsize_peek_length(*tx->write_pos);
	ASSERT_SPACE(size_len);
	size = compactsize_read(tx->write_pos, &res);
	assert(size > 0);

	tx->write_pos += size_len;

	debug("record pos %zu size_len %d size %"PRIu64"\n",
	      tx->write_pos - tx->data, size_len, size);

	if (res != PSBT_OK)
		return res;

	if (tx->write_pos + size > tx->data + src_size) {
		psbt_errmsg = "psbt_read: record key size too large";
		return PSBT_READ_ERROR;
	}

	ASSERT_SPACE(size);

	rec->key_size = size - 1; // don't include type in key size
	rec->type = *tx->write_pos;
	rec->key = tx->write_pos + 1;

	tx->write_pos += size;
	debug("%02x %02x %02x %02x %02x\n", *(tx->write_pos-2), *(tx->write_pos-1),
	      *tx->write_pos, *(tx->write_pos+1), *(tx->write_pos+2));

	debug("record pos %zu size_len %d size %"PRIu64"\n",
	      tx->write_pos - tx->data, size_len, size);

	switch (tx->state) {
		case PSBT_ST_GLOBAL:
			rec->scope = PSBT_SCOPE_GLOBAL;
			break;

		case PSBT_ST_INPUTS:
			rec->scope = PSBT_SCOPE_INPUTS;
			break;

		case PSBT_ST_OUTPUTS:
			rec->scope = PSBT_SCOPE_OUTPUTS;
			break;

		default:
			psbt_errmsg = "psbt_read_record: invalid record state";
			return PSBT_INVALID_STATE;
	}

	size_len = compactsize_peek_length(*tx->write_pos);

	ASSERT_SPACE(size_len);
	size = compactsize_read(tx->write_pos, &res);

	if (res != PSBT_OK)
		return res;

	tx->write_pos += size_len;

	if (tx->write_pos + size > tx->data + src_size) {
		psbt_errmsg = "psbt_read: record value size too large";
		return PSBT_READ_ERROR;
	}

	rec->val_size = size;
	rec->val = tx->write_pos;

	ASSERT_SPACE(size);
	tx->write_pos += size;

	return PSBT_OK;
}

struct psbt_tx_counter {
	int inputs;
	int outputs;
	void *user_data;
	psbt_elem_handler *handler;
} counter;

static void tx_counter(struct psbt_txelem *elem) {
	struct psbt_elem psbt_elem;
	struct psbt_tx_counter *counter =
		(struct psbt_tx_counter *)elem->user_data;

	psbt_elem.user_data = counter->user_data;
	psbt_elem.type = PSBT_ELEM_TXELEM;
	psbt_elem.elem.txelem = elem;

	// forward txelem events to user
	if (counter->handler)
		counter->handler(&psbt_elem);

	switch (elem->elem_type) {
	case PSBT_TXELEM_TXIN:
		counter->inputs++;
		return;
	case PSBT_TXELEM_TXOUT:
		counter->outputs++;
		return;
	default:
		return;
	}
}

enum psbt_result
psbt_read(const unsigned char *src, size_t src_size, struct psbt *tx,
	  psbt_elem_handler *elem_handler, void* user_data)
{
	struct psbt_record rec;
	enum psbt_result res;

	struct psbt_elem elem;
	elem.type = PSBT_ELEM_RECORD;
	elem.user_data = user_data;

	int kvs = 0;
	u8 *end;

	struct psbt_tx_counter counter = {
		.inputs = 0,
		.outputs = 0,
		.user_data = user_data,
		.handler = elem_handler,
	};

	if (tx->state != PSBT_ST_INIT) {
		psbt_errmsg = "psbt_read: psbt not initialized, use psbt_init first";
		return PSBT_INVALID_STATE;
	}

	if (src_size > tx->data_capacity) {
		psbt_errmsg = "psbt_read: read buffer is larger than psbt capacity";
		return PSBT_OOB_WRITE;
	}

	if (src != tx->data)
		memcpy(tx->data, src, src_size);

	// parsing should try to get this to the finalized state,
	// otherwise it's an invalid psbt
	tx->state = PSBT_ST_INIT;
	tx->write_pos = tx->data;

	// XXX: needed so that the asserts work properly. this is probably fine...
	tx->data_capacity = src_size;

	end = tx->data + src_size;

	while (tx->state != PSBT_ST_FINALIZED && tx->write_pos <= end) {
		switch(tx->state) {
		case PSBT_ST_INIT:
			debug("reading header at %zu\n", tx->write_pos - tx->data);
			res = psbt_read_header(tx);
			if (res != PSBT_OK)
				return res;
			break;

		case PSBT_ST_GLOBAL:
		case PSBT_ST_INPUTS:
		case PSBT_ST_OUTPUTS:

			if (*tx->write_pos == 0) {
				switch (tx->state) {
				case PSBT_ST_GLOBAL:
					tx->state = PSBT_ST_INPUTS_NEW;
					break;

				case PSBT_ST_INPUTS:
					if (++kvs >= counter.inputs) {
						tx->state = PSBT_ST_OUTPUTS_NEW;
						kvs = 0;
					} else
						tx->state = PSBT_ST_INPUTS_NEW;
					break;

				case PSBT_ST_OUTPUTS:
					if (++kvs >= counter.outputs)
						tx->state = PSBT_ST_FINALIZED;
					else
						tx->state = PSBT_ST_OUTPUTS_NEW;
					break;

				default:
					assert(!"psbt_read: invalid state at null byte");
				}
			}
			else {
				debug("reading record @ %zu\n", tx->write_pos - tx->data);
				res = psbt_read_record(tx, src_size, &rec);

				if (res != PSBT_OK)
					return res;

				if (tx->state == PSBT_ST_GLOBAL &&
				    rec.type == PSBT_GLOBAL_UNSIGNED_TX) {
					// parse transaction for number of inputs/outputs
					res = psbt_btc_tx_parse(rec.val,
								rec.val_size,
								(void*)&counter,
								tx_counter);

					if (res != PSBT_OK)
						return res;
				}

				// record callback
				if (elem_handler) {
					elem.type = PSBT_ELEM_RECORD;
					elem.index = kvs;
					elem.elem.rec = &rec;
					elem_handler(&elem);
				}
			}


			break;

		case PSBT_ST_OUTPUTS_NEW:
			assert(*tx->write_pos == 0);
			tx->write_pos++;
			tx->state = PSBT_ST_OUTPUTS;
			break;

		case PSBT_ST_INPUTS_NEW:
			assert(*tx->write_pos == 0);
			tx->write_pos++;
			tx->state = PSBT_ST_INPUTS;
			break;

		case PSBT_ST_FINALIZED:
			assert(!"impossible");
			break;
		}
	}

	if (tx->state != PSBT_ST_FINALIZED) {
		psbt_errmsg = "psbt_read: invalid psbt";
		return PSBT_INVALID_STATE;
	}
	else if (tx->state == PSBT_ST_FINALIZED && *tx->write_pos != 0) {
		psbt_errmsg = "psbt_read: expected null byte at end of psbt";
		return PSBT_READ_ERROR;
	}

	tx->write_pos++;

	return PSBT_OK;
}

enum psbt_result
psbt_write_global_record(struct psbt *tx, struct psbt_record *rec) {
	if (tx->state == PSBT_ST_INIT) {
		// write header if we haven't yet
		psbt_write_header(tx);
		tx->state = PSBT_ST_GLOBAL;
	}
	else if (tx->state != PSBT_ST_GLOBAL) {
		psbt_errmsg = "psbt_write_global_record: you can only write a "
			"global record after psbt_init and before "
			"psbt_write_input_record";
		return PSBT_INVALID_STATE;
	}

	return psbt_write_record(tx, rec);
}

enum psbt_result
psbt_new_input_record_set(struct psbt *tx) {
	enum psbt_result res;
	if (tx->state == PSBT_ST_GLOBAL
	 || tx->state == PSBT_ST_INPUTS_NEW
	 || tx->state == PSBT_ST_INPUTS) {
		res = psbt_close_records(tx);
		if (res != PSBT_OK)
			return res;
		tx->state = PSBT_ST_INPUTS_NEW;
		return PSBT_OK;
	}
	else if (tx->state != PSBT_ST_INPUTS) {
		psbt_errmsg = "psbt_new_input_record_set: "
			"this can only be called after psbt_write_global_record, "
                        "psbt_new_input_record_set, "
			"or psbt_write_input_record";
		return PSBT_INVALID_STATE;
	}

	return psbt_close_records(tx);
}


enum psbt_result
psbt_new_output_record_set(struct psbt *tx) {
	enum psbt_result res;
	if (tx->state == PSBT_ST_INPUTS
	    || tx->state == PSBT_ST_INPUTS_NEW
	    || tx->state == PSBT_ST_OUTPUTS_NEW
	    || tx->state == PSBT_ST_OUTPUTS)
	{
		res = psbt_close_records(tx);
		if (res != PSBT_OK)
			return res;
		tx->state = PSBT_ST_OUTPUTS_NEW;
		return PSBT_OK;
	}
	else if (tx->state != PSBT_ST_OUTPUTS) {
		psbt_errmsg = "psbt_new_output_record_set: "
			"this can only be called after writing input records";
		return PSBT_INVALID_STATE;
	}

	return psbt_close_records(tx);
}


enum psbt_result
psbt_print(struct psbt *tx, FILE *stream) {
	if (tx->state != PSBT_ST_FINALIZED) {
		psbt_errmsg = "psbt_print: transaction is not finished";
		return PSBT_INVALID_STATE;
	}

	size_t size = psbt_size(tx);
	for (size_t i = 0; i < size; ++i)
		fprintf(stream, "%02x", tx->data[i]);
	printf("\n");

	return PSBT_OK;
}

enum psbt_result
psbt_write_input_record(struct psbt *tx, struct psbt_record *rec) {
	enum psbt_result res;
	if (tx->state == PSBT_ST_GLOBAL) {
		// close global records
		if ((res = psbt_close_records(tx)) != PSBT_OK)
			return res;
		tx->state = PSBT_ST_INPUTS;
	}
	else if (tx->state != PSBT_ST_INPUTS && tx->state != PSBT_ST_INPUTS_NEW) {
		psbt_errmsg = "psbt_write_input_record: attempting to write an "
			"input record before any global records have been written."
			" use psbt_write_global_record first";
		return PSBT_INVALID_STATE;
	}

	return psbt_write_record(tx, rec);
}


enum psbt_result
psbt_write_output_record(struct psbt *tx, struct psbt_record *rec) {
	enum psbt_result res;
	if (tx->state == PSBT_ST_INPUTS) {
		// close global records
		if ((res = psbt_close_records(tx)) != PSBT_OK)
			return res;
		tx->state = PSBT_ST_OUTPUTS;
	}
	else if (tx->state != PSBT_ST_OUTPUTS && tx->state != PSBT_ST_OUTPUTS_NEW) {
		psbt_errmsg = "psbt_write_input_record: attempting to write an "
			"input record before any global records have been written."
			" use psbt_write_global_record first";
		return PSBT_INVALID_STATE;
	}

	return psbt_write_record(tx, rec);
}


static inline u8 hexdigit( char hex ) {
	return (hex <= '9') ? hex - '0' : toupper(hex) - 'A' + 10 ;
}

enum psbt_result
psbt_hex_decode(const char *src, size_t src_size, unsigned char *dest,
	        size_t dest_size) {

	enum psbt_result res = PSBT_OK;

	if (src_size % 2 != 0) {
		psbt_errmsg = "psbt_decode: invalid hex string";
		return PSBT_READ_ERROR;
	}

	if (dest_size < src_size / 2) {
		psbt_errmsg = "psbt_decode: dest_size must be at least half the"
			" size of src_size";
		return PSBT_READ_ERROR;
	}

	if (res != PSBT_OK)
		return res;

	for (size_t i = 0; i < src_size; i += 2) {
		u8 c1 = src[i];
		u8 c2 = src[i+1];
		if (!isxdigit(c1) || !isxdigit(c2)) {
			psbt_errmsg = "psbt_decode: invalid hex string";
			return PSBT_READ_ERROR;
		}

		*dest++ = hexdigit(c1) << 4 | hexdigit(c2);
	}

	return PSBT_OK;
}

enum psbt_result
psbt_decode(const char *src, size_t src_size, unsigned char *dest,
	    size_t dest_size, size_t *psbt_size) {
	enum psbt_result res;
	// TODO: detect base64 or hex encoding
	// default is hex encoding for now

	size_t b64_magic_size = sizeof("cHNid") - 1;

	// simple sanity check before we look for base64 encoding
	if (src_size < b64_magic_size) {
		psbt_errmsg = "psbt_decode: psbt too small";
		return PSBT_READ_ERROR;
	}

	// base64 detection
	if (memcmp(src, "cHNid", b64_magic_size) == 0) {
		u8 *c = base64_decode((unsigned char*)src, src_size, dest,
					dest_size, psbt_size);
		return c == NULL ? PSBT_READ_ERROR : PSBT_OK;
	}

	*psbt_size = src_size / 2;
	return psbt_hex_decode(src, src_size, dest, dest_size);
}

static char hexchar(unsigned int val)
{
	if (val < 10)
		return '0' + val;
	if (val < 16)
		return 'a' + val - 10;
	assert(!"hexchar invalid val");
}

static enum psbt_result
hex_encode(u8 *buf, size_t bufsize, u8 *dest, size_t dest_size) {
	size_t i;

	if (dest_size < bufsize * 2 + 1)
		return PSBT_OOB_WRITE;

	for (i = 0; i < bufsize; i++) {
		unsigned int c = buf[i];
		*(dest++) = hexchar(c >> 4);
		*(dest++) = hexchar(c & 0xF);
	}
	*dest = '\0';

	return PSBT_OK;
}

/* static enum psbt_result */
/* base64_encode(u8 *psbt, size_t psbt_size, u8 *dest, size_t dest_size) { */
/* 	return PSBT_NOT_IMPLEMENTED; */
/* } */

static enum psbt_result
protobuf_encode(u8 *psbt, size_t psbt_size, u8 *dest, size_t dest_size) {
	return PSBT_NOT_IMPLEMENTED;
}

enum psbt_result
psbt_encode_raw(unsigned char *psbt_data, size_t psbt_len,
		enum psbt_encoding encoding, unsigned char *dest,
		size_t dest_size, size_t* out_len)
{
	u8 *c;
	enum psbt_result res;

	switch (encoding) {
	case PSBT_ENCODING_HEX:
		res = hex_encode(psbt_data, psbt_len, dest, dest_size);
		*out_len = psbt_len * 2 + 1;
		return res;
	case PSBT_ENCODING_BASE64:
		c = base64_encode(psbt_data, psbt_len, dest, dest_size, out_len);
		if (c == NULL) {
			psbt_errmsg = "psbt_encode: base64 encode failure";
			return PSBT_WRITE_ERROR;
		}
		return PSBT_OK;
	case PSBT_ENCODING_BASE62:
		c = base62_encode(psbt_data, psbt_len, dest, dest_size, out_len);
		if (c == NULL) {
			psbt_errmsg = "psbt_encode: base62 encode failure";
			return PSBT_WRITE_ERROR;
		}
		return PSBT_OK;
	case PSBT_ENCODING_PROTOBUF:
		return protobuf_encode(psbt_data, psbt_len, dest, dest_size);
	}

	psbt_errmsg = "psbt_encode: invalid psbt_encoding enum value";
	return PSBT_NOT_IMPLEMENTED;
}

enum psbt_result
psbt_encode(struct psbt *psbt, enum psbt_encoding encoding, unsigned char *dest,
	    size_t dest_size, size_t *out_len)
{
	if (psbt->state != PSBT_ST_FINALIZED) {
		psbt_errmsg = "psbt_encode: psbt not in finalized state. "
			"use psbt_read to parse an existing psbt, or the "
			"psbt_write functions to create one.";

		return PSBT_WRITE_ERROR;
	}

	return psbt_encode_raw(psbt->data, psbt_size(psbt), encoding, dest,
			       dest_size, out_len);
}


const char *
psbt_geterr() {
	return psbt_errmsg;
}

```

### c_source/psbt.h (158 lines)
```c
#ifndef PSBT_H
#define PSBT_H

#include <stddef.h>
#include <stdio.h>
#include "result.h"
#include "tx.h"

enum psbt_global_type {
	PSBT_GLOBAL_UNSIGNED_TX = 0
};

enum psbt_encoding {
	PSBT_ENCODING_HEX,
	PSBT_ENCODING_BASE64,
	PSBT_ENCODING_BASE62,
	PSBT_ENCODING_PROTOBUF,
};

enum psbt_input_type {
	PSBT_IN_NON_WITNESS_UTXO    = 0,
	PSBT_IN_WITNESS_UTXO        = 1,
	PSBT_IN_PARTIAL_SIG         = 2,
	PSBT_IN_SIGHASH_TYPE        = 3,
	PSBT_IN_REDEEM_SCRIPT       = 4,
	PSBT_IN_WITNESS_SCRIPT      = 5,
	PSBT_IN_BIP32_DERIVATION    = 6,
	PSBT_IN_FINAL_SCRIPTSIG     = 7,
	PSBT_IN_FINAL_SCRIPTWITNESS = 8,
};


enum psbt_output_type {
	PSBT_OUT_REDEEM_SCRIPT      = 0,
	PSBT_OUT_WITNESS_SCRIPT     = 1,
	PSBT_OUT_BIP32_DERIVATION   = 2,
};

enum psbt_scope {
	PSBT_SCOPE_GLOBAL,
	PSBT_SCOPE_INPUTS,
	PSBT_SCOPE_OUTPUTS,
};

enum psbt_state {
	PSBT_ST_INIT = 2,
	PSBT_ST_GLOBAL,
	PSBT_ST_INPUTS,
	PSBT_ST_INPUTS_NEW,
	PSBT_ST_OUTPUTS,
	PSBT_ST_OUTPUTS_NEW,
	PSBT_ST_FINALIZED,
};

struct psbt {
	enum psbt_state state;
	unsigned char *data;
	unsigned char *write_pos;
	size_t data_capacity;
};

struct psbt_record {
	unsigned char type;
	unsigned char *key;
	unsigned int key_size;
	unsigned char *val;
	unsigned int val_size;
	enum psbt_scope scope;
};

enum psbt_elem_type {
	PSBT_ELEM_RECORD,
	PSBT_ELEM_TXELEM,
};

struct psbt_elem {
	enum psbt_elem_type type;
	void *user_data;
	int index;
	union {
		struct psbt_txelem *txelem;
		struct psbt_record *rec;
	} elem;
};

typedef void (psbt_elem_handler)(struct psbt_elem *rec);

size_t
psbt_size(struct psbt *tx);

enum psbt_result
psbt_read(const unsigned char *src, size_t src_size, struct psbt *psbt,
	  psbt_elem_handler *elem_handler, void* user_data);

enum psbt_result
psbt_decode(const char *src, size_t src_size, unsigned char *dest,
	    size_t dest_size, size_t *psbt_len);

enum psbt_result
psbt_encode(struct psbt *psbt, enum psbt_encoding encoding, unsigned char *dest,
	    size_t dest_size, size_t *out_len);

enum psbt_result
psbt_encode_raw(unsigned char *psbt_data, size_t psbt_len,
		enum psbt_encoding encoding, unsigned char *dest,
		size_t dest_size, size_t* out_len);

const char *
psbt_geterr();

const char *
psbt_state_tostr(enum psbt_state state);

const char *
psbt_type_tostr(unsigned char type, enum psbt_scope scope);

const char *
psbt_txelem_type_tostr(enum psbt_txelem_type txelem_type);

const char *
psbt_global_type_tostr(enum psbt_global_type type);

const char *
psbt_output_type_tostr(enum psbt_output_type type);

const char *
psbt_input_type_tostr(enum psbt_input_type type);

enum psbt_result
psbt_write_global_record(struct psbt *tx, struct psbt_record *rec);

enum psbt_result
psbt_write_input_record(struct psbt *tx, struct psbt_record *rec);

enum psbt_result
psbt_write_output_record(struct psbt *tx, struct psbt_record *rec);

enum psbt_result
psbt_new_input_record_set(struct psbt *tx);

enum psbt_result
psbt_new_output_record_set(struct psbt *tx);

enum psbt_result
psbt_init(struct psbt *tx, unsigned char *dest, size_t dest_size);

enum psbt_result
psbt_print(struct psbt *tx, FILE *stream);

enum psbt_result
psbt_finalize(struct psbt *tx);

extern const unsigned char PSBT_MAGIC[4];

extern char *psbt_errmsg;

#endif /* PSBT_H */

```

### c_source/result.h (18 lines)
```c

#ifndef PSBT_RESULT_H
#define PSBT_RESULT_H


enum psbt_result {
	PSBT_OK,
	PSBT_COMPACT_READ_ERROR,
	PSBT_READ_ERROR,
	PSBT_WRITE_ERROR,
	PSBT_INVALID_STATE,
	PSBT_NOT_IMPLEMENTED,
	PSBT_OOB_WRITE
};


#endif /* PSBT_RESULT_H */

```

### c_source/test.c (179 lines)
```c

#include "psbt.h"
#include <stdio.h>
#include <assert.h>
#include <stdlib.h>
#include <string.h>

#define ARRAY_SIZE(arr) (sizeof(arr) / sizeof(arr[0]))

static const char *psbt_hex = "70736274ff01009a020000000258e87a21b56daf0c23be8e7070456c336f7cbaa5c8757924f545887bb2abdd750000000000ffffffff838d0427d0ec650a68aa46bb0b098aea4422c071b2ca78352a077959d07cea1d0100000000ffffffff0270aaf00800000000160014d85c2b71d0060b09c9886aeb815e50991dda124d00e1f5050000000016001400aea9a2e5f0f876a588df5546e8742d1d87008f00000000000100bb0200000001aad73931018bd25f84ae400b68848be09db706eac2ac18298babee71ab656f8b0000000048473044022058f6fc7c6a33e1b31548d481c826c015bd30135aad42cd67790dab66d2ad243b02204a1ced2604c6735b6393e5b41691dd78b00f0c5942fb9f751856faa938157dba01feffffff0280f0fa020000000017a9140fb9463421696b82c833af241c78c17ddbde493487d0f20a270100000017a91429ca74f8a08f81999428185c97b5d852e4063f6187650000000104475221029583bf39ae0a609747ad199addd634fa6108559d6c5cd39b4c2183f1ab96e07f2102dab61ff49a14db6a7d02b0cd1fbb78fc4b18312b5b4e54dae4dba2fbfef536d752ae2206029583bf39ae0a609747ad199addd634fa6108559d6c5cd39b4c2183f1ab96e07f10d90c6a4f000000800000008000000080220602dab61ff49a14db6a7d02b0cd1fbb78fc4b18312b5b4e54dae4dba2fbfef536d710d90c6a4f0000008000000080010000800001012000c2eb0b0000000017a914b7f5faf40e3d40a5a459b1db3535f2b72fa921e88701042200208c2353173743b595dfb4a07b72ba8e42e3797da74e87fe7d9d7497e3b2028903010547522103089dc10c7ac6db54f91329af617333db388cead0c231f723379d1b99030b02dc21023add904f3d6dcf59ddb906b0dee23529b7ffb9ed50e5e86151926860221f0e7352ae2206023add904f3d6dcf59ddb906b0dee23529b7ffb9ed50e5e86151926860221f0e7310d90c6a4f000000800000008003000080220603089dc10c7ac6db54f91329af617333db388cead0c231f723379d1b99030b02dc10d90c6a4f00000080000000800200008000220203a9a4c37f5996d3aa25dbac6b570af0650394492942460b354753ed9eeca5877110d90c6a4f000000800000008004000080002202027f6399757d2eff55a136ad02c684b1838b6556e5f1b6b34282a94b6b5005109610d90c6a4f00000080000000800500008000";

// unsigned transaction from the bip174 test vector section
// 02000000022e8c7d8d37c427e060ec002ec1c2bc30196fc2f75d6a8844cbc03651c081430a0100000000ffffffff96a04e0cc636f377933e3d93accc627faacdbcdb5a9624df1b490bd045f24d2c0000000000ffffffff01e02be50e0000000017a914b53bb0dc1db8c8d803e3e39f784d42e4737ffa0d8700000000
static const unsigned char transaction[] = {0x02, 0x00, 0x00, 0x00, 0x02, 0x2e, 0x8c, 0x7d, 0x8d, 0x37, 0xc4, 0x27, 0xe0, 0x60, 0xec, 0x00, 0x2e, 0xc1, 0xc2, 0xbc, 0x30, 0x19, 0x6f, 0xc2, 0xf7, 0x5d, 0x6a, 0x88, 0x44, 0xcb, 0xc0, 0x36, 0x51, 0xc0, 0x81, 0x43, 0x0a, 0x01, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0x96, 0xa0, 0x4e, 0x0c, 0xc6, 0x36, 0xf3, 0x77, 0x93, 0x3e, 0x3d, 0x93, 0xac, 0xcc, 0x62, 0x7f, 0xaa, 0xcd, 0xbc, 0xdb, 0x5a, 0x96, 0x24, 0xdf, 0x1b, 0x49, 0x0b, 0xd0, 0x45, 0xf2, 0x4d, 0x2c, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0x01, 0xe0, 0x2b, 0xe5, 0x0e, 0x00, 0x00, 0x00, 0x00, 0x17, 0xa9, 0x14, 0xb5, 0x3b, 0xb0, 0xdc, 0x1d, 0xb8, 0xc8, 0xd8, 0x03, 0xe3, 0xe3, 0x9f, 0x78, 0x4d, 0x42, 0xe4, 0x73, 0x7f, 0xfa, 0x0d, 0x87, 0x00, 0x00, 0x00, 0x00};

// 522103c8727ce35f1c93eb0be21406ee9a923c89219fe9c9e8504c8314a6a22d1295c02103c74dc710c407d7db6e041ee212d985cd2826d93f806ed44912b9a1da691c977352ae
static const unsigned char redeem_script_a[] = {0x52, 0x21, 0x03, 0xc8, 0x72, 0x7c, 0xe3, 0x5f, 0x1c, 0x93, 0xeb, 0x0b, 0xe2, 0x14, 0x06, 0xee, 0x9a, 0x92, 0x3c, 0x89, 0x21, 0x9f, 0xe9, 0xc9, 0xe8, 0x50, 0x4c, 0x83, 0x14, 0xa6, 0xa2, 0x2d, 0x12, 0x95, 0xc0, 0x21, 0x03, 0xc7, 0x4d, 0xc7, 0x10, 0xc4, 0x07, 0xd7, 0xdb, 0x6e, 0x04, 0x1e, 0xe2, 0x12, 0xd9, 0x85, 0xcd, 0x28, 0x26, 0xd9, 0x3f, 0x80, 0x6e, 0xd4, 0x49, 0x12, 0xb9, 0xa1, 0xda, 0x69, 0x1c, 0x97, 0x73, 0x52, 0xae};

// 0020a8f44467bf171d51499153e01c0bd6291109fc38bd21b3c3224c9dc6b57590df
static const unsigned char redeem_script_b[] = {0x00, 0x20, 0xa8, 0xf4, 0x44, 0x67, 0xbf, 0x17, 0x1d, 0x51, 0x49, 0x91,  0x53, 0xe0, 0x1c, 0x0b, 0xd6, 0x29, 0x11, 0x09, 0xfc, 0x38, 0xbd, 0x21,  0xb3, 0xc3, 0x22, 0x4c, 0x9d, 0xc6, 0xb5, 0x75, 0x90, 0xdf};

// expected
// 70736274ff01007c02000000022e8c7d8d37c427e060ec002ec1c2bc30196fc2f75d6a8844cbc03651c081430a0100000000ffffffff96a04e0cc636f377933e3d93accc627faacdbcdb5a9624df1b490bd045f24d2c0000000000ffffffff01e02be50e0000000017a914b53bb0dc1db8c8d803e3e39f784d42e4737ffa0d87000000001501203736c3c06053896d7041ce8f5bae3df76cc49147522103c8727ce35f1c93eb0be21406ee9a923c89219fe9c9e8504c8314a6a22d1295c02103c74dc710c407d7db6e041ee212d985cd2826d93f806ed44912b9a1da691c977352ae1501f3ba8a120d960ae07d1dbe6f0c37fb4c926d76d5220020a8f44467bf171d51499153e01c0bd6291109fc38bd21b3c3224c9dc6b57590df2102a8f44467bf171d51499153e01c0bd6291109fc38bd21b3c3224c9dc6b57590df47522102e80dec31d167865c1685e9d7a9291e66a4ea22c65cfee324289a1667ccda3b87210258cbbc3cb295a8bebac233aadc7773978804993798be5390ab444f6dd4c5327e52ae000100fdff0002000000018b2dd2f735d0a9338af96402a8a91e4841cd3fed882362e7329fb04f1ff65325000000006a473044022077bedfea9910c9ba4e00dec941dace974f8b47349992c5d4312c1cf5796cce5502206164e6bfff7ac11590064ca571583709337c8a38973db2e70f4e9d93b3bcce1d0121032d64447459784e37cb2dda366c697adbbdc8aae2ad6db74ed2dade39d75882fafeffffff0382b42a04000000001976a914da533648fd339d5797790e6bb1667d9e86fdfb6888ac80f0fa020000000017a914203736c3c06053896d7041ce8f5bae3df76cc4918700b4c4040000000017a914b53bb0dc1db8c8d803e3e39f784d42e4737ffa0d879e2f13000001012000c2eb0b0000000017a914f3ba8a120d960ae07d1dbe6f0c37fb4c926d76d58700
static const unsigned char expected_psbt[] = {0x70, 0x73, 0x62, 0x74, 0xff, 0x01, 0x00, 0x7c, 0x02, 0x00, 0x00, 0x00, 0x02, 0x2e, 0x8c, 0x7d, 0x8d, 0x37, 0xc4, 0x27, 0xe0, 0x60, 0xec, 0x00, 0x2e, 0xc1, 0xc2, 0xbc, 0x30, 0x19, 0x6f, 0xc2, 0xf7, 0x5d, 0x6a, 0x88, 0x44, 0xcb, 0xc0, 0x36, 0x51, 0xc0, 0x81, 0x43, 0x0a, 0x01, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0x96, 0xa0, 0x4e, 0x0c, 0xc6, 0x36, 0xf3, 0x77, 0x93, 0x3e, 0x3d, 0x93, 0xac, 0xcc, 0x62, 0x7f, 0xaa, 0xcd, 0xbc, 0xdb, 0x5a, 0x96, 0x24, 0xdf, 0x1b, 0x49, 0x0b, 0xd0, 0x45, 0xf2, 0x4d, 0x2c, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0x01, 0xe0, 0x2b, 0xe5, 0x0e, 0x00, 0x00, 0x00, 0x00, 0x17, 0xa9, 0x14, 0xb5, 0x3b, 0xb0, 0xdc, 0x1d, 0xb8, 0xc8, 0xd8, 0x03, 0xe3, 0xe3, 0x9f, 0x78, 0x4d, 0x42, 0xe4, 0x73, 0x7f, 0xfa, 0x0d, 0x87, 0x00, 0x00, 0x00, 0x00, 0x15, 0x01, 0x20, 0x37, 0x36, 0xc3, 0xc0, 0x60, 0x53, 0x89, 0x6d, 0x70, 0x41, 0xce, 0x8f, 0x5b, 0xae, 0x3d, 0xf7, 0x6c, 0xc4, 0x91, 0x47, 0x52, 0x21, 0x03, 0xc8, 0x72, 0x7c, 0xe3, 0x5f, 0x1c, 0x93, 0xeb, 0x0b, 0xe2, 0x14, 0x06, 0xee, 0x9a, 0x92, 0x3c, 0x89, 0x21, 0x9f, 0xe9, 0xc9, 0xe8, 0x50, 0x4c, 0x83, 0x14, 0xa6, 0xa2, 0x2d, 0x12, 0x95, 0xc0, 0x21, 0x03, 0xc7, 0x4d, 0xc7, 0x10, 0xc4, 0x07, 0xd7, 0xdb, 0x6e, 0x04, 0x1e, 0xe2, 0x12, 0xd9, 0x85, 0xcd, 0x28, 0x26, 0xd9, 0x3f, 0x80, 0x6e, 0xd4, 0x49, 0x12, 0xb9, 0xa1, 0xda, 0x69, 0x1c, 0x97, 0x73, 0x52, 0xae, 0x15, 0x01, 0xf3, 0xba, 0x8a, 0x12, 0x0d, 0x96, 0x0a, 0xe0, 0x7d, 0x1d, 0xbe, 0x6f, 0x0c, 0x37, 0xfb, 0x4c, 0x92, 0x6d, 0x76, 0xd5, 0x22, 0x00, 0x20, 0xa8, 0xf4, 0x44, 0x67, 0xbf, 0x17, 0x1d, 0x51, 0x49, 0x91, 0x53, 0xe0, 0x1c, 0x0b, 0xd6, 0x29, 0x11, 0x09, 0xfc, 0x38, 0xbd, 0x21, 0xb3, 0xc3, 0x22, 0x4c, 0x9d, 0xc6, 0xb5, 0x75, 0x90, 0xdf, 0x21, 0x02, 0xa8, 0xf4, 0x44, 0x67, 0xbf, 0x17, 0x1d, 0x51, 0x49, 0x91, 0x53, 0xe0, 0x1c, 0x0b, 0xd6, 0x29, 0x11, 0x09, 0xfc, 0x38, 0xbd, 0x21, 0xb3, 0xc3, 0x22, 0x4c, 0x9d, 0xc6, 0xb5, 0x75, 0x90, 0xdf, 0x47, 0x52, 0x21, 0x02, 0xe8, 0x0d, 0xec, 0x31, 0xd1, 0x67, 0x86, 0x5c, 0x16, 0x85, 0xe9, 0xd7, 0xa9, 0x29, 0x1e, 0x66, 0xa4, 0xea, 0x22, 0xc6, 0x5c, 0xfe, 0xe3, 0x24, 0x28, 0x9a, 0x16, 0x67, 0xcc, 0xda, 0x3b, 0x87, 0x21, 0x02, 0x58, 0xcb, 0xbc, 0x3c, 0xb2, 0x95, 0xa8, 0xbe, 0xba, 0xc2, 0x33, 0xaa, 0xdc, 0x77, 0x73, 0x97, 0x88, 0x04, 0x99, 0x37, 0x98, 0xbe, 0x53, 0x90, 0xab, 0x44, 0x4f, 0x6d, 0xd4, 0xc5, 0x32, 0x7e, 0x52, 0xae, 0x00, 0x01, 0x00, 0xfd, 0xff, 0x00, 0x02, 0x00, 0x00, 0x00, 0x01, 0x8b, 0x2d, 0xd2, 0xf7, 0x35, 0xd0, 0xa9, 0x33, 0x8a, 0xf9, 0x64, 0x02, 0xa8, 0xa9, 0x1e, 0x48, 0x41, 0xcd, 0x3f, 0xed, 0x88, 0x23, 0x62, 0xe7, 0x32, 0x9f, 0xb0, 0x4f, 0x1f, 0xf6, 0x53, 0x25, 0x00, 0x00, 0x00, 0x00, 0x6a, 0x47, 0x30, 0x44, 0x02, 0x20, 0x77, 0xbe, 0xdf, 0xea, 0x99, 0x10, 0xc9, 0xba, 0x4e, 0x00, 0xde, 0xc9, 0x41, 0xda, 0xce, 0x97, 0x4f, 0x8b, 0x47, 0x34, 0x99, 0x92, 0xc5, 0xd4, 0x31, 0x2c, 0x1c, 0xf5, 0x79, 0x6c, 0xce, 0x55, 0x02, 0x20, 0x61, 0x64, 0xe6, 0xbf, 0xff, 0x7a, 0xc1, 0x15, 0x90, 0x06, 0x4c, 0xa5, 0x71, 0x58, 0x37, 0x09, 0x33, 0x7c, 0x8a, 0x38, 0x97, 0x3d, 0xb2, 0xe7, 0x0f, 0x4e, 0x9d, 0x93, 0xb3, 0xbc, 0xce, 0x1d, 0x01, 0x21, 0x03, 0x2d, 0x64, 0x44, 0x74, 0x59, 0x78, 0x4e, 0x37, 0xcb, 0x2d, 0xda, 0x36, 0x6c, 0x69, 0x7a, 0xdb, 0xbd, 0xc8, 0xaa, 0xe2, 0xad, 0x6d, 0xb7, 0x4e, 0xd2, 0xda, 0xde, 0x39, 0xd7, 0x58, 0x82, 0xfa, 0xfe, 0xff, 0xff, 0xff, 0x03, 0x82, 0xb4, 0x2a, 0x04, 0x00, 0x00, 0x00, 0x00, 0x19, 0x76, 0xa9, 0x14, 0xda, 0x53, 0x36, 0x48, 0xfd, 0x33, 0x9d, 0x57, 0x97, 0x79, 0x0e, 0x6b, 0xb1, 0x66, 0x7d, 0x9e, 0x86, 0xfd, 0xfb, 0x68, 0x88, 0xac, 0x80, 0xf0, 0xfa, 0x02, 0x00, 0x00, 0x00, 0x00, 0x17, 0xa9, 0x14, 0x20, 0x37, 0x36, 0xc3, 0xc0, 0x60, 0x53, 0x89, 0x6d, 0x70, 0x41, 0xce, 0x8f, 0x5b, 0xae, 0x3d, 0xf7, 0x6c, 0xc4, 0x91, 0x87, 0x00, 0xb4, 0xc4, 0x04, 0x00, 0x00, 0x00, 0x00, 0x17, 0xa9, 0x14, 0xb5, 0x3b, 0xb0, 0xdc, 0x1d, 0xb8, 0xc8, 0xd8, 0x03, 0xe3, 0xe3, 0x9f, 0x78, 0x4d, 0x42, 0xe4, 0x73, 0x7f, 0xfa, 0x0d, 0x87, 0x9e, 0x2f, 0x13, 0x00, 0x00, 0x01, 0x01, 0x20, 0x00, 0xc2, 0xeb, 0x0b, 0x00, 0x00, 0x00, 0x00, 0x17, 0xa9, 0x14, 0xf3, 0xba, 0x8a, 0x12, 0x0d, 0x96, 0x0a, 0xe0, 0x7d, 0x1d, 0xbe, 0x6f, 0x0c, 0x37, 0xfb, 0x4c, 0x92, 0x6d, 0x76, 0xd5, 0x87, 0x00};

const char empty_inputs[] = "cHNidP8BACoCAAAAAAGA8PoCAAAAABepFCufG2xKKzFR7+3XGjiAZPO/VDBkhwAAAAAAAA==";

#define CHECKRES(r) \
	if (r != PSBT_OK) {		\
	   printf("%s\n", psbt_errmsg); \
	   exit(1); \
	}

static void hex_print(unsigned char *data, size_t len) {
	for (size_t i = 0; i < len; ++i)
		printf("%02x", data[i]);
}

void test_vector() {
	struct psbt psbt;
	unsigned char buffer[1024] = {0};
	enum psbt_result res;

	struct psbt_record rec;

	res = psbt_init(&psbt, buffer, 1024);
	CHECKRES(res);

	res = psbt_write_input_record(&psbt, &rec);
	assert(res == PSBT_INVALID_STATE);

	rec.type     = PSBT_GLOBAL_UNSIGNED_TX;
	rec.key      = NULL;
	rec.key_size = 0;
	rec.val      = (unsigned char*)transaction;
	rec.val_size = ARRAY_SIZE(transaction);

	res = psbt_write_global_record(&psbt, &rec);
	CHECKRES(res);

	rec.type     = PSBT_IN_REDEEM_SCRIPT;
	rec.key_size = 0;
	rec.val      = (unsigned char*)redeem_script_a;
	rec.val_size = ARRAY_SIZE(redeem_script_a);

	res = psbt_write_input_record(&psbt, &rec);
	CHECKRES(res);

	rec.type     = PSBT_IN_REDEEM_SCRIPT;
	rec.key_size = 0;
	rec.val      = (unsigned char*)redeem_script_b;
	rec.val_size = ARRAY_SIZE(redeem_script_b);

	res = psbt_write_input_record(&psbt, &rec);
	CHECKRES(res);

	res = psbt_new_output_record_set(&psbt);
	CHECKRES(res);

	res = psbt_print(&psbt, stdout);
	assert(res == PSBT_INVALID_STATE);

	res = psbt_finalize(&psbt);
	CHECKRES(res);

	res = psbt_print(&psbt, stdout);
	CHECKRES(res);
}

void read_test_vector_checker(struct psbt_elem *elem) {
	int *step = (int*)elem->user_data;

	switch (elem->type) {
	case PSBT_ELEM_RECORD:
		switch (*step) {
		case 0:
			assert(elem->elem.rec->type == PSBT_GLOBAL_UNSIGNED_TX);
			break;
		case 1:
			assert(elem->elem.rec->type == PSBT_IN_NON_WITNESS_UTXO);
			break;
		}
		break;
	default:
		break;
	}

	(*step)++;
}

void read_test_vector() {
	static unsigned char buf[2048];
	static unsigned char intbuf[2048];
	size_t psbt_len;
	size_t hexlen = strlen(psbt_hex);
	struct psbt psbt;
	enum psbt_result res;
	int step = 0;

	res = psbt_decode(psbt_hex, hexlen, buf, 2048, &psbt_len);
	CHECKRES(res);

	psbt_init(&psbt, intbuf, 2048);

	res = psbt_read(buf, psbt_len, &psbt, read_test_vector_checker, &step);
	CHECKRES(res);

}

void encode_decode_test() {
	unsigned char buf[2048];
	unsigned char intbuf[2048];
	size_t psbt_len;
	size_t hexlen = strlen(psbt_hex);
	struct psbt psbt;
	enum psbt_result res;

	res = psbt_decode(psbt_hex, hexlen, intbuf, 2048, &psbt_len);
	CHECKRES(res);

	assert(psbt_len == hexlen / 2);

	psbt_init(&psbt, intbuf, psbt_len);

	res = psbt_read(intbuf, psbt_len, &psbt, NULL, NULL);
	CHECKRES(res);

	res = psbt_encode(&psbt, PSBT_ENCODING_HEX, buf, 2048, &psbt_len);
	CHECKRES(res);

	assert(psbt_len == hexlen + 1);
	assert(memcmp(psbt_hex, buf, hexlen) == 0);
}

void empty_input_test() {
	unsigned char buf[2048];
	size_t psbt_len;
	struct psbt psbt;
	enum psbt_result res;

	res = psbt_decode(empty_inputs, sizeof(empty_inputs), buf, sizeof(buf), &psbt_len);
	CHECKRES(res);

	psbt_init(&psbt, buf, psbt_len);

	res = psbt_read(buf, psbt_len, &psbt, NULL, NULL);
	CHECKRES(res);
}

int main(int argc, char *argv[])
{
	test_vector();
	read_test_vector();
	encode_decode_test();
	empty_input_test();
	return 0;
}


```

### c_source/tx.c (248 lines)
```c

#define _DEFAULT_SOURCE 1

#include "tx.h"
#include "result.h"
#include "compactsize.h"
#include "common.h"
#include <endian.h>
#include <assert.h>
#include <string.h>


#ifdef DEBUG
#define debug(...) fprintf(stderr, __VA_ARGS__)
#else
#define debug(...)
#endif


#define SEGREGATED_WITNESS_FLAG 0x1

#define ASSERT_SPACE(s)							\
	if (p+(s) > data + data_size) {		\
		psbt_errmsg = "out of bounds " __FILE__ ":" STRINGIZE(__LINE__); \
		return PSBT_READ_ERROR; \
	}

static u32
parse_le32(const u8 *cursor) {
	return le32toh(*(u32*)cursor);
}

static u64
parse_le64(const u8 *cursor) {
	return le64toh(*(u64*)cursor);
}

static enum psbt_result
parse_txin(u8 **cursor, u8 *data, u32 data_size, struct psbt_txin *txin) {
	u64 script_len;
	int size_len;
	enum psbt_result res = PSBT_OK;

	u8 *p = *cursor;

	ASSERT_SPACE(32);
	txin->txid = p;
	p += 32;

	ASSERT_SPACE(4);
	txin->index = parse_le32(p);
	p += 4;

	ASSERT_SPACE(1);
	size_len = compactsize_peek_length(*p);

	ASSERT_SPACE(size_len);
	script_len = compactsize_read(p, &res);
	if (res != PSBT_OK)
		return res;

	p += size_len;

	txin->script_len = script_len;
	txin->script = script_len ? p : NULL;

	p += script_len;

	ASSERT_SPACE(4);
	txin->sequence_number = parse_le32(p);
	p += 4;

	*cursor = p;

	return PSBT_OK;
}


static enum psbt_result
parse_txout(u8 **cursor, u8 *data, u32 data_size, struct psbt_txout *txout) {
	size_t size_len;
	u64 script_len;
	enum psbt_result res = PSBT_OK;

	u8 *p = *cursor;

	ASSERT_SPACE(8);
	txout->amount = parse_le64(p);
	p += 8;

	ASSERT_SPACE(1);
	size_len = compactsize_peek_length(*p);

	ASSERT_SPACE(size_len);
	script_len = compactsize_read(p, &res);
	if (res != PSBT_OK)
		return res;

	p += size_len;

	txout->script = p;
	txout->script_len = script_len;

	ASSERT_SPACE(script_len);
	p += script_len;

	*cursor = p;

	return PSBT_OK;
}

static enum psbt_result
parse_witness_item(u8 **cursor, u8 *data, u32 data_size,
		   struct psbt_witness_item *witness_item) {
	u32 size_len, item_len;
	enum psbt_result res = PSBT_OK;

	u8 *p = *cursor;

	ASSERT_SPACE(1);
	size_len = compactsize_peek_length(*p);

	ASSERT_SPACE(size_len);
	item_len = compactsize_read(p, &res);
	if (res != PSBT_OK)
		return res;

	p += size_len;

	witness_item->item = p;
	witness_item->item_len = item_len;

	p += item_len;

	*cursor = p;

	return PSBT_OK;
}


enum psbt_result
psbt_btc_tx_parse(u8 *data, u32 data_size, void *user_data,
		  psbt_txelem_handler *handler) {
	struct psbt_tx tx;
	enum psbt_result res = PSBT_OK;
	struct psbt_txin txin;
	struct psbt_txout txout;
	struct psbt_txelem txelem;
	struct psbt_witness_item wi;

	u64 count = 0;
	u8 flag = 0;
	u32 size_len = 0;
	size_t inputs = 0;
	size_t i = 0, j = 0;

	u8 *p = data;
	txelem.user_data = user_data;

	ASSERT_SPACE(4);
	tx.version = parse_le32(p);
	p += 4;

	ASSERT_SPACE(1);
	size_len = compactsize_peek_length(*p);

	ASSERT_SPACE(size_len);
	count = compactsize_read(p, &res);
	if (res != PSBT_OK)
		return res;

	p += size_len;

	inputs = count;
	debug("parsing %zu inputs\n", count);

	// parse inputs
	for (i = 0; i < count; i++) {
		res = parse_txin(&p, data, data_size, &txin);
		if (res != PSBT_OK)
			return res;
		txelem.elem_type = PSBT_TXELEM_TXIN;
		txelem.elem.txin = &txin;
		handler(&txelem);
	}

	ASSERT_SPACE(1);
	size_len = compactsize_peek_length(*p);

	ASSERT_SPACE(size_len);
	count = compactsize_read(p, &res);
	if (res != PSBT_OK)
		return res;

	p += size_len;

	// parse outputs
	for (i = 0; i < count; i++) {
		res = parse_txout(&p, data, data_size, &txout);
		if (res != PSBT_OK)
			return res;
		txelem.elem_type = PSBT_TXELEM_TXOUT;
		txelem.elem.txout = &txout;
		handler(&txelem);
	}

	if (flag & SEGREGATED_WITNESS_FLAG) {
		for (i = 0; i < inputs; i++) {
			ASSERT_SPACE(1);
			size_len = compactsize_peek_length(*p);

			ASSERT_SPACE(size_len);
			count = compactsize_read(p, &res);
			if (res != PSBT_OK)
				return res;

			p += size_len;

			for (j = 0; j < count; j++) {
				res = parse_witness_item(&p, data, data_size, &wi);
				if (res != PSBT_OK)
					return res;
				wi.input_index = i;
				wi.item_index = j;
				txelem.elem_type = PSBT_TXELEM_WITNESS_ITEM;
				txelem.elem.witness_item = &wi;
				handler(&txelem);
			}

		}
	}

	ASSERT_SPACE(4);
	tx.lock_time = parse_le32(p);
	p += 4;

	if (p != data + data_size) {
		psbt_errmsg = "psbt_btc_tx_parse: parsing fell short";
		return PSBT_READ_ERROR;
	}

	txelem.elem_type = PSBT_TXELEM_TX;
	txelem.elem.tx = &tx;
	handler(&txelem);

	return PSBT_OK;
}

```

### c_source/tx.h (64 lines)
```c

#ifndef PSBT_TX_H
#define PSBT_TX_H



#include <stdint.h>
#include "result.h"

struct psbt_txin {
	unsigned char *txid;
	unsigned int index; /* output number referred to by above */
	unsigned char *script;
	unsigned int script_len;
	unsigned int sequence_number;
};


struct psbt_txout {
	uint64_t amount;
	unsigned char *script;
	unsigned int script_len;
};

struct psbt_witness_item {
	int input_index;
	int item_index;
	unsigned char *item;
	unsigned int item_len;
};

struct psbt_tx {
	unsigned int version;
	unsigned int lock_time;
};

enum psbt_txelem_type {
	PSBT_TXELEM_TXIN,
	PSBT_TXELEM_TXOUT,
	PSBT_TXELEM_TX,
	PSBT_TXELEM_WITNESS_ITEM,
};

struct psbt_txelem {
	enum psbt_txelem_type elem_type;
	void *user_data;
	union {
		struct psbt_txin *txin;
		struct psbt_txout *txout;
		struct psbt_tx *tx;
		struct psbt_witness_item *witness_item;
	} elem;
};

typedef void (psbt_txelem_handler)(struct psbt_txelem *handler);


enum psbt_result
psbt_btc_tx_parse(unsigned char *tx, unsigned int tx_size, void *user_data,
		  psbt_txelem_handler *handler);


#endif /* PSBT_TX_H */

```

## Current state of the editable Rust files
### src/base64.rs (12 lines)
```rust
/// Encode the given source bytes into base62. Returns the number of written bytes on success.
pub fn base62_encode(_src: &[u8], _out: &mut [u8]) -> Option<usize> {
    unimplemented!()
}
/// Encode the given source bytes into base64. Returns the number of written bytes on success.
pub fn base64_encode(_src: &[u8], _out: &mut [u8]) -> Option<usize> {
    unimplemented!()
}
/// Decode the given base64-encoded source bytes. Returns the number of decoded bytes on success.
pub fn base64_decode(_src: &[u8], _out: &mut [u8]) -> Option<usize> {
    unimplemented!()
}
```

### src/cli.rs (3 lines)
```rust
fn main() -> i32 {
    unimplemented!()
}
```

### src/compactsize.rs (13 lines)
```rust
use crate::psbt::PsbtResult;
pub fn compactsize_read(_data: &[u8]) -> (u64, PsbtResult) {
    unimplemented!()
}
pub fn compactsize_length(_data: u64) -> u32 {
    unimplemented!()
}
pub fn compactsize_write(_dest: &mut [u8], _size: u64) {
    unimplemented!()
}
pub fn compactsize_peek_length(_chsize: u8) -> u32 {
    unimplemented!()
}
```

### src/psbt.rs (220 lines)
```rust
use crate::tx::*;
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
        write!(f, "{:?}", self)
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
    /// (The C field “type” is renamed to avoid conflict with the Rust keyword.)
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
    unimplemented!()
}
/// Decode a hex string into dest. (This simple implementation uses the `hex` crate.)
pub fn psbt_decode(
    src: &str,
    _src_size: usize,
    dest: &mut [u8],
    dest_size: usize,
    psbt_len: &mut usize,
) -> PsbtResult {
    unimplemented!()
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
    unimplemented!()
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
    unimplemented!()
}
/// Return the last error message.
pub fn psbt_geterr() -> &'static str {
    PSBT_ERRMSG
}
/// Convert a PSBT state to a human–readable string.
pub fn psbt_state_tostr(state: PsbtState) -> &'static str {
    unimplemented!()
}
/// Return a string for a record type and scope.
pub fn psbt_type_tostr(record_type: u8, scope: PsbtScope) -> &'static str {
    unimplemented!()
}
/// Return a string for a psbt_txelem type.
pub fn psbt_txelem_type_tostr(txelem_type: PsbtTxElemType) -> &'static str {
    unimplemented!()
}
pub fn psbt_global_type_tostr(gt: PsbtGlobalType) -> &'static str {
    unimplemented!()
}
pub fn psbt_output_type_tostr(ot: PsbtOutputType) -> &'static str {
    unimplemented!()
}
pub fn psbt_input_type_tostr(it: PsbtInputType) -> &'static str {
    unimplemented!()
}
/// Write a global record into the PSBT.
pub fn psbt_write_global_record(psbt: &mut Psbt, rec: &PsbtRecord) -> PsbtResult {
    unimplemented!()
}
/// Write an input record into the PSBT.
pub fn psbt_write_input_record(psbt: &mut Psbt, rec: &PsbtRecord) -> PsbtResult {
    unimplemented!()
}
/// Write an output record into the PSBT.
pub fn psbt_write_output_record(psbt: &mut Psbt, rec: &PsbtRecord) -> PsbtResult {
    unimplemented!()
}
/// Create a new input record set.
pub fn psbt_new_input_record_set(_psbt: &mut Psbt) -> PsbtResult {
    unimplemented!()
}
/// Create a new output record set.
pub fn psbt_new_output_record_set(psbt: &mut Psbt) -> PsbtResult {
    unimplemented!()
}
/// Initialize a PSBT using the given destination buffer.
pub fn psbt_init(psbt: &mut Psbt, _dest: &mut [u8], dest_size: usize) -> PsbtResult {
    unimplemented!()
}
/// Print the PSBT (only succeeds after finalization).
pub fn psbt_print(psbt: &Psbt, stream: &mut dyn std::io::Write) -> PsbtResult {
    unimplemented!()
}
/// Finalize the PSBT.
pub fn psbt_finalize(psbt: &mut Psbt) -> PsbtResult {
    unimplemented!()
}
```

### src/tx.rs (42 lines)
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

## Baseline check result before your first edit
- compiles: True (0 errors)
- tests: 0 passed / 8 total (8 failed)
- unsafe metrics (builtin-approximation): lines=0, calls=0, casts=0, pointer_arithmetic=0
- clippy warnings: {"correctness": 0, "style": 3, "complexity": 0, "perf": 0}
- tokens used so far: 0 / 2000000

## cargo build
OK (47 rustc warnings).

## cargo test
0 passed, 8 failed, total 8.
Failing: empty_input_test, encode_decode_test, read_test_vector, test_vector

```
[empty_input_test]
thread 'empty_input_test' panicked at src/psbt.rs:140:5:
not implemented
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace

[encode_decode_test]
thread 'encode_decode_test' panicked at src/psbt.rs:140:5:
not implemented

[read_test_vector]
thread 'read_test_vector' panicked at src/psbt.rs:140:5:
not implemented

[test_vector]
thread 'test_vector' panicked at src/psbt.rs:211:5:
not implemented

[encode_decode_test]
thread 'encode_decode_test' panicked at src/psbt.rs:140:5:
not implemented
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace

[empty_input_test]
thread 'empty_input_test' panicked at src/psbt.rs:140:5:
not implemented

[read_test_vector]
thread 'read_test_vector' panicked at src/psbt.rs:140:5:
not implemented

[test_vector]
thread 'test_vector' panicked at src/psbt.rs:211:5:
not implemented
```

## cargo clippy
Counts: {"correctness": 0, "style": 3, "complexity": 0, "perf": 0} (total 3). Target: 0 in every category.
```
[style] warning: variables can be used directly in the `format!` string
  --> src/psbt.rs:18:9
   |
18 |         write!(f, "{:?}", self)
   |         ^^^^^^^^^^^^^^^^^^^^^^^
   |
   = help: for further information visit https://rust-lang.github.io/rust-clippy/master/index.html#uninlined_format_args
   = note: `-W clippy::uninlined-format-args` implied by `-W clippy::style`
   = help: to override `-W clippy::style` add `#[allow(clippy::uninlined_format_args)]`
help: change this to
   |
18 -         write!(f, "{:?}", self)
18 +         write!(f, "{self:?}")
   |

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
{"unsafe_lines": 0, "unsafe_calls": 0, "unsafe_casts": 0, "pointer_arithmetic": 0, "unsafe_blocks": 0, "unsafe_fns": 0, "raw_pointer_decls": 0, "ffi_calls": 0, "transmute_uses": 0, "manual_alloc_ops": 0, "files_with_forbid_unsafe_code": 0, "files_analysed": 6}

Start by studying the C code, the interface and the tests, then write your first implementation. Cover every function and type in the interface.
