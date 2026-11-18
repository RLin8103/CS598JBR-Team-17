The first hash (`xxh64`) now matches C for short inputs. The remaining mismatch is the second value in each pair, which is the `xxh64_h` variant, so I need the C definition of that variant. The C header is truncated, so I'll read it before editing.

<notes>
- Iteration 3. Fixed: `xxh64` (non-h) now matches C for len < 32 (first value in each pair matches). Keep the merge-only-in-len>=32 change.
- Remaining failure: the `xxh64_h` variant (second value in each pair) differs for all len < 32 and sometimes for len >= 32 too. The C `_h` definition is in the truncated part of c_source/src/cset.h, so I am reading it before editing.
- Hypothesis: the `_h` lane seeds or short-input constant differ from C. Compare against the C body, not guesses.
- Unsafe sites (raw_bytes, alias_mut, copy_of, placeholder) are interface-forced; address after hashes are correct.
</notes>

<read path="c_source/src/cset.h"/>