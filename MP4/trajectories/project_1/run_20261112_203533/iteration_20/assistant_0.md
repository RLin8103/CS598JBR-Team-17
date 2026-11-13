<edit path="src/cset.rs">
<search>
h64 = h64.wrapping_add(len as XXHU64);
    xxh64_finalize(h64, &input[offset..], len)
// xxh64 endian align h - works with slice
</search>
<replace>
h64 = h64.wrapping_add(len as XXHU64);
    xxh64_finalize(h64, &input[offset..], len)
}

// xxh64 endian align h - works with slice
</replace>
</edit>