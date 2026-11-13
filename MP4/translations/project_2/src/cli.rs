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
