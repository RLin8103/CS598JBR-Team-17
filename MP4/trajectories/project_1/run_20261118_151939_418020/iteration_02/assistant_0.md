The controller reports that the last reply applied no edit. Tests (15/15) and Clippy are clean. The remaining unsafe sites are forced by the frozen interface, as my earlier notes explain. This reply makes one small, behaviour-neutral clarification to the `placeholder` documentation, so the remaining unsafe is stated precisely. I am not declaring done, because the zero-unsafe goal is still unmet.

<edit path="src/cset.rs">
<search>
    // Placeholder element for slots that are never read (pi == 0 or -1).
    // Known limitation: the frozen interface gives no Default or Clone bound,
    // so a value of T must be produced bitwise. This is unsound for some T
    // (e.g. references, Box, NonNull). A safe design needs a bound such as
    // T: Default, which the public contract does not allow.
</search>
<replace>
    // Placeholder element for slots that are never read (pi == 0 or -1).
    // Known limitation: the frozen interface gives no Default or Clone bound,
    // so a value of T must be produced bitwise. An all-zero bit pattern is not
    // a valid value for every T (e.g. &U, Box<U>, NonNull<U>), so this is
    // unsound for those T. Removing the unsafe requires a bound such as
    // T: Default on the impl, which the frozen public contract forbids.
</replace>
</edit>

<notes>
Status: 15/15 tests pass, Clippy clean, 0 interface deviations.
Remaining unsafe (4 lines, 4 calls, 1 raw deref), each forced by the frozen interface:
- raw_bytes (from_raw_parts): xxh64/xxh64_h take *const u8.
- alias_mut (&mut *p): get_buckets_ref / get_temp_buckets_ref return &mut from &self.
- copy_of (ptr::read): index/iter/intersect etc. return owned T with no Clone bound.
- placeholder (mem::zeroed): empty slots need a T value with no Default bound.
Also: xxh64 callbacks take &mut u8, so they only hash one byte when len > 1 (faithfulness gap forced by signatures; tests do not hit it).
Lint allows (invalid_reference_casting, mut_from_ref, not_unsafe_ptr_arg_deref) exist only because of the same frozen signatures.
Conclusion: zero unsafe is not reachable under the frozen interface. Not declaring done.
</notes>