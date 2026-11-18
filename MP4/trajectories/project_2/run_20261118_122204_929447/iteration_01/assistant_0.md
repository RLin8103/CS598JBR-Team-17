## Diagnosis

The failing test is `read_test_vector`. Its callback asserts `record_type == 0` for every record it sees, because `step` is a local variable reset on each call. The PSBT contains an input record of type 4 (redeem script, `0104 47 5221...` in the hex), so that assertion cannot hold for a faithful parser. This part is a benchmark defect in the test's checker and I am leaving it unresolved.

The harness output shows a real bug in the Rust reader. In the C code, `kvs` is only incremented at the zero separator of an input or output map, and it resets to 0 when a new map starts. The Rust code also does `kvs += 1` after every record. That is why the indices come out as `Global:1`, `Inputs:2`, and `Outputs:0:4`, and why the record totals are `[2, 2, 2]` instead of `[2, 4, 4]`. Removing the per-record increment should restore the C index semantics: `Global:0`, `Inputs:0`, `Inputs:1`, and so on.

## Edit

Remove the per-record `kvs += 1`. The separator branch already increments `kvs` and resets it when moving to the next output map, as the C code does.

<edit path="src/psbt.rs">
<search>
                        handler(&mut elem, user_data);
                    }
                    kvs += 1;
</search>
<replace>
                        handler(&mut elem, user_data);
                    }
</replace>
</edit>

<notes>
Hypothesis: the reader wrongly increments `kvs` for every record. C increments `kvs` only at map separators (0x00 in INPUTS/OUTPUTS), resetting it when the outputs map begins. Removing the per-record increment should fix the index and count mismatches in the record-callback and multi-map tests.
read_test_vector: its checker asserts record_type == 0 for every record (step is reset per call), but the fixture has an input record of type 4 (PSBT_IN_REDEEM_SCRIPT). This is a suspected benchmark defect in the test, not a translation bug. Leave it unresolved and report it.
Next: rerun, then check the multi-map/record-callback failures. Also check the encode/decode prefix and source-length failures, which look like they ignore declared sizes (src_size/dest capacity limits).
Clippy style warnings are only in the test file (protected), so they cannot be fixed by editing src.
</notes>