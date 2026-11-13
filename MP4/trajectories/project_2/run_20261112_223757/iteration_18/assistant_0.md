The state is unchanged. Six of eight tests pass, and `read_test_vector` is still the only failure.

The checker in `src/bin/test.rs` declares `let mut step = 0;` inside the function, so every call asserts `record_type == 0`. The second record in `PSBT_HEX` is a type-4 redeem script, so the assertion fails. Making this pass would mean either special-casing the test data or changing what the handler receives, which would diverge from `psbt.c`. Neither is acceptable without your decision. The only faithful options are:
1. Accept `read_test_vector` as a test-spec defect.
2. Permit editing `src/bin/test.rs` so `step` is shared across calls, as in the C test.

I still don't have the text of the ~11 rustc warnings, so I'm not guessing at fixes. This turn I'm only adding the `forbid(unsafe_code)` attribute to `psbt.rs`, which I had listed as pending.

<edit path="src/psbt.rs">
<search>
use crate::tx::*;
use crate::compactsize::{compactsize_read, compactsize_length, compactsize_write, compactsize_peek_length};</search>
<replace>#![forbid(unsafe_code)]

use crate::tx::*;
use crate::compactsize::{compactsize_read, compactsize_length, compactsize_write, compactsize_peek_length};</replace>
</edit>

<notes>
- Tests: 6/8 pass. read_test_vector is the only failure and cannot pass without special-casing. The checker in src/bin/test.rs declares `step` inside the function, so every call asserts record_type == 0. PSBT_HEX has a type-4 record, which fails that assertion. The C checker shares its counter and checks only the first two records.
- Decision needed from the controller: (a) accept as a test-spec defect, or (b) permit editing src/bin/test.rs so `step` is shared across calls. I will not special-case, and I will not filter the handler by scope because that diverges from psbt.c.
- Clippy: the 2 remaining style warnings are in src/bin/test.rs (read-only).
- rustc: about 11 dead-code/unused warnings. I need the exact compiler output to fix them.
- psbt.rs: psbt_read counts inputs and outputs from the global unsigned tx via tx_io_counts, as psbt.c does. The handler is called for every record, as psbt.c does.
- cli.rs: decode, read (prints records), base62 encode, mirroring cli.c. Not a tested target.
- Unsafe: none. base64.rs, compactsize.rs, psbt.rs and tx.rs carry #![forbid(unsafe_code)]. cli.rs still needs it.
</notes>