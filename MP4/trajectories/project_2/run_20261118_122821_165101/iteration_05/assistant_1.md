The checker is defective, and I can't make this test pass without special-casing it, so I'm making no source edits.

The checker's `step` variable is declared inside `checker` (`let mut step = 0;`), so it is reset to 0 on every call. Every record therefore has to have `record_type == 0`. The C vector contains input records with other types (the failing record has type 4, IN_REDEEM_SCRIPT). The C `test.c` callback does not assert this for every record. Our translation delivers the records in the same order and with the same types as the C parser, so the mismatch comes from the Rust test. Making it pass would mean skipping or altering the callbacks for non-global records, which is test-data special-casing and violates the faithful-translation rule. I'm leaving it as an unresolved benchmark defect.

<notes>
- Iteration 6 (final-ish): 7/8 expected to pass; read_test_vector remains failing.
- Confirmed defect in src/bin/test.rs:111-131: `let mut step = 0;` is local to `checker`, so `step` is always 0 and `record_type == 0` is asserted for every record. The C vector has input records with type 4 (IN_REDEEM_SCRIPT), so the assertion fails on a legitimate record. The C handler has no such constraint.
- Counterexample: psbt_read on PSBT_HEX calls the handler with a record of type 4 (scope Inputs), which is correct per C psbt_read_record. Changing the parser to avoid this would be special-casing.
- Not special-casing: no edits made. Protected file test.rs cannot be changed.
- Clippy: 2 style warnings in src/bin/test.rs (protected). Our files are clippy-clean.
- Remaining work: clean the 11 rustc warnings in our files (unused items/variables) without changing public signatures.
</notes>