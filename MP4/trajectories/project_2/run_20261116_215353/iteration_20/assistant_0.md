The `read_test_vector` failure is still caused by the protected test, not the library. Its `checker` declares `let mut step = 0;` inside the callback, so `step` is always 0 and every record is asserted to have `record_type == 0`. The C test keeps its counter in `user_data` and checks only the first two callbacks. The Rust reader delivers the same records as C, including type-4 input records that the test's assertion rejects. Passing this test would require editing `src/bin/test.rs` or special-casing its data, and I can't do either, so I am not declaring completion.

This turn I only correct a doc comment on `psbt_read` that describes it as "for testing". It is the real reader, not a test shim.

<edit path="src/psbt.rs">
<search>
/// For testing, we simulate reading by optionally calling the provided callback.
</search>
<replace>/// Parse a PSBT from `src`, mirroring C `psbt_read`. Each record is passed to `elem_handler`, if given.
</replace>
</edit>

<notes>
- Blocker (unchanged, not fixable from our side): read_test_vector fails because the protected test in src/bin/test.rs declares `let mut step = 0;` inside the callback, so every record is asserted to have record_type==0. The C test keeps its counter in user_data and checks only callbacks 0 and 1. PSBT_HEX has type-4 input records that the reader correctly delivers. Fixing this needs a change to src/bin/test.rs (protected). Do not special-case, do not declare done.
- Review rounds 17-20: fixed the psbt_decode prefix panic, clamped hex decode/encode destination checks to dest.len(), corrected stale doc comments on psbt_encode and psbt_read. Reader, compactsize, base64/base62, tx parse and write paths match C; no further differences found.
- Clippy style warnings (uninlined format args, single_match) are in src/bin/test.rs (protected).
- Open, low priority: about 12 rustc warnings (dead code / unused items such as PsbtElemType and the TxElem variant) not triaged. Keep public items as in the interface.
- If the test file is ever fixed, rerun the suite and confirm 8/8, then declare done.
</notes>