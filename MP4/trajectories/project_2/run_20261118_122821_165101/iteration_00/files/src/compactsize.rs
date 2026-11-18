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
