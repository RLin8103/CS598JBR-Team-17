**Hypothesis:** `xxh64_endian_align_inner` applies the four `xxh64_merge_round` calls on every input. Standard XXH64 (and the C code it mirrors) only does this when `len >= 32`. For shorter inputs the merge should be skipped, so `h64 = seed + PRIME64_5`, then `+ len`, then finalize.

Evidence: the failing `len=0 seed=0` case has C output `17241709254077376921` = `0xEF46DB3751D8E999`, the standard XXH64 value for the empty input. Our output differs, and the only divergence for short inputs is the unconditional merge. The same pattern (merges after the `else` branch) is the likely source of the `len=1..31` failures.

I'll move the merge into the `len >= 32` branch and leave the `h` variant untouched, since I can't verify its C definition from the truncated source.

<edit path="src/cset.rs">
<search>
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

// xxh64 endian align - public interface matches interface file</search>
<replace>fn xxh64_endian_align_inner(input: &[u8], len: usize, seed: XXHU64) -> XXHU64 {
    let mut offset = 0;
    let mut v1 = seed.wrapping_add(XXH_PRIME64_1).wrapping_add(XXH_PRIME64_2);
    let mut v2 = seed.wrapping_add(XXH_PRIME64_2);
    let mut v3 = seed;
    let mut v4 = seed.wrapping_sub(XXH_PRIME64_1);
    let h64 = if len >= 32 {
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
        let acc = v1
            .rotate_left(1)
            .wrapping_add(v2.rotate_left(7))
            .wrapping_add(v3.rotate_left(12))
            .wrapping_add(v4.rotate_left(18));
        let acc = xxh64_merge_round(acc, v1);
        let acc = xxh64_merge_round(acc, v2);
        let acc = xxh64_merge_round(acc, v3);
        xxh64_merge_round(acc, v4)
    } else {
        seed.wrapping_add(XXH_PRIME64_5)
    };
    let h64 = h64.wrapping_add(len as XXHU64);
    xxh64_finalize_inner(h64, &input[offset..], len)
}

// xxh64 endian align - public interface matches interface file</replace>
</edit>

Notes for next iteration:
- Hypothesis under test: short-input (`len < 32`) XXH64 was wrongly merging v1..v4. Expect `cset_hash_00`, `_01`, `_02`, `_07`, `_08`, `_15`, `_16`, `_31` to change; the `_32+` cases already pass.
- If `_00` (empty input) still fails, check `xxh64_finalize_inner` and `xxh64_avalanche` next.
- If only the `h` variant cases fail, its `else` seed constant or lane seeds need checking against the truncated C.
- Unsafe remains in `raw_bytes`, `copy_of`, `placeholder`, and `alias_mut`. Those are interface-forced (raw pointer params, missing `Default`/`Clone` bounds) and should be addressed after the hash results are correct.