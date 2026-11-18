The remaining failure looks like a defect in the test checker, not in the translation. `read_test_vector` asserts `record_type == 0` for every record, but the C vector contains input and output records whose types are nonzero. I'll confirm that against the checker code before deciding anything.

<read path="src/bin/test.rs" start="100" end="135"/>

<notes>
- Iteration 5: 6/8 tests pass. Only read_test_vector fails, at test.rs:126: `assert_eq!(record.record_type, 0)` gets 4 (IN_REDEEM_SCRIPT). Input and output records legitimately have nonzero types in the C vector.
- Hypothesis: the checker is wrong, since it applies the global-type assertion to every record. Not special-casing. Reading test.rs:100-135 to confirm the step counter logic.
- Clippy: 2 style warnings are in protected src/bin/test.rs (uninlined_format_args, single_match). Not fixable from our files.
- Compiler warnings (11) are in our files. Clean them up once the test outcome is settled.
- Open: encode/decode declared-length behaviour is covered by passing regression tests. Base64 decode dest limit is covered too.
- No source edits this turn.
</notes>