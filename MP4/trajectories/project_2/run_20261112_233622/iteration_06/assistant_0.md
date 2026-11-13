The previous edit failed because its search text did not match the current file. I'll replace the one remaining stub, `src/cli.rs`, as a whole file, which avoids the mismatch.

The `read_test_vector` failure is a bug in the test, not in the translation. Its `checker` matches on a local `step` that is always 0, so it asserts `record_type == 0` for every record. The PSBT contains input records of type 4 (`PSBT_IN_REDEEM_SCRIPT`), so the assertion fails on them. The C test used a shared counter, which the Rust fn-pointer handler cannot reproduce. Making that test pass would require suppressing records, which would not be a faithful translation, so I'm leaving it failing.

<file path="src/cli.rs">
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
</file>

<notes>
- Done: src/cli.rs implemented (decode, init, read, encode base62, print). Verify it compiles.
- Open: `read_test_vector` fails because the test's checker matches on a local `step` (always 0) and asserts `record_type == 0` for every record, but the PSBT has type-4 input records. This is a test bug; the translation itself follows C. Do not special-case it.
- Remaining work: check for any other `unimplemented!()`/`todo!()`; fix the 2 clippy style warnings only if they are in src (they are in src/bin/test.rs, which is protected).
- Possible cleanup: psbt.rs uses a `write!` on `&mut dyn io::Write` and `psbt.records` duplicates data; keep unsafe at zero.
</notes>