The state is unchanged: 6 of 8 tests pass, and `read_test_vector` is the only failure. I still can't fix it without special-casing. Its checker in `src/bin/test.rs` asserts `record_type == 0` for every record, but the second record in `PSBT_HEX` is a type-4 redeem script. The C checker never reaches that assertion because it shares one `step` counter across calls.

I also still don't have the text of the ~11 rustc warnings, so I'm not guessing at fixes. The edit below follows the hard rules: `base64.rs` and `compactsize.rs` contain no unsafe code, so each gets `#![forbid(unsafe_code)]` as its first line. It has no behavioural effect.

<edit path="src/base64.rs">
<search>const BASE64_TABLE: &[u8; 64] =</search>
<replace>#![forbid(unsafe_code)]
const BASE64_TABLE: &[u8; 64] =</replace>
</edit>

<edit path="src/compactsize.rs">
<search>use crate::psbt::{PsbtResult, MAX_SERIALIZE_SIZE};</search>
<replace>#![forbid(unsafe_code)]
use crate::psbt::{PsbtResult, MAX_SERIALIZE_SIZE};</replace>
</edit>

<notes>
- Tests: 6/8 pass. read_test_vector is the only failure and cannot pass without special-casing. The checker in src/bin/test.rs resets `step` per call and asserts record_type == 0 for every record. PSBT_HEX has a type-4 record, which fails that assertion. The C checker shares its counter and checks only the first two records.
- Decision needed from the controller: accept as a test-spec defect, or permit editing src/bin/test.rs (for example, sharing `step` across calls as the C test does). I will not special-case.
- Clippy: the 2 remaining style warnings are in src/bin/test.rs (read-only).
- rustc: about 11 dead-code/unused warnings. I need the exact compiler output to fix them. Candidates I have not verified: never-constructed `PsbtElem::TxElem`, unused `PsbtElemType`/`PsbtTxElemType` variants, and unused `write_pos`/`records` paths.
- psbt.rs: psbt_read counts inputs and outputs from the global unsigned tx via tx_io_counts, as psbt.c does. The handler is called for every record, as psbt.c does.
- cli.rs: decode, read (prints records), base62 encode, mirroring cli.c. Not a tested target.
- Unsafe: none. base64.rs, compactsize.rs and tx.rs carry #![forbid(unsafe_code)]. psbt.rs and cli.rs should get the same attribute next.
</notes>