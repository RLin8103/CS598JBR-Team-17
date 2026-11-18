//! Separate evaluation harness. No supplied benchmark files are changed.

#[cfg(test)]
mod tests {
    use libpsbt::base64::{base62_encode, base64_encode};
    use libpsbt::compactsize::compactsize_write;
    use libpsbt::psbt::*;
    use libpsbt::tx::PsbtTxElem;

    fn transaction() -> Vec<u8> {
        let mut tx = 2u32.to_le_bytes().to_vec();
        tx.push(2);
        for index in 0u32..2 {
            tx.extend([0x11; 32]);
            tx.extend(index.to_le_bytes());
            tx.push(0); // empty script
            tx.extend(u32::MAX.to_le_bytes());
        }
        tx.push(2);
        for amount in [7u64, 9] {
            tx.extend(amount.to_le_bytes());
            tx.push(0);
        }
        tx.extend(0u32.to_le_bytes());
        tx
    }

    fn record(out: &mut Vec<u8>, kind: u8, value: &[u8]) {
        assert!(value.len() < 253);
        out.extend([1, kind, value.len() as u8]);
        out.extend(value);
    }

    fn multi_map() -> Vec<u8> {
        let mut data = b"psbt\xff".to_vec();
        record(&mut data, 0, &transaction());
        record(&mut data, 0x99, &[1]);
        data.push(0);
        for _ in 0..2 {
            record(&mut data, 4, &[0x51]);
            record(&mut data, 5, &[0x52]);
            data.push(0);
        }
        for _ in 0..2 {
            record(&mut data, 0, &[0x51]);
            record(&mut data, 1, &[0x52]);
            data.push(0);
        }
        data
    }

    fn collect(elem: &mut PsbtElem, data: &mut dyn std::any::Any) {
        let events = data.downcast_mut::<Vec<String>>().unwrap();
        match elem {
            PsbtElem::Record { index, record } => events.push(format!("record:{:?}:{index}:{}", record.scope, record.record_type)),
            // The C forwarding wrapper does not initialize psbt_elem.index for transaction
            // events. Assert kinds/order; do not invent a C expectation for that index.
            PsbtElem::TxElem { txelem, .. } => events.push(match txelem {
                PsbtTxElem::TxIn(_) => "txin",
                PsbtTxElem::TxOut(_) => "txout",
                PsbtTxElem::Tx(_) => "tx",
                PsbtTxElem::WitnessItem(_) => "witness",
            }.to_string()),
        }
    }

    fn read_events() -> (PsbtResult, Vec<String>, Psbt) {
        let data = multi_map();
        let mut psbt = Psbt::new(data.len());
        let mut events = Vec::<String>::new();
        let result = psbt_read(&data, data.len(), &mut psbt, Some(collect), &mut events);
        (result, events, psbt)
    }

    #[test]
    fn multiple_maps_preserve_all_records_and_scopes() {
        let (result, _, psbt) = read_events();
        assert_eq!(result, PsbtResult::Ok, "two input and two output maps, two records each");
        let counts = [PsbtScope::Global, PsbtScope::Inputs, PsbtScope::Outputs]
            .map(|scope| psbt.records.iter().filter(|r| r.scope == scope).count());
        assert_eq!(counts, [2, 4, 4], "record totals in [global, input, output] scopes");
    }

    #[test]
    fn record_callback_indices_for_multi_map_fixture() {
        let (result, events, _) = read_events();
        assert_eq!(result, PsbtResult::Ok, "callback fixture with two input and two output maps");
        let records: Vec<_> = events.iter().filter(|e| e.starts_with("record:")).map(String::as_str).collect();
        assert_eq!(records, ["record:Global:0:0", "record:Global:0:153",
            "record:Inputs:0:4", "record:Inputs:0:5", "record:Inputs:1:4", "record:Inputs:1:5",
            "record:Outputs:0:0", "record:Outputs:0:1", "record:Outputs:1:0", "record:Outputs:1:1"]);
    }

    #[test]
    fn transaction_callbacks_precede_unsigned_record() {
        let (_, events, _) = read_events();
        assert!(events.starts_with(&["txin", "txin", "txout", "txout", "tx", "record:Global:0:0"].map(String::from)),
            "expected prefix [txin, txin, txout, txout, tx, record:Global:0:0], observed {events:?}");
    }

    #[test]
    fn read_rejects_length_larger_than_backing_slice() {
        let bytes = multi_map();
        let mut psbt = Psbt::new(bytes.len() + 1);
        assert_ne!(psbt_read(&bytes, bytes.len() + 1, &mut psbt, None, &mut ()), PsbtResult::Ok,
            "declared length {}, backing slice length {}", bytes.len() + 1, bytes.len());
    }

    #[test]
    fn decode_honors_input_prefix() {
        let mut dest = [0u8; 20]; let mut len = 0;
        assert_eq!(psbt_decode("70736274ffNOT_HEX", 10, &mut dest, 20, &mut len), PsbtResult::Ok,
            "input 70736274ffNOT_HEX, declared source length 10, destination capacity 20");
        assert_eq!((&dest[..len], len), (&b"psbt\xff"[..], 5));
    }

    #[test]
    fn decode_rejects_oversized_source_length() {
        let mut dest = [0u8; 20]; let mut len = 0;
        assert_ne!(psbt_decode("70736274ff", 11, &mut dest, 20, &mut len), PsbtResult::Ok,
            "hex input has 10 bytes, declared source length is 11, destination capacity 20");
    }

    #[test]
    fn decode_hex_checks_actual_destination() {
        let mut dest = [0u8; 1]; let mut len = 0;
        assert_ne!(psbt_decode("70736274ff", 10, &mut dest, 20, &mut len), PsbtResult::Ok);
    }

    #[test]
    fn decode_base64_honors_declared_destination_limit() {
        let mut dest = [0xabu8; 20]; let mut len = 0;
        assert_ne!(psbt_decode("cHNidP8=", 8, &mut dest, 1, &mut len), PsbtResult::Ok,
            "input cHNidP8=, declared destination capacity 1, backing slice capacity 20");
        assert_eq!(&dest[1..], &[0xab; 19]);
    }

    #[test]
    fn malformed_hex_and_non_ascii_return_errors() {
        for text in ["70736z74ff", "ééééé", "😀😀", "70736274f"] {
            let mut dest = [0u8; 32]; let mut len = 0;
            assert_ne!(psbt_decode(text, text.len(), &mut dest, 32, &mut len), PsbtResult::Ok, "{text}");
        }
    }

    #[test]
    fn encode_honors_input_prefix() {
        let mut dest = [0u8; 32]; let mut len = 0;
        assert_eq!(psbt_encode_raw(&[0x12, 0x34, 0xff], 2, PsbtEncoding::Hex, &mut dest, 32, &mut len), PsbtResult::Ok);
        assert_eq!(&dest[..len], b"1234\0", "hex encoding [0x12, 0x34, 0xff] with declared source length 2");
    }

    #[test]
    fn encode_rejects_oversized_source_length() {
        let mut dest = [0u8; 32]; let mut len = 0;
        assert_ne!(psbt_encode_raw(&[0x12], 2, PsbtEncoding::Hex, &mut dest, 32, &mut len), PsbtResult::Ok,
            "hex source [0x12] with declared source length 2");
    }

    #[test]
    fn encode_hex_checks_actual_destination() {
        let mut dest = [0u8; 1]; let mut len = 0;
        assert_ne!(psbt_encode_raw(&[0x12, 0x34], 2, PsbtEncoding::Hex, &mut dest, 32, &mut len), PsbtResult::Ok);
    }

    #[test]
    fn encode_base64_honors_declared_limit() {
        let mut dest = [0xabu8; 32]; let mut len = 0;
        assert_ne!(psbt_encode_raw(&[0x12, 0x34], 2, PsbtEncoding::Base64, &mut dest, 1, &mut len), PsbtResult::Ok,
            "Base64 source [0x12, 0x34], declared destination capacity 1, backing slice capacity 32");
        assert_eq!(&dest[1..], &[0xab; 31]);
    }

    #[test]
    fn encode_base62_honors_declared_limit() {
        let mut dest = [0xabu8; 32]; let mut len = 0;
        assert_ne!(psbt_encode_raw(&[0x12, 0x34], 2, PsbtEncoding::Base62, &mut dest, 1, &mut len), PsbtResult::Ok,
            "Base62 source [0x12, 0x34], declared destination capacity 1, backing slice capacity 32");
        assert_eq!(&dest[1..], &[0xab; 31]);
    }

    #[test]
    fn base62_defined_table_indices_match_c() {
        let mut out = [0u8; 20];
        assert_eq!(base62_encode(&[0xf4, 0, 0], &mut out), Some(4)); // first index 61
        assert_eq!(&out[..5], b"z000\0");
    }

    #[test]
    fn base62_undefined_c_index_63_returns_failure_without_panic() {
        // C indexes beyond its 63-byte array (62 symbols plus NUL). There is no
        // reference encoding here: test checked failure, not invented digits.
        assert_eq!(base62_encode(&[0xff], &mut [0u8; 20]), None);
    }

    #[test]
    fn base62_ambiguous_index_62_returns_failure_without_panic() {
        // C reads its terminating NUL at index 62. Await instructor encoding choice.
        assert_eq!(base62_encode(&[0xf8], &mut [0u8; 20]), None);
    }

    #[test]
    fn base64_known_defined_c_output() {
        let mut out = [0u8; 20];
        assert_eq!(base64_encode(b"psbt\xff", &mut out), Some(8));
        assert_eq!(&out[..9], b"cHNidP8=\0");
    }

    #[test]
    fn unknown_global_type_label() {
        assert_eq!(psbt_type_tostr(0x99, PsbtScope::Global), "UNKNOWN_GLOBAL_TYPE");
    }

    #[test]
    fn errors_include_useful_context() {
        let result = psbt_encode(&Psbt::new(32), PsbtEncoding::Hex, &mut [0u8; 32], 32, &mut 0);
        assert_eq!(result, PsbtResult::WriteError);
        let error = psbt_geterr();
        assert!(error.contains("finaliz"), "encoding a fresh PSBT, expected finalization context, got {error:?}");
    }

    #[test]
    fn compactsize_exact_buffers() {
        for (value, expected) in [(252, vec![252]), (253, vec![253, 253, 0]), (65536, vec![254, 0, 0, 1, 0])] {
            let mut out = vec![0u8; expected.len()];
            compactsize_write(&mut out, value);
            assert_eq!(out, expected);
        }
    }

    #[test]
    fn cset_padding_free_copy_generic() {
        let mut set = cset::cset::Cset::<[u8; 8]>::new();
        set.add([3; 8]); set.add([4; 8]);
        assert!(set.contains(&[3; 8]));
        assert_eq!(set.iter().len(), 2);
    }

    fn compare_cset_hashes(length: usize, h_variant: bool) {
        let path = std::env::var("MP4_CSET_ORACLE").expect("run src/run_regressions.py to generate the C oracle");
        let text = std::fs::read_to_string(path).unwrap();
        let data: Vec<u8> = (0..96).collect();
        let mut differences = Vec::new();
        let mut seeds = Vec::new();
        for line in text.lines() {
            let row: Vec<_> = line.split_whitespace().collect();
            let len: usize = row[0].parse().unwrap();
            if len != length { continue; }
            let seed: u64 = row[1].parse().unwrap();
            seeds.push(seed);
            let h1: u64 = row[2].parse().unwrap();
            let h2: u64 = row[3].parse().unwrap();
            // Valid initialized array, bounded len, no uninitialized generic padding.
            let (actual, expected) = if h_variant {
                (cset::cset::xxh64_h(data.as_ptr(), len, seed), h2)
            } else {
                (cset::cset::xxh64(data.as_ptr(), len, seed), h1)
            };
            if actual != expected {
                differences.push(format!("len={len} seed={seed}: Rust={actual}, C={expected}"));
            }
        }
        assert_eq!(seeds, [0, 2718182]);
        assert!(differences.is_empty(), "input bytes 0..96, truncated to len:\n{}", differences.join("\n"));
    }
    macro_rules! hash_cases {
        ($($standard:ident, $h_variant:ident: $length:literal),* $(,)?) => {
            $(
                #[test] fn $standard() { compare_cset_hashes($length, false); }
                #[test] fn $h_variant() { compare_cset_hashes($length, true); }
            )*
        };
    }

    hash_cases!(
        cset_hash_00, cset_hash_h_00: 0, cset_hash_01, cset_hash_h_01: 1,
        cset_hash_02, cset_hash_h_02: 2, cset_hash_07, cset_hash_h_07: 7,
        cset_hash_08, cset_hash_h_08: 8, cset_hash_15, cset_hash_h_15: 15,
        cset_hash_16, cset_hash_h_16: 16, cset_hash_31, cset_hash_h_31: 31,
        cset_hash_32, cset_hash_h_32: 32, cset_hash_33, cset_hash_h_33: 33,
        cset_hash_63, cset_hash_h_63: 63, cset_hash_64, cset_hash_h_64: 64,
        cset_hash_80, cset_hash_h_80: 80, cset_hash_96, cset_hash_h_96: 96,
    );
}
