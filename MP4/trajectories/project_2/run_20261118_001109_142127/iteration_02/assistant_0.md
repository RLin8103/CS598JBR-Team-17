<read path="src/bin/test.rs"/>
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

We need to see line 126. Let's count lines. The file is large. Let's open a snippet around line 120-130.<read path="src/bin/test.rs" start="120" end="140"/>
```rust
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
```

The error is at line 126: `assert_eq!(record.record_type, 0), // PSBT_GLOBAL_UNSIGNED_TX`. So the record_type is not 0. The test expects the first record to be type 0 (global unsigned tx). The second record also type 0 (input non-witness utxo). But our implementation seems to produce a different record_type.

Let's examine the PSBT_HEX. It's a hex string of a PSBT. The first record after the header is a global record (type 0). The second record is an input record (type 0? Actually PSBT_IN_NON_WITNESS_UTXO is 0). So both are type 0. The test expects that.

Our psbt_read implementation seems to parse records incorrectly. Let's examine the psbt_read function in src/psbt.rs. It reads header, then loops. It reads records via read_record. The read_record uses compactsize_read to read key length, then reads type, key, value length, value. It pushes a PsbtRecord with record_type = the byte after key length. That matches the C code: key length includes type byte? In C, the key includes the type byte? Let's check C code: In psbt.c, psbt_read_record: size = compactsize_read(...); rec->key_size = size - 1; rec->type = *tx->write_pos; rec->key = tx->write_pos + 1; So key includes type byte. So our Rust implementation matches that: key_size_with_type = key_size + 1? Wait we used compactsize_read to get key_size (size). Then we treat key_size as size (including type). In read_record we did:

```
let (key_size, res) = compactsize_read(&psbt.data[psbt.write_pos..]);
...
let key_with_type = key_size as usize;
let record_type = psbt.data[psbt.write_pos];
let key_start = psbt.write_pos + 1;
let key_len = key_with_type - 1;
```

So record_type is the first byte of the key. That's correct.

Now the test expects record_type to be 0 for the first record. But our record_type is something else. Let's examine what the PSBT_HEX contains. The PSBT_HEX is the same as the test vector? Actually PSBT_HEX is a hex string of a PSBT that includes a global unsigned tx (type 0) and an input record (type 0). The test expects that the first record is type 0 (global). The second record is also type 0 (input). But our implementation might be reading the global record as type 0? Let's debug by printing the record_type values. But we cannot run interactive debugging. Instead, we need to examine the logic.

The test's checker function is called for each element. It expects the first record's record_type to be 0. The second record's record_type to be 0. But the test fails at the first assertion: left: 4 right: 0. So record_type is 4. That suggests that the first record is not the global unsigned tx but something else. Perhaps our parsing of the PSBT is off: maybe we are reading the global record incorrectly, or the PSBT_HEX is not the same as the test vector? Let's examine the PSBT_HEX string. It's a hex string of a PSBT that includes a global unsigned tx (type 0) and an input record (type 0). But maybe the global record's type is not 0? Let's decode the hex to see the raw bytes. But we can also look at the C test.c to see what PSBT_HEX is. In c_source/test.c, there is a static const char *psbt_hex = "70736274ff01009a020000000258e87a21b56daf0c23be8e7070456c336f7cbaa5c8757924f545887bb2abdd750000000000ffffffff838d0427d0ec650a68aa46bb0b098aea4422c071b2ca78352a077959d07cea1d0100000000ffffffff0270aaf00800000000160014d85c2b71d0060b09c9886aeb815e50991dda124d00e1f5050000000016001400aea9a2e5f0f876a588df5546e8742d1d87008f00000000000100bb0200000001aad73931018bd25f84ae400b68848be09db706eac2ac18298babee71ab656f8b0000000048473044022058f6fc7c6a33e1b31548d481c826c015bd30135aad42cd67790dab66d2ad243b02204a1ced2604c6735b6393e5b41691dd78b00f0c5942fb9f751856faa938157dba01feffffff0280f0fa020000000017a9140fb9463421696b82c833af241c78c17ddbde493487d0f20a270100000017a91429ca74f8a08f81999428185c97b5d852e4063f6187650000000104475221029583bf39ae0a609747ad199addd634fa6108559d6c5cd39b4c2183f1ab96e07f2102dab61ff49a14db6a7d02b0cd1fbb78fc4b18312b5b4e54dae4dba2fbfef536d752ae2206029583bf39ae0a609747ad199addd634fa6108559d6c5cd39b4c2183f1ab96e07f10d90c6a4f000000800000008000000080220602dab61ff49a14db6a7d02b0cd1fbb78fc4b18312b5b4e54dae4dba2fbfef536d710d90c6a4f0000008000000080010000800001012000c2eb0b0000000017a914b7f5faf40e3d40a5a459b1db3535f2b72fa921e88701042200208c2353173743b595dfb4a07b72ba8e42e3797da74e87fe7d9d7497e3b2028903010547522103089dc10c7ac6db54f91329af617333db388cead0c231f723379d1b99030b02dc21023add904f3d6dcf59ddb906b0dee23529b7ffb9ed50e5e86151926860221f0e7352ae2206023add904f3d6dcf59ddb906b0dee23529b7ffb9ed50e5e86151926860221f0e7310d90c6a4f000000800000008003000080220603089dc10c7ac6db54f91329af617333db388cead0c231f723379d1b99030b02dc10d90c6a4f00000080000000800200008000220203a9a4c37f5996d3aa25dbac6b570af0650394492942460b354753ed9eeca5877110d90c6a4f000000800000008004000080002202027f6399757d2eff55a136ad02c684b1838b6556e5f1b6b34282a94b6b5005109610d90c6a4f00000080000000800500008000";

We need to parse this. The PSBT format: magic (4 bytes) 70 73 62 74 = "psbt". Then 0xff. Then global records (key-value pairs). The first global record is type 0 (unsigned tx). The key is empty (size 0). The value is the transaction bytes. Then after global records, there is a null byte (0x00) to separate global from inputs. Then input records start. The first input record is type 0 (non-witness utxo). The key is empty. The value is the utxo (maybe 153 bytes?). Then after input records, there is a null byte to separate inputs from outputs. Then output records start. The first output record is type 4 (redeem script). The key is empty. The value is redeem script A (maybe 153 bytes?). Then second output record type 4 (redeem script B). Then after outputs, null byte to finalize.

Thus the first record after the header is global record type 0. The second record is input record type 0. So the test expects record_type 0 for both.

Our implementation seems to produce record_type 4 for the first record. That suggests that we are misinterpreting the first record: maybe we are reading the global record's key length incorrectly, causing the type byte to be something else. Let's examine the read_record function more closely.

In read_record:

```
let (key_size, res) = compactsize_read(&psbt.data[psbt.write_pos..]);
if res != PsbtResult::Ok { return Err(res); }
if key_size == 0 { return Err(PsbtResult::ReadError); }

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

...
```

So key_size is the size of the key including the type byte. For the global record, the key is empty, so key_size should be 1 (just the type byte). The type byte is 0. So record_type should be 0. But we got 4. That suggests that key_size is not 1 but maybe 5? Let's compute: The global record's key length (including type) is 1. The compactsize encoding of 1 is just 0x01 (since <253). So the first byte after header is 0x01. Then the type byte is 0x00. So record_type should be 0. But we got 4. That suggests that maybe we are reading the wrong byte as record_type: maybe we are reading the type byte of the next record? Or maybe the PSBT_HEX is different? Let's decode the hex string to see the raw bytes. But we can also look at the C code's test.c to see what the PSBT_HEX is. In c_source/test.c, there is a static const char *psbt_hex = "70736274ff01009a020000000258e87a21b56daf0c23be8e7070456c336f7cbaa5c8757924f545887bb2abdd750000000000ffffffff838d0427d0ec650a68aa46bb0b098aea4422c071b2ca78352a077959d07cea1d0100000000ffffffff0270aaf00800000000160014d85c2b71d0060b09c9886aeb815e50991dda124d00e1f5050000000016001400aea9a2e5f0f876a588df5546e8742d1d87008f00000000000100bb0200000001aad73931018bd25f84ae400b68848be09db706eac2ac18298babee71ab656f8b0000000048473044022058f6fc7c6a33e1b31548d481c826c015bd30135aad42cd67790dab66d2ad243b02204a1ced2604c6735b6393e5b41691dd78b00f0c5942fb9f751856faa938157dba01feffffff0280f0fa020000000017a9140fb9463421696b82c833af241c78c17ddbde493487d0f20a270100000017a91429ca74f8a08f81999428185c97b5d852e4063f6187650000000104475221029583bf39ae0a609747ad199addd634fa6108559d6c5cd39b4c2183f1ab96e07f2102dab61ff49a14db6a7d02b0cd1fbb78fc4b18312b5b4e54dae4dba2fbfef536d752ae2206029583bf39ae0a609747ad199addd634fa6108559d6c5cd39b4c2183f1ab96e07f10d90c6a4f000000800000008000000080220602dab61ff49a14db6a7d02b0cd1fbb78fc4b18312b5b4e54dae4dba2fbfef536d710d90c6a4f0000008000000080010000800001012000c2eb0b0000000017a914b7f5faf40e3d40a5a459b1db3535f2b72fa921e88701042200208c2353173743b595dfb4a07b72ba8e42e3797da74e87fe7d9d7497e3b2028903010547522103089dc10c7ac6db54f91329af617333db388cead0c231f723379d1b99030b02dc21023add904f3d6dcf59ddb906b0dee23529b7ffb9ed50e5e86151926860221f0e7352ae2206023add904f3d6dcf59ddb906b0dee23529b7ffb9ed50e5e86151926860221f0e7310d90c6a4f000000800000008003000080220603089dc10c7ac6db54f91329af617333db388cead0c231f723379d1b99030b02dc10d90c6a4f00000080000000800200008000220203a9a4c37f5996d3aa25dbac6b570af0650394492942460b354753ed9eeca5877110d90c6a4f000000800000008004000080002202027f6399757d2eff55a136ad02c684b1838b6556e5f1b6b34282a94b6b5005109610d90c6a4f00000080000000800500008000";

We need to parse this. Let's write a small Rust program to decode the hex and print the bytes. But we cannot run arbitrary code. However, we can manually decode a few bytes. The hex string starts with "70736274ff01009a020000000258e87a21b56daf0c23be8e7070456c336f7cbaa5c8757924f545887bb2abdd750000000000ffffffff838d0427d0ec650a68aa46bb0b098aea4422c071b2ca78352a077959d07cea1d0100000000ffffffff0270aaf00800000000160014d85c2b71d0060b09c9886aeb815e50991dda124d00e1f5050000000016001400aea9a2e5f0f876a588df5546e8742d1d87008f00000000000100bb0200000001aad73931018bd25f84ae400b68848be09db706eac2ac18298babee71ab656f8b0000000048473044022058f6fc7c6a33e1b31548d481c826c015bd30135aad42cd67790dab66d2ad243b02204a1ced2604c6735b6393e5b41691dd78b00f0c5942fb9f751856faa938157dba01feffffff0280f0fa020000000017a9140fb9463421696b82c833af241c78c17ddbde493487d0f20a270100000017a91429ca74f8a08f81999428185c97b5d852e4063f6187650000000104475221029583bf39ae0a609747ad199addd634fa6108559d6c5cd39b4c2183f1ab96e07f2102dab61ff49a14db6a7d02b0cd1fbb78fc4b18312b5b4e54dae4dba2fbfef536d752ae2206029583bf39ae0a609747ad199addd634fa6108559d6c5cd39b4c2183f1ab96e07f10d90c6a4f000000800000008000000080220602dab61ff49a14db6a7d02b0cd1fbb78fc4b18312b5b4e54dae4dba2fbfef536d710d90c6a4f0000008000000080010000800001012000c2eb0b0000000017a914b7f5faf40e3d40a5a459b1db3535f2b72fa921e88701042200208c2353173743b595dfb4a07b72ba8e42e3797da74e87fe7d9d7497e3b2028903010547522103089dc10c7ac6db54f91329af617333db388cead0c231f723379d1b99030b02dc21023add904f3d6dcf59ddb906b0dee23529b7ffb9ed50e5e86151926860221f0e7352ae2206023add904f3d6dcf59ddb906b0dee23529b7ffb9ed50e5e86151926860221f0e7310d90c6a4f000000800000008003000080220603089dc10c7ac6db54f91329af617333db388cead0c231f723379d1b99030b02dc10d90c6a4f00000080000000800200008000220203a9a4c37f5996d3aa25dbac6b570af0650394492942460b354753ed9eeca5877110d90c6a4f000000800000008004000080002202027f6399757d2eff55a136ad02c684b1838b6556e5f1b6b34282a94b6b5005109610d90c6a4f00000080000000800500008000";

Let's decode the first few bytes manually. "70" = 0x70, "73" = 0x73, "62" = 0x62, "74" = 0x74 => magic "psbt". Then "ff" = 0xff. Then "01" = 0x01 (key length). Then "09" = 0x09 (type? Actually type is next byte). Wait after key length, the next byte is the type. So after "01", the next byte is "09"? Actually the hex string after "ff" is "01009a...". So "01" is key length (1). Then "00" is type (0). Then "9a" is start of value? Actually the value is the transaction bytes. So the global record's key is empty (type 0). So the first record's type is 0. Good.

Now the second record: after the global record's value, there is a null byte to separate global from inputs. The hex string after the global record's value? Let's decode more. The global record's value is the transaction bytes. The transaction bytes start with "9a020000000258e87a21b56daf0c23be8e7070456c336f7cbaa5c8757924f545887bb2abdd750000000000ffffffff838d0427d0ec650a68aa46bb0b098aea4422c071b2ca78352a077959d07cea1d0100000000ffffffff0270aaf00800000000160014d85c2b71d0060b09c9886aeb815e50991dda124d00e1f5050000000016001400aea9a2e5f0f876a588df5546e8742d1d87008f00000000000100bb0200000001aad73931018bd25f84ae400b68848be09db706eac2ac18298babee71ab656f8b0000000048473044022058f6fc7c6a33e1b31548d481c826c015bd30135aad42cd67790dab66d2ad243b02204a1ced2604c6735b6393e5b41691dd78b00f0c5942fb9f751856faa938157dba01feffffff0280f0fa020000000017a9140fb9463421696b82c833af241c78c17ddbde493487d0f20a270100000017a91429ca74f8a08f81999428185c97b5d852e4063f6187650000000104475221029583bf39ae0a609747ad199addd634fa6108559d6c5cd39b4c2183f1ab96e07f2102dab61ff49a14db6a7d02b0cd1fbb78fc4b18312b5b4e54dae4dba2fbfef536d752ae2206029583bf39ae0a609747ad199addd634fa6108559d6c5cd39b4c2183f1ab96e07f10d90c6a4f000000800000008000000080220602dab61ff49a14db6a7d02b0cd1fbb78fc4b18312b5b4e54dae4dba2fbfef536d710d90c6a4f0000008000000080010000800001012000c2eb0b0000000017a914b7f5faf40e3d40a5a459b1db3535f2b72fa921e88701042200208c2353173743b595dfb4a07b72ba8e42e3797da74e87fe7d9d7497e3b2028903010547522103089dc10c7ac6db54f91329af617333db388cead0c231f723379d1b99030b02dc21023add904f3d6dcf59ddb906b0dee23529b7ffb9ed50e5e86151926860221f0e7352ae2206023add904f3d6dcf59ddb906b0dee23529b7ffb9ed50e5e86151926860221f0e7310d90c6a4f000000800000008003000080220603089dc10c7ac6db54f91329af617333db388cead0c231f723379d1b99030b02dc10d90c6a4f00000080000000800200008000220203a9a4c37f5996d3aa25dbac6b570af0650394492942460b354753ed9eeca5877110 probably too long.

Anyway, the first record's type is 0. So why our record_type is 4? Let's examine our read_record function again. Perhaps we are misreading the key length: maybe we are reading the key length incorrectly because we are using compactsize_read which returns (size, result). But we also need to advance the write_pos by size_len before reading key? Actually we do:

```
let (key_size, res) = compactsize_read(&psbt.data[psbt.write_pos..]);
if res != PsbtResult::Ok { return Err(res); }
if key_size == 0 { return Err(PsbtResult::ReadError); }

let size_len = compactsize_peek_length(psbt.data[psbt.write_pos]);
psbt.write_pos += size_len as usize;
```

But note: we call compactsize_read on the slice starting at psbt.write_pos. compactsize_read reads the first byte and returns the size and result. However, we also need to advance the write_pos by the size of the compactsize encoding (size_len). The compactsize_peek_length function returns the length of the encoding given the first byte. So we compute size_len based on the first byte (which we haven't consumed yet). Then we advance write_pos by size_len. That's correct.

But there is a bug: we are using psbt.data[psbt.write_pos] after we have advanced write_pos? Actually we compute size_len before advancing, then we advance. Then we check if write_pos + key_size > src_size. But key_size is the size returned by compactsize_read, which is the size of the key (including type). However, we have already advanced write_pos by size_len, which is the length of the compactsize encoding. So the key data (including type) starts at the new write_pos. That's correct.

Now we read record_type = psbt.data[psbt.write_pos]; That's the first byte of the key (type). So for the global record, record_type should be 0. But we got 4. That suggests that maybe the key_size is not 1 but something else, causing the type byte to be something else. Let's compute: The global record's key length (including type) is 1. The compactsize encoding of 1 is just 0x01 (size_len = 1). So after reading key_size = 1, we advance write_pos by 1 (size_len). Then record_type = psbt.data[psbt.write_pos]; That's the byte after the compactsize encoding. That should be 0. But we got 4. That suggests that maybe the compactsize encoding is not 0x01 but something else. Let's look at the hex after the header: "ff01009a