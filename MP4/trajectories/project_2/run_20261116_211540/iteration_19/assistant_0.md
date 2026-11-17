The remaining `read_test_vector` failure is in the protected test file, so I can't fix it from `src/*.rs` without special-casing. This edit is a behaviour-neutral cleanup: it replaces the wildcard `use crate::tx::*;` in `src/psbt.rs` with the two items the module actually uses.

<edit path="src/psbt.rs">
<search>use crate::tx::*;</search>
<replace>use crate::tx::{tx_io_counts, PsbtTxElem};</replace>
</edit>

<notes>
- read_test_vector fails only because src/bin/test.rs `checker` resets `step` to 0 on each call and asserts record_type == 0 for every record; record 3 is type 4. A faithful psbt_read delivers that record, so no honest src/*.rs change passes it. Fix needs a test-file change (keep the counter in user_data, or check only the first two records). src/bin/test.rs is protected.
- Clippy style warnings (uninlined_format_args line 6, single_match line 123) are in src/bin/test.rs; protected.
- Library follows C for header, records, tx counting, encodings, state machine. No unsafe code.
- Not declaring completion: tests and clippy are not clean until the test file changes.
</notes>