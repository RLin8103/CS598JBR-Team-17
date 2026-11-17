<notes>
- Fix syntax error in xxh64_endian_align (extra closing brace on line 141)
- Remove generic bound `T: Clone` from impl blocks to match interface
- Fix unsafe code by using safe alternatives where possible
</notes>

<file path="src/cset.rs">[608 lines omitted from history; see current files]</file>