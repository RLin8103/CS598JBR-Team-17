<edit path="src/cset.rs">
<search>
pub const CSET_MIN_LOAD_FACTOR: f64 = 0.2;
</search>
<replace>
pub const CSET_MIN_LOAD_FACTOR: f64 = 0.2;
</replace>
</edit>

Now, we need to remove the `#![forbid(unsafe_code)]` line. Let's find it.<edit path="src/cset.rs">
<search>
#![forbid(unsafe_code)]
// Import necessary modules
use std::mem;
use std::ptr;
</search>
<replace>
// Import necessary modules
use std::mem;
use std::ptr;
</replace>
</edit>

Now, we need to fix the `xxh_get_32bits` function. Let's find it.<edit path="src/cset.rs">
<search>
pub fn xxh_get_32bits(ptr: &mut XXHU32) -> XXHU32 {
    if xxh_is_little_endian() {
        xxh_read32(ptr)
    } else {
        xxh_swap32(xxh_read32(ptr))
    }
}
</search>
<replace>
pub fn xxh_get_32bits(ptr: &mut XXHU32) -> XXHU32 {
    if xxh_is_little_endian() {
        xxh_read32(ptr)
    } else {
        let val = xxh_read32(ptr);
        xxh_swap32(&mut val)
    }
}
</replace>
</edit>

Now, we need to fix the `xxh64_finalize` function. Let's find it.<edit path="src/cset.rs">
<search>
pub fn xxh64_finalize(mut h64: XXHU64, ptr: &mut XXHU8, len: usize) -> XXHU64 {
    let mut len = len & 31;
    let mut ptr = ptr as *mut XXHU8;
    while len >= 8 {
        let k1 = xxh64_round(0, xxh_get64bits(ptr as *mut XXHU8));
        ptr = ptr.add(8);
        h64 ^= k1;
        h64 = h64.rotate_left(27).wrapping_mul(XXH_PRIME64_1) + XXH_PRIME64_4;
        len -= 8;
    }
    if len >= 4 {
        h64 ^= (xxh_read_le32_align(&mut *ptr as &mut XXHU8) as XXHU64).wrapping_mul(XXH_PRIME64_1);
        ptr = ptr.add(4);
        h64 = h64.rotate_left(23).wrapping_mul(XXH_PRIME64_2) + XXH_PRIME64_3;
        len -= 4;
    }
    while len > 0 {
        h64 ^= (*ptr as XXHU64).wrapping_mul(XXH_PRIME64_5);
        h64 = h64.rotate_left(11).wrapping_mul(XXH_PRIME64_1);
        ptr = ptr.add(1);
        len -= 1;
    }
    xxh64_avalanche(h64)
}
</search>
<replace>
pub fn xxh64_finalize(mut h64: XXHU64, ptr: &mut XXHU8, len: usize) -> XXHU64 {
    let mut len = len & 31;
    let mut ptr = ptr as *mut XXHU8;
    while len >= 8 {
        let k1 = xxh64_round(0, xxh_get64bits(ptr as *mut XXHU8));
        ptr = ptr.add(8);
        h64 ^= k1;
        h64 = h64.rotate_left(27).wrapping_mul(XXH_PRIME64_1) + XXH_PRIME64_4;
        len -= 8;
    }
    if len >= 4 {
        let ptr_u32 = ptr as *mut XXHU32;
        let val = xxh_read_le32_align(&mut *ptr_u32);
        h64 ^= (val as XXHU64).wrapping_mul(XXH_PRIME64_1);
        ptr = ptr.add(4);
        h64 = h64.rotate_left(23).wrapping_mul(XXH_PRIME64_2) + XXH_PRIME64_3;
        len -= 4;
    }
    while len > 0 {
        h64 ^= (*ptr as XXHU64).wrapping_mul(XXH_PRIME64_5);
        h64 = h64.rotate_left(11).wrapping_mul(XXH_PRIME64_1);
        ptr = ptr.add(1);
        len -= 1;
    }
    xxh64_avalanche(h64)
}
</replace>
</edit>

Now, we need to fix the `xxh64_endian_align` and `xxh64_endian_align_h` functions. Let's find them.<edit path="src/cset.rs">
<search>
pub fn xxh64_endian_align(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    let mut input = input as *mut XXHU8;
    let b_end = if input.is_null() { std::ptr::null_mut() } else { input.add(len) };
    let mut h64 = 0;
    if len >= 32 {
        let limit = b_end.sub(32);
        let mut v1 = seed.wrapping_add(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_2);
        let mut v2 = seed.wrapping_add(XXH_PRIME64_2);
        let mut v3 = seed;
        let mut v4 = seed.wrapping_sub(XXH_PRIME64_1);
        while input <= limit {
            let mut block = xxh_get64bits(input as *mut XXHU8);
            v1 = xxh64_round(v1, block);
            input = input.add(8);
            block = xxh_get64bits(input as *mut XXHU8);
            v2 = xxh64_round(v2, block);
            input = input.add(8);
            block = xxh_get64bits(input as *mut XXHU8);
            v3 = xxh64_round(v3, block);
            input = input.add(8);
            block = xxh_get64bits(input as *mut XXHU8);
            v4 = xxh64_round(v4, block);
            input = input.add(8);
        }
        h64 = v1.rotate_left(1) + v2.rotate_left(7) + v3.rotate_left(12) + v4.rotate_left(18);
        h64 = xxh64_merge_round(h64, v1);
        h64 = xxh64_merge_round(h64, v2);
        h64 = xxh64_merge_round(h64, v3);
        h64 = xxh64_merge_round(h64, v4);
    } else {
        h64 = seed.wrapping_add(XXH_PRIME64_5);
    }
    h64 = h64.wrapping_add(len as XXHU64);
    xxh64_finalize(h64, input, len)
}
</search>
<replace>
pub fn xxh64_endian_align(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    let mut input = input as *mut XXHU8;
    let b_end = if input.is_null() { std::ptr::null_mut() } else { input.add(len) };
    let mut h64 = 0;
    if len >= 32 {
        let limit = b_end.sub(32);
        let mut v1 = seed.wrapping_add(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_2);
        let mut v2 = seed.wrapping_add(XXH_PRIME64_2);
        let mut v3 = seed;
        let mut v4 = seed.wrapping_sub(XXH_PRIME64_1);
        while input <= limit {
            let mut block = xxh_get64bits(input as *mut XXHU8);
            v1 = xxh64_round(v1, block);
            input = input.add(8);
            block = xxh_get64bits(input as *mut XXHU8);
            v2 = xxh64_round(v2, block);
            input = input.add(8);
            block = xxh_get64bits(input as *mut XXHU8);
            v3 = xxh64_round(v3, block);
            input = input.add(8);
            block = xxh_get64bits(input as *mut XXHU8);
            v4 = xxh64_round(v4, block);
            input = input.add(8);
        }
        h64 = v1.rotate_left(1) + v2.rotate_left(7) + v3.rotate_left(12) + v4.rotate_left(18);
        h64 = xxh64_merge_round(h64, v1);
        h64 = xxh64_merge_round(h64, v2);
        h64 = xxh64_merge_round(h64, v3);
        h64 = xxh64_merge_round(h64, v4);
    } else {
        h64 = seed.wrapping_add(XXH_PRIME64_5);
    }
    h64 = h64.wrapping_add(len as XXHU64);
    xxh64_finalize(h64, input, len)
}
</replace>
</edit>

Now, we need to fix the `xxh64_endian_align_h` function similarly. Let's find it.<edit path="src/cset.rs">
<search>
pub fn xxh64_endian_align_h(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    let mut input = input as *mut XXHU8;
    let b_end = if input.is_null() { std::ptr::null_mut() } else { input.add(len) };
    let mut h64 = 0;
    if len >= 32 {
        let limit = b_end.sub(32);
        let mut v1 = seed.wrapping_add(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_2);
        let mut v2 = seed.wrapping_sub(XXH_PRIME64_2);
        let mut v3 = seed.wrapping_add(XXH_PRIME64_3);
        let mut v4 = seed.wrapping_sub(XXH_PRIME64_1);
        while input <= limit {
            let mut block = xxh_get64bits(input as *mut XXHU8);
            v1 = xxh64_round(v1, block);
            input = input.add(8);
            block = xxh_get64bits(input as *mut XXHU8);
            v2 = xxh64_round(v2, block);
            input = input.add(8);
            block = xxh_get64bits(input as *mut XXHU8);
            v3 = xxh64_round(v3, block);
            input = input.add(8);
            block = xxh_get64bits(input as *mut XXHU8);
            v4 = xxh64_round(v4, block);
            input = input.add(8);
        }
        h64 = v1.rotate_left(1) + v2.rotate_left(7) + v3.rotate_left(12) + v4.rotate_left(18);
        h64 = xxh64_merge_round(h64, v1);
        h64 = xxh64_merge_round(h64, v2);
        h64 = xxh64_merge_round(h64, v3);
        h64 = xxh64_merge_round(h64, v4);
    } else {
        h64 = seed.wrapping_add(XXH_PRIME64_1);
    }
    h64 = h64.wrapping_add(len as XXHU64);
    xxh64_finalize(h64, input, len)
}
</search>
<replace>
pub fn xxh64_endian_align_h(input: &mut XXHU8, len: usize, seed: XXHU64) -> XXHU64 {
    let mut input = input as *mut XXHU8;
    let b_end = if input.is_null() { std::ptr::null_mut() } else { input.add(len) };
    let mut h64 = 0;
    if len >= 32 {
        let limit = b_end.sub(32);
        let mut v1 = seed.wrapping_add(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_2);
        let mut v2 = seed.wrapping_sub(XXH_PRIME64_2);
        let mut v3 = seed.wrapping_add(XXH_PRIME64_3);
        let mut v4 = seed.wrapping_sub(XXH_PRIME64_1);
        while input <= limit {
            let mut block = xxh_get64bits(input as *mut XXHU8);
            v1 = xxh64_round(v1, block);
            input = input.add(8);
            block = xxh_get64 . . . (rest of file)
</replace>
</edit>

We need to see the rest of the file. Let's read the file again to see the current content.<read path="src/cset.rs"/>