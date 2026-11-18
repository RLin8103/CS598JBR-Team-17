The failing cases are `xxh64_h` with `len < 32`. In the C `XXH64_endian_align_h`, the four `XXH64_mergeRound` calls happen only inside the `len >= 32` branch. The Rust port runs them unconditionally, so short inputs get extra mixing. Long inputs already match, which is consistent with the failure list. I'll move the merge rounds inside the long-input branch.

<notes>
Hypothesis: `xxh64_endian_align_h_inner` applies the four `xxh64_merge_round` calls outside the `len >= 32` branch. In C they live only inside it, so every input with len < 32 gets wrongly mixed. Failing tests are exactly the short `cset_hash_h` lengths (0-31), while 32+ pass. Fix: move the merges into the long branch and skip them for short inputs.
Remaining (not this turn): unsafe in raw_bytes, alias_mut, copy_of, placeholder, and the view_bytes limitation for hash callbacks with len > 1 (frozen signature takes &mut u8).
</notes>

<edit path="src/cset.rs">
<search>
    let mut h64 = if len >= 32 {
        let limit = len - 32;
</search>
<replace>    let h64 = if len >= 32 {
        let limit = len - 32;
</replace>
</edit>
<edit path="src/cset.rs">
<search>
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
</search>
<replace>        let acc = v1
            .rotate_left(1)
            .wrapping_add(v2.rotate_left(7))
            .wrapping_add(v3.rotate_left(12))
            .wrapping_add(v4.rotate_left(18));
        let acc = xxh64_merge_round(acc, v1);
        let acc = xxh64_merge_round(acc, v2);
        let acc = xxh64_merge_round(acc, v3);
        xxh64_merge_round(acc, v4)
    } else {
        seed.wrapping_add(XXH_PRIME64_1)
    };
    let h64 = h64.wrapping_add(len as XXHU64);
</replace>
</edit>