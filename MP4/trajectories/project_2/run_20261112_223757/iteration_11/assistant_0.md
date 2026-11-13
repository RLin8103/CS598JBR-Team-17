The remaining failure is still `read_test_vector`, and I'm not going to special-case it. The Rust checker starts `step` at 0 on every call and asserts `record_type == 0` for every record. The PSBT's second record is `PSBT_IN_REDEEM_SCRIPT` (type 4), so any faithful implementation that calls the handler for each record will fail that assertion. The C checker shares one counter across calls and only checks the first two records, so the two tests don't match.

This edit replaces an O(n) `chars().nth()` lookup in the hex decoder with a direct byte index. Behaviour on valid input is unchanged, and non-hex bytes are still rejected.

<edit path="src/psbt.rs">
<search>                let c2 = src.chars().nth(i + 1).unwrap();</search>
<replace>                let c2 = src.as_bytes()[i + 1] as char;</replace>
</edit>

<notes>
- Tests: 6/8 pass. The only failure is read_test_vector, which no faithful implementation can pass. Its checker (src/bin/test.rs) resets `step = 0` on every call, so it asserts record_type == 0 for every record. The second record in PSBT_HEX is PSBT_IN_REDEEM_SCRIPT (type 4), so the assertion fails. The C checker shares one counter and only checks the first two records. Special-casing would violate the rules. Needs a controller decision: accept as a test-spec defect or allow a test edit.
- Clippy: the 2 remaining style warnings are in src/bin/test.rs, which is read-only.
- psbt.rs: psbt_read counts inputs/outputs from the global unsigned tx via tx_io_counts, as in psbt.c. The hex decoder now indexes bytes directly (no quadratic char scan).
- cli.rs: decode -> read (prints records) -> base62 encode, mirroring cli.c. Not a tested target.
- Unsafe: none; tx.rs has #![forbid(unsafe_code)].
- Remaining: rustc warnings only (dead code/unused items).
</notes>