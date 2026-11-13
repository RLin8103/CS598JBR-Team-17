<notes>
## Plan

Fix the following compiler errors:
1. Add base64 imports to psbt.rs
2. Fix BASE64_TABLE size (64 vs 65) - the string is 64 chars, not 65
3. Add Clone derive to PsbtRecord
4. Fix enum casting in psbt_type_tostr using match instead of as
5. Fix unused variable warning in psbt_init by prefixing with underscore
</notes>

<edit path="src/psbt.rs">
<search>
use crate::tx::*;
use crate::compactsize::{compactsize_read, compactsize_length, compactsize_write, compactsize_peek_length};
use std::fmt;
</search>
<replace>
use crate::tx::*;
use crate::compactsize::{compactsize_read, compactsize_length, compactsize_write, compactsize_peek_length};
use crate::base64::{base64_encode, base64_decode, base62_encode};
use std::fmt;
</replace>
</edit>