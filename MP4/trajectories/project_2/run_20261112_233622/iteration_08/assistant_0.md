The test failure is still the protected test's `step` checker, so this iteration only makes a small robustness fix in `src/psbt.rs`. `psbt_decode` calls `unwrap()` on `chars().nth(i + 1)`. The odd-length check already rejects bad input, but the `unwrap` is still a panic path on what should be a recoverable error. A missing second character now maps to `'\0'`, which `hex_to_val` rejects with `ReadError`.

<edit path="src/psbt.rs">
<search>
                let c2 = src.chars().nth(i + 1).unwrap();
</search>
<replace>
                let c2 = src.chars().nth(i + 1).unwrap_or('\0');
</replace>
</edit>

<notes>
- All stubs are implemented; no unimplemented!() left. Unsafe count is zero; all modules forbid unsafe_code.
- 6/8 tests pass. `read_test_vector` fails because the protected src/bin/test.rs checker asserts `record_type == 0` for every record (local `step` is always 0), and the PSBT has type-4 input records. This is a test bug. Do not special-case it.
- Clippy in src is clean. The 2 style warnings are in the protected test.rs.
- TODO: the 11 rustc warnings are not clippy warnings; inspect them with `cargo build` output and fix if they come from src/*.rs (unused variables or imports).
- psbt_decode hex path now avoids unwrap (unwrap_or('\0') then ReadError). Could be rewritten to iterate bytes in pairs for O(n) performance.
</notes>