The state is unchanged. Six of eight tests pass, and `read_test_vector` is still the only failure. I can't make it pass without special-casing. Its checker in `src/bin/test.rs` asserts `record_type == 0` for every record, but the second record in `PSBT_HEX` is a type-4 redeem script. The C checker shares one `step` counter across calls and only checks the first two records, so the Rust port can't reproduce that behaviour without changing the test.

I also still don't have the text of the ~11 rustc warnings. Without that I can't target them, so I'm not guessing at fixes. Please send the warning output, or a decision on whether `src/bin/test.rs` may be changed to share `step` across calls (as the C test does).

The edit below is documentation only. It has no behavioural effect.

<edit path="src/cli.rs">
<search>fn main() -> i32 {</search>
<replace>/// Decode, read, print and re-encode a PSBT given as the first argument (mirrors cli.c).
fn main() -> i32 {</replace>
</edit>

<notes>
- Tests: 6/8 pass. read_test_vector is the only failure and cannot pass without special-casing. The checker in src/bin/test.rs resets `step` per call and asserts record_type == 0 for every record. PSBT_HEX has a type-4 record, which fails that assertion. The C checker shares its counter and checks only the first two records.
- Decision needed from the controller: accept as a test-spec defect, or permit editing the read-only test file (for example, sharing `step` across calls). I will not special-case.
- Clippy: the 2 remaining style warnings are in src/bin/test.rs (read-only).
- rustc: about 11 dead-code/unused warnings. I need the exact compiler output to fix them. Likely candidates are unused imports in psbt.rs and dead functions reachable only through the private `cli` module, but I have not verified this.
- psbt.rs: psbt_read counts inputs and outputs from the global unsigned tx via tx_io_counts, as psbt.c does. The handler is called for every record, as psbt.c does.
- cli.rs: decode, read (prints records), base62 encode, mirroring cli.c. Not a tested target.
- Unsafe: none. tx.rs has #![forbid(unsafe_code)].
</notes>