This is the last iteration. The current snapshot compiles, and the rejected edit was reverted. The one fix I can make safely and in isolation is the global-type label: `psbt_type_tostr` ignores `record_type` for the Global scope, so an unknown global type prints `GLOBAL_UNSIGNED_TX`. The C code returns `UNKNOWN_GLOBAL_TYPE` for any value other than 0. The change is local to one match arm and does not touch the destination-buffer code that caused the build failure.

<edit path="src/psbt.rs">
<search>
        PsbtScope::Global => psbt_global_type_tostr(PsbtGlobalType::UnsignedTx),
</search>
<replace>
        PsbtScope::Global => match record_type {
            0 => psbt_global_type_tostr(PsbtGlobalType::UnsignedTx),
            _ => "UNKNOWN_GLOBAL_TYPE",
        },
</replace>
</edit>

<notes>
- Iteration 3 (final). The snapshot compiles; last rejected edit (borrow error in psbt_decode/psbt_encode_raw `let dest = &mut dest[..dest_size.min(dest.len())]`) was reverted, so it is not applied.
- This edit: Global-scope type label now returns UNKNOWN_GLOBAL_TYPE for record types other than 0, matching the C psbt_global_type_tostr default.
- Still open, not fixed: read_test_vector asserts record_type == 0 for every record, but the fixture contains a type-4 record. Suspected benchmark defect; not special-cased.
- Still open from the regression harness: several tests fail on destination/source-length honouring (decode/encode prefix and declared-limit checks), psbt_geterr returns a fixed string (no error context), and callbacks for transaction elements are not emitted before the unsigned-tx record. These need a fresh, carefully scoped pass beyond this iteration.
- Clippy: the two style warnings are in protected src/bin/test.rs and cannot be changed by me.
</notes>