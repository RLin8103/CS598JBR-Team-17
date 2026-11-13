use crate::psbt::{
    psbt_decode, psbt_encode, psbt_geterr, psbt_init, psbt_read, psbt_type_tostr, Psbt,
    PsbtElem, PsbtEncoding, PsbtResult,
};
use std::any::Any;

/// Print a record in the same layout as `print_rec` in cli.c.
fn print_elem(elem: &mut PsbtElem, _user_data: &mut dyn Any) {
    if let PsbtElem::Record { index, record } = elem {
        let type_str = psbt_type_tostr(record.record_type, record.scope.clone());
        print!("{type_str}\t{index} ");
        if !record.key.is_empty() {
            for b in &record.key {
                print!("{b:02x}");
            }
            print!(" ");
        }
        for b in &record.val {
            print!("{b:02x}");
        }
        println!();
    }
}

fn main() -> i32 {
    let args: Vec<String> = std::env::args().collect();
    let Some(arg) = args.get(1) else {
        println!("usage: psbt <psbt>");
        return 1;
    };

    const CAPACITY: usize = 4096;
    let mut buffer = vec![0u8; CAPACITY];
    let mut psbt_len = 0;
    let mut psbt = Psbt::new(CAPACITY);

    let res = psbt_decode(arg, arg.len(), &mut buffer, CAPACITY, &mut psbt_len);
    if res != PsbtResult::Ok {
        println!("error ({res}): {}. last_state = {:?}", psbt_geterr(), psbt.state);
        return 1;
    }

    let res = psbt_init(&mut psbt, &mut buffer, CAPACITY);
    if res != PsbtResult::Ok {
        return 1;
    }

    let res = psbt_read(&buffer, psbt_len, &mut psbt, Some(print_elem), &mut ());
    if res != PsbtResult::Ok {
        println!("error ({res}): {}. last_state = {:?}", psbt_geterr(), psbt.state);
        return 1;
    }

    let mut out = vec![0u8; CAPACITY];
    let mut out_len = 0;
    let res = psbt_encode(&psbt, PsbtEncoding::Base62, &mut out, CAPACITY, &mut out_len);
    if res != PsbtResult::Ok {
        println!("error ({res}): {}. last_state = {:?}", psbt_geterr(), psbt.state);
        return 1;
    }

    0
}
