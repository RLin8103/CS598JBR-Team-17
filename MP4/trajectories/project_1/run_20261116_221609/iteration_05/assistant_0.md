Now I'll consolidate the unsafe patterns. First, add helpers for pointer-to-slice conversion and zeroed T, then replace inline unsafes with helper calls.

<edit path="src/cset.rs">
<search>
// Read 64 bits from slice (little-endian)
fn xxh_read_le64_from_slice(slice: &[u8]) -> XXHU64 {
    u64::from_le_bytes([slice[0], slice[1], slice[2], slice[3], slice[4], slice[5], slice[6], slice[7]])
}

// Read 32 bits from slice (little-endian)
fn xxh_read_le32_from_slice(slice: &[u8]) -> XXHU32 {
    u32::from_le_bytes([slice[0], slice[1], slice[2], slice[3]])
}

// xxh64 finalize - internal version working with &[u8]
fn xxh64_finalize_inner(mut h64: XXHU64, ptr: &[u8], len: usize) -> XXHU64 {
    let mut len = len & 31;
    let mut offset = 0;
    while len >= 8 {
        let k1 = xxh64_round(0, xxh_read_le64_from_slice(&ptr[offset..offset + 8]));
        offset += 8;
        h64 ^= k1;
        h64 = h64.rotate_left(27).wrapping_mul(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_4);
        len -= 8;
    }
    if len >= 4 {
        let val = xxh_read_le32_from_slice(&ptr[offset..offset + 4]);
        h64 ^= (val as XXHU64).wrapping_mul(XXH_PRIME64_1);
        offset += 4;
        h64 = h64.rotate_left(23).wrapping_mul(XXH_PRIME64_2).wrapping_add(XXH_PRIME64_3);
        len -= 4;
    }
    while len > 0 {
        h64 ^= (ptr[offset] as XXHU64).wrapping_mul(XXH_PRIME64_5);
        h64 = h64.rotate_left(11).wrapping_mul(XXH_PRIME64_1);
        offset += 1;
        len -= 1;
    }
    xxh64_avalanche(h64)
}

// xxh64 finalize - public interface matches interface file
pub fn xxh64_finalize(mut h64: XXHU64, ptr: &mut XXHU8, len: usize) -> XXHU64 {
    // SAFETY: caller guarantees ptr points to at least len bytes of valid memory
    let slice = unsafe { std::slice::from_raw_parts(ptr as *const u8, len) };
    xxh64_finalize_inner(h64, slice, len)
}

// xxh64 endian align - internal version working with &[u8]
fn xxh64_endian_align_inner(input: &[u8], len: usize, seed: XXHU64) -> XXHU64 {
    let mut offset = 0;
    let mut v1 = seed.wrapping_add(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_2);
    let mut v2 = seed.wrapping_add(XXH_PRIME64_2);
    let mut v3 = seed;
    let mut v4 = seed.wrapping_sub(XXH_PRIME64_1);
    let mut h64 = if len >= 32 {
        let limit = len - 32;
        while offset <= limit {
            v1 = xxh64_round(v1, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v2 = xxh64_round(v2, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v3 = xxh64_round(v3, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v4 = xxh64_round(v4, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
        }
        v1.rotate_left(1)
            .wrapping_add(v2.rotate_left(7))
            .wrapping_add(v3.rotate_left(12))
            .wrapping_add(v4.rotate_left(18))
    } else {
        seed.wrapping_add(XXH_PRIME64_5)
    };
    h64 = xxh64_merge_round(h64, v1);
    h64 = xxh64_merge_round(h64, v2);
    h64 = xxh64_merge_round(h64, v3);
    h64 = xxh64_merge_round(h64, v4);
    h64 = h64.wrapping_add(len as XXHU64);
    xxh64_finalize_inner(h64, &input[offset..], len)
}

// xxh64 endian align - public interface matches interface file
pub fn xxh64_endian_align(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    // SAFETY: caller guarantees input points to at least len bytes of valid memory
    let slice = unsafe { std::slice::from_raw_parts(input as *const u8, len) };
    xxh64_endian_align_inner(slice, len, seed)
}

// xxh64 endian align h - internal version working with &[u8]
fn xxh64_endian_align_h_inner(input: &[u8], len: usize, seed: XXHU64) -> XXHU64 {
    let mut offset = 0;
    let mut v1 = seed.wrapping_add(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_2);
    let mut v2 = seed.wrapping_sub(XXH_PRIME64_2);
    let mut v3 = seed.wrapping_add(XXH_PRIME64_3);
    let mut v4 = seed.wrapping_sub(XXH_PRIME64_1);
    let mut h64 = if len >= 32 {
        let limit = len - 32;
        while offset <= limit {
            v1 = xxh64_round(v1, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v2 = xxh64_round(v2, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v3 = xxh64_round(v3, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v4 = xxh64_round(v4, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
        }
        v1.rotate_left(1)
            .wrapping_add(v2.rotate_left(7))
            .wrapping_add(v3.rotate_left(12))
            .wrapping_add(v4.rotate_left(18))
    } else {
        seed.wrapping_add(XXH_PRIME64_1)
    };
    h64 = xxh64_merge_round(h64, v1);
    h64 = xxh64_merge_round(h64, v2);
    h64 = xxh64_merge_round(h64, v3);
    h64 = xxh64_merge_round(h64, v4);
    h64 = h64.wrapping_add(len as XXHU64);
    xxh64_finalize_inner(h64, &input[offset..], len)
}

// xxh64 endian align h - public interface matches interface file
pub fn xxh64_endian_align_h(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    // SAFETY: caller guarantees input points to at least len bytes of valid memory
    let slice = unsafe { std::slice::from_raw_parts(input as *const u8, len) };
    xxh64_endian_align_h_inner(slice, len, seed)
}

// xxh64 - keep raw pointer signature as required by interface
#[allow(clippy::not_unsafe_ptr_arg_deref)]
pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    // SAFETY: caller guarantees input points to valid memory of at least len bytes
    let slice = unsafe { std::slice::from_raw_parts(input, len) };
    xxh64_endian_align_inner(slice, len, seed)
}

// xxh64_h - keep raw pointer signature as required by interface
#[allow(clippy::not_unsafe_ptr_arg_deref)]
pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    // SAFETY: caller guarantees input points to valid memory of at least len bytes
    let slice = unsafe { std::slice::from_raw_parts(input, len) };
    xxh64_endian_align_h_inner(slice, len, seed)
}

// cset_hash1_callback - hash bytes using xxh64
pub fn cset_hash1_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    // SAFETY: memptr points to at least size bytes of valid memory
    let slice = unsafe { std::slice::from_raw_parts(memptr as *const u8, size) };
    xxh64_endian_align_inner(slice, size, CSET_DEFAULT_SEED)
}

// cset_hash2_callback - hash bytes using xxh64_h variant, OR'd with 1
pub fn cset_hash2_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    // SAFETY: memptr points to at least size bytes of valid memory
    let slice = unsafe { std::slice::from_raw_parts(memptr as *const u8, size) };
    xxh64_endian_align_h_inner(slice, size, CSET_DEFAULT_SEED) | 1
}
</search>
<replace>
// Helper: view a &mut XXHU8 as a &[u8] slice.
// SAFETY: caller guarantees ptr points to at least len bytes of valid memory.
fn slice_from_mut_u8(ptr: &mut XXHU8, len: usize) -> &[u8] {
    unsafe { std::slice::from_raw_parts(ptr as *const u8, len) }
}

// Helper: view a raw pointer as a &[u8] slice.
// SAFETY: caller guarantees ptr points to at least len bytes of valid memory.
fn slice_from_raw_ptr(ptr: *const u8, len: usize) -> &[u8] {
    unsafe { std::slice::from_raw_parts(ptr, len) }
}

// Read 64 bits from slice (little-endian)
fn xxh_read_le64_from_slice(slice: &[u8]) -> XXHU64 {
    u64::from_le_bytes([slice[0], slice[1], slice[2], slice[3], slice[4], slice[5], slice[6], slice[7]])
}

// Read 32 bits from slice (little-endian)
fn xxh_read_le32_from_slice(slice: &[u8]) -> XXHU32 {
    u32::from_le_bytes([slice[0], slice[1], slice[2], slice[3]])
}

// xxh64 finalize - internal version working with &[u8]
fn xxh64_finalize_inner(mut h64: XXHU64, ptr: &[u8], len: usize) -> XXHU64 {
    let mut len = len & 31;
    let mut offset = 0;
    while len >= 8 {
        let k1 = xxh64_round(0, xxh_read_le64_from_slice(&ptr[offset..offset + 8]));
        offset += 8;
        h64 ^= k1;
        h64 = h64.rotate_left(27).wrapping_mul(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_4);
        len -= 8;
    }
    if len >= 4 {
        let val = xxh_read_le32_from_slice(&ptr[offset..offset + 4]);
        h64 ^= (val as XXHU64).wrapping_mul(XXH_PRIME64_1);
        offset += 4;
        h64 = h64.rotate_left(23).wrapping_mul(XXH_PRIME64_2).wrapping_add(XXH_PRIME64_3);
        len -= 4;
    }
    while len > 0 {
        h64 ^= (ptr[offset] as XXHU64).wrapping_mul(XXH_PRIME64_5);
        h64 = h64.rotate_left(11).wrapping_mul(XXH_PRIME64_1);
        offset += 1;
        len -= 1;
    }
    xxh64_avalanche(h64)
}

// xxh64 finalize - public interface matches interface file
pub fn xxh64_finalize(mut h64: XXHU64, ptr: &mut XXHU8, len: usize) -> XXHU64 {
    let slice = slice_from_mut_u8(ptr, len);
    xxh64_finalize_inner(h64, slice, len)
}

// xxh64 endian align - internal version working with &[u8]
fn xxh64_endian_align_inner(input: &[u8], len: usize, seed: XXHU64) -> XXHU64 {
    let mut offset = 0;
    let mut v1 = seed.wrapping_add(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_2);
    let mut v2 = seed.wrapping_add(XXH_PRIME64_2);
    let mut v3 = seed;
    let mut v4 = seed.wrapping_sub(XXH_PRIME64_1);
    let mut h64 = if len >= 32 {
        let limit = len - 32;
        while offset <= limit {
            v1 = xxh64_round(v1, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v2 = xxh64_round(v2, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v3 = xxh64_round(v3, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v4 = xxh64_round(v4, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
        }
        v1.rotate_left(1)
            .wrapping_add(v2.rotate_left(7))
            .wrapping_add(v3.rotate_left(12))
            .wrapping_add(v4.rotate_left(18))
    } else {
        seed.wrapping_add(XXH_PRIME64_5)
    };
    h64 = xxh64_merge_round(h64, v1);
    h64 = xxh64_merge_round(h64, v2);
    h64 = xxh64_merge_round(h64, v3);
    h64 = xxh64_merge_round(h64, v4);
    h64 = h64.wrapping_add(len as XXHU64);
    xxh64_finalize_inner(h64, &input[offset..], len)
}

// xxh64 endian align - public interface matches interface file
pub fn xxh64_endian_align(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    let slice = slice_from_mut_u8(input, len);
    xxh64_endian_align_inner(slice, len, seed)
}

// xxh64 endian align h - internal version working with &[u8]
fn xxh64_endian_align_h_inner(input: &[u8], len: usize, seed: XXHU64) -> XXHU64 {
    let mut offset = 0;
    let mut v1 = seed.wrapping_add(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_2);
    let mut v2 = seed.wrapping_sub(XXH_PRIME64_2);
    let mut v3 = seed.wrapping_add(XXH_PRIME64_3);
    let mut v4 = seed.wrapping_sub(XXH_PRIME64_1);
    let mut h64 = if len >= 32 {
        let limit = len - 32;
        while offset <= limit {
            v1 = xxh64_round(v1, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v2 = xxh64_round(v2, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v3 = xxh64_round(v3, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
            v4 = xxh64_round(v4, xxh_read_le64_from_slice(&input[offset..offset + 8]));
            offset += 8;
        }
        v1.rotate_left(1)
            .wrapping_add(v2.rotate_left(7))
            .wrapping_add(v3.rotate_left(12))
            .wrapping_add(v4.rotate_left(18))
    } else {
        seed.wrapping_add(XXH_PRIME64_1)
    };
    h64 = xxh64_merge_round(h64, v1);
    h64 = xxh64_merge_round(h64, v2);
    h64 = xxh64_merge_round(h64, v3);
    h64 = xxh64_merge_round(h64, v4);
    h64 = h64.wrapping_add(len as XXHU64);
    xxh64_finalize_inner(h64, &input[offset..], len)
}

// xxh64 endian align h - public interface matches interface file
pub fn xxh64_endian_align_h(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    let slice = slice_from_mut_u8(input, len);
    xxh64_endian_align_h_inner(slice, len, seed)
}

// xxh64 - keep raw pointer signature as required by interface
#[allow(clippy::not_unsafe_ptr_arg_deref)]
pub fn xxh64(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    let slice = slice_from_raw_ptr(input, len);
    xxh64_endian_align_inner(slice, len, seed)
}

// xxh64_h - keep raw pointer signature as required by interface
#[allow(clippy::not_unsafe_ptr_arg_deref)]
pub fn xxh64_h(input: *const u8, len: usize, seed: XXH64HashT) -> XXH64HashT {
    if input.is_null() || len == 0 {
        return 0;
    }
    let slice = slice_from_raw_ptr(input, len);
    xxh64_endian_align_h_inner(slice, len, seed)
}

// cset_hash1_callback - hash bytes using xxh64
pub fn cset_hash1_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    let slice = slice_from_mut_u8(memptr, size);
    xxh64_endian_align_inner(slice, size, CSET_DEFAULT_SEED)
}

// cset_hash2_callback - hash bytes using xxh64_h variant, OR'd with 1
pub fn cset_hash2_callback(memptr: &mut XXHU8, size: usize) -> XXHU64 {
    let slice = slice_from_mut_u8(memptr, size);
    xxh64_endian_align_h_inner(slice, size, CSET_DEFAULT_SEED) | 1
}
</replace>
</edit>