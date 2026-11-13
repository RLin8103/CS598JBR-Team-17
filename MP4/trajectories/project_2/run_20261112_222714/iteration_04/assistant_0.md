<notes>
## Plan

Fix the following compiler errors:
1. Add `MAX_SERIALIZE_SIZE` import to compactsize.rs
2. Add base64 imports to psbt.rs
3. Fix BASE64_TABLE size (64 vs 65)
4. Add Clone derive to PsbtRecord
5. Fix enum casting in psbt_type_tostr
6. Fix unused variable warning in psbt_init
</notes>

<edit path="src/compactsize.rs">
<search>
use crate::psbt::PsbtResult;
</search>
<replace>
use crate::psbt::{PsbtResult, MAX_SERIALIZE_SIZE};
</replace>
</edit>