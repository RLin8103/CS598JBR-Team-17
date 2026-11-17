The `read_test_vector` failure is still a bug in the test, not in the reader. Its `checker` uses a fresh local `step` that is always 0, so it asserts `record_type == 0` on every callback. `PSBT_HEX` contains type-4 input records that the C reader delivers. Passing it would mean skipping records or special-casing the input, so I'm not doing either and I'm not declaring completion.

This turn I'm adding `#![forbid(unsafe_code)]` to the three module files that contain no unsafe code. This is the first-line enforcement the rules require, and it doesn't change behaviour.

<edit path="src/psbt.rs">
<search>
use crate::tx::*;
</search>
<replace>
#![forbid(unsafe_code)]
use crate::tx::*;
</replace>
</edit>
<edit path="src/compactsize.rs">
<search>
use crate::psbt::{PsbtResult, MAX_SERIALIZE_SIZE};
</search>
<replace>
#![forbid(unsafe_code)]
use crate::psbt::{PsbtResult, MAX_SERIALIZE_SIZE};
</replace>
</edit>
<edit path="src/base64.rs">
<search>
const BASE64_TABLE: &[u8; 64]</search>
<replace>
#![forbid(unsafe_code)]
const BASE64_TABLE: &[u8; 64]</replace>
</edit>

<notes>
- read_test_vector: test bug. Its checker uses a fresh local `step`, so it asserts record_type==0 for every callback, but PSBT_HEX has type-4 input records that the C reader must deliver. Not passable without special-casing. Do not special-case. Do not declare done.
- Done: hex decode rejects non-ASCII, uses byte indexing. psbt_read returns OobWrite when src_size > data_capacity, as C does. forbid(unsafe_code) added to psbt.rs, compactsize.rs, base64.rs.
- Clippy style warnings are in src/bin/test.rs (protected), so they cannot be cleared from our side.
- Open: base64 decode parity on short/padded input not yet reviewed; rustc unused-import warnings (e.g. PsbtElemType, base64 imports) still present and could be cleaned.
</notes>