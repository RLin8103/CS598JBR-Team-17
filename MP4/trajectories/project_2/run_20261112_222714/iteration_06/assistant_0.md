<notes>
## Plan

Fix the following compiler errors:
1. Fix BASE64_TABLE size (64 chars, not 65) - remove the trailing slash
2. Add Clone derive to PsbtRecord
3. Fix enum casting in psbt_type_tostr using match instead of as
4. Fix unused variable warning in psbt_init by prefixing with underscore
</notes>

<edit path="src/base64.rs">
<search>
const BASE64_TABLE: &[u8; 65] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
</search>
<replace>
const BASE64_TABLE: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
</replace>
</edit>