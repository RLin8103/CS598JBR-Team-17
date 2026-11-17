The `read_test_vector` failure is still caused by the protected test, not the library. Its `checker` declares `let mut step = 0;` inside the callback, so `step` is always 0 and every record is asserted to have `record_type == 0`. The C test keeps its counter in `user_data` and only checks the first two callbacks. The Rust reader delivers the same records as C, and `PSBT_HEX` contains type-4 input records that C also delivers. Making this test pass would mean special-casing or editing `src/bin/test.rs`, and I can't do either, so I am not declaring completion.

This turn I fixed a stale doc comment on `psbt_encode`, which claimed only Hex is implemented. Hex, Base64 and Base62 are implemented, and Protobuf returns `NotImplemented` as in C.

<edit path="src/psbt.rs">
<search>
/// (Only Hex encoding is implemented for simplicity.)
</search>
<replace>/// Supports Hex, Base64 and Base62. Protobuf returns `NotImplemented`, as in C.
</replace>
</edit>

<notes>
- Blocker (unchanged, not fixable from our side): read_test_vector fails because the protected test in src/bin/test.rs declares `let mut step = 0;` inside the callback, so every record is asserted to have record_type==0. The C test keeps its counter in user_data and checks only callbacks 0 and 1. PSBT_HEX has type-4 input records that the reader correctly delivers. Fixing this needs a change to src/bin/test.rs (protected). Do not special-case, do not declare done.
- Review rounds 17-19: fixed the psbt_decode prefix panic (byte-level starts_with), clamped hex decode/encode destination checks to dest.len(), corrected a stale doc comment on psbt_encode. Reader, compactsize, base64/base62, tx parse and write paths match C; no further differences found.
- Clippy style warnings (uninlined format args, single_match) are in src/bin/test.rs (protected).
- Open, low priority: about 12 rustc warnings (dead code / unused items such as PsbtElemType and the TxElem variant) not triaged. Keep public items as in the interface.
- If the test file is ever fixed, rerun the suite and confirm 8/8, then declare done.
</notes>