Nothing has changed since the last iteration. Six of eight tests pass, and `read_test_vector` is still the only failure. Its checker in `src/bin/test.rs` declares `step` inside the function, so each call asserts `record_type == 0`. The second record in `PSBT_HEX` is a type-4 redeem script, so that assertion fails. Passing it would require special-casing the test data or filtering the handler by scope, which diverges from `psbt.c`. I won't do either.

This turn I'm adding the last missing `forbid(unsafe_code)` attribute, to `cli.rs`. That makes every module in the crate unsafe-free and compiler-enforced. It has no behavioural effect.

I also still don't have the text of the ~11 rustc warnings, so I'm not guessing at fixes for them.

<edit path="src/cli.rs">
<search>use crate::psbt::{</search>
<replace>#![forbid(unsafe_code)]

use crate::psbt::{</replace>
</edit>

<notes>
- Tests: 6/8 pass. read_test_vector is the only failure and cannot pass without special-casing. The checker in src/bin/test.rs declares `step` inside the function, so every call asserts record_type == 0. PSBT_HEX has a type-4 record, which fails that assertion. The C checker shares its counter and checks only the first two records.
- Decision needed from the controller: (a) accept as a test-spec defect, or (b) permit editing src/bin/test.rs so `step` is shared across calls, as the C test does. I will not special-case, and I will not filter the handler by scope because that diverges from psbt.c.
- Clippy: the 2 remaining style warnings are in src/bin/test.rs (read-only).
- rustc: about 11 dead-code/unused warnings. I still need the exact compiler output to fix them.
- psbt.rs: psbt_read counts inputs and outputs from the global unsigned tx via tx_io_counts, as psbt.c does. The handler is called for every record, as psbt.c does.
- cli.rs: decode, read (prints records), base62 encode, mirroring cli.c. Not a tested target.
- Unsafe: none. All six source files now carry #![forbid(unsafe_code)] (base64, compactsize, cli, psbt, tx; lib.rs and the test binary are protected).
</notes>